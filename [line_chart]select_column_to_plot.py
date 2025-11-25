import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import json

# ~~~~~~~~~~~~~~~~~~~~~
# Formatting related functions
# ~~~~~~~~~~~~~~~~~~~~~
def get_chart_padding():
    return {"top": 5, "bottom":5, "left":50, "right":5}


def get_table_widget_info(table_name:str) -> dict:
    """
    This function returns a dict cotaining information for buttons.
    """
    widget_info = {
            "modify_button":{
                "label":"Modify",
                "key":f"{table_name}_modify_button"
                },
            "table_button":{
                "label":"Table",
                "key":f"{table_name}_table_button"
                },
            "chart_button":{
                "label":"Chart",
                "key":f"{table_name}_chart_button"
                },
            }
    return widget_info


def adjust_table_indent(df_show_index, indent_step:int = 4):
    """
    This function returns a df index that is indent-adjusted.
    """
    indent_config = st.session_state['indent_config']
    index = [f"{' ' * indent_config[i] * indent_step}{i}" for i in df_show_index]

    return index


def format_tooltip(cols):
    result = ['Time']
    for col in cols:
        result.append(alt.Tooltip(f"{col}:Q", format = ',.2f'))

    return result



def NumCol_accounting_format(cols:list) -> dict:
    """
    This function return a column format dict that let the number column take acounting form.
    """
    col_format = {}
    for col in cols:
        col_format[col] = st.column_config.NumberColumn(format = 'accounting')
    return col_format




def update_table_indent(state_name_df, state_name_adj_indent):
    """
    Adjust table indent.
    """
    st.session_state[state_name_df].index = adjust_table_indent(st.session_state[state_name_df].index)
    # Turn adjust indent signal to False
    st.session_state[state_name_adj_indent] = False



# ~~~~~~~~~~~~~~~~~~~~~
# Performance functions
# ~~~~~~~~~~~~~~~~~~~~~

def get_frequency(data_name: str) -> str:
    """
    This function determines the type of time series data. It will be either monthly (M), quarterly (Q), or annual (A).
    How it works:
        This function will extract the last letter of data name. 

    If data_name = 'PCE_M', return "M"
    """

    return data_name.split('_')[-1]



def get_default_period(time_list:list, default_obs):
    """
    Return the first and last period given the value of prefered number of observations (default_obs).
    If default_obs = n > 0, return the begin and end period for the FIRST n obs.
    If default_obs = n <= 0, return the begin and end period for the LAST n obs.
    """
    if default_obs > 0:
        time_hor = time_list[:default_obs]
    else:
        time_hor = time_list[default_obs:]
    first_period, last_period = time_hor[0], time_hor[-1]


    return first_period, last_period





def get_table_df(df):
    """
    df: 
               Time  Gross domestic product  ...  Nondefense  State and local
        0    1947Q1                 243.164  ...       4.166           13.318
        1    1947Q2                 245.968  ...       5.319           13.714


    df.transpose() is the following:
                                                   0        1    ...        312        313
        Time                                    1947Q1   1947Q2  ...     2025Q1     2025Q2
        Gross domestic product                 243.164  245.968  ...  30042.113  30485.729
        Personal consumption expenditures      156.161  160.031  ...  20554.984  20789.926

    Returned df:
                                                1947Q1   1947Q2  ...     2025Q1     2025Q2
        Gross domestic product                 243.164  245.968  ...  30042.113  30485.729
        Personal consumption expenditures      156.161  160.031  ...  20554.984  20789.926
    """
    df = df.transpose()
    df.columns = df.loc['Time', :].values
    df = df.drop('Time')


    return df



def init_session_state(state_name, state_value):
    """
    Initialize the default value for session state.
    """
    if state_name not in st.session_state:
        st.session_state[state_name] = state_value


