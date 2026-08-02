import streamlit as st

from datetime import datetime

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

from src.utils import currency, number, days


def render_control_tower():

    # ----------------------------------------------------
    # LOAD DATA
    # ----------------------------------------------------

    df = load_inventory()

    # ----------------------------------------------------
    # HEADER
    # ----------------------------------------------------

    st.title("🏠 Control Tower")

    st.caption(
        "Enterprise Supply Chain Operations Dashboard"
    )

    c1, c2 = st.columns([8, 2])

    with c1:

        st.markdown(
            f"""
**Operational Status:** 🟢 Healthy

Last Updated: **{datetime.now().strftime('%d %b %Y • %H:%M')}**
"""
        )

    with c2:

        st.success("LIVE")

    st.divider()

    # ----------------------------------------------------
    # KPI ROW
    # ----------------------------------------------------

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:

        st.metric(
            label="Inventory Value",
            value=currency(
                total_inventory_value(df)
            ),
            delta="+3.4%"
        )

    with kpi2:

        st.metric(
            label="Average EOQ",
            value=number(
                average_eoq(df)
            ),
            delta="Optimal"
        )

    with kpi3:

        st.metric(
            label="Critical SKUs",
            value=number(
                critical_skus(df)
            ),
            delta="-2"
        )

    with kpi4:

        st.metric(
            label="Average Lead Time",
            value=days(
                average_lead_time(df)
            ),
            delta="-0.8 Days"
        )

    st.divider()