import altair as alt

def get_format_tooltip(cols: list) -> list:
    """
    Return a format tooltip (add , to numbers, and round to 2 decimal point) 
    setup for multiple columns, such as
        [
        alt.Tooltip('one_col_name', format = ',.2f'),
        alt.Tooltip('one_col_name', format = ',.2f'),
        alt.Tooltip('one_col_name', format = ',.2f'),
        ...
        ]
    
    Arguments:
        cols: a list contains column names.
    """
    results = []
    for col in cols:
        results.append(alt.Tooltip(col, format = ',.2f'))

    return results
