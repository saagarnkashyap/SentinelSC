# import streamlit as st
#
# from datetime import datetime
#
# from src.data_loader import load_inventory
# from src.metrics import (
#     total_inventory_value,
#     average_eoq,
#     critical_skus,
#     average_lead_time,
# )
#
# from src.charts import (
#     inventory_value_chart,
#     category_distribution,
# )
#
# from src.utils import currency, number, days
#
#
# def render_control_tower():
#
#     # ----------------------------------------------------
#     # LOAD DATA
#     # ----------------------------------------------------
#
#     df = load_inventory()
#
#     # ----------------------------------------------------
#     # HEADER
#     # ----------------------------------------------------
#
#     st.title("🏠 Control Tower")
#
#     st.caption(
#         "Enterprise Supply Chain Operations Dashboard"
#     )
#
#     c1, c2 = st.columns([8, 2])
#
#     with c1:
#
#         st.markdown(
#             f"""
# **Operational Status:** 🟢 Healthy
#
# Last Updated: **{datetime.now().strftime('%d %b %Y • %H:%M')}**
# """
#         )
#
#     with c2:
#
#         st.success("LIVE")
#
#     st.divider()
#
#     # ----------------------------------------------------
#     # KPI ROW
#     # ----------------------------------------------------
#
#     kpi1, kpi2, kpi3, kpi4 = st.columns(4)
#
#     with kpi1:
#
#         st.metric(
#             label="Inventory Value",
#             value=currency(
#                 total_inventory_value(df)
#             ),
#             delta="+3.4%"
#         )
#
#     with kpi2:
#
#         st.metric(
#             label="Average EOQ",
#             value=number(
#                 average_eoq(df)
#             ),
#             delta="Optimal"
#         )
#
#     with kpi3:
#
#         st.metric(
#             label="Critical SKUs",
#             value=number(
#                 critical_skus(df)
#             ),
#             delta="-2"
#         )
#
#     with kpi4:
#
#         st.metric(
#             label="Average Lead Time",
#             value=days(
#                 average_lead_time(df)
#             ),
#             delta="-0.8 Days"
#         )
#
#     st.divider()


import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.data_loader import load_inventory
from src.metrics import total_inventory_value, average_eoq, critical_skus, average_lead_time
from src.utils import currency, number, days


def render_control_tower():
    df = load_inventory()

    required = [
        "SKU", "Category", "Supplier", "Warehouse",
        "Current Inventory", "Safety Stock", "Reorder Point", "Unit Cost", "EOQ", "Lead Time"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.title("🏠 Control Tower")
        st.error(f"Missing columns: {missing}")
        st.write("Available:", df.columns.tolist())
        return

    # numeric safety
    for c in ["Current Inventory", "Safety Stock", "Reorder Point", "Unit Cost", "EOQ", "Lead Time"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Current Inventory", "Reorder Point", "Unit Cost", "EOQ", "Lead Time"])

    if df.empty:
        st.warning("No valid data available.")
        return

    df["Inventory Value"] = df["Current Inventory"] * df["Unit Cost"]
    df["Health"] = df.apply(
        lambda r: "Critical" if r["Current Inventory"] < r["Reorder Point"]
        else "Low" if r["Current Inventory"] < r["Safety Stock"]
        else "Healthy",
        axis=1,
    )

    st.title("🏠 Control Tower")
    st.caption("Enterprise Supply Chain Operations Dashboard")

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

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Inventory Value", currency(total_inventory_value(df)), "+3.4%")
    with k2:
        st.metric("Average EOQ", number(average_eoq(df)), "Optimal")
    with k3:
        st.metric("Critical SKUs", number(critical_skus(df)), "-2")
    with k4:
        st.metric("Average Lead Time", days(average_lead_time(df)), "-0.8 Days")

    st.divider()

    # Charts
    ch1, ch2 = st.columns(2)

    with ch1:
        cat = (
            df.groupby("Category", dropna=False)["Inventory Value"]
            .sum()
            .reset_index()
            .sort_values("Inventory Value", ascending=False)
        )
        fig_cat = px.bar(
            cat, x="Category", y="Inventory Value",
            title="Inventory Value by Category",
            color="Inventory Value", color_continuous_scale="Blues"
        )
        fig_cat.update_layout(template="plotly_white", height=350, coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with ch2:
        crit = df[df["Health"] == "Critical"]
        if crit.empty:
            st.info("No critical SKUs by supplier.")
        else:
            sup = (
                crit.groupby("Supplier")["SKU"]
                .count()
                .reset_index(name="Critical SKUs")
                .sort_values("Critical SKUs", ascending=False)
            )
            fig_sup = px.bar(
                sup, x="Supplier", y="Critical SKUs",
                title="Critical SKUs by Supplier",
                color="Critical SKUs", color_continuous_scale="Reds"
            )
            fig_sup.update_layout(template="plotly_white", height=350, coloraxis_showscale=False)
            st.plotly_chart(fig_sup, use_container_width=True)

    st.divider()

    # Alert table
    st.subheader("🚨 Priority Alerts")
    alerts = df[df["Health"].isin(["Critical", "Low"])].copy()
    alerts = alerts.sort_values(["Health", "Current Inventory"], ascending=[True, True]).head(10)

    if alerts.empty:
        st.success("No priority alerts.")
    else:
        st.dataframe(
            alerts[["SKU", "Category", "Supplier", "Warehouse", "Current Inventory", "Reorder Point", "Health"]],
            use_container_width=True,
            hide_index=True
        )