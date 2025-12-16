import os, json, warnings, glob
import parse_data
import request_data
from pathlib import Path
import pandas as pd


def get_data_params(file_name, add_new_data_seires, path_data_parse):
    """
    file_name: base name of json file.
    """
    with open(Path('config_data_request')/file_name) as f:
        dataset_list = json.load(f)

    if add_new_data_seires:
        exist_series = [os.path.basename(i).replace('.csv', '') for i in glob.glob(os.path.join(path_data_parse, '*.csv'))]

        result = {}
        for i in dataset_list.keys():
            if i not in exist_series:
                result[i] = dataset_list[i]
        if len(result) == 0:
            print(f"No new data series to add in :[{file_name}]")

        return result

    else:
        return dataset_list




def print_new_records(record):
    label = ' New Record '
    n = 20
    print(f"{'='*n}{label}{'='*n}\n{record}\n{'='*(2*n+len(label))}\n")


def record_downloaded_data_series(dataset_list:list, data_name:str, path_df):
    var_name = dataset_list[data_name]['name']  # name of variable.
    freq = data_name.split('-')[-1]
    platform = data_name.split('-')[1]
    new_record = [var_name, platform, freq]

    if not os.path.exists(path_df):
        df = pd.DataFrame(columns = ['variable', 'platform', 'frequncy'])
        df.loc[data_name, :] = new_record
        # save to csv, data_name is index.
        df.to_csv(path_df)
        print_new_records(df.query('variable == @var_name'))

    else:
        # load csv, and let the first column as index, i.e., data_name is index column.
        df = pd.read_csv(path_df, index_col = 0)
        if not data_name in df.index:
            df.loc[data_name, :] = new_record
            print_new_records(df.query('variable == @var_name'))
            df.to_csv(path_df)



def update_database(path_data_request, path_data_parse, path_variables, computer, override, add_new_data_seires):
    """
    This is the main function that will request and parse data.
    Steps:
        1. request data and save json to ./data/request_data
        2. parse data and save csv to ./data/parse_data
        3. if it is a new data series, add to ./variables_in_database.csv
    """
    #############################################
    #        Download data from BEA
    #############################################
    
    dataset_list = get_data_params('BEA.json', add_new_data_seires, path_data_parse)
    
    for dataset in dataset_list.keys():
        # Request data
        request_data.get_BEA_data(path_data_request, dataset, computer)
    
        # Parse data
        drop_cols = dataset_list[dataset]['drop_cols']
        MnToBn = dataset_list[dataset]['MnToBn']
    
        parse_data.parse_BEA_data(path_data_request, path_data_parse, dataset, override = override, drop_cols=drop_cols, MnToBn = MnToBn)
    
        record_downloaded_data_series(dataset_list, dataset, path_variables)
        print('-'*80)
    
    #############################################
    #        Download data from FRED
    #############################################
    
    dataset_list = get_data_params('FRED.json', add_new_data_seires, path_data_parse)
    for dataset in dataset_list:
        # Request data
        request_data.get_FRED_data(path_data_request, dataset, computer)
        # Parse data
        parse_data.parse_FRED_data(path_data_request, path_data_parse, dataset, override)
    
        record_downloaded_data_series(dataset_list, dataset, path_variables)
        print('-'*80)
    


    


####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################

"""
Instruction:
    1.  To download new dataset, you first need to create a new key-value dict in config files in ./config_data_request/*.json
        -- The key is a self-defined data name which will also be used to name streamlit elements later on. Name the key following the rule below:
            Name rule:
                DataName-Platform-Frequency, e.g., NGDP-BEA-Q

        -- Format of config file:

            <data_name>:{
                "params":       {},             # parameters used for data request.
                "drop_cols":    [],             # col you want to drop in data parsing.
                "MnToBn":       bool,           # If to divide raw values by 1000 to convert Mn. of $ to Bn. of $.
                "name":         string          # name of variable that will be save in record df.
            }


    2.  If you would like to adjust the indent of this table when it is being presented on the website, you also need to add a key-value dict to ./config/chart_config.json where the key is data name.
"""


#===========================================
#       General Setup

warnings.filterwarnings('ignore')

# Set to True if you want to download a new dataset instead of updating all data series.
# Set to False if you want to update all existed data series.
add_new_data_seires = True

# If you want to wipe out previous data.
override = False

# specify which computer you are using, so it will find the correct api-key.
computer = 'popos' # or dell, popos

path_data_request = os.path.join('data', 'request_data')
path_data_parse = os.path.join('data', 'parse_data')
Path(path_data_request).mkdir(exist_ok=True, parents = True)
Path(path_data_parse).mkdir(exist_ok=True, parents = True)

path_variables = './variables_in_database.csv'
#===========================================


#################################
#       Run program
#################################




###------Update database------###

"""
Run this to request and update your database.
"""
update_database(path_data_request, path_data_parse, path_variables, computer, override, add_new_data_seires)


###------Check data series in database------###

db = pd.read_csv(path_variables, index_col = 0).sort_values('variable')
print("\nData series in the database:")
print(db.to_string())





#################################
#       Tools
#################################

###------format dictionary for indent config file------###

#data_name = 'GDI-BEA-A'
#path_data = Path('data')/'parse_data'/f'{data_name}.csv'
#df = pd.read_csv(path_data)
#for i in df.columns:
#    print(f'"{i}":,')
#








