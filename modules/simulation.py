import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_inventory
from src.utils import currency, number, days


def _safe_div(a, b):
    return (a / b) if b else 0


def _simulate_inventory(df: pd.DataFrame, params: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (before_df, after_df)
    """
    before = df.copy()
    after = df.copy()

    # Ensure numeric columns
    numeric_cols = [
        "Current Inventory",
        "Daily Demand",
        "Lead Time",
        "Safety Stock",
        "Reorder Point",
        "EOQ",
        "Unit Cost",
    ]
    for c in numeric_cols:
        if c in after.columns:
            after[c] = pd.to_numeric(after[c], errors="coerce")

    after = after.dropna(subset=["Current Inventory", "Lead Time", "Safety Stock", "Reorder Point", "EOQ", "Unit Cost"])
    before = before.loc[after.index].copy()

    if after.empty:
        return before, after

    # Inputs
    demand_spike = params["demand_spike_pct"] / 100.0
    demand_drop = params["demand_drop_pct"] / 100.0
    lead_time_increase = params["lead_time_increase_days"]
    inventory_buffer_pct = params["inventory_buffer_pct"] / 100.0
    target_service = params["service_level"]  # 0.90, 0.95, ...
    failed_supplier = params["failed_supplier"]
    shutdown_warehouse = params["shutdown_warehouse"]
    transport_delay_days = params["transport_delay_days"]
    raw_shortage_pct = params["raw_shortage_pct"] / 100.0

    # Demand effect
    demand_multiplier = 1 + demand_spike - demand_drop
    demand_multiplier = max(demand_multiplier, 0.1)

    if "Daily Demand" not in after.columns:
        # derive synthetic daily demand if missing
        after["Daily Demand"] = (after["Current Inventory"] / 30).clip(lower=1)

    after["Daily Demand"] = after["Daily Demand"] * demand_multiplier

    # Lead time shocks
    after["Lead Time"] = after["Lead Time"] + lead_time_increase + transport_delay_days

    # Supplier failure shock
    if failed_supplier != "None":
        mask = after["Supplier"].astype(str) == failed_supplier
        after.loc[mask, "Lead Time"] = after.loc[mask, "Lead Time"] + 10
        after.loc[mask, "Current Inventory"] = after.loc[mask, "Current Inventory"] * 0.75

    # Warehouse shutdown shock
    if shutdown_warehouse != "None":
        mask = after["Warehouse"].astype(str) == shutdown_warehouse
        after.loc[mask, "Current Inventory"] = after.loc[mask, "Current Inventory"] * 0.60
        after.loc[mask, "Lead Time"] = after.loc[mask, "Lead Time"] + 7

    # Raw material shortage
    after["Current Inventory"] = after["Current Inventory"] * (1 - raw_shortage_pct)

    # Service level influences safety factor
    # Approx mapping
    service_z = {
        0.90: 1.28,
        0.95: 1.65,
        0.98: 2.05,
        0.99: 2.33,
    }
    z = service_z.get(target_service, 1.65)

    demand_std = after["Daily Demand"] * 0.20
    after["Safety Stock"] = (z * demand_std * (after["Lead Time"] ** 0.5)).round()

    # User inventory buffer
    after["Safety Stock"] = (after["Safety Stock"] * (1 + inventory_buffer_pct)).round()

    after["Reorder Point"] = (after["Daily Demand"] * after["Lead Time"] + after["Safety Stock"]).round()

    # EOQ recalibration (simple synthetic approximation if costs missing)
    if "Annual Demand" in after.columns and "Ordering Cost" in after.columns and "Holding Cost" in after.columns:
        ad = pd.to_numeric(after["Annual Demand"], errors="coerce").fillna(after["Daily Demand"] * 365)
        oc = pd.to_numeric(after["Ordering Cost"], errors="coerce").fillna(200)
        hc = pd.to_numeric(after["Holding Cost"], errors="coerce").fillna(10).replace(0, 10)
        after["EOQ"] = ((2 * ad * oc) / hc) ** 0.5
    else:
        after["EOQ"] = (after["Daily Demand"] * 30).clip(lower=1)

    after["EOQ"] = after["EOQ"].round()

    # Inventory value
    before["Inventory Value"] = before["Current Inventory"] * before["Unit Cost"]
    after["Inventory Value"] = after["Current Inventory"] * after["Unit Cost"]

    return before, after


def _kpis(df: pd.DataFrame) -> dict:
    critical = (df["Current Inventory"] < df["Reorder Point"]).sum()
    low = ((df["Current Inventory"] >= df["Reorder Point"]) & (df["Current Inventory"] < df["Safety Stock"])).sum()
    health_score = max(0, 100 - (critical * 2) - (low * 1))
    return {
        "inventory_value": df["Inventory Value"].sum(),
        "avg_eoq": df["EOQ"].mean(),
        "avg_safety": df["Safety Stock"].mean(),
        "avg_rop": df["Reorder Point"].mean(),
        "avg_lead_time": df["Lead Time"].mean(),
        "critical_skus": int(critical),
        "low_skus": int(low),
        "health_score": float(health_score),
    }


def render_simulation():
    st.title("⚠ Scenario Simulator")
    st.caption("Digital Twin simulation for supply chain shocks and policy tuning.")

    df = load_inventory()
    if df is None or df.empty:
        st.warning("Inventory dataset is empty.")
        return

    required = ["SKU", "Supplier", "Warehouse", "Current Inventory", "Safety Stock", "Reorder Point", "EOQ", "Lead Time", "Unit Cost"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        return

    st.divider()

    # -------------------------
    # Simulation Controls
    # -------------------------
    st.subheader("🧪 Simulation Controls")

    c1, c2, c3 = st.columns(3)
    with c1:
        lead_time_increase_days = st.slider("Lead Time Increase (days)", 0, 30, 5)
        demand_spike_pct = st.selectbox("Demand Spike", [0, 10, 25, 50, 100], index=1)
        demand_drop_pct = st.selectbox("Demand Drop", [0, 5, 10, 20, 30], index=0)

    with c2:
        service_level = st.selectbox("Service Level", [0.90, 0.95, 0.98, 0.99], index=1)
        inventory_buffer_pct = st.slider("Inventory Buffer (%)", 0, 50, 10)
        transport_delay_days = st.slider("Transportation Delay (days)", 0, 20, 3)

    with c3:
        suppliers = ["None"] + sorted(df["Supplier"].astype(str).dropna().unique().tolist())
        warehouses = ["None"] + sorted(df["Warehouse"].astype(str).dropna().unique().tolist())

        failed_supplier = st.selectbox("Supplier Failure", suppliers, index=0)
        shutdown_warehouse = st.selectbox("Warehouse Shutdown", warehouses, index=0)
        raw_shortage_pct = st.slider("Raw Material Shortage (%)", 0, 50, 10)

    run = st.button("▶ Run Simulation", type="primary", use_container_width=True)

    if not run:
        st.info("Set parameters and click **Run Simulation**.")
        return

    params = {
        "lead_time_increase_days": lead_time_increase_days,
        "demand_spike_pct": demand_spike_pct,
        "demand_drop_pct": demand_drop_pct,
        "service_level": service_level,
        "inventory_buffer_pct": inventory_buffer_pct,
        "failed_supplier": failed_supplier,
        "shutdown_warehouse": shutdown_warehouse,
        "transport_delay_days": transport_delay_days,
        "raw_shortage_pct": raw_shortage_pct,
    }

    before, after = _simulate_inventory(df, params)

    if after.empty:
        st.error("Simulation produced no valid rows.")
        return

    before_k = _kpis(before)
    after_k = _kpis(after)

    st.divider()
    st.subheader("📊 Results: Before vs After")

    # KPI changes
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Inventory Value", currency(after_k["inventory_value"]), delta=currency(after_k["inventory_value"] - before_k["inventory_value"]))
    with k2:
        st.metric("Average EOQ", number(after_k["avg_eoq"]), delta=f"{after_k['avg_eoq'] - before_k['avg_eoq']:.1f}")
    with k3:
        st.metric("Average Safety Stock", number(after_k["avg_safety"]), delta=f"{after_k['avg_safety'] - before_k['avg_safety']:.1f}")
    with k4:
        st.metric("Average Lead Time", days(after_k["avg_lead_time"]), delta=f"{after_k['avg_lead_time'] - before_k['avg_lead_time']:.1f} days")

    k5, k6, k7 = st.columns(3)
    with k5:
        st.metric("Critical SKUs", after_k["critical_skus"], delta=after_k["critical_skus"] - before_k["critical_skus"])
    with k6:
        st.metric("Low SKUs", after_k["low_skus"], delta=after_k["low_skus"] - before_k["low_skus"])
    with k7:
        st.metric("Inventory Health Score", f"{after_k['health_score']:.1f}/100", delta=f"{after_k['health_score'] - before_k['health_score']:.1f}")

    st.divider()

    # Comparison chart
    chart_df = pd.DataFrame(
        {
            "KPI": [
                "Inventory Value",
                "Avg EOQ",
                "Avg Safety Stock",
                "Avg Reorder Point",
                "Avg Lead Time",
                "Critical SKUs",
            ],
            "Before": [
                before_k["inventory_value"],
                before_k["avg_eoq"],
                before_k["avg_safety"],
                before_k["avg_rop"],
                before_k["avg_lead_time"],
                before_k["critical_skus"],
            ],
            "After": [
                after_k["inventory_value"],
                after_k["avg_eoq"],
                after_k["avg_safety"],
                after_k["avg_rop"],
                after_k["avg_lead_time"],
                after_k["critical_skus"],
            ],
        }
    )

    m = chart_df.melt(id_vars="KPI", value_vars=["Before", "After"], var_name="Scenario", value_name="Value")
    fig = px.bar(m, x="KPI", y="Value", color="Scenario", barmode="group", title="Before vs After KPI Comparison")
    fig.update_layout(template="plotly_white", height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Risk analysis
    st.subheader("🚨 Risk Analysis")
    newly_critical = after[
        (after["Current Inventory"] < after["Reorder Point"])
        & ~(before["Current Inventory"] < before["Reorder Point"])
    ]

    potential_revenue_impact = (newly_critical["Inventory Value"].sum()) * 0.15  # synthetic

    r1, r2, r3 = st.columns(3)
    r1.metric("New Stockouts (Potential)", int(len(newly_critical)))
    r2.metric("Critical SKUs (After)", int(after_k["critical_skus"]))
    r3.metric("Potential Revenue Impact", currency(potential_revenue_impact))

    if not newly_critical.empty:
        st.dataframe(
            newly_critical[["SKU", "Supplier", "Warehouse", "Current Inventory", "Reorder Point", "Lead Time"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # AI recommendations (rule-based)
    st.subheader("🤖 AI Recommendations")
    recs = []

    if after_k["critical_skus"] > before_k["critical_skus"]:
        recs.append("Increase safety stock for high-velocity SKUs and split replenishment frequency.")
    if params["failed_supplier"] != "None":
        recs.append(f"Activate alternate supplier strategy for **{params['failed_supplier']}**.")
    if params["shutdown_warehouse"] != "None":
        recs.append(f"Shift inventory from impacted warehouse **{params['shutdown_warehouse']}** to nearest node.")
    if after_k["avg_lead_time"] - before_k["avg_lead_time"] > 3:
        recs.append("Place earlier purchase orders to offset increased lead-time volatility.")
    if not recs:
        recs.append("Current policy remains stable under this scenario. Continue monitoring weekly.")

    for r in recs:
        st.info(r)

    st.divider()
    st.caption("Simulation timeline: Day 1 → Day 5 → Day 10 → Recovery (synthetic model)")