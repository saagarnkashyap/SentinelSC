import streamlit as st
import pandas as pd
from datetime import datetime

from src.data_loader import load_inventory
from src.utils import currency, number, days


def _health(row):
    if row["Current Inventory"] < row["Reorder Point"]:
        return "Critical"
    elif row["Current Inventory"] < row["Safety Stock"]:
        return "Low"
    return "Healthy"


def _safe_num(v, d=0.0):
    try:
        return float(v)
    except Exception:
        return d


def _build_inventory_recommendations(df: pd.DataFrame):
    recs = []
    for _, r in df.iterrows():
        current = _safe_num(r["Current Inventory"])
        eoq = max(_safe_num(r["EOQ"]), 0)
        reorder = _safe_num(r["Reorder Point"])
        safety = _safe_num(r["Safety Stock"])
        lead = _safe_num(r["Lead Time"])
        unit_cost = _safe_num(r["Unit Cost"])

        if current < reorder:
            qty = int(max(eoq, reorder - current))
            recs.append(
                {
                    "Priority": "High",
                    "Type": "Raise Purchase Order",
                    "SKU": r["SKU"],
                    "Supplier": r["Supplier"],
                    "Recommendation": f"Raise PO for ~{qty} units",
                    "Estimated Cost": qty * unit_cost,
                }
            )

        if current > (eoq * 3) and eoq > 0:
            recs.append(
                {
                    "Priority": "Medium",
                    "Type": "Delay Procurement",
                    "SKU": r["SKU"],
                    "Supplier": r["Supplier"],
                    "Recommendation": "Overstock risk detected; delay next order cycle",
                    "Estimated Cost": 0,
                }
            )

        if lead > 18:
            recs.append(
                {
                    "Priority": "Medium",
                    "Type": "Supplier Risk",
                    "SKU": r["SKU"],
                    "Supplier": r["Supplier"],
                    "Recommendation": "Lead time high; evaluate alternate supplier",
                    "Estimated Cost": 0,
                }
            )

        if current < safety:
            recs.append(
                {
                    "Priority": "High",
                    "Type": "Increase Safety Stock",
                    "SKU": r["SKU"],
                    "Supplier": r["Supplier"],
                    "Recommendation": "Current inventory below safety stock; increase buffer",
                    "Estimated Cost": 0,
                }
            )
    return pd.DataFrame(recs)


def _executive_summary(df: pd.DataFrame) -> str:
    total_skus = len(df)
    critical = (df["Health"] == "Critical").sum()
    low = (df["Health"] == "Low").sum()
    healthy = (df["Health"] == "Healthy").sum()

    total_value = (df["Current Inventory"] * df["Unit Cost"]).sum()
    avg_lead = df["Lead Time"].mean()
    risky_suppliers = (
        df.groupby("Supplier")["Lead Time"].mean().reset_index().query("Lead Time > 18")
    )

    health_score = max(0, 100 - (critical * 2) - (low * 1))

    return f"""
### Overall Supply Chain Health
- **Health Score:** {health_score:.1f}/100
- **Total Active SKUs:** {total_skus}
- **Healthy / Low / Critical:** {healthy} / {low} / {critical}
- **Total Inventory Value:** {currency(total_value)}
- **Average Lead Time:** {avg_lead:.1f} days

### Current Risks
- **Critical SKUs:** {critical}
- **Low Stock SKUs:** {low}
- **Suppliers with High Lead Time (>18d):** {len(risky_suppliers)}

### Top Priorities
1. Replenish SKUs below reorder point
2. Address lead-time risk suppliers
3. Rebalance overstocked inventory
"""


