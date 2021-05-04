import pandas as pd
import os
from os import walk
from tqdm import tqdm
import numpy as np
import pandas_ta as ta
from main.src.code.utils.sys_utils import read_config
from main.src.code.utils.utils import extract_folder_path,\
    get_yaml_value, create_lagged_features, cache_info


class BuildFeatures(object):

    def __init__(self):
        self.opj = os.path.join
        self.price_column_used = get_yaml_value(
            'process', 'technical_indicator_inputs.column')
        self.column_name = get_yaml_value(
            'process', 'variable_names.' + self.price_column_used)
        self.country = get_yaml_value('process', 'FC_processing_flags.country')
        self.data_path = self.opj(
            extract_folder_path("process_daily_price"), self.country)

        self.ticker_list = get_yaml_value(
            "process", "FC_processing_flags.ticker_list")

        self.columns_ti = ['MACDs_12_26_9', 'MACD_12_26_9', 'WILLR_14', 'RSI_14',
                      'STOCHk_14_3_3', 'SMA_20', 'ADOSC_3_10', 'MOM_10', 'FWMA_20',
                      'STOCHd_14_3_3', 'MACDh_12_26_9', 'CCI_14_0.015']

        self.raw_columns_analysis = get_yaml_value(
            "process", "feature_creation_inputs.columns_normalize")

        if self.ticker_list == "all":
            _, _, self.filenames = next(walk(self.data_path))

        else:
            self.filenames = [ticker+"_TI.csv" for ticker in self.ticker_list]

        self.fc_data_dictionary = {}

    def create_lagged_ti(self, data):

        data_ti_lagged = create_lagged_features(data, self.columns_ti)
        return data_ti_lagged

    def create_lagged_raw(self, data):

        historic_datapoint_for_pred = get_yaml_value(
            "process", "feature_creation_inputs.normalization_tf")
        data_raw_lagged = create_lagged_features(
            data, self.raw_columns_analysis, historic_datapoint_for_pred)
        return data_raw_lagged

    def normalize_columns(self, data, columns):

        for column in columns:
            column_names = [col for col in data.columns if column in col]
            data_frame_subset = data[column_names]
            column_mean = data_frame_subset.mean(axis=1)
            data[column] = data[column] / column_mean

        return data

    def create_target_variable(self, data):

        pred_window = get_yaml_value(
            "process", "feature_creation_inputs.time_ahead_to_pred")

        shifted = pd.DataFrame(data[self.column_name].shift(pred_window))

        shifted.columns = [self.column_name+"_lag"]

        data_tv = pd.concat((data, shifted), axis=1)
        lag_column = self.column_name+"_lag"
        data_tv["target_variable"] = (data_tv[lag_column] -
                                   data_tv[self.column_name])/data_tv[self.column_name]

        return data_tv

    def create_dts(self, data):

        data["SMA_DTS"] = np.where(data[self.column_name] > data["SMA_20"], 1, 0)
        data["WMA_DTS"] = np.where(data[self.column_name] > data["FWMA_20"], 1, 0)
        data["MOM_DTS"] = np.where(data["MOM_10"] > 0, 1, 0)
        data["STOCHK_DTS"] = np.where(
            data["STOCHk_14_3_3"] > data["STOCHk_14_3_3_lag1"], 1, 0)
        data["STOCHD_DTS"] = np.where(
            data["STOCHd_14_3_3"] > data["STOCHd_14_3_3_lag1"], 1, 0)
        data["MACD_DTS"] = np.where(
            data["MACD_12_26_9"] > data["MACD_12_26_9_lag1"], 1, 0)
        data["WILLR_DTS"] = np.where(data["WILLR_14"] > data["WILLR_14_lag1"], 1, 0)
        data["ADOSC_DTS"] = np.where(data["ADOSC_3_10"] > data["ADOSC_3_10_lag1"], 1, 0)

        data["RSI_DTS"] = np.where(
            ((data["RSI_14"] <= 30) | (data["RSI_14"] > data["RSI_14_lag1"])), 1, 0)

        data["CCI_DTS"] = np.where(
            ((data["CCI_14_0.015"] < -200) | (data["CCI_14_0.015"] > data["CCI_14_0.015_lag1"])), 1, 0)

        return data

    def build_features(self, mode="train"):

        if mode == "train":
            combined_df = pd.DataFrame()

            for filename in tqdm(self.filenames):

                ticker = filename.replace("_TI.csv", "")

                data_ticker = pd.read_csv(self.opj(self.data_path, filename))
                data_ti_columns = set(data_ticker.columns)

                data_ticker = self.create_lagged_raw(data_ticker)

                data_ticker = self.create_lagged_ti(data_ticker)
                data_ti_lagged = set(data_ticker.columns)

                data_ticker = self.create_dts(data_ticker)
                data_dts = set(data_ticker.columns)

                data_ticker.sort_values(by="date", inplace=True, ascending=False)
                data_ticker = self.create_target_variable(data_ticker)
                data_ticker.sort_values(by="date", inplace=True)

                data_ticker = self.normalize_columns(
                    data_ticker, self.raw_columns_analysis + ["SMA_20", "FWMA_20"])

                data_ticker["ticker"] = ticker
                #data_ticker.to_csv("test.csv")
                if len(combined_df) == 0:
                    combined_df = data_ticker
                else:
                    combined_df = pd.concat((combined_df, data_ticker))

            dts_data_columns = list(data_dts - data_ti_lagged)

            keys = "dts_data_columns"

            cache_info("variables_info.json", keys, dts_data_columns)
            combined_df = combined_df[list(data_ti_columns) +
                                      dts_data_columns + ["ticker"] + ["target_variable"]]

            data_write_path = self.opj(
                extract_folder_path('features'), "data_features.csv")
            print("Feature building is completed")
            print("Currently writing the file to the features directory")
            combined_df.to_csv(data_write_path, index=False)
            print("Features file successfully written to the directory")


a = BuildFeatures()
a.build_features()