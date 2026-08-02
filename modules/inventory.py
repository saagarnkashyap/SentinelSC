# # import numpy as np
# # import pandas as pd
# #
# # Z_SCORE = 1.65
# #
# # #eoq section
# # def calculate_eoq(df: pd.DataFrame) -> pd.DataFrame:
# #
# #     df = df.copy()
# #
# #     df["EOQ"] = np.sqrt(
# #         (2 * df["Annual Demand"] * df["Ordering Cost"])
# #         / df["Holding Cost"]
# #     ).round(0)
# #
# #     return df
# #
# # #safety stock
# # def calculate_safety_stock(df: pd.DataFrame):
# #
# #     df = df.copy()
# #
# #     demand_std = df["Daily Demand"] * 0.20
# #
# #     df["Safety Stock"] = (
# #         Z_SCORE
# #         * demand_std
# #         * np.sqrt(df["Lead Time"])
# #     ).round()
# #
# #     return df
# #
# # #reorder point
# # def calculate_reorder_point(df):
# #
# #     df = df.copy()
# #
# #     df["Reorder Point"] = (
# #         df["Daily Demand"] * df["Lead Time"]
# #         + df["Safety Stock"]
# #     ).round()
# #
# #     return df
# #
# # #pipeline
# # def optimize_inventory(df):
# #
# #     df = calculate_eoq(df)
# #
# #     df = calculate_safety_stock(df)
# #
# #     df = calculate_reorder_point(df)
# #
# #     return df
# #
# # if __name__ == "__main__":
# #
# #     from dataset import generate_inventory_dataset
# #
# #     df = generate_inventory_dataset()
# #
# #     df = optimize_inventory(df)
# #
# #     print(df.head())
#
#
# import streamlit as st
#
#
# def render_inventory():
#
#     st.title("📦 Inventory Intelligence")



