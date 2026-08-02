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




# import streamlit as st
# import pandas as pd
# from datetime import datetime
#
# from src.data_loader import load_inventory
# from src.metrics import (
#     total_inventory_value,
#     average_eoq,
#     critical_skus,
#     average_lead_time,
# )
# from src.utils import currency, number, days
# from src.charts import inventory_value_chart, category_distribution
#
#
# REQUIRED_COLUMNS = [
#     "SKU",
#     "Description",
#     "Category",
#     "Supplier",
#     "Warehouse",
#     "Current Inventory",
#     "Safety Stock",
#     "Reorder Point",
#     "EOQ",
#     "Lead Time",
#     "Unit Cost",
# ]
#
#
# def _validate_df(df: pd.DataFrame):
#     if df is None:
#         return False, ["DataFrame is None"]
#     missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
#     return len(missing) == 0, missing
#
#
# def _health_label(row):
#     if row["Current Inventory"] < row["Reorder Point"]:
#         return "Critical"
#     elif row["Current Inventory"] < row["Safety Stock"]:
#         return "Low"
#     return "Healthy"
#
#
# def _abc_analysis(df: pd.DataFrame) -> pd.DataFrame:
#     x = df.copy()
#     x = x.sort_values("Inventory Value", ascending=False).reset_index(drop=True)
#     total = x["Inventory Value"].sum()
#     if total == 0:
#         x["ABC Class"] = "C"
#         return x
#     x["Cum %"] = (x["Inventory Value"].cumsum() / total) * 100
#     x["ABC Class"] = x["Cum %"].apply(lambda v: "A" if v <= 80 else ("B" if v <= 95 else "C"))
#     return x
#
#
# def render_inventory():
#     try:
#         # ---------------------------------------------------------
#         # LOAD + VALIDATE
#         # ---------------------------------------------------------
#         df = load_inventory()
#
#         ok, missing = _validate_df(df)
#         st.title("📦 Inventory Intelligence")
#         st.caption("Monitor inventory health, suppliers, warehouses and replenishment policies.")
#
#         if not ok:
#             st.error(f"Missing required columns: {missing}")
#             if isinstance(df, pd.DataFrame):
#                 st.write("Available columns:", df.columns.tolist())
#             return
#
#         if df.empty:
#             st.warning("Inventory dataset is empty.")
#             return
#
#         # numeric cleaning
#         num_cols = ["Current Inventory", "Safety Stock", "Reorder Point", "EOQ", "Lead Time", "Unit Cost"]
#         for c in num_cols:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#
#         df = df.dropna(subset=["SKU", "Description", "Category", "Supplier", "Warehouse"] + num_cols)
#         if df.empty:
#             st.warning("No usable rows after data cleanup.")
#             return
#
#         df["Inventory Value"] = df["Current Inventory"] * df["Unit Cost"]
#         df["Health"] = df.apply(_health_label, axis=1)
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # KPI CARDS
#         # ---------------------------------------------------------
#         k1, k2, k3, k4 = st.columns(4)
#         with k1:
#             st.metric("Inventory Value", currency(total_inventory_value(df)), "+2.8%")
#         with k2:
#             st.metric("Average EOQ", number(average_eoq(df)), "Optimal")
#         with k3:
#             st.metric("Critical SKUs", number(critical_skus(df)), "-2")
#         with k4:
#             st.metric("Average Lead Time", days(average_lead_time(df)), "-0.6 Days")
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # FILTERS
#         # ---------------------------------------------------------
#         f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
#
#         with f1:
#             search = st.text_input("🔍 Search SKU / Description", placeholder="Example: ASIC-001")
#         with f2:
#             category = st.selectbox("Category", ["All"] + sorted(df["Category"].dropna().astype(str).unique().tolist()))
#         with f3:
#             supplier = st.selectbox("Supplier", ["All"] + sorted(df["Supplier"].dropna().astype(str).unique().tolist()))
#         with f4:
#             warehouse = st.selectbox("Warehouse", ["All"] + sorted(df["Warehouse"].dropna().astype(str).unique().tolist()))
#
#         filtered = df.copy()
#
#         if search:
#             filtered = filtered[
#                 filtered["SKU"].astype(str).str.contains(search, case=False, na=False)
#                 | filtered["Description"].astype(str).str.contains(search, case=False, na=False)
#             ]
#         if category != "All":
#             filtered = filtered[filtered["Category"] == category]
#         if supplier != "All":
#             filtered = filtered[filtered["Supplier"] == supplier]
#         if warehouse != "All":
#             filtered = filtered[filtered["Warehouse"] == warehouse]
#
#         st.success(f"Showing {len(filtered)} of {len(df)} SKUs")
#         if filtered.empty:
#             st.warning("No SKUs match your selected filters.")
#             return
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # SNAPSHOT
#         # ---------------------------------------------------------
#         st.subheader("📋 Inventory Snapshot")
#         snapshot = filtered.copy()
#         snapshot["Health"] = snapshot["Health"].map(
#             {"Critical": "🔴 Critical", "Low": "🟡 Low", "Healthy": "🟢 Healthy"}
#         )
#
#         st.dataframe(
#             snapshot[
#                 [
#                     "SKU", "Description", "Category", "Supplier", "Warehouse",
#                     "Current Inventory", "Safety Stock", "Reorder Point",
#                     "EOQ", "Lead Time", "Health"
#                 ]
#             ],
#             use_container_width=True,
#             hide_index=True,
#         )
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # SUMMARY + HEALTH
#         # ---------------------------------------------------------
#         left, right = st.columns(2)
#
#         healthy = (filtered["Health"] == "Healthy").sum()
#         low = (filtered["Health"] == "Low").sum()
#         critical = (filtered["Health"] == "Critical").sum()
#
#         with left:
#             st.subheader("📦 Inventory Summary")
#             st.markdown(
#                 f"""
# **Total SKUs**
# {len(filtered)}
#
# **Total Inventory Value**
# {currency(filtered["Inventory Value"].sum())}
#
# **Average Inventory**
# {number(filtered["Current Inventory"].mean())}
#
# **Average Unit Cost**
# {currency(filtered["Unit Cost"].mean())}
# """
#             )
#
#         with right:
#             st.subheader("⚠ Inventory Health")
#             st.metric("Healthy SKUs", int(healthy))
#             st.metric("Low Stock", int(low))
#             st.metric("Critical Stock", int(critical))
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # ANALYTICS (GRAPHS)
#         # ---------------------------------------------------------
#         st.subheader("📊 Inventory Analytics")
#         c_left, c_right = st.columns(2)
#
#         with c_left:
#             try:
#                 st.plotly_chart(inventory_value_chart(filtered), use_container_width=True)
#             except Exception as e:
#                 st.error(f"Inventory value chart failed: {e}")
#
#         with c_right:
#             try:
#                 st.plotly_chart(category_distribution(filtered), use_container_width=True)
#             except Exception as e:
#                 st.error(f"Category distribution chart failed: {e}")
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # ABC ANALYSIS (NEW)
#         # ---------------------------------------------------------
#         st.subheader("🧠 ABC Classification (by Inventory Value)")
#         abc_df = _abc_analysis(filtered[["SKU", "Description", "Category", "Supplier", "Inventory Value"]].copy())
#
#         a_count = (abc_df["ABC Class"] == "A").sum()
#         b_count = (abc_df["ABC Class"] == "B").sum()
#         c_count = (abc_df["ABC Class"] == "C").sum()
#
#         a1, a2, a3 = st.columns(3)
#         a1.metric("A-Class SKUs", int(a_count))
#         a2.metric("B-Class SKUs", int(b_count))
#         a3.metric("C-Class SKUs", int(c_count))
#
#         st.dataframe(
#             abc_df[["SKU", "Description", "Category", "Supplier", "Inventory Value", "Cum %", "ABC Class"]].head(20),
#             use_container_width=True,
#             hide_index=True,
#         )
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # TOP/BOTTOM
#         # ---------------------------------------------------------
#         l1, l2 = st.columns(2)
#
#         with l1:
#             st.subheader("📈 Highest Inventory")
#             hi = filtered.sort_values("Current Inventory", ascending=False).head(5)
#             st.dataframe(
#                 hi[["SKU", "Description", "Current Inventory", "Warehouse"]],
#                 use_container_width=True,
#                 hide_index=True,
#             )
#
#         with l2:
#             st.subheader("🚨 Lowest Inventory")
#             lo = filtered.sort_values("Current Inventory", ascending=True).head(5)
#             st.dataframe(
#                 lo[["SKU", "Description", "Current Inventory", "Warehouse"]],
#                 use_container_width=True,
#                 hide_index=True,
#             )
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # SKU INTELLIGENCE
#         # ---------------------------------------------------------
#         st.subheader("🔍 SKU Intelligence")
#         sku = st.selectbox("Select a SKU", filtered["SKU"].astype(str).tolist())
#         sku_df = filtered[filtered["SKU"].astype(str) == sku].iloc[0]
#
#         col1, col2 = st.columns([2, 1])
#         with col1:
#             st.markdown(f"### {sku_df['Description']}")
#             st.write(f"**SKU:** {sku_df['SKU']}")
#             st.write(f"**Category:** {sku_df['Category']}")
#             st.write(f"**Supplier:** {sku_df['Supplier']}")
#             st.write(f"**Warehouse:** {sku_df['Warehouse']}")
#
#         with col2:
#             if sku_df["Health"] == "Critical":
#                 st.error("🔴 Critical Inventory")
#             elif sku_df["Health"] == "Low":
#                 st.warning("🟡 Low Inventory")
#             else:
#                 st.success("🟢 Healthy Inventory")
#
#         p1, p2, p3, p4 = st.columns(4)
#         p1.metric("Current Inventory", number(sku_df["Current Inventory"]))
#         p2.metric("EOQ", number(sku_df["EOQ"]))
#         p3.metric("Safety Stock", number(sku_df["Safety Stock"]))
#         p4.metric("Reorder Point", number(sku_df["Reorder Point"]))
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # ALERT CENTER
#         # ---------------------------------------------------------
#         st.subheader("🚨 Alert Center")
#         critical_items = filtered[filtered["Current Inventory"] < filtered["Reorder Point"]]
#         low_items = filtered[
#             (filtered["Current Inventory"] >= filtered["Reorder Point"])
#             & (filtered["Current Inventory"] < filtered["Safety Stock"])
#         ]
#
#         if critical_items.empty and low_items.empty:
#             st.success("✅ No critical inventory alerts detected.")
#         else:
#             if not critical_items.empty:
#                 st.error(f"🔴 {len(critical_items)} SKU(s) are below the Reorder Point.")
#                 st.dataframe(
#                     critical_items[
#                         ["SKU", "Description", "Supplier", "Warehouse", "Current Inventory", "Reorder Point"]
#                     ],
#                     hide_index=True,
#                     use_container_width=True,
#                 )
#
#             if not low_items.empty:
#                 st.warning(f"🟡 {len(low_items)} SKU(s) are approaching Safety Stock.")
#                 st.dataframe(
#                     low_items[
#                         ["SKU", "Description", "Supplier", "Current Inventory", "Safety Stock"]
#                     ],
#                     hide_index=True,
#                     use_container_width=True,
#                 )
#
#         st.divider()
#
#         # ---------------------------------------------------------
#         # EXECUTIVE INSIGHTS + EXPORT
#         # ---------------------------------------------------------
#         st.subheader("📈 Executive Insights")
#         total_skus = len(filtered)
#         healthy_percent = (healthy / total_skus) * 100 if total_skus else 0
#         avg_inventory = filtered["Current Inventory"].mean() if total_skus else 0
#         highest_supplier = (
#             filtered["Supplier"].value_counts().idxmax()
#             if total_skus and filtered["Supplier"].notna().any()
#             else "N/A"
#         )
#
#         i1, i2 = st.columns(2)
#         with i1:
#             st.info(
#                 f"""
# ### Inventory Overview
# • Total Active SKUs: **{total_skus}**
# • Healthy Inventory: **{healthy_percent:.1f}%**
# • Average Inventory: **{avg_inventory:.0f} Units**
# • Highest Stocking Supplier: **{highest_supplier}**
# """
#             )
#
#         with i2:
#             st.info(
#                 f"""
# ### Operational Summary
# • Average EOQ: **{average_eoq(filtered):.0f}**
# • Average Lead Time: **{average_lead_time(filtered):.1f} Days**
# • Critical SKUs: **{critical_skus(filtered)}**
# • Inventory Value: **{currency(total_inventory_value(filtered))}**
# """
#             )
#
#         st.divider()
#
#         st.subheader("📥 Export Inventory")
#         csv = filtered.to_csv(index=False).encode("utf-8")
#         st.download_button(
#             "⬇ Download Inventory CSV",
#             csv,
#             file_name="inventory_report.csv",
#             mime="text/csv",
#         )
#
#         st.divider()
#         f1, f2, f3 = st.columns(3)
#         f1.caption(f"Records Loaded: {len(filtered)}")
#         f2.caption("Source: Synthetic Semiconductor Dataset")
#         f3.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')}")
#
#     except Exception as e:
#         st.exception(e)

