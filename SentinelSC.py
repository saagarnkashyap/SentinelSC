# import streamlit as st
#
# from ui.theme import load_theme
# from ui.command_console import render_command_console
#
# st.set_page_config(
#     page_title="SentinelSC",
#     page_icon="📦",
#     layout="wide",
# )
#
# load_theme()
#
# page = render_command_console()
#
# st.write(page)


import streamlit as st

from ui.theme import load_theme
from ui.command_console import render_command_console
from ui.router import render_page

st.set_page_config(
    page_title="SentinelSC",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_theme()

selected_page = render_command_console()

render_page(selected_page)