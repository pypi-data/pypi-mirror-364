from . import data_processing
from .ai_clients import AIClientManager
import re
def process(input_path):
    di = data_processing.get_roadInfo_by_gpkg(input_path)
    roadArea = di.get('xz_provinc', '') + di.get('xz_city', '') + di.get('xz_country', '') + di.get('xz_name', '')
    roadName = di.get('road_name', None)
    if roadName is None:
        print('解析错误')
        raise
    ai_client = AIClientManager()
    res = ai_client.ask_all_models([roadName],[roadArea])
    fields1 = ['curb_top', 'curb_bottom', 'guardrail_top', 'guardrail_bottom']
    fields2 = set(res[0].keys()) - set(fields1)
    part1 = {k: res[0][k] for k in fields1 if k in res[0]}
    part2 = {k: res[0][k] for k in fields2 if k in res[0]}
    print(res)
    data_processing.write_dict_to_txt('道路附属统计1.txt', part1, ['道路附属统计结果:', 'motorway:'])
    match = re.search(r'/([^/]+)\.', input_path)
    if match:
        filename = match.group(1) + '.txt'
    else:
        filename = 'output.txt'  # 匹配不到时默认文件名
    data_processing.write_dict_to_txt(filename, part2)