# import streamlit as st
# import pandas as pd
# from datetime import datetime
#
# from src.data_loader import load_inventory
# from src.metrics import (
#     total_inventory_value,
#     average_eoq,
#     critical_skus,
#     average_lead_time,
# )
# from src.utils import currency, number, days
# from src.charts import inventory_value_chart, category_distribution
#
#
# REQUIRED_COLUMNS = [
#     "SKU",
#     "Description",
#     "Category",
#     "Supplier",
#     "Warehouse",
#     "Current Inventory",
#     "Safety Stock",
#     "Reorder Point",
#     "EOQ",
#     "Lead Time",
#     "Unit Cost",
# ]
#
#
# def _health_label(row):
#     if row["Current Inventory"] < row["Reorder Point"]:
#         return "Critical"
#     elif row["Current Inventory"] < row["Safety Stock"]:
#         return "Low"
#     return "Healthy"
#
#
# def render_inventory():
#     try:
#         # ---------------------------------------------------------
#         # LOAD + VALIDATE
#         # ---------------------------------------------------------
#         df = load_inventory()
#
#         st.title("📦 Inventory Intelligence")
#         st.caption("Monitor inventory health, suppliers, warehouses and replenishment policies.")
#
#         if df is None or df.empty:
#             st.warning("Inventory dataset is empty.")
#             return
#
#         missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
#         if missing:
#             st.error(f"Missing required columns: {missing}")
#             st.write("Available columns:", df.columns.tolist())
#             return
#
#         # Numeric cleanup
#         num_cols = ["Current Inventory", "Safety Stock", "Reorder Point", "EOQ", "Lead Time", "Unit Cost"]
#         for c in num_cols:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#
#         df = df.dropna(subset=["SKU", "Description", "Category", "Supplier", "Warehouse"] + num_cols)
#         if df.empty:
#             st.warning("No usable rows after data cleanup.")
#             return
#
#         df["Inventory Value"] = df["Current Inventory"] * df["Unit Cost"]
#         df["Health"] = df.apply(_health_label, axis=1)
#
#         st.divider()
#
#         # =========================================================
#         # 1) FILTERS + SKU INTELLIGENCE
#         # =========================================================
#         st.subheader("🔎 Filters")
#
#         f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
#         with f1:
#             search = st.text_input("Search SKU / Description", placeholder="Example: ASIC-001")
#         with f2:
#             category = st.selectbox("Category", ["All"] + sorted(df["Category"].astype(str).unique().tolist()))
#         with f3:
#             supplier = st.selectbox("Supplier", ["All"] + sorted(df["Supplier"].astype(str).unique().tolist()))
#         with f4:
#             warehouse = st.selectbox("Warehouse", ["All"] + sorted(df["Warehouse"].astype(str).unique().tolist()))
#
#         filtered = df.copy()
#
#         if search:
#             filtered = filtered[
#                 filtered["SKU"].astype(str).str.contains(search, case=False, na=False)
#                 | filtered["Description"].astype(str).str.contains(search, case=False, na=False)
#             ]
#         if category != "All":
#             filtered = filtered[filtered["Category"] == category]
#         if supplier != "All":
#             filtered = filtered[filtered["Supplier"] == supplier]
#         if warehouse != "All":
#             filtered = filtered[filtered["Warehouse"] == warehouse]
#
#         st.success(f"Showing {len(filtered)} of {len(df)} SKUs")
#
#         if filtered.empty:
#             st.warning("No SKUs match selected filters.")
#             return
#
#         st.divider()
#         st.subheader("🔍 SKU Intelligence")
#
#         sku = st.selectbox("Select a SKU", filtered["SKU"].astype(str).tolist())
#         sku_df = filtered[filtered["SKU"].astype(str) == sku].iloc[0]
#
#         c1, c2 = st.columns([2, 1])
#         with c1:
#             st.markdown(f"### {sku_df['Description']}")
#             st.write(f"**SKU:** {sku_df['SKU']}")
#             st.write(f"**Category:** {sku_df['Category']}")
#             st.write(f"**Supplier:** {sku_df['Supplier']}")
#             st.write(f"**Warehouse:** {sku_df['Warehouse']}")
#
#         with c2:
#             if sku_df["Health"] == "Critical":
#                 st.error("🔴 Critical Inventory")
#             elif sku_df["Health"] == "Low":
#                 st.warning("🟡 Low Inventory")
#             else:
#                 st.success("🟢 Healthy Inventory")
#
#         p1, p2, p3, p4 = st.columns(4)
#         p1.metric("Current Inventory", number(sku_df["Current Inventory"]))
#         p2.metric("EOQ", number(sku_df["EOQ"]))
#         p3.metric("Safety Stock", number(sku_df["Safety Stock"]))
#         p4.metric("Reorder Point", number(sku_df["Reorder Point"]))
#
#         st.divider()
#
#         # =========================================================
#         # 2) INVENTORY SUMMARY + INVENTORY HEALTH
#         # =========================================================
#         left, right = st.columns(2)
#
#         healthy = int((filtered["Health"] == "Healthy").sum())
#         low = int((filtered["Health"] == "Low").sum())
#         critical = int((filtered["Health"] == "Critical").sum())
#
#         with left:
#             st.subheader("📦 Inventory Summary")
#             st.markdown(
#                 f"""
# **Total SKUs**
# {len(filtered)}
#
# **Total Inventory Value**
# {currency(filtered["Inventory Value"].sum())}
#
# **Average Inventory**
# {number(filtered["Current Inventory"].mean())}
#
# **Average Unit Cost**
# {currency(filtered["Unit Cost"].mean())}
# """
#             )
#
#         with right:
#             st.subheader("⚠ Inventory Health")
#             st.metric("Healthy SKUs", healthy)
#             st.metric("Low Stock", low)
#             st.metric("Critical Stock", critical)
#
#         st.divider()
#
#         # =========================================================
#         # 3) INVENTORY ANALYTICS + HIGHEST/LOWEST INVENTORY
#         # =========================================================
#         st.subheader("📊 Inventory Analytics")
#         a1, a2 = st.columns(2)
#
#         with a1:
#             try:
#                 st.plotly_chart(inventory_value_chart(filtered), use_container_width=True)
#             except Exception as e:
#                 st.error(f"Inventory value chart error: {e}")
#
#         with a2:
#             try:
#                 st.plotly_chart(category_distribution(filtered), use_container_width=True)
#             except Exception as e:
#                 st.error(f"Category chart error: {e}")
#
#         st.divider()
#
#         t1, t2 = st.columns(2)
#
#         with t1:
#             st.subheader("📈 Highest Inventory")
#             high = filtered.sort_values("Current Inventory", ascending=False).head(5)
#             st.dataframe(
#                 high[["SKU", "Description", "Current Inventory", "Warehouse"]],
#                 use_container_width=True,
#                 hide_index=True,
#             )
#
#         with t2:
#             st.subheader("🚨 Lowest Inventory")
#             low_df = filtered.sort_values("Current Inventory", ascending=True).head(5)
#             st.dataframe(
#                 low_df[["SKU", "Description", "Current Inventory", "Warehouse"]],
#                 use_container_width=True,
#                 hide_index=True,
#             )
#
#         st.divider()
#
#         # =========================================================
#         # 4) INVENTORY SNAPSHOT (LAST)
#         # =========================================================
#         st.subheader("📋 Inventory Snapshot")
#
#         snapshot = filtered.copy()
#         snapshot["Health"] = snapshot["Health"].map(
#             {"Critical": "🔴 Critical", "Low": "🟡 Low", "Healthy": "🟢 Healthy"}
#         )
#
#         st.dataframe(
#             snapshot[
#                 [
#                     "SKU", "Description", "Category", "Supplier", "Warehouse",
#                     "Current Inventory", "Safety Stock", "Reorder Point",
#                     "EOQ", "Lead Time", "Health"
#                 ]
#             ],
#             use_container_width=True,
#             hide_index=True,
#         )
#
#         st.divider()
#
#         f1, f2, f3 = st.columns(3)
#         f1.caption(f"Records Loaded: {len(filtered)}")
#         f2.caption("Source: Synthetic Semiconductor Dataset")
#         f3.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')}")
#
#     except Exception as e:
#         st.exception(e)


