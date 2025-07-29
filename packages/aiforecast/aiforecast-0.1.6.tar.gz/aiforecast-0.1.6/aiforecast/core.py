from pathlib import Path
from . import data_processing
from .ai_clients import AIClientManager
import os

REQUIRED_FIELDS = ['curb_top', 'curb_bottom', 'guardrail_top', 'guardrail_bottom']
OUTPUT_FILENAME_PREFIX = "道路附属统计"
DEFAULT_OUTPUT_FILENAME = "output.txt"

def extract_filename(input_path):
    """从路径中提取文件名（不带扩展名）"""
    path = Path(input_path)
    return path.stem

def process(input_path, output_path1=None, output_path2=None):

    """
    处理输入文件，提取道路信息，调用AI服务获取分析结果，并将结果分为两部分分别写入输出文件。
    参数：
        input_path (str): 输入文件路径。
        output_path1 (str, 可选): 第一部分结果输出文件路径，若为None则自动生成。
        output_path2 (str, 可选): 第二部分结果输出文件路径，若为None则自动生成。
    """
    try:
        # 1. 获取道路信息
        input_path = os.path.abspath(input_path)
        di = data_processing.get_roadInfo_by_gpkg(input_path)
        
        # 验证必要字段存在
        if 'road_name' not in di or not di['road_name']:
            raise ValueError("解析错误: 未找到有效的道路名称")
            
        # 2. 构建区域信息
        area_keys = ['xz_provinc', 'xz_city', 'xz_country', 'xz_name']
        road_area = ''.join(di.get(key, '') for key in area_keys)
        road_name = di['road_name']
        
        # 3. 调用AI服务
        ai_client = AIClientManager()
        results = ai_client.ask_all_models([road_name], [road_area])
        
        if not results:
            raise RuntimeError("未获取到有效的AI响应结果")
        
        # 4. 处理结果数据
        result_data = results[0]
        
        # 分离字段
        part1 = {k: result_data[k] for k in REQUIRED_FIELDS if k in result_data}
        part2 = {k: result_data[k] for k in result_data if k not in REQUIRED_FIELDS}
        
        # 5. 生成输出文件名
        filename_base = extract_filename(input_path) or DEFAULT_OUTPUT_FILENAME
        part1_filename = os.path.join(output_path1, f"{OUTPUT_FILENAME_PREFIX}.txt") if output_path1 else f"{OUTPUT_FILENAME_PREFIX}.txt"
        part2_filename = os.path.join(output_path2, f"{filename_base}.txt") if output_path2 else f"{filename_base}.txt"
        
        # 6. 写入结果
        data_processing.write_dict_to_txt(
            part1_filename, 
            part1, 
            ['道路附属统计结果:', 'motorway:']
        )
        
        data_processing.write_dict_to_txt(
            part2_filename, 
            part2
        )
        
        
    except Exception as e:
        error_msg = f"处理过程中发生错误: {str(e)}"
        print(error_msg)
        raise