# import streamlit as st
# import pandas as pd
#
# from src.data_loader import load_inventory
# from src.metrics import (
#     total_inventory_value,
#     average_eoq,
#     critical_skus,
#     average_lead_time,
# )
#
# from src.utils import (
#     currency,
#     number,
#     days,
# )
#
#
# def render_inventory():
#
#     # ---------------------------------------------------------
#     # LOAD DATA
#     # ---------------------------------------------------------
#
#     df = load_inventory()
#
#     st.title("📦 Inventory Intelligence")
#
#     st.caption(
#         "Monitor inventory health, suppliers, warehouses and replenishment policies."
#     )
#
#     st.divider()
#
#     # ---------------------------------------------------------
#     # KPI CARDS
#     # ---------------------------------------------------------
#
#     k1, k2, k3, k4 = st.columns(4)
#
#     with k1:
#
#         st.metric(
#             "Inventory Value",
#             currency(
#                 total_inventory_value(df)
#             ),
#             "+2.8%"
#         )
#
#     with k2:
#
#         st.metric(
#             "Average EOQ",
#             number(
#                 average_eoq(df)
#             ),
#             "Optimal"
#         )
#
#     with k3:
#
#         st.metric(
#             "Critical SKUs",
#             number(
#                 critical_skus(df)
#             ),
#             "-2"
#         )
#
#     with k4:
#
#         st.metric(
#             "Average Lead Time",
#             days(
#                 average_lead_time(df)
#             ),
#             "-0.6 Days"
#         )
#
#     st.divider()
#
#     # ---------------------------------------------------------
#     # FILTERS
#     # ---------------------------------------------------------
#
#     left, right = st.columns([3, 2])
#
#     with left:
#
#         search = st.text_input(
#             "🔍 Search SKU / Description",
#             placeholder="Example: ASIC-001"
#         )
#
#     with right:
#
#         category = st.selectbox(
#             "Category",
#             ["All"] + sorted(df["Category"].unique())
#         )
#
#     c1, c2 = st.columns(2)
#
#     with c1:
#
#         supplier = st.selectbox(
#             "Supplier",
#             ["All"] + sorted(df["Supplier"].unique())
#         )
#
#     with c2:
#
#         warehouse = st.selectbox(
#             "Warehouse",
#             ["All"] + sorted(df["Warehouse"].unique())
#         )
#
#     # ---------------------------------------------------------
#     # APPLY FILTERS
#     # ---------------------------------------------------------
#
#     filtered = df.copy()
#
#     if search:
#
#         filtered = filtered[
#             filtered["SKU"].str.contains(search, case=False)
#             |
#             filtered["Description"].str.contains(search, case=False)
#         ]
#
#     if category != "All":
#
#         filtered = filtered[
#             filtered["Category"] == category
#         ]
#
#     if supplier != "All":
#
#         filtered = filtered[
#             filtered["Supplier"] == supplier
#         ]
#
#     if warehouse != "All":
#
#         filtered = filtered[
#             filtered["Warehouse"] == warehouse
#         ]
#
#     st.success(
#         f"Showing {len(filtered)} of {len(df)} SKUs"
#     )
#     # ---------------------------------------------------------
#     # INVENTORY SNAPSHOT
#     # ---------------------------------------------------------
#
#     st.divider()
#
#     st.subheader("📋 Inventory Snapshot")
#
#     inventory_view = filtered.copy()
#
#     # Inventory Health
#
#     inventory_view["Health"] = inventory_view.apply(
#         lambda row:
#         "🔴 Critical"
#         if row["Current Inventory"] < row["Reorder Point"]
#         else (
#             "🟡 Low"
#             if row["Current Inventory"] < row["Safety Stock"] * 1.2
#             else "🟢 Healthy"
#         ),
#         axis=1,
#     )
#
#     inventory_view["Inventory Value"] = (
#             inventory_view["Current Inventory"]
#             * inventory_view["Unit Cost"]
#     )
#
#     display_columns = [
#         "SKU",
#         "Description",
#         "Category",
#         "Supplier",
#         "Warehouse",
#         "Current Inventory",
#         "Safety Stock",
#         "Reorder Point",
#         "EOQ",
#         "Lead Time",
#         "Health",
#     ]
#
#     st.dataframe(
#         inventory_view[display_columns],
#         use_container_width=True,
#         hide_index=True,
#     )
#
#     st.divider()
#
#     # ---------------------------------------------------------
#     # INVENTORY SUMMARY
#     # ---------------------------------------------------------
#
#     left, right = st.columns(2)
#
#     with left:
#
#         st.subheader("📦 Inventory Summary")
#
#         st.markdown(
#             f"""
#     **Total SKUs**
#
#     {len(filtered)}
#
#     ---
#
#     **Total Inventory Value**
#
#     {currency(inventory_view['Inventory Value'].sum())}
#
#     ---
#
#     **Average Inventory**
#
#     {number(inventory_view['Current Inventory'].mean())}
#
#     ---
#
#     **Average Unit Cost**
#
#     {currency(inventory_view['Unit Cost'].mean())}
#     """
#         )
#
#     with right:
#
#         st.subheader("⚠ Inventory Health")
#
#         healthy = len(
#             inventory_view[
#                 inventory_view["Health"] == "🟢 Healthy"
#                 ]
#         )
#
#         low = len(
#             inventory_view[
#                 inventory_view["Health"] == "🟡 Low"
#                 ]
#         )
#
#         critical = len(
#             inventory_view[
#                 inventory_view["Health"] == "🔴 Critical"
#                 ]
#         )
#
#         st.metric(
#             "Healthy SKUs",
#             healthy,
#         )
#
#         st.metric(
#             "Low Stock",
#             low,
#         )
#
#         st.metric(
#             "Critical Stock",
#             critical,
#         )
#         # ---------------------------------------------------------
#         # ANALYTICS
#         # ---------------------------------------------------------
#
#         st.divider()
#
#         st.subheader("📊 Inventory Analytics")
#
#         chart_left, chart_right = st.columns(2)
#
#         with chart_left:
#             st.plotly_chart(
#                 inventory_value_chart(filtered),
#                 use_container_width=True,
#             )
#
#         with chart_right:
#             st.plotly_chart(
#                 category_distribution(filtered),
#                 use_container_width=True,
#             )
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # CATEGORY ANALYTICS
#         # ---------------------------------------------------------
#
#         st.subheader("📦 Category Performance")
#
#         category_summary = (
#             filtered.groupby("Category")
#             .agg(
#                 Total_SKUs=("SKU", "count"),
#                 Inventory=("Current Inventory", "sum"),
#                 Inventory_Value=("Unit Cost", "sum"),
#                 Avg_Lead_Time=("Lead Time", "mean"),
#             )
#             .reset_index()
#         )
#
#         category_summary.rename(
#             columns={
#                 "Total_SKUs": "Total SKUs",
#                 "Avg_Lead_Time": "Average Lead Time",
#                 "Inventory_Value": "Average Unit Cost",
#             },
#             inplace=True,
#         )
#
#         st.dataframe(
#             category_summary,
#             use_container_width=True,
#             hide_index=True,
#         )
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # TOP INVENTORY
#         # ---------------------------------------------------------
#
#         left, right = st.columns(2)
#
#         with left:
#             st.subheader("📈 Highest Inventory")
#
#             highest_inventory = (
#                 filtered.sort_values(
#                     by="Current Inventory",
#                     ascending=False,
#                 )
#                 .head(5)
#             )
#
#             st.dataframe(
#                 highest_inventory[
#                     [
#                         "SKU",
#                         "Description",
#                         "Current Inventory",
#                         "Warehouse",
#                     ]
#                 ],
#                 use_container_width=True,
#                 hide_index=True,
#             )
#
#         with right:
#             st.subheader("🚨 Lowest Inventory")
#
#             lowest_inventory = (
#                 filtered.sort_values(
#                     by="Current Inventory"
#                 )
#                 .head(5)
#             )
#
#             st.dataframe(
#                 lowest_inventory[
#                     [
#                         "SKU",
#                         "Description",
#                         "Current Inventory",
#                         "Warehouse",
#                     ]
#                 ],
#                 use_container_width=True,
#                 hide_index=True,
#             )
#             # ---------------------------------------------------------
#             # SKU INTELLIGENCE
#             # ---------------------------------------------------------
#
#             st.divider()
#
#             st.subheader("🔍 SKU Intelligence")
#
#             sku = st.selectbox(
#                 "Select a SKU",
#                 filtered["SKU"].tolist()
#             )
#
#             sku_df = filtered[
#                 filtered["SKU"] == sku
#                 ].iloc[0]
#
#             st.divider()
#
#             col1, col2 = st.columns([2, 1])
#
#             with col1:
#
#                 st.markdown(f"## {sku_df['Description']}")
#
#                 st.markdown(f"""
#             **SKU**
#
#             {sku_df['SKU']}
#
#             ---
#
#             **Category**
#
#             {sku_df['Category']}
#
#             ---
#
#             **Supplier**
#
#             {sku_df['Supplier']}
#
#             ---
#
#             **Warehouse**
#
#             {sku_df['Warehouse']}
#             """)
#
#             with col2:
#
#                 if sku_df["Current Inventory"] < sku_df["Reorder Point"]:
#
#                     st.error("🔴 Critical Inventory")
#
#                 elif sku_df["Current Inventory"] < sku_df["Safety Stock"]:
#
#                     st.warning("🟡 Low Inventory")
#
#                 else:
#
#                     st.success("🟢 Healthy Inventory")
#
#             st.divider()
#
#             # ---------------------------------------------------------
#             # INVENTORY PARAMETERS
#             # ---------------------------------------------------------
#
#             p1, p2, p3, p4 = st.columns(4)
#
#             with p1:
#
#                 st.metric(
#                     "Current Inventory",
#                     number(
#                         sku_df["Current Inventory"]
#                     )
#                 )
#
#             with p2:
#
#                 st.metric(
#                     "EOQ",
#                     number(
#                         sku_df["EOQ"]
#                     )
#                 )
#
#             with p3:
#
#                 st.metric(
#                     "Safety Stock",
#                     number(
#                         sku_df["Safety Stock"]
#                     )
#                 )
#
#             with p4:
#
#                 st.metric(
#                     "Reorder Point",
#                     number(
#                         sku_df["Reorder Point"]
#                     )
#                 )
#
#             st.divider()
#
#             # ---------------------------------------------------------
#             # FINANCIALS
#             # ---------------------------------------------------------
#
#             f1, f2, f3 = st.columns(3)
#
#             with f1:
#
#                 st.metric(
#                     "Unit Cost",
#                     currency(
#                         sku_df["Unit Cost"]
#                     )
#                 )
#
#             with f2:
#
#                 st.metric(
#                     "Lead Time",
#                     days(
#                         sku_df["Lead Time"]
#                     )
#                 )
#
#             with f3:
#
#                 inventory_value = (
#                         sku_df["Current Inventory"]
#                         * sku_df["Unit Cost"]
#                 )
#
#                 st.metric(
#                     "Inventory Value",
#                     currency(
#                         inventory_value
#                     )
#                 )
#                 # ---------------------------------------------------------
#                 # INVENTORY RISK ASSESSMENT
#                 # ---------------------------------------------------------
#
#                 st.divider()
#
#                 st.subheader("🧠 Inventory Intelligence")
#
#                 current = sku_df["Current Inventory"]
#                 safety = sku_df["Safety Stock"]
#                 reorder = sku_df["Reorder Point"]
#                 eoq = sku_df["EOQ"]
#                 lead_time = sku_df["Lead Time"]
#
#                 risk_score = 100
#
#                 if current < reorder:
#                     risk_score -= 40
#
#                 if current < safety:
#                     risk_score -= 20
#
#                 if lead_time > 15:
#                     risk_score -= 20
#
#                 if current > (eoq * 3):
#                     risk_score -= 15
#
#                 risk_score = max(risk_score, 0)
#
#                 c1, c2 = st.columns([1, 2])
#
#                 with c1:
#
#                     st.metric(
#                         "Inventory Health Score",
#                         f"{risk_score}/100"
#                     )
#
#                 with c2:
#
#                     if risk_score >= 85:
#
#                         st.success("🟢 Inventory health is excellent.")
#
#                     elif risk_score >= 65:
#
#                         st.warning("🟡 Inventory requires monitoring.")
#
#                     else:
#
#                         st.error("🔴 Immediate inventory action recommended.")
#
#                 st.divider()
#
#                 # ---------------------------------------------------------
#                 # AI RECOMMENDATIONS
#                 # ---------------------------------------------------------
#
#                 st.subheader("🤖 Smart Recommendations")
#
#                 recommendations = []
#
#                 if current < reorder:
#                     recommendations.append(
#                         f"🔴 Current inventory is below the reorder point. Raise a purchase order for approximately **{int(eoq)} units**."
#                     )
#
#                 if current < safety:
#                     recommendations.append(
#                         "🟡 Safety stock has been breached. Monitor incoming replenishment closely."
#                     )
#
#                 if current > (eoq * 3):
#                     recommendations.append(
#                         "📦 Overstock detected. Consider reducing future procurement quantities."
#                     )
#
#                 if lead_time > 15:
#                     recommendations.append(
#                         "🚚 Supplier lead time is high. Evaluate alternate suppliers or increase safety stock."
#                     )
#
#                 if sku_df["Unit Cost"] > 300:
#                     recommendations.append(
#                         "💰 High-value inventory. Frequent monitoring is recommended to reduce carrying cost."
#                     )
#
#                 if not recommendations:
#                     recommendations.append(
#                         "✅ Inventory policy is operating within expected thresholds."
#                     )
#
#                 for recommendation in recommendations:
#                     st.info(recommendation)
#
#                 st.divider()
#
#                 # ---------------------------------------------------------
#                 # PROCUREMENT INSIGHT
#                 # ---------------------------------------------------------
#
#                 st.subheader("📦 Procurement Insight")
#
#                 reorder_qty = max(
#                     int(eoq - current),
#                     0
#                 )
#
#                 est_order_cost = reorder_qty * sku_df["Unit Cost"]
#
#                 i1, i2 = st.columns(2)
#
#                 with i1:
#
#                     st.metric(
#                         "Recommended Order Qty",
#                         reorder_qty
#                     )
#
#                 with i2:
#
#                     st.metric(
#                         "Estimated Procurement Cost",
#                         currency(est_order_cost)
#                     )
#
#                 st.divider()
#
#                 # ---------------------------------------------------------
#                 # SUPPLIER SUMMARY
#                 # ---------------------------------------------------------
#
#                 st.subheader("🚚 Supplier Summary")
#
#                 supplier_df = filtered[
#                     filtered["Supplier"] == sku_df["Supplier"]
#                     ]
#
#                 s1, s2, s3 = st.columns(3)
#
#                 with s1:
#
#                     st.metric(
#                         "Supplier",
#                         sku_df["Supplier"]
#                     )
#
#                 with s2:
#
#                     st.metric(
#                         "Managed SKUs",
#                         len(supplier_df)
#                     )
#
#                 with s3:
#
#                     st.metric(
#                         "Average Lead Time",
#                         days(
#                             supplier_df["Lead Time"].mean()
#                         )
#                     )
#                     # ---------------------------------------------------------
#                     # ALERT CENTER
#                     # ---------------------------------------------------------
#
#                     st.divider()
#
#                     st.subheader("🚨 Alert Center")
#
#                     critical_items = filtered[
#                         filtered["Current Inventory"] < filtered["Reorder Point"]
#                         ]
#
#                     low_items = filtered[
#                         (filtered["Current Inventory"] >= filtered["Reorder Point"]) &
#                         (filtered["Current Inventory"] < filtered["Safety Stock"])
#                         ]
#
#                     if critical_items.empty and low_items.empty:
#
#                         st.success(
#                             "✅ No critical inventory alerts detected."
#                         )
#
#                     else:
#
#                         if not critical_items.empty:
#                             st.error(
#                                 f"🔴 {len(critical_items)} SKU(s) are below the Reorder Point."
#                             )
#
#                             st.dataframe(
#                                 critical_items[
#                                     [
#                                         "SKU",
#                                         "Description",
#                                         "Supplier",
#                                         "Warehouse",
#                                         "Current Inventory",
#                                         "Reorder Point",
#                                     ]
#                                 ],
#                                 hide_index=True,
#                                 use_container_width=True,
#                             )
#
#                         if not low_items.empty:
#                             st.warning(
#                                 f"🟡 {len(low_items)} SKU(s) are approaching Safety Stock."
#                             )
#
#                             st.dataframe(
#                                 low_items[
#                                     [
#                                         "SKU",
#                                         "Description",
#                                         "Supplier",
#                                         "Current Inventory",
#                                         "Safety Stock",
#                                     ]
#                                 ],
#                                 hide_index=True,
#                                 use_container_width=True,
#                             )
#
#                     st.divider()
#
#                     # ---------------------------------------------------------
#                     # EXECUTIVE INSIGHTS
#                     # ---------------------------------------------------------
#
#                     st.subheader("📈 Executive Insights")
#
#                     total_skus = len(filtered)
#
#                     healthy_percent = (
#                         (healthy / total_skus) * 100
#                         if total_skus else 0
#                     )
#
#                     avg_inventory = filtered["Current Inventory"].mean()
#
#                     highest_supplier = (
#                         filtered["Supplier"]
#                         .value_counts()
#                         .idxmax()
#                     )
#
#                     insight1, insight2 = st.columns(2)
#
#                     with insight1:
#
#                         st.info(
#                             f"""
#                     ### Inventory Overview
#
#                     • Total Active SKUs : **{total_skus}**
#
#                     • Healthy Inventory : **{healthy_percent:.1f}%**
#
#                     • Average Inventory : **{avg_inventory:.0f} Units**
#
#                     • Highest Stocking Supplier : **{highest_supplier}**
#                     """
#                         )
#
#                     with insight2:
#
#                         st.info(
#                             f"""
#                     ### Operational Summary
#
#                     • Average EOQ : **{average_eoq(filtered):.0f}**
#
#                     • Average Lead Time : **{average_lead_time(filtered):.1f} Days**
#
#                     • Critical SKUs : **{critical_skus(filtered)}**
#
#                     • Inventory Value : **{currency(total_inventory_value(filtered))}**
#                     """
#                         )
#
#                     st.divider()
#
#                     # ---------------------------------------------------------
#                     # DOWNLOAD
#                     # ---------------------------------------------------------
#
#                     st.subheader("📥 Export Inventory")
#
#                     csv = filtered.to_csv(index=False).encode("utf-8")
#
#                     st.download_button(
#                         "⬇ Download Inventory CSV",
#                         csv,
#                         file_name="inventory_report.csv",
#                         mime="text/csv",
#                     )
#
#                     st.divider()
#
#                     # ---------------------------------------------------------
#                     # FOOTER
#                     # ---------------------------------------------------------
#
#                     footer1, footer2, footer3 = st.columns(3)
#
#                     with footer1:
#
#                         st.caption(
#                             f"Records Loaded : {len(filtered)}"
#                         )
#
#                     with footer2:
#
#                         st.caption(
#                             "Source : Synthetic Semiconductor Dataset"
#                         )
#
#                     with footer3:
#
#                         st.caption(
#                             f"Last Refresh : {datetime.now().strftime('%H:%M:%S')}"
#                         )


