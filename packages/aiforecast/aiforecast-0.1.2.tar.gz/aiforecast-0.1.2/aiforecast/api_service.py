import json
import math
from openai import OpenAI
from . import config

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