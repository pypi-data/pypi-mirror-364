import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import json
import math
from openai import OpenAI
from . import config
from concurrent.futures import ThreadPoolExecutor, as_completed

class APIService:
    def __init__(self, api_key=None, api_url=None, model_name=None):
        self.api_key = api_key or config.API_KEY
        self.api_url = api_url or config.API_URL
        self.model_name = model_name or config.MODEL_NAME
        self.client = OpenAI(base_url=self.api_url, api_key=self.api_key)

    def fetch_road_info(self, roadName, roadLocation, json_template=None):
        # 兼容传入json_template参数
        if json_template is None:
            json_template = json.dumps(config.JSON_TEMPLATE, ensure_ascii=False)
        # 修复: roadName 可能包含 float(nan)，需全部转为字符串并过滤 nan
        road_names_string = "和".join(
            str(x) for x in roadName if not (isinstance(x, float) and math.isnan(x))
        )

        print(f"请求模型 {self.model_name} 处理道路名称: {road_names_string}，位置: {roadLocation}")
        try:
            # 兼容模板无参数的情况
            try:
                system_prompt = config.SYSTEM_PROMPT_TEMPLATE.format(
                    road_location=roadLocation,
                    json_template=json_template
                )
            except Exception:
                system_prompt = config.SYSTEM_PROMPT_TEMPLATE
            try:
                user_prompt = config.USER_PROMPT_TEMPLATE.format(
                    road_names_string=road_names_string
                )
            except Exception:
                user_prompt = config.USER_PROMPT_TEMPLATE
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                response_format={
                    "type": "json_object"
                },
                seed=42
            )
            if not completion.choices or not completion.choices[0].message:
                print("API响应格式不正确")
                return None
            return completion.choices[0].message.content
        except Exception as e:
            import traceback
            print(f"API请求失败：{str(e)}")
            traceback.print_exc()

class AIClientManager:
    def __init__(self):
        self.model_configs = {
            name: {
                "api_key": config.API_KEY,
                "api_url": config.API_URL,
                "model_name": config.MODEL_NAME
            }
            for name in ["deepseek"]
        }
        self.max_workers = config.MAX_WORKERS

    def ask_all_models(self, roadNames, roadLocation, json_template=config.JSON_TEMPLATE, batch_size=10):
        """
        并行调用所有配置的AI模型，获取各自的道路信息识别结果。

        参数：
            roadNames (list): 需要处理的道路名称列表。
            json_template (dict): 用于API请求的JSON模板。

        返回：
            dict: 每个模型名称为键，对应模型返回结果为值的字典。
        """
        def batch_list(lst, batch_size):
            for i in range(0, len(lst), batch_size):
                yield lst[i:i+batch_size]

        results = {}
        def call_model(model_name, cfg):
            api_service = APIService(
                api_key=cfg["api_key"],
                api_url=cfg["api_url"],
                model_name=cfg["model_name"]
            )
            # print(f"Processing batch with {model_name} model...")

            # 内层分批并发（无进度条）
            batch_results = []
            batches = list(batch_list(roadNames, batch_size))
            roadLocations = list(batch_list(roadLocation, batch_size))
            with ThreadPoolExecutor() as batch_executor:
                batch_futures = [
                    batch_executor.submit(api_service.fetch_road_info, batch, roadLocations[i], json_template=json_template)
                    for i, batch in enumerate(batches)
                ]
                for future in as_completed(batch_futures):
                    batch_results.append(future.result())
            # 合并所有批次结果
            merged = []
            for r in batch_results:
                parsed = self.parse_json_output(r)
                if parsed:
                    merged.extend(parsed)
            return model_name, merged

        # 外层多模型并发
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(call_model, model_name, cfg)
                for model_name, cfg in self.model_configs.items()
            ]
            for future in as_completed(futures):
                model_name, result = future.result()
                results[model_name] = result

        temp = {k: self.parse_json_output(v) for k, v in results.items() if v}
        temp = temp[model_name] if temp else {}
        return temp


    def parse_json_output(self, json_input, field_names=None):
        """
        解析给定的 JSON 字符串，去除格式标记并返回包含每个 JSON 对象值的列表。
        支持自定义字段名和嵌套字段（如 a.b）。
        """
        def get_nested(d, key):
            """支持 a.b.c 形式的嵌套字段提取"""
            if not isinstance(d, dict):
                return None
            keys = key.split('.')
            for k in keys:
                if isinstance(d, dict) and k in d:
                    d = d[k]
                else:
                    return None
            return d

        if isinstance(json_input, (list, dict)):
            return json_input
        json_input = (json_input or '').strip()
        # 优先提取两个[]之间的内容，且带上[]
        match = re.search(r'(\[.*?\])', json_input, re.DOTALL)
        if match:
            json_input = match.group(1).strip()
        # 自动修正裸的无为"无"
        json_input = re.sub(r':\s*无(,|\n|\r|\})', r': "无"\1', json_input)
        if not json_input:
            print("[调试] AI返回内容为空或无有效JSON片段")
            return None
        try:
            parsed_output = json.loads(json_input)
            # print("[调试] 解析成功，内容：", parsed_output)
            if isinstance(parsed_output, dict):
                parsed_output = [parsed_output]
            if not isinstance(parsed_output, list):
                print("[调试] 解析后不是列表或字典")
                return None
            if field_names:
                result = []
                for item in parsed_output:
                    row = [get_nested(item, f) for f in field_names]
                    result.append(row)
                return result
            else:
                return parsed_output
        except Exception as e:
            print("[调试] 解析 JSON 时出错:", e)
            print("[调试] 原始内容：", json_input)
            return None