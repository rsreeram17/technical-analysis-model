import pandas as pd
import os
from main.src.code.utils.fmp_python.fmp import FMP
from main.src.code.utils.sys_utils import read_config
from main.src.code.utils.utils import extract_folder_path, get_yaml_value, cache_info, dump_pickle, read_pickle
from tqdm import tqdm
import json
import numpy as np
from datetime import datetime

model_mode = get_yaml_value("model", "mode")

opj = os.path.join
feature_data_path = opj(extract_folder_path("features"), "data_features.csv")
variables_info_path = opj(extract_folder_path("cache"), "variables_info.json")

features_data = pd.read_csv(feature_data_path)
var_info_file = open(variables_info_path)
variables_info = json.load(var_info_file)

features_data_na_removed = features_data.dropna()

raw_data_features = get_yaml_value("process", "feature_creation_inputs.columns_normalize")\
                    + get_yaml_value("model", "features.raw_normalized_available")

ti_features = variables_info["technical_indicator_data_columns"]
dts_features = variables_info["dts_data_columns"]

date_feature = get_yaml_value("process", "variable_names.date")

subset_features = [date_feature] + ["ticker"] + raw_data_features + ti_features +\
                  dts_features + ["target_variable"]

features_data_na_removed = features_data_na_removed[subset_features]

ticker_list_data = list(set(features_data_na_removed["ticker"]))
ticker_list_data = ticker_list_data[:1]

dateframe_start = pd.to_datetime(get_yaml_value("model","train.dateframe_start"))
dateframe_end = pd.to_datetime(get_yaml_value("model","train.dateframe_end"))

print(dateframe_end + pd.DateOffset(days=45))


data_dictionary_model = {}

dictionary_index = 0
dates_list = list(set(features_data_na_removed[
    (pd.to_datetime(features_data_na_removed[date_feature]) > dateframe_start) &
    (pd.to_datetime(features_data_na_removed[date_feature]) < dateframe_end)][date_feature]))

dates_list = dates_list[:1]

target_variable_list = []

for ticker in ticker_list_data:

    data_ticker = features_data_na_removed[features_data_na_removed["ticker"] == ticker]

    for date in dates_list:

        date = pd.to_datetime(date)

        data_ticker_date = data_ticker[pd.to_datetime(data_ticker[date_feature]) <= date]
        data_ticker_date.sort_values(by=date_feature, inplace=True, ascending=False)

        if len(data_ticker_date)>45:
            data_ticker_date = data_ticker_date.head(45)
            target_variable = data_ticker_date[
                pd.to_datetime(data_ticker_date[date_feature])
                == date]["target_variable"].values[0]

            data_model = data_ticker_date[raw_data_features + ti_features + dts_features].to_numpy()
            print(data_model.shape)

            data_dictionary_model[dictionary_index] = data_model
            dictionary_index = dictionary_index + 1
            target_variable_list.extend([target_variable])
            print(target_variable_list)
        else:
            continue
















