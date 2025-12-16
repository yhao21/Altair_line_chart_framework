import json, os
import pandas as pd
from pathlib import Path

import streamlit as st
from streamlit.components.v1 import iframe

from MyTools import chart_tools as chart
from MyTools.chart_template.select_column_to_plot import line_frame

from MyTools.load_data import load_dataset
from MyTools.load_data import get_percentage_share_GDP




# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Path
# ~~~~~~~~~~~~~~~~~~~~~~~
current_dir = Path.cwd()



# ~~~~~~~~~~~~~~~~~~~~~~~
# Set Page Layout
# ~~~~~~~~~~~~~~~~~~~~~~~
#st.set_page_config(layout = 'wide')
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

###------css config file------###
with open(os.path.join(current_dir, 'config', 'config.css')) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)


# ~~~~~~~~~~~~~~~~~~~~~~~
# Load Datasets
# ~~~~~~~~~~~~~~~~~~~~~~~
PCE_BEA_M = 'PCE-BEA-M'
path_PCE_BEA_M = os.path.join(current_dir, 'data', 'parse_data', f"{PCE_BEA_M}.csv")
df_PCE_BEA_M = load_dataset(path_PCE_BEA_M)



# ~~~~~~~~~~~~~~~~~~~~~~~
# Load Data config
# ~~~~~~~~~~~~~~~~~~~~~~~

# a dict containing the indent information.
PCE_BEA_indent = chart_config[PCE_BEA_M[:-2]] 


# ~~~~~~~~~~~~~~~~~~~~~~~
# Data name
# ~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~
# Data Source
# ~~~~~~~~~~~~~~~~~~~~~
PCE_M_table_2_8_5 = '[BEA](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*nbj3it*_ga*MTQ5ODgyNDYwNS4xNzM2Nzc1ODM1*_ga_J4698JNNFT*czE3NjM5OTE5ODUkbzI3JGcxJHQxNzYzOTkyMTUzJGoxOSRsMCRoMA..#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDMsM10sImRhdGEiOltbImNhdGVnb3JpZXMiLCJTdXJ2ZXkiXSxbIk5JUEFfVGFibGVfTGlzdCIsIjgyIl0sWyJGaXJzdF9ZZWFyIiwiMTk1OSJdLFsiTGFzdF9ZZWFyIiwiMjAyNSJdLFsiU2NhbGUiLCItOSJdLFsiU2VyaWVzIiwiTSJdXX0=)'




# ~~~~~~~~~~~~~~~~~~~~~~~
# Main Content
# ~~~~~~~~~~~~~~~~~~~~~~~


###------PCE monthly------###


st.write("# Personal Consumption Expenditure (PCE)")
container = st.container(border = border, horizontal_alignment = hor_align, vertical_alignment = ver_align)

with container:

    line_frame(PCE_BEA_M, df_PCE_BEA_M, indent_config = PCE_BEA_indent, description = 'Billions of dollars; seasonally adjusted at annual rates', source = PCE_M_table_2_8_5, show_zero = False).show()
