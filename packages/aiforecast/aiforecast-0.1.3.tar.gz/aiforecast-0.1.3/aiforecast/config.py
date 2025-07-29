import os
from dotenv import load_dotenv
load_dotenv()

# deepseek
API_KEY = os.environ.get("API_KEY")
API_URL = os.environ.get("API_URL")
MODEL_NAME = os.environ.get("MODEL_NAME")
BATCH_SIZE = 12 # 批量处理的大小


MAX_WORKERS = 12  # 根据需要调整线程数
ROAD_LOCATION = '北京市'  # 存储道路位置

# 提示词 TODO
# 定义 JSON 格式模板
JSON_TEMPLATE = {
    "roadName": "<道路名称，示例：解放路>",
    "curb_top": "<是否有顶部路缘石，True或者False>",
    "curb_bottom": "<是否有底部路缘石，True或者False>",
    "guardrail_top": "<是否有顶部护栏，True或者False>",
    "guardrail_bottom": "<是否有底部护栏，True或者False>",
    "motorway": "<机动车道长度，单位米>",
    "sidewalk": "<人行道长度，单位米，如果没有人行道则是0m>"
}



# 用户消息模板 - 增加精度要求提示
USER_PROMPT_TEMPLATE = (
    "请提供{road_names_string}的完整属性信息，"
    "特别注意道路红线宽度与各部件宽度总和的精确匹配验证"
)


SYSTEM_PROMPT_TEMPLATE = (
    "用户将提供位于{road_location}的道路名称，请执行以下操作：\n\n"
    "### 操作流程：\n"
    "1. 初始查询：获取道路完整属性数据\n"
    "2. 一致性验证：严格检查以下规则\n"
    "3. 最终输出：无论验证结果如何，输出json格式严格保持{json_template}\n\n"


    "### 输出规则：\n"
    "1. 无论经过多少次重试，最终输出格式严格保持：\n"
    "   {json_template}\n\n"

    "### 数据要求：\n"
    "- 红线宽度取整到米\n"
    "- 所有宽度使用实测值\n"
    "- 重试时优先修正矛盾最突出的字段"
)