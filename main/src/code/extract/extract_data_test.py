import pandas as pd
import os
from main.src.code.utils.fmp_python.fmp import FMP
from main.src.code.utils.sys_utils import read_config
from main.src.code.utils.utils import identify_os, extract_folder_path, get_yaml_value


opj = os.path.join
api_key = get_yaml_value('API', 'api_info.api_key')
data_path = extract_folder_path('daily_price')
extraction_cfg = read_config('extraction')

country = get_yaml_value('extraction','extraction_flags.country')
extraction_type = get_yaml_value('extraction', 'extraction_flags.type')

ticker_list = get_yaml_value('extraction', 'extraction_flags.ticker_list')

if ticker_list != 'all':
    ticker_list = ['AAPL'] # Change this while implementing this

else:

    symbols = pd.read_csv(opj(extract_folder_path('FMP_company_details'), "symbols.csv"))

    stock_exchanges = get_yaml_value('API', 'country_exchanges'+"."+country)
    ticker_list = list(symbols[symbols['exchange'].isin(stock_exchanges)]["symbol"])

    ticker_list = ["AAPL","MSFT"]

fmp = FMP(api_key=api_key, output_format='pandas')

for ticker in ticker_list:



















