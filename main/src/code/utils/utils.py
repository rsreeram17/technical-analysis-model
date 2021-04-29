import os
from main.src.code.utils.sys_utils import read_config

def get_yaml_value(filename: str, key: str):

    cfg = read_config(filename)
    value = cfg.get(key)
    return value

def extract_folder_path(type_):

    opj = os.path.join
    sys_cfg = read_config('system')
    path_cfg = read_config('path')

    path_key = get_yaml_value('system', 'OS')+"."+type_
    output_folder_path = opj(sys_cfg.get('folder.root'), path_cfg.get(path_key))

    return output_folder_path


