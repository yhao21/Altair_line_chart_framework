import json, os, re
import pandas as pd
from pathlib import Path

import streamlit as st
from streamlit.components.v1 import iframe

from MyTools import chart_tools as chart
from MyTools.chart_template.select_column_to_plot import line_frame
from MyTools.load_data import load_dataset
from MyTools.load_data import get_percentage_share_GDP
from MyTools.load_data import get_rgdp
from MyTools.frequency_conversion import convert_frequency


def merge_data_df(data_name_list:list, target_freq = ''):
    """
    For each data_name in data_name_list:
        1. Load corresponding df named <data_name.csv> in directory parse_data.
            -- Use "Time" column as index, and drop "Time" column.
        2. Merge all dfs.
            -- You must make sure that data in all dfs are measured in the same frequency, such as daily, monthly, quarterly...
    """
    result = pd.DataFrame()
    for data_name in data_name_list:
        df = pd.read_csv(os.path.join('data', 'parse_data', f'{data_name}.csv'), index_col = 'Time')
        result = pd.concat([result, df], axis = 1)
        print(df[df.columns.to_list()[0]])


    # Convert "Time" index to datetime type, then sort value from past to the present.
    result.index = pd.to_datetime(result.index)
    result = result.sort_index()
    result['Time'] = result.index

    if target_freq:
        result = convert_frequency(result, target_freq)
    print(result)

    return result




class show_chart():
    def __init__(self):
        self.current_dir = Path.cwd()
        self.isRGDP = False
        self.percent_share_GDP = False
        self.data_source()

    def data_source(self):

        self.BEA_table_1_1_4 = '[BEA(GDP Deflator)](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*gwn0bv*_ga*MTYwMTE4MjkzMS4xNzYxNTExMTMw*_ga_J4698JNNFT*czE3NjQwNzM3MzckbzgkZzEkdDE3NjQwNzQ5NDAkajU0JGwwJGgw#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDNdLCJkYXRhIjpbWyJjYXRlZ29yaWVzIiwiU3VydmV5Il0sWyJOSVBBX1RhYmxlX0xpc3QiLCI0Il1dfQ==)'
        self.BEA_table_1_1_5 = '[BEA(NGDP)](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*16sjbxu*_ga*MTQ5ODgyNDYwNS4xNzM2Nzc1ODM1*_ga_J4698JNNFT*czE3NjM3NTYxOTAkbzI0JGcxJHQxNzYzNzU3MDQyJGo1NSRsMCRoMA..#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDNdLCJkYXRhIjpbWyJjYXRlZ29yaWVzIiwiU3VydmV5Il0sWyJOSVBBX1RhYmxlX0xpc3QiLCI1Il1dfQ==)'
        self.BEA_table_1_1_6 = '[BEA(RGDP)](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*16sjbxu*_ga*MTQ5ODgyNDYwNS4xNzM2Nzc1ODM1*_ga_J4698JNNFT*czE3NjM3NTYxOTAkbzI0JGcxJHQxNzYzNzU3MDQyJGo1NSRsMCRoMA..#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDNdLCJkYXRhIjpbWyJjYXRlZ29yaWVzIiwiU3VydmV5Il0sWyJOSVBBX1RhYmxlX0xpc3QiLCI2Il1dfQ==)'
        self.BEA_table_1_10 = '[BEA(GDI)](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*1s61qpy*_ga*MTYwMTE4MjkzMS4xNzYxNTExMTMw*_ga_J4698JNNFT*czE3NjU0NjY1MDUkbzEzJGcxJHQxNzY1NDY2NTI1JGo0MCRsMCRoMA..#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDNdLCJkYXRhIjpbWyJjYXRlZ29yaWVzIiwiU3VydmV5Il0sWyJOSVBBX1RhYmxlX0xpc3QiLCI1MSJdXX0=)'
        self.FRED_implementation_of_MP = '[FRED(Monetary Policy Rates)](https://fred.stlouisfed.org/graph/?g=1Ng5J)'
        

    def show(self, fig_name, chart_config):
        """
        This function decides which chart to plot based on the fig_name chose by users.

        To show rgdp data, set self.isRGDP = True
        """
        self.chart_config = chart_config

        ###------National Income------###
        # NGDP
        if fig_name == "Gross domestic product (quarterly)":
            data_name = "NGDP-BEA-Q"
            data_source = self.BEA_table_1_1_5
            description = 'Billions of dollars; seasonally adjusted'
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Gross domestic product (annual)":
            data_name = "NGDP-BEA-A"
            data_source = self.BEA_table_1_1_5
            description = 'Billions of dollars; seasonally adjusted'
            self.show_GDP(data_source, description, data_name)

        # Percentage share of NGDP
        elif fig_name == "Percentage share of GDP (quarterly)":
            data_name = "NGDP-BEA-Q"
            self.percent_share_GDP = True
            data_source = self.BEA_table_1_1_5
            description = 'Percent, %'
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Percentage share of GDP (annual)":
            data_name = "NGDP-BEA-A"
            self.percent_share_GDP = True
            data_source = self.BEA_table_1_1_5
            description = 'Percent, %'
            self.show_GDP(data_source, description, data_name)

        # RGDP
        elif fig_name == "Real gross domestic product (quarterly)":
            data_name = "NGDP-BEA-Q"
            self.isRGDP = True
            data_source = f'{self.BEA_table_1_1_5}, {self.BEA_table_1_1_4}'
            description = f'Billions of chained (2017) dollars; seasonally adjusted'
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Real gross domestic product (annual)":
            data_name = "NGDP-BEA-A"
            self.isRGDP = True
            data_source = f'{self.BEA_table_1_1_5}, {self.BEA_table_1_1_4}'
            description = f'Billions of chained (2017) dollars; seasonally adjusted'
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Nominal vs. real GDP":
            src = "https://fred.stlouisfed.org/graph/graph-landing.php?g=1NOOf"
            ngdp_rgdp = chart.add_html_chart(src, border, hor_align, ver_align, chart_width, chart_height, iframe_height)

        # GDI
        elif fig_name == "Gross domestic income (quarterly)":
            data_name = "GDI-BEA-Q"
            data_source = self.BEA_table_1_10
            description = 'Billions of dollars; seasonally adjusted'
            self.show_GDP(data_source, description, data_name)

        elif fig_name == "Gross domestic income (annual)":
            data_name = "GDI-BEA-A"
            data_source = self.BEA_table_1_10
            description = 'Billions of dollars; seasonally adjusted'
            self.show_GDP(data_source, description, data_name)



        ###------Monetary Policy------###
        # FFR, FFR target, IORB rate, ONRRP rate and other policy rates.
        elif fig_name == "Monetary Policy and Interest Rate (monthly)":
            policy_rates = [
                    'FFER-FRED-D',
                    'FFRTUPPER-FRED-D',
                    'FFRTLOWER-FRED-D',
                    'FFRT-FRED-D',
                    'DISCOUNTPRIMARY-FRED-D',
                    'SREPOMR-FRED-D',
                    'IORR-FRED-D',
                    'IORB-FRED-D',
                    'ONRRP-FRED-D',
                    ]
            df = merge_data_df(policy_rates, target_freq = 'M')
            #df = pd.read_csv(os.path.join('data', 'parse_data', 'FFER-FRED-D.csv'))
            data_source = self.FRED_implementation_of_MP
            description = 'Percent, %'
            line_frame(fig_name, df, indent_config = {}, description = description, source = data_source).show(n_legend_cols = 3)

        elif fig_name == "Monetary Policy and Interest Rate (daily)":
            src = "https://fred.stlouisfed.org/graph/graph-landing.php?g=1OQiC"
            ngdp_rgdp = chart.add_html_chart(src, border, hor_align, ver_align, chart_width, chart_height, iframe_height)





    def show_GDP(self, data_source, description, data_name):
        indent_config = self.chart_config[data_name[:-2]]

        path_data = os.path.join(self.current_dir, 'data', 'parse_data', f"{data_name}.csv")
        df = load_dataset(path_data)

        # If to display percentage share of NGDP
        if self.percent_share_GDP:
            data_name = f"{data_name}_share"
            df = get_percentage_share_GDP(df, 'Gross domestic product')
        
        if self.isRGDP:
            # Load GDP deflator
            if data_name.split('-')[-1] == 'A':
                df_GDPDeflator = load_dataset(os.path.join(self.current_dir, 'data', 'parse_data', 'GDPDeflator-BEA-A.csv'))
                data_name = 'RGDP_A'
            else:
                df_GDPDeflator = load_dataset(os.path.join(self.current_dir, 'data', 'parse_data', 'GDPDeflator-BEA-Q.csv'))
                data_name = 'RGDP_Q'

            df = get_rgdp(df, df_GDPDeflator)

        line_frame(data_name, df, indent_config = indent_config, description = description, source = data_source).show()





# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Path
# ~~~~~~~~~~~~~~~~~~~~~~~
# Note your current_dir is the path of py file that you run streamlit. In this case, is app.py
# Hence, current_dir is /home/.../[python]streamlit/project/lecture_data
current_dir = Path.cwd()



# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Page Layout
# ~~~~~~~~~~~~~~~~~~~~~~~
# If show border. Set to True when design. Set to False when publish.
border = False 
# horizontal and vertical alignment in container.
hor_align, ver_align = 'center', 'center'



# ~~~~~~~~~~~~~~~~~~~~~~~
# Load Config Files
# ~~~~~~~~~~~~~~~~~~~~~~~
###------Chart config------###
with open(os.path.join(current_dir, 'config', 'chart_config.json')) as f:
    chart_config = json.load(f)

# Set the width and height of container used to present chart.
chart_width = chart_config['chart']['chart_width']
chart_height = chart.get_chart_height(chart_config['chart']['WHratio'], chart_width)
# I leave another 30px so it has enough space to show icons such as "Customize" and "Download Data".
iframe_height = chart_height + 30



##############################
# Main Content
##############################

# ~~~~~~~~~~~~~~~~~~~~~~~
# Figure name
# ~~~~~~~~~~~~~~~~~~~~~~~

fig_list = [
    ###------National Income------###
    # nominal gdp
    "Gross domestic product (quarterly)",
    "Gross domestic product (annual)",
    # % share of ngdp
    "Percentage share of GDP (quarterly)",
    "Percentage share of GDP (annual)",
    # real gdp
    "Real gross domestic product (quarterly)",
    "Real gross domestic product (annual)",
    # nominal vs. rgdp
    'Nominal vs. real GDP',
    # Gross domestic income (GDI)
    "Gross domestic income (quarterly)",
    "Gross domestic income (annual)",
    
    
    ###------Monetary Policy------###
    "Monetary Policy and Interest Rate (monthly)",
    "Monetary Policy and Interest Rate (daily)",
        ]


fig_name = st.selectbox('Choose a chart', fig_list, label_visibility = 'hidden')
st.divider()

show_chart().show(fig_name, chart_config)







