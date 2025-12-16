from datetime import time
import os, json
from pathlib import Path
import pandas as pd
import numpy as np
from MyTools.frequency_conversion import parse_BEA_month


def save_and_update_data(df, path_data, override, data_name):
    """
    Save and update dataset to parse_data.
    """
    freq = data_name.split('-')[-1]
    df = format_time(freq, df)

    if override or not os.path.exists(path_data):
        df.to_csv(path_data, index = False)
        print(df)
        print("New dataset is saved.")
    else:
        old_df = pd.read_csv(path_data)
        old_df = format_time(freq, old_df)
        df = df[~df['Time'].isin(old_df['Time'])]

        if len(df) > 0:
            print('New data:')
            print(df)
            df = pd.concat([old_df, df])
            df.to_csv(path_data, index = False)
            print("Your data is up-to-date.")

        else:
            print("No new data.")




def format_time(freq, df):
    if freq == 'A':
        df['Time'] = df['Time'].astype('int')
    elif freq == 'Q':
        df['Time'] = pd.PeriodIndex(pd.to_datetime(df['Time']), freq = 'Q')

    return df



def detect_existence_time_period_BEA(one_dict:dict):
    """
    This function detect whether to extract time period info from BEA json.
    As BEA arrange data in rows like this,
        Time 1990 1991 ...
        GDP   x1   x2  ...
        C     c1   c2  ...
    There is no need to collect time period after the GDP row.

    Return: a signal (bool) of whether extract time period, and the time period itself.
    """
    line_number = one_dict['LineNumber']
    if line_number == '1':
        time_period = one_dict['TimePeriod']
        return True, time_period
    else:
        return False, None




def parse_BEA_data(request_data_dir:str, parse_data_dir:str, data_name:str, override: bool = False, drop_cols: list = [], MnToBn: bool = False):
    """
    This function extract NGDP data from json file.

        Example of <one_dict>:
                    {
                    "TableName": "T10105",
                    "SeriesCode": "A191RC",
                    "LineNumber": "1",
                    "LineDescription": "Gross domestic product",
                    "TimePeriod": "1947Q1",
                    "METRIC_NAME": "Current Dollars",
                    "CL_UNIT": "Level",
                    "UNIT_MULT": "6",
                    "DataValue": "243,164",
                    "NoteRef": "T10105"
                    }
    """

    data_path = os.path.join(request_data_dir, f'{data_name}.json')
    with open(data_path) as f:
        data = json.load(f)['BEAAPI']['Results']['Data']

    df = pd.DataFrame()
    col_value = []
    time_value = []
    variable = None  # column name
    row_index = None # row index of BEA data. There are 26 rows in the table of nominal GDP (expenditure approach).
    item_index, last_item_index = 1, len(data)

    
    items = []

    for one_dict in data:
        col_name = one_dict['LineDescription']
        line_number = one_dict['LineNumber']

        # If this this first now, do nothing
        if row_index == None:
            row_index = line_number
            variable = col_name
        else:
            # This is a new row and it is not the first row.
            # If this variable (row) does not occur in df, empty the list to store this new variable.
            if line_number != row_index:

                df_temp = pd.DataFrame(col_value, columns = [variable], index = time_value)
                df = pd.concat([df, df_temp], axis = 1)
                col_value = []
                row_index = line_number
                variable = col_name
                time_value = []


        time_value.append(one_dict['TimePeriod'])
        component_value = float(one_dict['DataValue'].replace(',','')) # Get billions of dollars
        if MnToBn:
            component_value = component_value/1000 # Get billions of dollars

        col_value.append(component_value)


        ## if it is the last item, save the last column to df.
        if item_index == last_item_index:
            df_temp = pd.DataFrame(col_value, columns = [col_name], index = time_value)
            df = pd.concat([df, df_temp], axis = 1)

        item_index += 1


    df_t = pd.DataFrame(df.index.values, columns = ['Time'])
    df = pd.concat([df_t, df.reset_index(drop = True)], axis = 1)

    ###------Drop unwanted columns------###
    if drop_cols:
        df = df.drop(drop_cols, axis = 1)


    ###------Adjust Time column name for monthly data------###
    # BEA monthly data (e.g., 2025M01) is not accepted by pd.datetime(). Hence I need to manually
    # convert it to YYYY-MM form.
    data_freq = data_name.split('-')[-1]
    if data_freq == 'M':
        df['Time'] = parse_BEA_month(df['Time'])



    data_path = os.path.join(parse_data_dir, f"{data_name}.csv")
    save_and_update_data(df, data_path, override, data_name)





def parse_FRED_data(raw_data_dir:str, parse_data_dir:str, data_name:str, override = False):
    ###------load raw data------###
    path_raw_data = Path(raw_data_dir)/f"{data_name}.json"
    with open(path_raw_data) as f:
        json_data = json.load(f)
    data = json_data['observations']
    title = json_data['title']

    
    ###------parse data------###
    result = []
    for row in data:
        # FRED uses "." for missing values.
        if row['value'] == '.':
            result.append([row['date'], np.nan])
        else:
            result.append([row['date'], row['value']])

    df = pd.DataFrame(result, columns = ['Time', title])
    ###------save csv------###
    path_data = Path(parse_data_dir, f"{data_name}.csv")
    save_and_update_data(df, path_data, override, data_name)




if __name__ == "__main__":

    raw_data_dir = os.path.join('data', 'request_data')

    data_dir = os.path.join('data', 'parse_data')
    Path(data_dir).mkdir(exist_ok = True, parents = True)
    
    drop_cols = {
            "RGDP-BEA-A":['Residual'],
            }

    
    ###------Parse BEA data------###
    #data_name = "NGDP-BEA-A"
    #parse_BEA_data(raw_data_dir, data_dir, data_name, MnToBn=True)


    ###------Parse FRED data------###
    override = True
    data_name = 'ONRRP-FRED-D'
    parse_FRED_data(raw_data_dir, data_dir, data_name, override=override)