def get_plot_df(selected_index, state_name_df):
    """
    This function returns a df for ploting.

    st.session_state[state_name_df]:
                                              1947Q1 1947Q2  ...    2025Q1    2025Q2
        Gross domestic product                243.16 245.97  ... 30,042.11 30,485.73
        Personal consumption expenditures     156.16 160.03  ... 20,554.98 20,789.93
            Goods                              95.59  98.25  ...  6,432.30  6,471.11

    Returned plot_df:
               Gross domestic product Personal consumption expenditures    Goods Durable goods
        1947Q1                 243.16                            156.16    95.59         20.72
        1947Q2                 245.97                            160.03    98.25         21.35
    """
    index = st.session_state[state_name_df].index[selected_index].values
    plot_df = st.session_state[state_name_df].copy().loc[index, :].transpose()
    plot_df.columns = [i.strip() for i in plot_df] # remove indent.

    return plot_df
    


def get_chart_lines(df, content_height:int, zero_line = False):
    """
    Return a line chart.

    bg_lines:   An alt.Chart() item, e.g., a plot of growth rate of gdp.
                If you pass a `bg_lines`, this function will add `bg_lines` (an alt chart item) to the main chart.
    zero_line:  If True, draw y = 0 in chart. Usually used in growth rate chart.

    """

    ###------Define height for elements------###
    bar_height = 0.07 * content_height
    legend_height = 0.25 * content_height
    chart_height = content_height - bar_height - legend_height


    ###------Format df------###
    # replace good.1 with good1
    plot_cols = [i.replace('.', '') for i in df.columns]
    df.columns = plot_cols
    df['Time'] = df.index.values

    color_items = df.columns.to_list()
    color_items.remove('Time')


    ###------Define selector------###
    selector = alt.selection_point(
            nearest = True,
            on = 'pointerover',
            clear = 'pointerout',
            empty = 'none'
            )

    bar_selector = alt.selection_interval(encodings = ['x'])

    ###------Define spike line------###
    rule_tooltip = format_tooltip(plot_cols)
    rule = alt.Chart(df).mark_rule(color = 'grey').encode(
            x = 'Time',
            y = alt.value(0),
            y2 = alt.value('height'),
            opacity = alt.condition(selector, alt.value(1), alt.value(0)),
            #tooltip = ['Time'] + rule_tooltip,
            tooltip = rule_tooltip,
            ).add_params(selector)


    ###------Define lines------###

    lines = alt.Chart(df).transform_fold(plot_cols).mark_line().encode(
            x = alt.X('Time', title = None, axis = alt.Axis(labelAngle = 0)),
            y = alt.Y('value:Q', title = None),
            #tooltip = rule_tooltip,
            color = alt.Color(
                'key:N',
                scale = alt.Scale(domain = color_items),
                legend = alt.Legend(
                    title = None,
                    orient = 'bottom',
                    direction = 'vertical',
                    columns = 5,
                    labelLimit = 500
                    )
                ),
            ).properties(height = chart_height)


    ###------If zero_line = True, show zero line (y = 0)------###
    zero_mark_opacity = alt.value(0)
    if zero_line:
        zero_mark_opacity = alt.value(1)

    zero_mark = alt.Chart(df).mark_line(color = 'grey', size = 3).encode(
            x = 'Time',
            y = alt.datum(0),
            opacity = zero_mark_opacity,
            )

    ###------Add selection bar below the chart------###
    bar = alt.Chart(df).mark_bar().encode(
            x = alt.X('Time', title = None, axis = None),
            y = alt.Y(df.columns[0], title = None, axis = None),
            opacity = alt.condition(bar_selector, alt.value(1), alt.value(0.2))
            ).add_params(bar_selector).properties(height = bar_height)

    ###------Merge chart items------###

    chart = alt.layer(rule, lines, zero_mark).transform_filter(bar_selector)

    # Use configure_view to change color and size of the chart border.
    chart = (chart & bar).configure_view(stroke = 'white', strokeWidth = .2)




    return chart




