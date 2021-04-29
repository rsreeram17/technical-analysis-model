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





















