import streamlit as st
from streamlit.components.v1 import iframe

def get_chart_height(WHratio: str, chart_width: int) -> int:
    """
    This function compute and return the correspoinding chart height give a certain width-height
    ratio (WHratio, e.g., 16:9) and the chart width (chart_width).
    """
    chart_height = chart_width / int(WHratio.split(":")[0]) * int(WHratio.split(":")[1])
    return int(chart_height)



def add_width_and_height_to_src(src: str, chart_width:int, chart_height:int) -> str:
    """
    This function add width and height parameter to the source url of a html chart.
    """
    return src + f"&width={chart_width}&height={chart_height}"



def create_a_container(border:bool, hor_align:str, ver_align:str):
    """
    Return a preset container.
    """
    return st.container(border = border, horizontal_alignment = hor_align, vertical_alignment = ver_align)



def load_html_chart(src: str, chart_width:int, iframe_height:int):
    chart = iframe(
            src = src,
            width = chart_width,
            # leave a little more space to show icons such as "Customize" and "Download Data".
            height = iframe_height,
            scrolling = False
            )
    return chart



def add_html_chart(src:str, border:bool, hor_align:str, ver_align:str, chart_width:int, chart_height:int, iframe_height:int):
    """
    This function creates a container and put a html chart in it. Then it return the container.
    """
    container = st.container(border = border, horizontal_alignment = hor_align, vertical_alignment = ver_align)
    with container:
        src = add_width_and_height_to_src(src, chart_width, chart_height)
        html_chart = load_html_chart(src, chart_width, iframe_height)
    return container



