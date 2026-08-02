import streamlit as st
from streamlit_option_menu import option_menu


def render_command_console():

    with st.sidebar:

        st.markdown("# 📦 SentinelSC")

        st.caption(
            "Enterprise Supply Chain Intelligence"
        )

        st.success("🟢 LIVE")

        st.divider()

        page = option_menu(
            menu_title="CONTROL CENTER",

            options=[
                "Control Tower",
                "Inventory Intelligence",
                "Scenario Simulator",
                "Analytics",
                "AI Advisor",
                "About",
            ],

            icons=[
                "house",
                "boxes",
                "exclamation-triangle",
                "graph-up",
                "robot",
                "info-circle",
            ],

            default_index=0,
        )

        st.divider()

        # st.markdown("### SYSTEM STATUS")
        #
        # st.success("Inventory Engine")
        #
        # st.success("Optimization Engine")
        #
        # st.warning("Simulation Engine")
        #
        # st.error("AI Copilot")

        st.divider()

        st.caption("Version 1.0.0")

        st.caption("© SentinelSC")

    return page