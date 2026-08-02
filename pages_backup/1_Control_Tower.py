import streamlit as st
from src.utils import days
from src.data_loader import load_inventory

from src.metrics import (
    total_inventory_value,
    average_eoq,
    critical_skus,
    average_lead_time,
)

from src.charts import (
    inventory_value_chart,
    category_distribution,
)

from config import *

from ui.theme import load_theme

load_theme()

st.set_page_config(
    page_title=APP_NAME,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
)

df = load_inventory()

st.title("🏠 Control Tower")

st.caption(APP_DESCRIPTION)


st.divider()


###########################################################
# SYSTEM STATUS
###########################################################

st.subheader("🟢 System Status")

col1, col2, col3 = st.columns(3)

with col1:

    st.success("Inventory Engine Online")

with col2:

    st.success("Optimization Engine Active")

with col3:

    st.success("Synthetic Dataset Loaded")

###########################################################
# KPI ROW
###########################################################

c1, c2, c3, c4 = st.columns(4)

from src.utils import currency

with c1:

    st.metric(
        "Inventory Value",
        currency(total_inventory_value(df)),
    )

from src.utils import number

with c2:

    st.metric(
        "Average EOQ",
        number(average_eoq(df)),
    )

with c3:

    st.metric(
        "Critical SKUs",
        number(critical_skus(df)),
    )

with c4:

    st.metric(
        "Average Lead Time",
        days(average_lead_time(df)),
    )

st.divider()

###########################################################
# CHARTS
###########################################################

left, right = st.columns(2)

with left:

    st.plotly_chart(
        inventory_value_chart(df),
        use_container_width=True,
    )

with right:

    st.plotly_chart(
        category_distribution(df),
        use_container_width=True,
    )

st.divider()

###########################################################
# INVENTORY TABLE
###########################################################

st.subheader("📦 Inventory Snapshot")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