import streamlit as st
import pandas as pd
from datetime import datetime
from src.charts import inventory_value_chart, category_distribution

from src.data_loader import load_inventory
from src.metrics import total_inventory_value, average_eoq, critical_skus, average_lead_time
from src.utils import currency, number, days
from src.charts import inventory_value_chart, category_distribution  # adjust if path differs4


def render_inventory():
    # ---------------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------------
    df = load_inventory()

    st.title("📦 Inventory Intelligence")
    st.caption("Monitor inventory health, suppliers, warehouses and replenishment policies.")
    st.divider()

    # ---------------------------------------------------------
    # KPI CARDS
    # ---------------------------------------------------------
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("Inventory Value", currency(total_inventory_value(df)), "+2.8%")

    with k2:
        st.metric("Average EOQ", number(average_eoq(df)), "Optimal")

    with k3:
        st.metric("Critical SKUs", number(critical_skus(df)), "-2")

    with k4:
        st.metric("Average Lead Time", days(average_lead_time(df)), "-0.6 Days")

    st.divider()

    # ---------------------------------------------------------
    # FILTERS
    # ---------------------------------------------------------
    left, right = st.columns([3, 2])

    with left:
        search = st.text_input("🔍 Search SKU / Description", placeholder="Example: ASIC-001")

    with right:
        category = st.selectbox("Category", ["All"] + sorted(df["Category"].dropna().unique().tolist()))

    c1, c2 = st.columns(2)

    with c1:
        supplier = st.selectbox("Supplier", ["All"] + sorted(df["Supplier"].dropna().unique().tolist()))

    with c2:
        warehouse = st.selectbox("Warehouse", ["All"] + sorted(df["Warehouse"].dropna().unique().tolist()))

    # ---------------------------------------------------------
    # APPLY FILTERS
    # ---------------------------------------------------------
    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["SKU"].astype(str).str.contains(search, case=False, na=False)
            | filtered["Description"].astype(str).str.contains(search, case=False, na=False)
        ]

    if category != "All":
        filtered = filtered[filtered["Category"] == category]

    if supplier != "All":
        filtered = filtered[filtered["Supplier"] == supplier]

    if warehouse != "All":
        filtered = filtered[filtered["Warehouse"] == warehouse]

    st.success(f"Showing {len(filtered)} of {len(df)} SKUs")

    if filtered.empty:
        st.warning("No SKUs match the selected filters. Please adjust your filter criteria.")
        return

    # ---------------------------------------------------------
    # INVENTORY SNAPSHOT
    # ---------------------------------------------------------
    st.divider()
    st.subheader("📋 Inventory Snapshot")

    inventory_view = filtered.copy()

    inventory_view["Health"] = inventory_view.apply(
        lambda row: (
            "🔴 Critical"
            if row["Current Inventory"] < row["Reorder Point"]
            else "🟡 Low"
            if row["Current Inventory"] < row["Safety Stock"] * 1.2
            else "🟢 Healthy"
        ),
        axis=1,
    )

    inventory_view["Inventory Value"] = (
        inventory_view["Current Inventory"] * inventory_view["Unit Cost"]
    )

    display_columns = [
        "SKU",
        "Description",
        "Category",
        "Supplier",
        "Warehouse",
        "Current Inventory",
        "Safety Stock",
        "Reorder Point",
        "EOQ",
        "Lead Time",
        "Health",
    ]

    st.dataframe(
        inventory_view[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ---------------------------------------------------------
    # INVENTORY SUMMARY
    # ---------------------------------------------------------
    left, right = st.columns(2)

    with left:
        st.subheader("📦 Inventory Summary")
        st.markdown(
            f"""
**Total SKUs**

{len(filtered)}

---

**Total Inventory Value**

{currency(inventory_view["Inventory Value"].sum())}

---

**Average Inventory**

{number(inventory_view["Current Inventory"].mean())}

---

**Average Unit Cost**

{currency(inventory_view["Unit Cost"].mean())}
"""
        )

    with right:
        st.subheader("⚠ Inventory Health")

        healthy = len(inventory_view[inventory_view["Health"] == "🟢 Healthy"])
        low = len(inventory_view[inventory_view["Health"] == "🟡 Low"])
        critical = len(inventory_view[inventory_view["Health"] == "🔴 Critical"])

        st.metric("Healthy SKUs", healthy)
        st.metric("Low Stock", low)
        st.metric("Critical Stock", critical)

    st.divider()

    # ---------------------------------------------------------
    # ANALYTICS
    # ---------------------------------------------------------
    st.subheader("📊 Inventory Analytics")

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.plotly_chart(
            inventory_value_chart(filtered),
            use_container_width=True,
        )

    with chart_right:
        st.plotly_chart(
            category_distribution(filtered),
            use_container_width=True,
        )

    st.divider()

    # ---------------------------------------------------------
    # CATEGORY ANALYTICS
    # ---------------------------------------------------------
    st.subheader("📦 Category Performance")

    category_summary = (
        inventory_view.groupby("Category", dropna=False)
        .agg(
            Total_SKUs=("SKU", "count"),
            Inventory=("Current Inventory", "sum"),
            Inventory_Value=("Inventory Value", "sum"),
            Avg_Lead_Time=("Lead Time", "mean"),
            Avg_Unit_Cost=("Unit Cost", "mean"),
        )
        .reset_index()
    )

    category_summary.rename(
        columns={
            "Total_SKUs": "Total SKUs",
            "Inventory_Value": "Inventory Value",
            "Avg_Lead_Time": "Average Lead Time",
            "Avg_Unit_Cost": "Average Unit Cost",
        },
        inplace=True,
    )

    st.dataframe(
        category_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ---------------------------------------------------------
    # TOP / LOWEST INVENTORY
    # ---------------------------------------------------------
    left, right = st.columns(2)

    with left:
        st.subheader("📈 Highest Inventory")
        highest_inventory = filtered.sort_values(by="Current Inventory", ascending=False).head(5)

        st.dataframe(
            highest_inventory[["SKU", "Description", "Current Inventory", "Warehouse"]],
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.subheader("🚨 Lowest Inventory")
        lowest_inventory = filtered.sort_values(by="Current Inventory", ascending=True).head(5)

        st.dataframe(
            lowest_inventory[["SKU", "Description", "Current Inventory", "Warehouse"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ---------------------------------------------------------
    # SKU INTELLIGENCE
    # ---------------------------------------------------------
    st.subheader("🔍 SKU Intelligence")

    sku_list = filtered["SKU"].dropna().tolist()
    if not sku_list:
        st.warning("No SKUs available for intelligence view.")
        return

    sku = st.selectbox("Select a SKU", sku_list)
    sku_df = filtered[filtered["SKU"] == sku].iloc[0]

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"## {sku_df['Description']}")
        st.markdown(
            f"""
**SKU**

{sku_df['SKU']}

---

**Category**

{sku_df['Category']}

---

**Supplier**

{sku_df['Supplier']}

---

**Warehouse**

{sku_df['Warehouse']}
"""
        )

    with col2:
        if sku_df["Current Inventory"] < sku_df["Reorder Point"]:
            st.error("🔴 Critical Inventory")
        elif sku_df["Current Inventory"] < sku_df["Safety Stock"]:
            st.warning("🟡 Low Inventory")
        else:
            st.success("🟢 Healthy Inventory")

    st.divider()

    # ---------------------------------------------------------
    # INVENTORY PARAMETERS
    # ---------------------------------------------------------
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric("Current Inventory", number(sku_df["Current Inventory"]))

    with p2:
        st.metric("EOQ", number(sku_df["EOQ"]))

    with p3:
        st.metric("Safety Stock", number(sku_df["Safety Stock"]))

    with p4:
        st.metric("Reorder Point", number(sku_df["Reorder Point"]))

    st.divider()

    # ---------------------------------------------------------
    # FINANCIALS
    # ---------------------------------------------------------
    f1, f2, f3 = st.columns(3)

    with f1:
        st.metric("Unit Cost", currency(sku_df["Unit Cost"]))

    with f2:
        st.metric("Lead Time", days(sku_df["Lead Time"]))

    with f3:
        inventory_value = sku_df["Current Inventory"] * sku_df["Unit Cost"]
        st.metric("Inventory Value", currency(inventory_value))

    st.divider()

    # ---------------------------------------------------------
    # INVENTORY RISK ASSESSMENT
    # ---------------------------------------------------------
    st.subheader("🧠 Inventory Intelligence")

    current = sku_df["Current Inventory"]
    safety = sku_df["Safety Stock"]
    reorder = sku_df["Reorder Point"]
    eoq = sku_df["EOQ"]
    lead_time = sku_df["Lead Time"]

    risk_score = 100

    if current < reorder:
        risk_score -= 40
    if current < safety:
        risk_score -= 20
    if lead_time > 15:
        risk_score -= 20
    if current > (eoq * 3):
        risk_score -= 15

    risk_score = max(risk_score, 0)

    c1, c2 = st.columns([1, 2])

    with c1:
        st.metric("Inventory Health Score", f"{risk_score}/100")

    with c2:
        if risk_score >= 85:
            st.success("🟢 Inventory health is excellent.")
        elif risk_score >= 65:
            st.warning("🟡 Inventory requires monitoring.")
        else:
            st.error("🔴 Immediate inventory action recommended.")

    st.divider()

    # ---------------------------------------------------------
    # AI RECOMMENDATIONS
    # ---------------------------------------------------------
    st.subheader("🤖 Smart Recommendations")

    recommendations = []

    if current < reorder:
        recommendations.append(
            f"🔴 Current inventory is below the reorder point. Raise a purchase order for approximately **{int(eoq)} units**."
        )

    if current < safety:
        recommendations.append(
            "🟡 Safety stock has been breached. Monitor incoming replenishment closely."
        )

    if current > (eoq * 3):
        recommendations.append(
            "📦 Overstock detected. Consider reducing future procurement quantities."
        )

    if lead_time > 15:
        recommendations.append(
            "🚚 Supplier lead time is high. Evaluate alternate suppliers or increase safety stock."
        )

    if sku_df["Unit Cost"] > 300:
        recommendations.append(
            "💰 High-value inventory. Frequent monitoring is recommended to reduce carrying cost."
        )

    if not recommendations:
        recommendations.append("✅ Inventory policy is operating within expected thresholds.")

    for recommendation in recommendations:
        st.info(recommendation)

    st.divider()

    # ---------------------------------------------------------
    # PROCUREMENT INSIGHT
    # ---------------------------------------------------------
    st.subheader("📦 Procurement Insight")

    reorder_qty = max(int(eoq - current), 0)
    est_order_cost = reorder_qty * sku_df["Unit Cost"]

    i1, i2 = st.columns(2)

    with i1:
        st.metric("Recommended Order Qty", reorder_qty)

    with i2:
        st.metric("Estimated Procurement Cost", currency(est_order_cost))

    st.divider()

    # ---------------------------------------------------------
    # SUPPLIER SUMMARY
    # ---------------------------------------------------------
    st.subheader("🚚 Supplier Summary")

    supplier_df = filtered[filtered["Supplier"] == sku_df["Supplier"]]
    s1, s2, s3 = st.columns(3)

    with s1:
        st.metric("Supplier", sku_df["Supplier"])

    with s2:
        st.metric("Managed SKUs", len(supplier_df))

    with s3:
        st.metric("Average Lead Time", days(supplier_df["Lead Time"].mean()))

    st.divider()

    # ---------------------------------------------------------
    # ALERT CENTER
    # ---------------------------------------------------------
    st.subheader("🚨 Alert Center")

    critical_items = filtered[filtered["Current Inventory"] < filtered["Reorder Point"]]
    low_items = filtered[
        (filtered["Current Inventory"] >= filtered["Reorder Point"])
        & (filtered["Current Inventory"] < filtered["Safety Stock"])
    ]

    if critical_items.empty and low_items.empty:
        st.success("✅ No critical inventory alerts detected.")
    else:
        if not critical_items.empty:
            st.error(f"🔴 {len(critical_items)} SKU(s) are below the Reorder Point.")
            st.dataframe(
                critical_items[
                    ["SKU", "Description", "Supplier", "Warehouse", "Current Inventory", "Reorder Point"]
                ],
                hide_index=True,
                use_container_width=True,
            )

        if not low_items.empty:
            st.warning(f"🟡 {len(low_items)} SKU(s) are approaching Safety Stock.")
            st.dataframe(
                low_items[
                    ["SKU", "Description", "Supplier", "Current Inventory", "Safety Stock"]
                ],
                hide_index=True,
                use_container_width=True,
            )

    st.divider()

    # ---------------------------------------------------------
    # EXECUTIVE INSIGHTS
    # ---------------------------------------------------------
    st.subheader("📈 Executive Insights")

    total_skus = len(filtered)
    healthy_percent = (healthy / total_skus) * 100 if total_skus else 0
    avg_inventory = filtered["Current Inventory"].mean() if total_skus else 0
    highest_supplier = (
        filtered["Supplier"].value_counts().idxmax()
        if total_skus and filtered["Supplier"].notna().any()
        else "N/A"
    )

    insight1, insight2 = st.columns(2)

    with insight1:
        st.info(
            f"""
### Inventory Overview

• Total Active SKUs : **{total_skus}**

• Healthy Inventory : **{healthy_percent:.1f}%**

• Average Inventory : **{avg_inventory:.0f} Units**

• Highest Stocking Supplier : **{highest_supplier}**
"""
        )

    with insight2:
        st.info(
            f"""
### Operational Summary

• Average EOQ : **{average_eoq(filtered):.0f}**

• Average Lead Time : **{average_lead_time(filtered):.1f} Days**

• Critical SKUs : **{critical_skus(filtered)}**

• Inventory Value : **{currency(total_inventory_value(filtered))}**
"""
        )

    st.divider()

    # ---------------------------------------------------------
    # DOWNLOAD
    # ---------------------------------------------------------
    st.subheader("📥 Export Inventory")

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Inventory CSV",
        csv,
        file_name="inventory_report.csv",
        mime="text/csv",
    )

    st.divider()

    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------
    footer1, footer2, footer3 = st.columns(3)

    with footer1:
        st.caption(f"Records Loaded : {len(filtered)}")

    with footer2:
        st.caption("Source : Synthetic Semiconductor Dataset")

    with footer3:
        st.caption(f"Last Refresh : {datetime.now().strftime('%H:%M:%S')}")