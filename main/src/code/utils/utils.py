import os
from main.src.code.utils.sys_utils import read_config

def get_yaml_value(filename: str, key: str):

    cfg = read_config(filename)
    value = cfg.get(key)
    return value

def identify_os():

    sys_cfg = read_config('system')
    operating_sys = str(sys_cfg.get('OS'))

    return operating_sys

def extract_folder_path(type):

    opj = os.path.join
    sys_cfg = read_config('system')
    path_cfg = read_config('path')

    path_key = identify_os()+"."+type
    output_folder_path = opj(sys_cfg.get('folder.root'), path_cfg.get(path_key))

    return output_folder_path


