import pandas as pd
import os
from os import walk
import pandas_ta as ta
from main.src.code.utils.sys_utils import read_config
from main.src.code.utils.utils import extract_folder_path, get_yaml_value
from tqdm import tqdm


def test():
    class ComputeTechnicalIndicators(object):

        def __init__(self):
            self.opj = os.path.join
            self.country = get_yaml_value('process', 'processing_flags.country')
            self.ticker_list = get_yaml_value('process', 'processing_flags.ticker_list')
            self.process_history = get_yaml_value('process', 'processing_flags.history')

            self.available_strategies = get_yaml_value(
                'process', 'technical_indicator_inputs.available_strategies')
            self.custom_strategy = ta.Strategy(
                name="Input strategy",
                ta=get_yaml_value(
                    'process', 'technical_indicator_inputs.indicators_details'))

            self.daily_price_data_path = self.opj(
                extract_folder_path("daily_price"), self.country)
            self.process_data_path = self.opj(
                extract_folder_path("process_daily_price"), self.country)

            if self.ticker_list == "all":

                _, _, filenames = next(walk(self.daily_price_data_path))
                print(filenames)
                self.ticker_list = [fname.replace(".csv", "") for fname in filenames]

        def compute_ti(self):

            if self.available_strategies != "None":

                for ticker in tqdm(self.ticker_list):
                    data = pd.read_csv(self.opj(self.daily_price_data_path, ticker+".csv"))

                    for strategy_ in self.available_strategies:
                        data.ta.strategy(strategy_, verbose=True)

                    data.ta.strategy(self.custom_strategy)

                    write_filename = self.opj(self.process_data_path, ticker+".csv")
                    data.to_csv(write_filename)

            else:
                for ticker in tqdm(self.ticker_list):
                    data = pd.read_csv(self.opj(self.daily_price_data_path, ticker + ".csv"))

                    data.ta.strategy(self.custom_strategy)

                    write_filename = self.opj(self.process_data_path, ticker + "_TI.csv")
                    data.to_csv(write_filename)

    a = ComputeTechnicalIndicators()
    a.compute_ti()


if __name__ == "__main__":
    test()