def render_advisor():
    st.title("🧠 AI Advisor")
    st.caption("Rule-based executive advisor (LLM-ready architecture).")

    df = load_inventory()
    if df is None or df.empty:
        st.warning("Inventory dataset is empty.")
        return

    required = [
        "SKU", "Description", "Category", "Supplier", "Warehouse",
        "Current Inventory", "EOQ", "Safety Stock", "Reorder Point",
        "Lead Time", "Unit Cost"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        return

    # Clean
    x = df.copy()
    num_cols = ["Current Inventory", "EOQ", "Safety Stock", "Reorder Point", "Lead Time", "Unit Cost"]
    for c in num_cols:
        x[c] = pd.to_numeric(x[c], errors="coerce")

    x = x.dropna(subset=required)
    if x.empty:
        st.warning("No valid rows after cleaning.")
        return

    x["Inventory Value"] = x["Current Inventory"] * x["Unit Cost"]
    x["Health"] = x.apply(_health, axis=1)

    st.divider()

    # ----------------------------------------
    # Executive Summary
    # ----------------------------------------
    st.subheader("📌 Executive Summary")
    if st.button("Generate Executive Summary", type="primary"):
        st.info(_executive_summary(x))
    else:
        st.caption("Click **Generate Executive Summary** to refresh guidance.")

    st.divider()

    # ----------------------------------------
    # Inventory Advisor (per SKU)
    # ----------------------------------------
    st.subheader("📦 Inventory Advisor")

    sku = st.selectbox("Select SKU", sorted(x["SKU"].astype(str).unique().tolist()))
    sku_df = x[x["SKU"].astype(str) == sku].iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Current Inventory", number(sku_df["Current Inventory"]))
    with c2:
        st.metric("Reorder Point", number(sku_df["Reorder Point"]))
    with c3:
        st.metric("Safety Stock", number(sku_df["Safety Stock"]))

    if sku_df["Current Inventory"] < sku_df["Reorder Point"]:
        qty = int(max(sku_df["EOQ"], sku_df["Reorder Point"] - sku_df["Current Inventory"]))
        st.error(f"🔴 Immediate action: Raise PO for ~**{qty} units**.")
    elif sku_df["Current Inventory"] < sku_df["Safety Stock"]:
        st.warning("🟡 Warning: Inventory below safety stock. Monitor closely.")
    elif sku_df["Current Inventory"] > sku_df["EOQ"] * 3:
        st.info("📦 Overstock signal. Consider delaying next procurement cycle.")
    else:
        st.success("🟢 Inventory position is healthy.")

    st.divider()

    # ----------------------------------------
    # Supplier Advisor
    # ----------------------------------------
    st.subheader("🚚 Supplier Advisor")

    supplier_perf = (
        x.groupby("Supplier")
        .agg(
            Managed_SKUs=("SKU", "nunique"),
            Avg_Lead_Time=("Lead Time", "mean"),
            Inventory_Value=("Inventory Value", "sum"),
            Critical_SKUs=("Health", lambda s: (s == "Critical").sum()),
        )
        .reset_index()
    )

    supplier_perf["Risk"] = supplier_perf.apply(
        lambda r: "High" if r["Avg_Lead_Time"] > 18 or r["Critical_SKUs"] > 5
        else ("Medium" if r["Avg_Lead_Time"] > 12 or r["Critical_SKUs"] > 2 else "Low"),
        axis=1
    )

    supplier_perf.rename(
        columns={
            "Managed_SKUs": "Managed SKUs",
            "Avg_Lead_Time": "Average Lead Time",
            "Inventory_Value": "Inventory Value",
            "Critical_SKUs": "Critical SKUs",
        },
        inplace=True,
    )

    st.dataframe(supplier_perf, use_container_width=True, hide_index=True)

    st.divider()

    # ----------------------------------------
    # Procurement Advisor
    # ----------------------------------------
    st.subheader("🛒 Procurement Advisor")

    need_po = x[x["Current Inventory"] < x["Reorder Point"]].copy()
    if need_po.empty:
        st.success("No immediate PO requirements.")
    else:
        need_po["Recommended Qty"] = (need_po["EOQ"]).clip(lower=1).round().astype(int)
        need_po["Estimated PO Cost"] = need_po["Recommended Qty"] * need_po["Unit Cost"]

        st.dataframe(
            need_po[
                [
                    "SKU", "Description", "Supplier", "Warehouse",
                    "Current Inventory", "Reorder Point", "EOQ",
                    "Recommended Qty", "Estimated PO Cost"
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.metric("Total Estimated PO Cost", currency(need_po["Estimated PO Cost"].sum()))

    st.divider()

    # ----------------------------------------
    # Cost Optimization
    # ----------------------------------------
    st.subheader("💰 Cost Optimization")

    carrying_rate = st.slider("Annual Carrying Cost Rate (%)", 5, 40, 20)
    carrying_rate_dec = carrying_rate / 100.0

    x["Annual Carrying Cost"] = x["Inventory Value"] * carrying_rate_dec
    total_carry = x["Annual Carrying Cost"].sum()

    overstock = x[x["Current Inventory"] > (x["EOQ"] * 3)].copy()
    potential_savings = (overstock["Inventory Value"].sum() * 0.08)  # synthetic

    c1, c2 = st.columns(2)
    c1.metric("Estimated Annual Carrying Cost", currency(total_carry))
    c2.metric("Potential Savings (if overstock optimized)", currency(potential_savings))

    st.divider()

    # ----------------------------------------
    # Recommendation Feed
    # ----------------------------------------
    st.subheader("📰 Recommendation Feed")

    recs = _build_inventory_recommendations(x)
    if recs.empty:
        st.info("No major recommendations right now.")
    else:
        priority_rank = {"High": 1, "Medium": 2, "Low": 3}
        recs["priority_sort"] = recs["Priority"].map(priority_rank).fillna(9)
        recs = recs.sort_values(["priority_sort", "Estimated Cost"], ascending=[True, False]).drop(columns=["priority_sort"])

        st.dataframe(recs, use_container_width=True, hide_index=True)

    st.divider()

    # ----------------------------------------
    # Risk Forecast (synthetic)
    # ----------------------------------------
    st.subheader("🔮 Risk Forecast")

    forecast_horizon = st.selectbox("Forecast Horizon", ["7 days", "14 days", "30 days"], index=1)

    critical_now = (x["Health"] == "Critical").sum()
    lead_risk = (x["Lead Time"] > 18).sum()
    shortage_risk = int((critical_now * 1.15) + (lead_risk * 0.5))  # synthetic

    r1, r2, r3 = st.columns(3)
    r1.metric("Current Critical SKUs", int(critical_now))
    r2.metric("Lead-Time Risk SKUs", int(lead_risk))
    r3.metric(f"Projected Shortages ({forecast_horizon})", int(shortage_risk))

    st.divider()

    # ----------------------------------------
    # Explainability
    # ----------------------------------------
    st.subheader("🧾 Explainability")
    st.info(
        """
Recommendations are generated using deterministic policy rules:
- If Current Inventory < Reorder Point → Raise Purchase Order
- If Current Inventory < Safety Stock → Increase Safety Buffer
- If Lead Time is high → Supplier risk mitigation
- If Current Inventory > 3x EOQ → Delay or rebalance procurement
"""
    )

    st.caption(f"Last advisor refresh: {datetime.now().strftime('%d %b %Y • %H:%M:%S')}")