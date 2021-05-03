import os
from main.src.code.utils.sys_utils import read_config
import pandas as pd
import json

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


def create_lagged_features(df, columns, trailing_window = 1):

    data_lagged = df.copy()
    for window in range(1, trailing_window + 1):
        shifted = df[columns].shift(window)
        shifted.columns = [x + "_lag" + str(window) for x in columns]
        data_lagged = pd.concat((data_lagged, shifted), axis=1)

    return data_lagged

def cache_info(json_fname, key, value):

    opj = os.path.join
    file_path = opj(extract_folder_path("cache"), json_fname)

    with open(file_path, "r") as json_file:
        data = json.load(json_file)

        if isinstance(key, list):
            for i, key_ in enumerate(key):
                data[key_] = value[i]
        else:
            data[key] = value

    with open(file_path, "w") as json_file:
        json.dump(data, json_file)
