import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import json

# ~~~~~~~~~~~~~~~~~~~~~
# Formatting related functions
# ~~~~~~~~~~~~~~~~~~~~~

def default_line_format():
    return {
            "line_width": 3.0,
            "line_style":[1,0] # solid line
            }


def init_line_format(col_selected):
    """
    This function save format information for each line in a dictionary.
    {
        <line_name>:{
                        "line_style":[],
                        "line_width":float,
                        "line_color":string
                    }
    }
    """
    format_info = {}
    for i in col_selected:
        format_info[i] = default_line_format()
        format_info[i]['line_color'] = get_a_color()

    return format_info


def builtin_line_styles():
    """
    Return a dictionary contains built-in line styles (strokeDash).
    """
    return {
            "Solid":[1,0],
            "Dash":[10,7.5],
            "Short Dash":[5,3.5],
            "Long Dash":[20,15],
            "Dot":[2,10],
            "Short Dot":[2,3],
            "Dash Dot":[10,7,2,7],
            "Dash Dot Dot": [10,7,2,7,2,7],
            }


def line_style_mapping(value):
    """
    Given value is a list, return the name of corresponding line style defined in function <builtin_line_styles>.
    Given value is a name of line style, return the corresponding list used to specify altair line style (strkeDash).
    """
    line_style_dic = builtin_line_styles()
    return line_style_dic[value] if type(value) is str else list(line_style_dic.keys())[list(line_style_dic.values()).index(value)]


def standardize_col_name(col_name:list):
    """
    Format column name of df for plotting.
    """
    # format column names with :
    col_name = [
            i.replace('.', '').replace(':', '')
            for i in col_name
            ]
    return col_name


