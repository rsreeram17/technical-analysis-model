import pandas as pd
import os
from main.src.code.utils.utils import extract_folder_path, get_yaml_value, cache_info, dump_pickle, read_pickle
from tqdm import tqdm
import json


class PrepareData(object):

    def __init__(self):

        self.mode = get_yaml_value("model", "mode")
        self.opj = os.path.join

        self.feature_data_path = self.opj(extract_folder_path("features"),
                                     "data_features.csv")
        variables_info_path = self.opj(extract_folder_path("cache"),
                                       "variables_info.json")

        self.features_data = pd.read_csv(self.feature_data_path)

        var_info_file = open(variables_info_path)
        self.variables_info = json.load(var_info_file)

        if self.mode == "train":

            self.ticker_date_fname = "ticker_date_train.pkl"
            self.clean_data_name = "data_train.csv"

            raw_data_features = get_yaml_value("process",
                                               "feature_creation_inputs.columns_normalize") \
                                + get_yaml_value("model",
                                                 "features.raw_normalized_available")

            ti_features = self.variables_info["technical_indicator_data_columns"]
            dts_features = self.variables_info["dts_data_columns"]

            self.date_feature = get_yaml_value("process", "variable_names.date")

            self.subset_feature = [self.date_feature] + ["ticker"] + raw_data_features\
                             + ti_features + dts_features + ["target_variable"]

            self.model_features = raw_data_features + ti_features + dts_features

            sub_features = list(set(self.subset_feature) - set(["target_variable"]))

            cache_info(
                "variables_info.json", ["subset_features", "model_features"],
                [sub_features, self.model_features])

        else:
            self.subset_feature = self.variables_info["subset_features"] #Edit this when including test pipeline
            self.model_features = self.variables_info["model_features"]

    def clean_data(self, data):

        data = data.dropna()
        data = data[self.subset_feature]
        return data

    def prep_model_data_inputs(self):

        features_data = pd.read_csv(self.feature_data_path)
        cleaned_data = self.clean_data(features_data)

        ticker_list_data = list(set(cleaned_data["ticker"]))
        #ticker_list_data = ticker_list_data[37:39]

        dateframe_start = pd.to_datetime(get_yaml_value("model", "train.dateframe_start"))
        dateframe_end = pd.to_datetime(get_yaml_value("model", "train.dateframe_end"))

        date_ticker_list = []
        for ticker in tqdm(ticker_list_data):

            data_ticker = cleaned_data[cleaned_data["ticker"] == ticker]
            print(ticker)

            dates_list = list(set(
                data_ticker[
                    (pd.to_datetime(data_ticker[self.date_feature]) > dateframe_start) &
                    (pd.to_datetime(data_ticker[self.date_feature]) < dateframe_end)][self.date_feature]))

            for date in dates_list:

                date = pd.to_datetime(date)
                data_ticker_date = data_ticker[
                    pd.to_datetime(data_ticker[self.date_feature]) <= date]
                data_ticker_date.sort_values(
                    by=self.date_feature, inplace=True, ascending=False)

                if len(data_ticker_date) > 45:
                    date_ticker_list.append((ticker, date))

        pickle_path = self.opj(extract_folder_path("model_data"), self.ticker_date_fname)
        dump_pickle(pickle_path, date_ticker_list)

        cleaned_data.to_csv(self.opj(extract_folder_path("model_data"),
                                     self.clean_data_name))


a = PrepareData()
a.prep_model_data_inputs()