import streamlit as st
import pandas as pd
from datetime import datetime

from src.data_loader import load_inventory
from src.metrics import (
    total_inventory_value,
    average_eoq,
    critical_skus,
    average_lead_time,
)
from src.utils import currency, number, days
from src.charts import inventory_value_chart, category_distribution


REQUIRED_COLUMNS = [
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
    "Unit Cost",
]


def _health_label(row):
    if row["Current Inventory"] < row["Reorder Point"]:
        return "Critical"
    elif row["Current Inventory"] < row["Safety Stock"]:
        return "Low"
    return "Healthy"

def render_sku_intelligence_cards(sku_df):
    # status color
    if sku_df["Current Inventory"] < sku_df["Reorder Point"]:
        status_text = "🔴 Critical Inventory"
        status_bg = "#fee2e2"
        status_color = "#b91c1c"
    elif sku_df["Current Inventory"] < sku_df["Safety Stock"]:
        status_text = "🟡 Low Inventory"
        status_bg = "#fef3c7"
        status_color = "#92400e"
    else:
        status_text = "🟢 Healthy Inventory"
        status_bg = "#dcfce7"
        status_color = "#166534"

    st.markdown(
        """
        <style>
        .sku-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            height: 100%;
        }
        .sku-title {
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 6px;
        }
        .sku-value {
            font-size: 34px;
            font-weight: 700;
            color: #111827;
            line-height: 1.1;
        }
        .sku-meta {
            font-size: 16px;
            color: #111827;
            margin-bottom: 8px;
        }
        .sku-pill {
            border-radius: 12px;
            padding: 12px 14px;
            font-weight: 600;
            font-size: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Top row: description + status
    top1, top2 = st.columns([2.2, 1.2])
    with top1:
        st.markdown(f"### {sku_df['Description']}")
        st.markdown(f"<div class='sku-meta'><b>SKU:</b> {sku_df['SKU']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sku-meta'><b>Category:</b> {sku_df['Category']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sku-meta'><b>Supplier:</b> {sku_df['Supplier']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sku-meta'><b>Warehouse:</b> {sku_df['Warehouse']}</div>", unsafe_allow_html=True)

    with top2:
        st.markdown(
            f"<div class='sku-pill' style='background:{status_bg}; color:{status_color};'>{status_text}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # KPI cards row
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="sku-card">
                <div class="sku-title">Current Inventory</div>
                <div class="sku-value">{int(sku_df["Current Inventory"]):,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="sku-card">
                <div class="sku-title">EOQ</div>
                <div class="sku-value">{int(sku_df["EOQ"]):,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="sku-card">
                <div class="sku-title">Safety Stock</div>
                <div class="sku-value">{int(sku_df["Safety Stock"]):,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="sku-card">
                <div class="sku-title">Reorder Point</div>
                <div class="sku-value">{int(sku_df["Reorder Point"]):,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_inventory():
    try:
        # ---------------------------------------------------------
        # LOAD + VALIDATE
        # ---------------------------------------------------------
        df = load_inventory()

        st.title("📦 Inventory Intelligence")
        st.caption("Monitor inventory health, suppliers, warehouses and replenishment policies.")

        if df is None or df.empty:
            st.warning("Inventory dataset is empty.")
            return

        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
            st.write("Available columns:", df.columns.tolist())
            return

        # Numeric cleanup
        num_cols = ["Current Inventory", "Safety Stock", "Reorder Point", "EOQ", "Lead Time", "Unit Cost"]
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna(subset=["SKU", "Description", "Category", "Supplier", "Warehouse"] + num_cols)
        if df.empty:
            st.warning("No usable rows after data cleanup.")
            return

        df["Inventory Value"] = df["Current Inventory"] * df["Unit Cost"]
        df["Health"] = df.apply(_health_label, axis=1)

        st.divider()

        # # =========================================================
        # # 1) SKU INTELLIGENCE FIRST (POWER BI CARD STYLE)
        # # =========================================================
        # st.subheader("🔎 SKU Intelligence")
        #
        # sku = st.selectbox("Select a SKU", sorted(df["SKU"].astype(str).unique().tolist()))
        # sku_df = df[df["SKU"].astype(str) == sku].iloc[0]
        #
        # # Status config
        # if sku_df["Current Inventory"] < sku_df["Reorder Point"]:
        #     status_text = "🔴 Critical Inventory"
        #     status_bg = "#fee2e2"
        #     status_color = "#b91c1c"
        # elif sku_df["Current Inventory"] < sku_df["Safety Stock"]:
        #     status_text = "🟡 Low Inventory"
        #     status_bg = "#fef3c7"
        #     status_color = "#92400e"
        # else:
        #     status_text = "🟢 Healthy Inventory"
        #     status_bg = "#dcfce7"
        #     status_color = "#166534"
        #
        # # Shared CSS
        # st.markdown(
        #     """
        #     <style>
        #     .pbi-card {
        #         background: #ffffff;
        #         border: 1px solid #e5e7eb;
        #         border-radius: 12px;
        #         padding: 12px 14px;
        #         box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        #         min-height: 82px;
        #     }
        #     .pbi-label {
        #         font-size: 12px;
        #         color: #6b7280;
        #         text-transform: uppercase;
        #         letter-spacing: .04em;
        #         margin-bottom: 6px;
        #     }
        #     .pbi-value {
        #         font-size: 22px;
        #         font-weight: 700;
        #         color: #111827;
        #         line-height: 1.15;
        #         word-break: break-word;
        #     }
        #     .pbi-value-sm {
        #         font-size: 18px;
        #         font-weight: 700;
        #         color: #111827;
        #         line-height: 1.2;
        #         word-break: break-word;
        #     }
        #     .pbi-pill {
        #         border-radius: 10px;
        #         padding: 10px 12px;
        #         font-size: 16px;
        #         font-weight: 700;
        #         display: inline-block;
        #         width: 100%;
        #     }
        #     </style>
        #     """,
        #     unsafe_allow_html=True,
        # )
        #
        # # Row 1: SKU, Category, Supplier, Warehouse, Status
        # r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns([1, 1, 1, 1, 1.2])
        #
        # with r1c1:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">SKU</div>
        #             <div class="pbi-value-sm">{sku_df['SKU']}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with r1c2:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">Category</div>
        #             <div class="pbi-value-sm">{sku_df['Category']}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with r1c3:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">Supplier</div>
        #             <div class="pbi-value-sm">{sku_df['Supplier']}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with r1c4:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">Warehouse</div>
        #             <div class="pbi-value-sm">{sku_df['Warehouse']}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with r1c5:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card" style="border:none; box-shadow:none; background:transparent;">
        #             <div class="pbi-label">Status</div>
        #             <div class="pbi-pill" style="background:{status_bg}; color:{status_color};">{status_text}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        #
        # # Optional description row
        # st.markdown(f"### {sku_df['Description']}")
        #
        # # Row 2: KPI cards
        # k1, k2, k3, k4 = st.columns(4)
        #
        # with k1:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">Current Inventory</div>
        #             <div class="pbi-value">{int(sku_df['Current Inventory']):,}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with k2:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">EOQ</div>
        #             <div class="pbi-value">{int(sku_df['EOQ']):,}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with k3:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">Safety Stock</div>
        #             <div class="pbi-value">{int(sku_df['Safety Stock']):,}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # with k4:
        #     st.markdown(
        #         f"""
        #         <div class="pbi-card">
        #             <div class="pbi-label">Reorder Point</div>
        #             <div class="pbi-value">{int(sku_df['Reorder Point']):,}</div>
        #         </div>
        #         """,
        #         unsafe_allow_html=True,
        #     )
        #
        # st.divider()

        # =========================
        # SKU INTELLIGENCE (COMPLETE BLOCK)
        # =========================
        st.subheader("🔎 SKU Intelligence")

        # CSS (safe to keep here; or move once to top of file)
        st.markdown(
            """
            <style>
            .pbi-card {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 14px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.04);
                min-height: 82px;
            }
            .pbi-label {
                font-size: 12px;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: .04em;
                margin-bottom: 6px;
            }
            .pbi-value {
                font-size: 32px;
                font-weight: 700;
                color: #111827;
                line-height: 1.1;
            }
            .pbi-value-sm {
                font-size: 18px;
                font-weight: 700;
                color: #111827;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .pbi-pill {
                border-radius: 10px;
                padding: 10px 12px;
                font-size: 15px;
                font-weight: 700;
                display: inline-block;
                width: 100%;
                text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # SKU selector
        sku_options = sorted(df["SKU"].astype(str).dropna().unique().tolist())
        if not sku_options:
            st.warning("No SKUs available.")
        else:
            sku = st.selectbox("Select a SKU", sku_options)
            sku_df = df[df["SKU"].astype(str) == sku].iloc[0]

            # status logic
            if sku_df["Current Inventory"] < sku_df["Reorder Point"]:
                status_text = "🔴 Critical Inventory"
                status_bg = "#fee2e2"
                status_color = "#b91c1c"
            elif sku_df["Current Inventory"] < sku_df["Safety Stock"]:
                status_text = "🟡 Low Inventory"
                status_bg = "#fef3c7"
                status_color = "#92400e"
            else:
                status_text = "🟢 Healthy Inventory"
                status_bg = "#dcfce7"
                status_color = "#166534"

            # title + status
            head_left, head_right = st.columns([2.3, 1.0])

            with head_left:
                st.markdown(f"### {sku_df['Description']}")

            with head_right:
                st.markdown(
                    f"""
                    <div class="pbi-pill" style="background:{status_bg}; color:{status_color};">
                        {status_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # metadata cards: 2 + 2
            meta_cards = [
                ("SKU", sku_df["SKU"]),
                ("Category", sku_df["Category"]),
                ("Supplier", sku_df["Supplier"]),
                ("Warehouse", sku_df["Warehouse"]),
            ]

            for i in range(0, len(meta_cards), 2):
                c1, c2 = st.columns(2)

                label_1, value_1 = meta_cards[i]
                label_2, value_2 = meta_cards[i + 1]

                with c1:
                    st.markdown(
                        f"""
                        <div class="pbi-card">
                            <div class="pbi-label">{label_1}</div>
                            <div class="pbi-value-sm">{value_1}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with c2:
                    st.markdown(
                        f"""
                        <div class="pbi-card">
                            <div class="pbi-label">{label_2}</div>
                            <div class="pbi-value-sm">{value_2}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

            # KPI cards row
            k1, k2, k3, k4 = st.columns(4)

            with k1:
                st.markdown(
                    f"""
                    <div class="pbi-card">
                        <div class="pbi-label">Current Inventory</div>
                        <div class="pbi-value">{int(sku_df["Current Inventory"]):,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with k2:
                st.markdown(
                    f"""
                    <div class="pbi-card">
                        <div class="pbi-label">EOQ</div>
                        <div class="pbi-value">{int(sku_df["EOQ"]):,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with k3:
                st.markdown(
                    f"""
                    <div class="pbi-card">
                        <div class="pbi-label">Safety Stock</div>
                        <div class="pbi-value">{int(sku_df["Safety Stock"]):,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with k4:
                st.markdown(
                    f"""
                    <div class="pbi-card">
                        <div class="pbi-label">Reorder Point</div>
                        <div class="pbi-value">{int(sku_df["Reorder Point"]):,}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.divider()


        # =========================================================
        # 2) FILTERS
        # =========================================================
        st.subheader("🧰 Filters")

        f1, f2, f3, f4 = st.columns([3, 2, 2, 2])
        with f1:
            search = st.text_input("Search SKU / Description", placeholder="Example: ASIC-001")
        with f2:
            category = st.selectbox("Category", ["All"] + sorted(df["Category"].astype(str).unique().tolist()))
        with f3:
            supplier = st.selectbox("Supplier", ["All"] + sorted(df["Supplier"].astype(str).unique().tolist()))
        with f4:
            warehouse = st.selectbox("Warehouse", ["All"] + sorted(df["Warehouse"].astype(str).unique().tolist()))

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
            st.warning("No SKUs match selected filters.")
            return

        st.divider()

        # =========================================================
        # 3) SUMMARY + HEALTH
        # =========================================================
        left, right = st.columns(2)

        healthy = int((filtered["Health"] == "Healthy").sum())
        low = int((filtered["Health"] == "Low").sum())
        critical = int((filtered["Health"] == "Critical").sum())

        with left:
            st.subheader("📦 Inventory Summary")
            st.markdown(
                f"""
**Total SKUs**  
{len(filtered)}

**Total Inventory Value**  
{currency(filtered["Inventory Value"].sum())}

**Average Inventory**  
{number(filtered["Current Inventory"].mean())}

**Average Unit Cost**  
{currency(filtered["Unit Cost"].mean())}
"""
            )

        with right:
            st.subheader("⚠ Inventory Health")
            st.metric("Healthy SKUs", healthy)
            st.metric("Low Stock", low)
            st.metric("Critical Stock", critical)

        st.divider()

        # =========================================================
        # 4) ANALYTICS + HIGH/LOW TABLES
        # =========================================================
        st.subheader("📊 Inventory Analytics")
        a1, a2 = st.columns(2)

        with a1:
            st.plotly_chart(inventory_value_chart(filtered), use_container_width=True)

        with a2:
            st.plotly_chart(category_distribution(filtered), use_container_width=True)

        st.divider()

        t1, t2 = st.columns(2)

        with t1:
            st.subheader("📈 Highest Inventory")
            high = filtered.sort_values("Current Inventory", ascending=False).head(5)
            st.dataframe(
                high[["SKU", "Description", "Current Inventory", "Warehouse"]],
                use_container_width=True,
                hide_index=True,
            )

        with t2:
            st.subheader("🚨 Lowest Inventory")
            low_df = filtered.sort_values("Current Inventory", ascending=True).head(5)
            st.dataframe(
                low_df[["SKU", "Description", "Current Inventory", "Warehouse"]],
                use_container_width=True,
                hide_index=True,
            )

        st.divider()

        # =========================================================
        # 5) INVENTORY SNAPSHOT (LAST)
        # =========================================================
        st.subheader("📋 Inventory Snapshot")

        snapshot = filtered.copy()
        snapshot["Health"] = snapshot["Health"].map(
            {"Critical": "🔴 Critical", "Low": "🟡 Low", "Healthy": "🟢 Healthy"}
        )

        st.dataframe(
            snapshot[
                [
                    "SKU", "Description", "Category", "Supplier", "Warehouse",
                    "Current Inventory", "Safety Stock", "Reorder Point",
                    "EOQ", "Lead Time", "Health"
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        f1, f2, f3 = st.columns(3)
        f1.caption(f"Records Loaded: {len(filtered)}")
        f2.caption("Source: Synthetic Semiconductor Dataset")
        f3.caption(f"Last Refresh: {datetime.now().strftime('%H:%M:%S')}")

    except Exception as e:
        st.exception(e)