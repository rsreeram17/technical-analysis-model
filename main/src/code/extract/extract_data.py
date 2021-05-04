import pandas as pd
import os
from main.src.code.utils.fmp_python.fmp import FMP
from main.src.code.utils.sys_utils import read_config
from main.src.code.utils.utils import extract_folder_path, get_yaml_value, cache_info
from tqdm import tqdm

def extract_tickers():

    opj = os.path.join
    op_file_path = opj(extract_folder_path('FMP_company_details'), "symbols.csv")

    fmp = FMP(api_key= get_yaml_value('API', 'api_info.api_key'), output_format='pandas')
    symbols = fmp.get_symbols_list()
    symbols.to_csv(op_file_path, index=False)

    return


class ExtractDailyPrice(object):

    def __init__(self):

        opj = os.path.join
        main_cfg = read_config('main')
        sys_cfg = read_config('system')
        extraction_cfg = read_config('extraction')

        self.api_key = get_yaml_value('API', 'api_info.api_key')
        self.country = get_yaml_value('extraction', 'extraction_flags.country')
        self.data_path = opj(extract_folder_path('daily_price'), self.country)
        self.extraction_type = get_yaml_value('extraction', 'extraction_flags.type')

        self.ticker_list = get_yaml_value('extraction', 'extraction_flags.ticker_list')

        if self.ticker_list != 'all':

            self.ticker_list = get_yaml_value('extraction', 'extraction_flags.ticker_list')
        else:

            symbols = pd.read_csv(opj(extract_folder_path('FMP_company_details'), "symbols.csv"))
            stock_exchanges = get_yaml_value('API', 'country_exchanges' + "." + self.country)
            self.ticker_list = list(symbols[symbols['exchange'].isin(stock_exchanges)]["symbol"])

            self.ticker_list = self.ticker_list[1180:1181] # Remove this after testing

    def extract_daily_price(self):

        opj = os.path.join
        fmp = FMP(api_key=self.api_key, output_format="pandas")

        if self.extraction_type == "history":
            for ticker in tqdm(self.ticker_list):
                data = fmp.get_historical_price(ticker)
                daily_price_columns = list(data.columns)
                write_file_path = opj(self.data_path, ticker+".csv")
                data.to_csv(write_file_path, index=False)

            cache_info("variables_info.json", "daily_price_data_columns", daily_price_columns)


extract_data = ExtractDailyPrice()
extract_data.extract_daily_price()