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

    def __init__(self):
        super(TADataset, self).__init__()

        self.opj = os.path.join

        if self.mode == "train":

            ticker_date_path = self.opj(extract_folder_path("model_data"),
                                          "ticker_date_train.pkl")
            ticker_date_list = read_pickle(ticker_date_path)

        elif self.mode == "val":

            ticker_date_path = self.opj(extract_folder_path("model_data"),
                                          "ticker_date_val.pkl")
            ticker_date_list = read_pickle(ticker_date_path)

        self.no_of_samples = len(ticker_date)