def format_time_column(df):

    time_col = df['Time'].astype('string')
    return time_col




class line_frame():
    def __init__(self, data_name, df, description:str = 'test', box_height:int = 700, default_obs:int = -4, indent_config:dict = {}, source:str = '', df_bg_line = [], show_zero = False):
        self.data_name = data_name
        self.df = df
        self.description = description
        self.box_height = box_height
        self.obs = default_obs
        self.indent_config = indent_config
        self.data_source = source
        self.df_bg_line = df_bg_line # it will be True if you call `add_baselines` to  add lines at the background.
        self.zero_line = show_zero




    
        
    def show(self):
        """
        This function returns a format chart which allow you to select a particular column to plot.




        df: dataframe contains data. 
             Time     Gross domestic product  Personal consumption expenditures  ...  State and local  
            1947Q1                   243.164                            156.161  ...           13.318  
            1947Q2                   245.968                            160.031  ...           13.714  
            1947Q3                   249.585                            163.543  ...           14.324  
        default_obs: a NON-ZERO numerical value,
                        If it is 4, then show data in the first 4 years.
                        If it is -4, then show data in the last 4 years.
                        If user mistakenly pass a 0, then replace it by -4.

        indent_config: a dict contains indent info for the variable name in the table.
                       Example:
                                    {"Gross domestic product":0,
	    			"Personal consumption expenditures":0,
	    			"Goods":1}
        """

        ###------Format Time column and get first, last period------###
        # Convert values in Time column to string.
        self.df['Time'] = format_time_column(self.df)

        # Get start and end period
        first_period, last_period = get_default_period(list(self.df['Time']), self.obs)


        ###------Form dataset------###
        # df to show by default. By default, it shows the last four obs.
        # Do not format the indent of df until it is being persented in the box.
        df_show = self.df.query("Time >= @first_period and Time <= @last_period")
        df_show = get_table_df(df_show)


        ###------Init session states------###
        #For data_name
        init_session_state('data_name', self.data_name)

        # For df to show
        self.state_name_df = f'df_show_{self.data_name}'
        init_session_state(self.state_name_df, df_show)


        # For indent adjument signal
        self.state_name_adj_indent = f'adj_indent_{self.data_name}'
        init_session_state(self.state_name_adj_indent, True)

        # For table-chart switch signal
        self.state_name_show_table = f'show_table_{self.data_name}'
        init_session_state(self.state_name_show_table, True)

        # For modify signal
        self.state_name_modify_content = f'modify_content_{self.data_name}'
        init_session_state(self.state_name_modify_content, False)



        ###------Container for description and buttons------###
        container = st.container(
                border = False,
                horizontal_alignment = 'left', vertical_alignment = 'bottom',
                horizontal = True
                )

        # Button config
        button_config = get_table_widget_info(self.data_name)
        button_modify = button_config['modify_button']
        button_table = button_config['table_button']
        button_chart = button_config['chart_button']

        with container:

            if self.data_source:
                st.write(
                        f"""
                        {self.description}

                        Source: {self.data_source}
                        """
                        )
            else:
                st.write(self.description)

            st.space() # add space, so all bottoms align to the right.

            # Add "Modify" button that allows users to modify time range.
            if st.button(button_modify['label'], button_modify['key']):
                self.modify_BEA_table()

            if st.button(button_table['label'], button_table['key']):
                st.session_state[self.state_name_show_table] = True

            if st.button(button_chart['label'], button_chart['key']):
                st.session_state[self.state_name_show_table] = False




        ###------Container of data table------###
        box = st.container(border = False, horizontal_alignment = 'left', vertical_alignment = 'center', horizontal = True, height = self.box_height, key = self.key('DataTableFrame'))

        with box:
            if st.session_state[self.state_name_show_table]: # show table
                self.show_table()

            else: # show chart
                self.show_chart()
            


    @st.dialog("Choose Time Horizon")
    def modify_BEA_table(self):
    
        qrts_list = self.df['Time'].values
        with st.form(f'{self.data_name}_modify'):
            first_period = st.selectbox('First Period:', options = qrts_list, key = self.key('st'))
            last_period = st.selectbox('Last Period:', options = qrts_list, key = self.key('et'))
    
    
            if st.checkbox('All Years', key = self.key('AllYear')):
                first_period, last_period = qrts_list[0], qrts_list[-1]
    
            submit = st.form_submit_button('Refresh Table', key = self.key('ModifySubmit'))
            if submit:
                # Save filtered df.
                df_show = get_table_df(self.df.query('Time >= @first_period and Time <= @last_period'))
                # Add indent to variable column.
                st.session_state[self.state_name_df] = df_show
                # Reset adjust df indent signal since new df is formed.
                st.session_state[self.state_name_adj_indent] = True
                st.session_state[self.state_name_modify_content] = True
    
            
                st.rerun()
    
    
    
    def show_table(self):
    
        # If pass indent config file, then format table index.
        if self.indent_config and st.session_state[self.state_name_adj_indent]:
            init_session_state('indent_config', self.indent_config)
            update_table_indent(self.state_name_df, self.state_name_adj_indent)
    
        st.dataframe(
                st.session_state[self.state_name_df],
                height = 'stretch',
                column_config = NumCol_accounting_format(st.session_state[self.state_name_df].columns),
                key = self.key('DataTableContent')
                )
    
    
    
    def show_chart(self, border = False):
        content_height = self.box_height - 40
    
        # By default, df is a indent-adjusted. After clicking on Modify, it becomes an unadjusted df.
        df = st.session_state[self.state_name_df]
    
        boxLeft = st.container(border = border, vertical_alignment = 'top', width = 300, height = content_height, key = self.key('ChartLeftBox'))
        boxRight = st.container(border = border, vertical_alignment = 'bottom', height = content_height, key = self.key('ChartRightBox'))
    
        # Adjust indent
        if st.session_state[self.state_name_modify_content] and st.session_state[self.state_name_adj_indent]:
            update_table_indent(self.state_name_df, self.state_name_adj_indent)
    
        with boxLeft:
            gdp_items = st.dataframe(
                        pd.DataFrame(df.index, columns = ['Items']),
                        on_select = 'rerun',
                        selection_mode = 'multi-row',
                        hide_index = True,
                        height = content_height - 30,
                        key = self.key('ChartLeftBoxList')
                    )
            # a list of index for rows being selected, such as [0, 1, 2].
            selected_items = gdp_items.selection['rows']
    
        with boxRight:
            plot_df = get_plot_df(selected_items, self.state_name_df)
            if len(self.df_bg_line):
                plot_df = self.append_bg_line(plot_df)

            # Show chart only if users select one or more items.
            if selected_items:
                # Hide grid line for both axis.
                chart = get_chart_lines(plot_df, content_height, zero_line = self.zero_line).configure_axis(grid = False)

                st.altair_chart(chart, height = content_height - 30, key = self.key('ChartRightBoxChart'))
    
    
    
    def key(self, key_name):
        """
        This function returns a key name for your streamlit elements
        """
        return f'{self.data_name}_{key_name}'
            
    def append_bg_line(self, df):
        """
        This function append columns in df_bg_line to the main df so they will be ploted
        together.
        """

        first_period, last_period = df.index.min(), df.index.max()
        df_bg = self.df_bg_line
        df_bg['Time'] = format_time_column(df_bg)
        df_bg.index = df_bg['Time'].values
        df_bg = (df_bg
                .query("Time >= @first_period and Time <= @last_period")
                .drop('Time', axis = 1)
                )
        df = pd.concat([df, df_bg], axis = 1)

        return df
                    