def get_a_color():
    """
    Generate a hex code.
    """
    color_code = np.random.randint(0, 0xFFFFFF)
    hex_code = f"#{color_code:06x}"
    return hex_code



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
            "format_button":{
                "label":"Format",
                "key":f"{table_name}_format_button"
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

def get_YoY_window(freq:str):
    """
    This function compute the window for YoY change or percentage change.
    Example: given monthly data, window should be 12; given quarterly data, window should be 4.
    freq: M, Q, A, ...
    """
    return 12 if freq == 'M' else (4 if freq == 'Q' else 1)


def get_indexed_df(df):
    """
    This function return a df contains transformed indexed data, in which the the value for obs
    in the first period (first row) will be set to 100.

    Restriction: 
        The first column must be Time.
        Each row refers to obs from a period.
    Example of return df:

           Gross domestic product    ...  Nondefense  State and local
        0              100.000000    ...  100.000000       100.000000
        1              101.153131    ...  127.676428       102.973419
    """
    # Drop Time column
    df = df.drop('Time', axis = 1)
    indexed_first_row = df.iloc[0, :].values
    df = df/indexed_first_row * 100

    return df


def unit_transformation(unit:str, df, data_name, original_description):
    """
    This function convert the df to a specific unit listed below.

    unit_list = [
            'Level',
            'Change', 'Change from Year Ago',
            'Percent Change', 'Percent Change from Year Ago',
            'Natural Log', 'Index'
            ]
    data_unit:  a certain unit above.
    """
    cols = df.columns.to_list()
    cols.remove('Time')
    freq = data_name[-1] # data frequency, such as M, Q, A.
    window = get_YoY_window(freq)

    result = df[['Time']]
    if unit == 'Level':
        result = df
        st.session_state[f'description_{data_name}'] = original_description
    elif unit == 'Change':
        result = pd.concat([result, df[cols].diff(1)], axis = 1)
        st.session_state[f'description_{data_name}'] = original_description
    elif unit == 'Change from Year Ago':
        result = pd.concat([result, df[cols].diff(window)], axis = 1)
    elif unit == 'Percent Change':
        result = pd.concat([result, df[cols].pct_change(periods = 1) * 100], axis = 1)
        st.session_state[f'description_{data_name}'] = 'Percent, %'
    elif unit == 'Percent Change from Year Ago':
        result = pd.concat([result, df[cols].pct_change(periods = window) * 100], axis = 1)
        st.session_state[f'description_{data_name}'] = 'Percent, %'
    elif unit == 'Natural Log':
        result = pd.concat([result, np.log(df[cols])], axis = 1)
        st.session_state[f'description_{data_name}'] = 'Natural Log'
    elif unit == 'Index':
        df_indexed = get_indexed_df(df)
        result = pd.concat([result, df_indexed], axis = 1)
        st.session_state[f'description_{data_name}'] = 'Index (Scale Value to 100 for The First Period)'

    return result


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

        self.initialize_session_state()

    def init_default_df_to_show(self):
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
        return df_show, first_period, last_period


    def initialize_session_state(self):
        """
        When you need to define a new session state:
            First, assign its name to a class attribute (self.state_name_<variable name>)
            Second, append its value to dict "ss" through ss[self.state_name_<variable name>] = ...
        """
        df_show, first_period, last_period = self.init_default_df_to_show()

        ss = {
                f'description_{self.data_name}': self.description,  # For description
                f'zero_line_{self.data_name}': self.zero_line,   # For y = 0 line
                }

        # Used to save users choice of variable unit, such as "Level", "Percentage Change", ...
        self.state_name_var_unit = f'var_unit_{self.data_name}'
        # Used to save users choice of if to display data from "All Periods".
        self.state_name_all_periods = f'all_period_checkbox_{self.data_name}'
        # Used to save users choice of the first period of dataset.
        self.state_name_first_period = f'first_period_{self.data_name}'
        # Used to save users choice of the last period of dataset.
        self.state_name_last_period = f'last_period_{self.data_name}'
        # For df to show
        self.state_name_df = f'df_show_{self.data_name}'
        # For df to plot when user clicks "Chart" button.
        self.state_name_selected_cols = f'selected_cols_{self.data_name}'
        # For indent adjument signal
        self.state_name_adj_indent = f'adj_indent_{self.data_name}'
        # For table-chart switch signal
        self.state_name_show_table = f'show_table_{self.data_name}'
        # For modify signal
        self.state_name_modify_content = f'modify_content_{self.data_name}'
        # For line formats (line style, width, and color)
        np.random.seed(400) # Specify random seed to generate color scheme.
        self.state_name_line_format_info = f'line_format_info_{self.data_name}'


        ss[self.state_name_var_unit] = 'Level'
        ss[self.state_name_all_periods] = False
        ss[self.state_name_first_period] = first_period
        ss[self.state_name_last_period] = last_period
        ss[self.state_name_df] = df_show
        ss[self.state_name_selected_cols] = []
        ss[self.state_name_adj_indent] = True
        ss[self.state_name_show_table] = True
        ss[self.state_name_modify_content] = False
        ss[self.state_name_line_format_info] = init_line_format(standardize_col_name(self.df.columns.to_list()[1:]))

        for i in ss.keys():
            init_session_state(i, ss[i])
        print(init_line_format(standardize_col_name(self.df.columns.to_list()[1:])))

        
    def show(self, n_legend_cols:int = 4):
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

        # Allow altair to deal with a dataset with more than 5000 obs.
        alt.data_transformers.disable_max_rows()

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
        button_format = button_config['format_button']

        with container:

            if self.data_source:
                st.write(
                        f"""
                        {st.session_state[f'description_{self.data_name}']}

                        Source: {self.data_source}
                        """
                        )
            else:
                st.write(st.session_state[f'description_{self.data_name}'])

            st.space() # add space, so all bottoms align to the right.

            # Add "Modify" button that allows users to modify time range.
            if st.button(button_modify['label'], button_modify['key']):
                self.modify_BEA_table()

            if st.button(button_table['label'], button_table['key']):
                st.session_state[self.state_name_show_table] = True

            if st.button(button_chart['label'], button_chart['key']):
                st.session_state[self.state_name_show_table] = False

            if st.button(
                    button_format['label'],
                    button_format['key'],
                    disabled = st.session_state[self.state_name_show_table]
                    ):
                self.format_lines_in_chart()


        ###------Container of data table------###
        box = st.container(border = False, horizontal_alignment = 'left', vertical_alignment = 'center', horizontal = True, height = self.box_height, key = self.key('DataTableFrame'))

        with box:
            # If pass indent config file, then format table index.
            if self.indent_config and st.session_state[self.state_name_adj_indent]:
                st.session_state['indent_config'] = self.indent_config
                update_table_indent(self.state_name_df, self.state_name_adj_indent)

            if st.session_state[self.state_name_show_table]: # show table
                self.show_table()
            else: # show chart
                self.show_chart(n_legend_cols = n_legend_cols)
            


    @st.dialog("Choose Time Horizon")
    def modify_BEA_table(self):
    
        qrts_list = list(self.df['Time'].values)
        with st.form(f'{self.data_name}_modify'):
            # Selectbox: First period.
            first_period = st.selectbox(
                    'First Period:',
                    options = qrts_list,
                    key = self.key('st'),
                    index = qrts_list.index(st.session_state[self.state_name_first_period])
                    )

            # Selectbox: Last period.
            last_period = st.selectbox(
                    'Last Period:',
                    options = qrts_list,
                    key = self.key('et'),
                    index = qrts_list.index(st.session_state[self.state_name_last_period])
                    )
    
            # Check box: if to plot data in all periods.
            st.session_state[self.state_name_all_periods] = st.checkbox(
                    'All Periods',
                    key = self.key('AllPeriods'),
                    value = st.session_state[self.state_name_all_periods]
                    )

            if st.session_state[self.state_name_all_periods]:
                first_period, last_period = qrts_list[0], qrts_list[-1]

            # Update first and last period to session state.
            st.session_state[self.state_name_first_period] = first_period
            st.session_state[self.state_name_last_period] = last_period


            ###------Select data unit------###
            unit_list = [
                    'Level',
                    'Change', 'Change from Year Ago',
                    'Percent Change', 'Percent Change from Year Ago',
                    'Natural Log', 'Index'
                    ]
            data_unit = st.selectbox(
                    'Units',
                    options = unit_list,
                    key = self.key('data_unit'),
                    index = unit_list.index(st.session_state[self.state_name_var_unit])
                    )
            st.session_state[self.state_name_var_unit] = data_unit
            ###------Decide if to show y = 0------###
            if data_unit in ['Percent Change', 'Percent Change from Year Ago']:
                st.session_state[f'zero_line_{self.data_name}'] = True

    

            ###------Submit button------###
            submit = st.form_submit_button('Refresh Table', key = self.key('ModifySubmit'))
            if submit:
                # Save filtered df.
                df_show = unit_transformation(
                        data_unit,
                        self.df.query('Time >= @first_period and Time <= @last_period'),
                        self.data_name,
                        self.description
                        )

                # Adjust indent for variable column.
                df_show = get_table_df(df_show)
                st.session_state[self.state_name_df] = df_show
                # Reset adjust df indent signal since new df is formed.
                if self.indent_config:
                    st.session_state[self.state_name_adj_indent] = True
                else:
                    st.session_state[self.state_name_adj_indent] = False
                    
                st.session_state[self.state_name_modify_content] = True

                st.rerun()

    
    @st.dialog("Lines Format")
    def format_lines_in_chart(self):
        """
        Allow users to format lines.
        """
        disable_save_button = True
        with st.form(f'form_format_{self.data_name}'):

            Format_info = {} # A dict to save format info for each line.
            # Users need to select at least one data series, otherwise hide format setups and disable "save" button.
            if st.session_state[self.state_name_selected_cols]:
                disable_save_button = False
                for one_line_name in standardize_col_name(st.session_state[self.state_name_selected_cols]):
                    format_module, one_format_info = self.line_format_module(one_line_name)
                    Format_info[one_line_name] = one_format_info

            else:
                st.write("Please first select one or more data series listed on the left side.")


            ###------Submit buton------###
            submit = st.form_submit_button('Save', key = self.key('FormatSubmit'), disabled = disable_save_button)

            if submit:
                for one_line_name in Format_info.keys():
                    st.session_state[self.state_name_line_format_info][one_line_name] = Format_info[one_line_name]
                print(st.session_state[self.state_name_line_format_info])
                print(Format_info)

                st.rerun()
                print(st.session_state[self.state_name_line_format_info])



    def line_format_module(self, line_name:str):
        """
        Return a standardize module that allows user to customize the style, width, and color of a line.
            line_width      line_style      color
        """
        # A list of names for built-in line styles.
        line_style_list = list(builtin_line_styles().keys())
        # location index of line style name to show in "line_style_list".
        default_index = line_style_list.index(line_style_mapping(st.session_state[self.state_name_line_format_info][line_name]['line_style']))

        container = st.container(border = True)
        with container:
            st.write(f"### {line_name}")
            with st.container(horizontal = True, vertical_alignment = 'center'):
                col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
                line_width = col1.number_input(
                        'Line width',
                        min_value = 1.0,
                        key = f'line_width_{line_name}',
                        value = st.session_state[self.state_name_line_format_info][line_name]['line_width']
                        )
                line_style = col2.selectbox(
                        'Line style',
                        key = f'line_style_{line_name}',
                        options = line_style_list,
                        # Use index to specify default value. It saves the latest change.
                        index = default_index
                        )
                line_color = col3.color_picker(
                        'Color',
                        key = f'line_color_{line_name}',
                        value = st.session_state[self.state_name_line_format_info][line_name]['line_color']
                        )
    
        return container, {"line_width":line_width, "line_style":line_style_mapping(line_style), "line_color":line_color}
        
    
    def show_table(self):
    
        st.dataframe(
                st.session_state[self.state_name_df],
                height = 'stretch',
                column_config = NumCol_accounting_format(st.session_state[self.state_name_df].columns),
                key = self.key('DataTableContent')
                )
    
    
    
    def show_chart(self, n_legend_cols = 4, border = False):

        content_height = self.box_height - 40
        df = st.session_state[self.state_name_df]
        boxLeft, boxRight = st.columns(
                [0.2, 0.7],
                border = border,
                vertical_alignment = 'top',
                )
    
        # Adjust indent
        if st.session_state[self.state_name_modify_content] and st.session_state[self.state_name_adj_indent]:
            update_table_indent(self.state_name_df, self.state_name_adj_indent)
    
        # A list of variables to plot.
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
    
        # Chart
        with boxRight:
            plot_df = get_plot_df(selected_items, self.state_name_df)
            # Update selected col to session state for formatting lines.
            st.session_state[self.state_name_selected_cols] = plot_df.columns.to_list()

            if len(self.df_bg_line):
                plot_df = self.append_bg_line(plot_df)

            # Show chart only if users select one or more items.
            if selected_items:
                # Hide grid line for both axis.
                chart = self.get_chart_lines(plot_df, content_height, n_legend_cols = n_legend_cols).configure_axis(grid = False)

                st.altair_chart(chart, key = self.key('ChartRightBoxChart'))
    
    


    def get_chart_lines(self, df, content_height:int, n_legend_cols = 4):
        """
        Return a line chart.
    
        bg_lines:   An alt.Chart() item, e.g., a plot of growth rate of gdp.
                    If you pass a `bg_lines`, this function will add `bg_lines` (an alt chart item) to the main chart.
        zero_line:  If True, draw y = 0 in chart. Usually used in growth rate chart.
    
        """

        ###------Standardize column name for df------###
        df.columns = standardize_col_name(df.columns.to_list())
        col_selected = df.columns.to_list()
        df['Time'] = df.index.values

    
        ###------Define height for elements------###
        bar_height = 0.07 * content_height
        legend_height = 0.25 * content_height
        chart_height = content_height - bar_height - legend_height
    
    
        ###------Define selector------###
        selector = alt.selection_point(
                nearest = True,
                on = 'pointerover',
                clear = 'pointerout',
                empty = False
                )
    
        bar_selector = alt.selection_interval(encodings = ['x'])

        legend_selector = alt.selection_point(
                fields = ['key'],
                bind = 'legend',
                on = 'click',
                clear = 'dblclick',
                )
    
        ###------Define spike line------###
        rule_tooltip = format_tooltip(col_selected)
        rule = alt.Chart(df).mark_rule(color = 'grey').encode(
                x = 'Time',
                y = alt.value(0),
                y2 = alt.value('height'),
                opacity = alt.condition(selector, alt.value(1), alt.value(0)),
                tooltip = rule_tooltip,
                ).add_params(selector).transform_filter(bar_selector)
    
    
        ###------Define lines------###
        lines = alt.Chart(df).transform_fold(col_selected).mark_line().encode(
                x = alt.X('Time', title = None, axis = alt.Axis(labelAngle = 0)),
                y = alt.Y('value:Q', title = None),
                color = alt.Color(
                    'key:N',
                    scale = alt.Scale(
                        domain = col_selected,
                        range = [st.session_state[self.state_name_line_format_info][i]['line_color'] for i in col_selected]
                        ),
                    legend = alt.Legend(
                        title = f"""
                                Click on one of the items below to highligh a single line.
                                Hold Shift button and click to select multiple items.
                                Double click in the main chart to restore default setup.
                                """,
                        titleLimit = 1500,
                        orient = 'bottom',
                        direction = 'horizontal',
                        columns = n_legend_cols,
                        labelLimit = 500,
                        symbolSize = 400,
                        symbolStrokeWidth = 4,
                        ),
                    # Legend is arranged in the same order as in self.df
                    sort = list(st.session_state[self.state_name_line_format_info].keys())
                    ),

                size = alt.Size(
                    'key:N',
                    scale = alt.Scale(
                        domain = col_selected,
                        range = [st.session_state[self.state_name_line_format_info][i]['line_width'] for i in col_selected] if len(col_selected) > 1 else [st.session_state[self.state_name_line_format_info][col_selected[0]]['line_width'], st.session_state[self.state_name_line_format_info][col_selected[0]]['line_width'] - 0.01]
                        ),
                    # If I set legend = None, if will overlap with the color legend, and the symbol
                    # will not present properly (clipped). I have not yet figure out how to solve
                    # this problem, so I simply put the Size legend on the left of chart and 
                    # set the strokewidth to 0 to hide it.
                    legend = alt.Legend(
                        orient = 'left', values = [''], title = None, symbolStrokeWidth = 0
                        )
                    #legend = None
                    ),

                strokeDash = alt.StrokeDash(
                    'key:N',
                    scale = alt.Scale(
                        domain = col_selected,
                        range = [st.session_state[self.state_name_line_format_info][i]['line_style'] for i in col_selected]
                        ),

                    legend = None
                    ),

                opacity = alt.condition(
                    legend_selector,
                    alt.value(1),
                    alt.value(0.2)
                    ),
                ).add_params(legend_selector).transform_filter(bar_selector).properties(height = chart_height)
    
        ###------If zero_line = True, show zero line (y = 0)------###
        zero_mark_opacity = alt.value(0)
        if st.session_state[f'zero_line_{self.data_name}']:
            zero_mark_opacity = alt.value(1)
    
        zero_mark = alt.Chart(df).mark_line(color = 'grey', size = 3).encode(
                x = 'Time',
                y = alt.datum(0),
                opacity = zero_mark_opacity,
                ).transform_filter(bar_selector)
    
        ###------Add selection bar below the chart------###
        bar = alt.Chart(self.df).mark_bar().encode(
                x = alt.X('Time', title = None, axis = None),
                y = alt.Y(self.df.columns[1], title = None, axis = None),
                #y = alt.Y(df.columns[0], title = None, axis = None),
                opacity = alt.condition(bar_selector, alt.value(1), alt.value(0.2))
                ).add_params(bar_selector).properties(height = bar_height)
    
        ###------Merge chart items------###
        chart = alt.layer(rule, lines, zero_mark)
    
        # Use configure_view to change color and size of the chart border.
        chart = (chart & bar).configure_view(stroke = 'grey', strokeWidth = .2)

        return chart
    

    
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
                    


