import pandas as pd
from pathlib import Path
import streamlit as st


def parse_BEA_month(time_col):
    """
    This function convert BEA month (e.g., 2025M08) to regular pandas datetime object (e.g., 2025-08).
    time_col: a pandas series, refers to the time column.
    """
    return [i.replace('M', '-') for i in time_col]


#=======================================================

def determine_frequency(path_data: str) -> str:
    """
    This function determines the type of time series data. It will be either monthly (M), quarterly (Q), or annual (A).
    How it works:
        This function will extract the last letter of file name. 

    If path_data = './PCE_M.csv'
    `Path().stem` returns PCE_M
    """

    return Path(path_data).stem.split('_')[1]



#def convert_frequency(path_data:str, target_frequency:str):
def convert_frequency(raw_data, target_frequency:str):
    """
    This function can do the following conversion:
        1. from monthly to quarterly or anual data
        2. from quarterly to anual data.
    Then it return the new df in which Time is the first column.

    target_frequency:  Frequency you would like to convert the data to.
                        "MS", month start;
                        "ME", month end;
                        "QS",
                        "QE",
                        "AS",
                        "AE",...


    """
    #raw_data = pd.read_csv(path_data)
    raw_data['Time'] = pd.to_datetime(raw_data['Time'])
    # resample to target frequency
    df = raw_data.resample(target_frequency, on = 'Time').mean()
    # If target_frequency = "QS", then freq = 'Q', etc.
    df_t = pd.PeriodIndex(df.index, freq = target_frequency[0]).to_frame().reset_index(drop = True)
    df = df.reset_index(drop = True)
    df = pd.concat([df_t, df], axis = 1).round(2)

    print(df)


    return df



