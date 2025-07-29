import geopandas as gpd


def get_roadInfo_by_gpkg(file_path):
    """
    从 GeoPackage 文件中获取道路相关字段的首行信息。
    :param file_path: GeoPackage 文件路径
    :return: 字典，包含各字段首行内容。字段缺失时返回 None。
    """
    gdf = gpd.read_file(file_path)
    def safe_get(col):
        return gdf[col][0] if col in gdf.columns and len(gdf[col]) > 0 else None

    return {
        'xz_provinc': safe_get('xz_provinc'),
        'xz_city': safe_get('xz_city'),
        'xz_country': safe_get('xz_country'),
        'xz_name': safe_get('xz_name'),
        'road_type': safe_get('road_type'),
        'road_name': safe_get('road_name')
    }



def write_dict_to_txt(filename, data_dict, pre_lines=None, blank_line_before_dict=False):
    """
    将字典数据写入文本文件，格式为 key: value（每行一对）
    可选：在写入字典前插入额外内容或空行。
    参数:
        filename (str): 要写入的文件名（包括路径）
        data_dict (dict): 要写入的字典数据
        pre_lines (list[str]|None): 写入字典前要写入的多行内容（每行一个字符串）。
        blank_line_before_dict (bool): 是否在字典前加一个空行。
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            if pre_lines:
                for line in pre_lines:
                    file.write(str(line) + '\n')
            prefix = ' ' if blank_line_before_dict else ''
            for key, value in data_dict.items():
                file.write(f"{prefix}{key}: {value}\n")
    except Exception as e:
        print(f"写入文件时出错: {str(e)}")
        raise