import pandas as pd
import os
from main.src.code.utils.utils import extract_folder_path, get_yaml_value,\
    cache_info, dump_pickle, read_pickle
from tqdm import tqdm
import json
import torch
import torch.utils.data as data
import torch.nn as nn
from torch.autograd import Variable
import torch.nn.functional as F
from torch.utils.data.sampler import SubsetRandomSampler
import torch.optim as optim
from torch.optim import lr_scheduler

class TADataset(data.Dataset):

    def __init__(self, mode):
        super(TADataset, self).__init__()

        opj = os.path.join
        self.model_data_path = opj(extract_folder_path("model_data"))
        self.model_data = pd.read_csv(
            opj(self.model_data_path, "data_train.csv"))

        variables_info_path = opj(
            extract_folder_path("cache"), "variables_info.json")
        var_info_file = open(variables_info_path)
        self.variables_info = json.load(var_info_file)

        self.date_feature = get_yaml_value("process", "variable_names.date")
        self.model_features = self.variables_info["model_features"]
        self.historic_datapoint_for_pred = get_yaml_value(
            "model", "features.historic_datapoint_for_pred")

        if mode == "train":
            ticker_date_path = opj(
                self.model_data_path, "ticker_date_train.pkl")
            self.ticker_date_list = read_pickle(ticker_date_path)

        elif mode == "val":
            ticker_date_path = opj(
                self.model_data_path, "ticker_date_val.pkl")
            self.ticker_date_list = read_pickle(ticker_date_path)

        self.no_of_samples = len(self.ticker_date_list)

    def __len__(self):

        return self.no_of_samples

    def __getitem__(self, ix):

        ticker, date = self.ticker_date_list[ix]

        data_ticker_date = self.model_data[
            (self.model_data["ticker"] == ticker) &
            (pd.to_datetime(self.model_data[self.date_feature]) <= date)]

        data_ticker_date.sort_values(
            by=self.date_feature, inplace=True, ascending=False)
        data_ticker_date = data_ticker_date.head(
            self.historic_datapoint_for_pred)

        target_variable = torch.tensor([data_ticker_date[
            pd.to_datetime(data_ticker_date[self.date_feature])
            == date]["target_variable"].values[0]])

        data_ticker_date = data_ticker_date[self.model_features].to_numpy()
        data_ticker_date = torch.from_numpy(data_ticker_date)

        return data_ticker_date, target_variable


def build_dataloaders(batch_size=100):

    data_loaders = {}
    data_lengths = {}
    for mode_ in ["train", "val"]:

        dataset_ = TADataset(mode_)
        data_loaders[mode_] = data.DataLoader(dataset_,batch_size=batch_size)
        data_lengths[mode_] = len(dataset_)

        return data_loaders, data_lengths
    
















