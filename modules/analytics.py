import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_inventory
from src.utils import currency, number, days


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()

    numeric_cols = ["Current Inventory", "Unit Cost", "Lead Time", "EOQ"]
    for c in numeric_cols:
        if c in x.columns:
            x[c] = pd.to_numeric(x[c], errors="coerce")

    required = ["SKU", "Category", "Supplier", "Warehouse", "Current Inventory", "Unit Cost", "Lead Time", "EOQ"]
    missing = [c for c in required if c not in x.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    x = x.dropna(subset=required)
    x["Inventory Value"] = x["Current Inventory"] * x["Unit Cost"]
    x["Inventory Health"] = x.apply(
        lambda r: "Critical" if r["Current Inventory"] < r.get("Reorder Point", 0)
        else "Low" if r["Current Inventory"] < r.get("Safety Stock", 0)
        else "Healthy",
        axis=1,
    )
    return x


def _abc_analysis(df: pd.DataFrame) -> pd.DataFrame:
    a = df.groupby("SKU", dropna=False)["Inventory Value"].sum().reset_index()
    a = a.sort_values("Inventory Value", ascending=False).reset_index(drop=True)
    total = a["Inventory Value"].sum()
    if total <= 0:
        a["CumPct"] = 0
        a["ABC"] = "C"
        return a

    a["CumPct"] = (a["Inventory Value"].cumsum() / total) * 100
    a["ABC"] = a["CumPct"].apply(lambda v: "A" if v <= 80 else ("B" if v <= 95 else "C"))
    return a


def render_analytics():
    st.title("📊 Analytics")
    st.caption("Data-driven supply chain insights.")

    df = load_inventory()
    if df is None or df.empty:
        st.warning("Inventory dataset is empty.")
        return

    try:
        df = _clean_df(df)
    except Exception as e:
        st.error(str(e))
        return

    if df.empty:
        st.warning("No valid records after data cleanup.")
        return

    st.divider()

    # ----------------------------------------
    # Executive summary cards
    # ----------------------------------------
    k1, k2, k3, k4 = st.columns(4)

    total_value = df["Inventory Value"].sum()
    total_skus = df["SKU"].nunique()
    avg_lead = df["Lead Time"].mean()
    avg_eoq = df["EOQ"].mean()

    with k1:
        st.metric("Total Inventory Value", currency(total_value))
    with k2:
        st.metric("Unique SKUs", number(total_skus))
    with k3:
        st.metric("Average Lead Time", days(avg_lead))
    with k4:
        st.metric("Average EOQ", number(avg_eoq))

    st.divider()

    # ----------------------------------------
    # ABC Analysis + Pareto
    # ----------------------------------------
    st.subheader("🧠 ABC & Pareto Analysis")

    abc = _abc_analysis(df)

    c1, c2 = st.columns(2)
    with c1:
        class_counts = abc["ABC"].value_counts().reindex(["A", "B", "C"]).fillna(0).reset_index()
        class_counts.columns = ["Class", "SKUs"]

        fig_abc = px.bar(
            class_counts,
            x="Class",
            y="SKUs",
            title="ABC Classification",
            color="Class",
            color_discrete_map={"A": "#2563eb", "B": "#f59e0b", "C": "#10b981"},
        )
        fig_abc.update_layout(template="plotly_white", height=360)
        st.plotly_chart(fig_abc, use_container_width=True)

    with c2:
        pareto = abc.copy()
        pareto["Rank"] = range(1, len(pareto) + 1)

        fig_pareto = px.bar(
            pareto.head(30),
            x="Rank",
            y="Inventory Value",
            title="Pareto (Top 30 SKUs by Value)",
        )
        fig_pareto.add_scatter(
            x=pareto.head(30)["Rank"],
            y=pareto.head(30)["CumPct"],
            mode="lines+markers",
            name="Cumulative %",
            yaxis="y2",
        )
        fig_pareto.update_layout(
            template="plotly_white",
            height=360,
            yaxis2=dict(overlaying="y", side="right", title="Cum %"),
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    st.divider()

    # ----------------------------------------
    # Value by category + supplier
    # ----------------------------------------
    st.subheader("📦 Inventory Value Composition")

    ch1, ch2 = st.columns(2)

    with ch1:
        by_cat = (
            df.groupby("Category", dropna=False)["Inventory Value"]
            .sum()
            .reset_index()
            .sort_values("Inventory Value", ascending=False)
        )
        fig_cat = px.bar(
            by_cat,
            x="Category",
            y="Inventory Value",
            title="Inventory Value by Category",
            color="Inventory Value",
            color_continuous_scale="Blues",
        )
        fig_cat.update_layout(template="plotly_white", height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with ch2:
        by_sup = (
            df.groupby("Supplier", dropna=False)["Inventory Value"]
            .sum()
            .reset_index()
            .sort_values("Inventory Value", ascending=False)
        )
        fig_sup = px.bar(
            by_sup,
            x="Supplier",
            y="Inventory Value",
            title="Inventory Value by Supplier",
            color="Inventory Value",
            color_continuous_scale="Greens",
        )
        fig_sup.update_layout(template="plotly_white", height=380, coloraxis_showscale=False)
        st.plotly_chart(fig_sup, use_container_width=True)

    st.divider()

    # ----------------------------------------
    # Warehouse + Health visuals
    # ----------------------------------------
    st.subheader("🏭 Warehouse & Health Intelligence")

    w1, w2 = st.columns(2)

    with w1:
        by_wh = (
            df.groupby("Warehouse", dropna=False)["Inventory Value"]
            .sum()
            .reset_index()
            .sort_values("Inventory Value", ascending=False)
        )
        fig_wh = px.pie(
            by_wh,
            names="Warehouse",
            values="Inventory Value",
            hole=0.45,
            title="Warehouse Distribution",
        )
        fig_wh.update_layout(template="plotly_white", height=380)
        st.plotly_chart(fig_wh, use_container_width=True)

    with w2:
        health_counts = df["Inventory Health"].value_counts().reset_index()
        health_counts.columns = ["Health", "Count"]
        fig_health = px.treemap(
            health_counts,
            path=["Health"],
            values="Count",
            title="Inventory Health Treemap",
            color="Health",
            color_discrete_map={"Healthy": "#10b981", "Low": "#f59e0b", "Critical": "#ef4444"},
        )
        fig_health.update_layout(template="plotly_white", height=380)
        st.plotly_chart(fig_health, use_container_width=True)

    st.divider()

    # ----------------------------------------
    # Lead time + EOQ distributions
    # ----------------------------------------
    st.subheader("📈 Lead Time & EOQ Analysis")

    d1, d2 = st.columns(2)

    with d1:
        fig_lt = px.histogram(
            df,
            x="Lead Time",
            nbins=20,
            title="Lead Time Distribution",
            color_discrete_sequence=["#6366f1"],
        )
        fig_lt.update_layout(template="plotly_white", height=360)
        st.plotly_chart(fig_lt, use_container_width=True)

        lt_mean = df["Lead Time"].mean()
        lt_med = df["Lead Time"].median()
        st.caption(f"Lead Time Avg: **{lt_mean:.2f} days** | Median: **{lt_med:.2f} days**")

    with d2:
        fig_eoq = px.box(
            df,
            y="EOQ",
            points="outliers",
            title="EOQ Distribution & Outliers",
            color_discrete_sequence=["#0ea5e9"],
        )
        fig_eoq.update_layout(template="plotly_white", height=360)
        st.plotly_chart(fig_eoq, use_container_width=True)

    st.divider()

    # ----------------------------------------
    # Supplier scorecard
    # ----------------------------------------
    st.subheader("🚚 Supplier Scorecard")

    supplier_scorecard = (
        df.groupby("Supplier", dropna=False)
        .agg(
            Managed_SKUs=("SKU", "nunique"),
            Avg_Lead_Time=("Lead Time", "mean"),
            Total_Value=("Inventory Value", "sum"),
            Avg_Inventory=("Current Inventory", "mean"),
        )
        .reset_index()
    )

    supplier_scorecard["Risk"] = supplier_scorecard["Avg_Lead_Time"].apply(
        lambda x: "High" if x > 18 else ("Medium" if x > 12 else "Low")
    )

    supplier_scorecard.rename(
        columns={
            "Managed_SKUs": "Managed SKUs",
            "Avg_Lead_Time": "Average Lead Time",
            "Total_Value": "Inventory Value",
            "Avg_Inventory": "Average Inventory",
        },
        inplace=True,
    )

    st.dataframe(supplier_scorecard, use_container_width=True, hide_index=True)

    st.divider()

    # ----------------------------------------
    # Download report
    # ----------------------------------------
    st.subheader("⬇ Download Reports")

    export_df = df.copy()
    export_df["Inventory Value"] = export_df["Inventory Value"].round(2)

    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Analytics CSV",
        csv,
        file_name="analytics_report.csv",
        mime="text/csv",
        use_container_width=True,
    )