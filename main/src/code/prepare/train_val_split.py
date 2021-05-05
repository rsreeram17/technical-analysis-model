import os
from main.src.code.utils.utils import extract_folder_path, dump_pickle, read_pickle
from sklearn.model_selection import train_test_split

def split_train_test():

    opj = os.path.join
    model_data_path = extract_folder_path("model_data")
    ticker_date_train_val_path = opj(model_data_path, "ticker_date_train_val.pkl")

    ticker_date_train_val = read_pickle(ticker_date_train_val_path)

    ticker_date_train, ticker_date_val = train_test_split(
        ticker_date_train_val, test_size=0.2, random_state=42)

    dump_pickle(opj(model_data_path,"ticker_date_train.pkl"), ticker_date_train)
    dump_pickle(opj(model_data_path,"ticker_date_val.pkl"), ticker_date_val)


split_train_test()


