import os
from pathlib import Path
from dotenv import load_dotenv

# Make sure to load only once
_loaded = False

def load_config():
    global _loaded
    if _loaded:
        return

    # Only search for .env files in the current working directory
    env_path = Path.cwd() / '.env'
    
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        print(f"No .env file found in current directory: {Path.cwd()}")
    
    _loaded = True

load_config()


API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
BATCH_SIZE = 10 # The size of batch processing
MAX_WORKERS = 10  # Adjust the number of threads as needed

# Define JSON format template
JSON_TEMPLATE = {
    "roadName": "<道路名称，示例：解放路>",
    "curb_top": "<是否有顶部路缘石，True或者False>",
    "curb_bottom": "<是否有底部路缘石，True或者False>",
    "guardrail_top": "<是否有顶部护栏，True或者False>",
    "guardrail_bottom": "<是否有底部护栏，True或者False>",
    "motorway": "<机动车道长度，单位米>",
    "sidewalk": "<人行道长度，单位米，如果没有人行道则是0m>"
}

# User message template - Add precision requirement prompt
USER_PROMPT_TEMPLATE = (
    "请提供{road_names_string}的完整属性信息，"
    "特别注意道路红线宽度与各部件宽度总和的精确匹配验证"
)

# System message template - Add strict output format requirement
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