if __name__ == '__main__':

#   ______________________________________________________________
#  |                                 |                            |
#  | Description                     |     Modify | Table | Chart |
#  |_________________________________|____________________________|
#   _______________  _____________________________________________
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |   columns     ||               chart                         |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |               ||                                             |
#  |_______________||_____________________________________________|
#  
#
#    Requirement:
#        1. a dataframe
#        2. an indent config file (optional). If not, the program will not adjust indent for the first column (index) of df.
#
#    Instruction:
#        Call `line_frame(data_name, df, indent_config, description, source).show()` to present the chart/table frame.
#
#        data_name:      the name of dataset, also, it will be the flag of key for streamlit components.
#        df:             dataframe
#        indent_config:  [optional] a dictionary contains configure info to adjust indent of the first column/index of your presented dataframe.
#        Description:    [optional]Text used to explain the table. It will show up at the top left corner of the frame.
#        source:         [optional]Text will hyperlink (in markdown form) that tells the data source. It will show up below the Description.
#                        Example: 
#                            source_bea, source_fred = '[BEA](your_url)', '[FRED](your_url)'
#                            source = f'{source_bea}, {source_fred}' # This is the one you pass to `line_frame`.
#        df_bg_line:     Dataframe contains the data you want to show in chart but not in table. 
#                        For example, the main df contains the growth rate of C, I, G, and NX. And you want to include the growth rate of RGDP in the chart, but you do not want to show
#                        the growth rate of RGDP in table.
#                            1. The first column must be 'Time', and its value must be consistent with the main df, e.g., if Time in df is 2020Q1, then Time in df_bg_line must also
#                                be 2022Q1, 2024Q1, ... It CANNOT be in other form, such as 2024-01-01.
#



    #from mytools.load_data import get_percentage_share_GDP
    #from mytools.frequency_conversion import get_frequency




    st.set_page_config(layout = 'wide')

    percentage_share_of_GDP = False

    data_name = 'NGDP-BEA-A'
    #data_name = 'RGDP-BEA-A'
    df = pd.read_csv(f'./data/{data_name}.csv')

    #if percentage_share_of_GDP:
    #    # get % share of GDP
    #    df = get_percentage_share_GDP(df)

    ###------Format Data Source------###
    source_bea = '[BEA](https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey&_gl=1*1dmdvxn*_ga*MTQ5ODgyNDYwNS4xNzM2Nzc1ODM1*_ga_J4698JNNFT*czE3NjM3Mzc2NjUkbzIyJGcxJHQxNzYzNzM3NjY5JGo1NiRsMCRoMA..#eyJhcHBpZCI6MTksInN0ZXBzIjpbMSwyLDNdLCJkYXRhIjpbWyJjYXRlZ29yaWVzIiwiU3VydmV5Il0sWyJOSVBBX1RhYmxlX0xpc3QiLCI1Il1dfQ==)'
    source_unemployment = '[FRED](https://fred.stlouisfed.org/series/UNRATE)'

    data_source = f"{source_bea}, {source_unemployment}"

    ###------Load indent config file for row index of table------###
    with open('./config/chart_config.json') as f:
        indent_config = json.load(f)[data_name[:-2]]


    line_frame(data_name, df, indent_config = indent_config, description = '[Billions of dollars] Seasonally adjusted', source = data_source).show()



    #=====================================================
    # ~~~~~~~~~~~~~~~~~~~~~
    # Example of plotting both the main df and background lines as comparison.
    # ~~~~~~~~~~~~~~~~~~~~~
#
#    data = pd.read_csv('../../data/RGDP-BEA-A.csv')
#    df_line = data[['Time']]
#    df_line['Growth Rate of RGDP'] = (data['Gross domestic product'].pct_change() * 100).round(2)
#
#
#    line_frame(data_name, df, indent_config = indent_config, description = '[Billions of dollars] Seasonally adjusted', source = data_source, df_bg_line = df_line, show_zero = True).show()
#
#
