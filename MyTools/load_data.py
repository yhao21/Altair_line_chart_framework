import pandas as pd
import numpy as np
import streamlit as st

def load_dataset(path_data):
    df = pd.read_csv(path_data)

    return df




def get_percentage_share_GDP(df, denominator:str):
    """
    Gross domestic product
    Compute % share through [each col]/denominator, except for the Time column.
    """
    result = df[['Time']]
    base = df[denominator]


    for col in df.columns:
        if col != 'Time':
            result[col] = (df[col]/base) * 100


    return result.round(2)



def get_rgdp(df, p):
    """
    This function compute and return a df contains RGDP using NGDP (df) and GDP deflator (p).

    df: a df contains NGDP (quarterly, or annual data)
    p:  a df contains the corresponding GDP deflator

    Note:
        1. Real Net export = real export - real import
        2. This function will not compute real `change in private inventories`.

    """
    
    rgdp = pd.DataFrame({'Time':df['Time'].values})
    # start from the second items since the first is Time.
    for col in df.columns.to_list()[1:]:
        try:
            rgdp[col] = df[col]/p[col] * 100
        except:
            rgdp[col] = np.nan

    rgdp['Net exports of goods and services'] = rgdp['Exports'] - rgdp['Imports']


    return rgdp



if __name__ == '__main__':
    df = pd.read_csv('../data/parse_data/NGDP-BEA-A.csv')
    p = pd.read_csv('../data/parse_data/GDPDeflator-BEA-A.csv')
    rgdp = get_rgdp(df, p)
    print(rgdp)
