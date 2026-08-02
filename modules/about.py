import streamlit as st
from datetime import datetime


def render_about():
    st.title("About SentinelSC")
    st.caption("Enterprise Supply Chain Intelligence Platform")

    st.divider()

    # ---------------------------------------------------------
    # Hero Section
    # ---------------------------------------------------------
    st.markdown(
        """
### SentinelSC

**SentinelSC** is a modern, executive-grade supply chain intelligence platform designed to help teams monitor inventory health, optimize replenishment, simulate disruptions, and take faster decisions with AI-assisted recommendations.
"""
    )

    h1, h2, h3 = st.columns(3)
    with h1:
        st.metric("Platform Version", "v1.0.0")
    with h2:
        st.metric("Release Track", "Stable")
    with h3:
        st.metric("Environment", "Production Demo")

    st.divider()

    # ---------------------------------------------------------
    # Platform Modules
    # ---------------------------------------------------------
    st.subheader("🧩 Platform Modules")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
#### 🏠 Control Tower
Executive overview of:
- Inventory performance
- Risk posture
- Alert center
- System health
- Latest operational signals

#### 📦 Inventory Intelligence
Deep-dive operational module for:
- SKU-level intelligence
- Reorder, safety stock and EOQ monitoring
- Supplier and warehouse analysis
- Inventory health and optimization
"""
        )

    with c2:
        st.markdown(
            """
#### ⚠ Scenario Simulator
Digital twin simulation engine for:
- Demand spikes and drops
- Supplier/warehouse disruptions
- Lead-time volatility
- Before vs After KPI impact analysis

#### 📊 Analytics
Insight module for:
- ABC/Pareto analysis
- Category/supplier/warehouse value composition
- Lead time and EOQ distribution
- Downloadable analytical reports
"""
        )

    st.markdown(
        """
#### 🧠 AI Advisor
Decision intelligence layer for:
- Executive summaries
- Procurement recommendations
- Supplier risk insights
- Cost optimization opportunities
- Explainable recommendation feed
"""
    )

    st.divider()

    # ---------------------------------------------------------
    # Core Capabilities
    # ---------------------------------------------------------
    st.subheader("✅ Core Capabilities")

    cap1, cap2, cap3 = st.columns(3)

    with cap1:
        st.success("Real-time dashboard experience")
        st.success("SKU-level operational monitoring")
        st.success("Risk and alert intelligence")

    with cap2:
        st.success("Inventory optimization support")
        st.success("What-if simulation workflows")
        st.success("Supplier and warehouse diagnostics")

    with cap3:
        st.success("Executive decision support")
        st.success("Actionable recommendation feed")
        st.success("Export-ready reporting outputs")

    st.divider()

    # ---------------------------------------------------------
    # Architecture Snapshot
    # ---------------------------------------------------------
    st.subheader("🏗 Architecture Snapshot")

    st.code(
        """SentinelSC/
├─ app.py
├─ ui/
│  ├─ command_console.py
│  ├─ router.py
│  └─ theme.py
├─ modules/
│  ├─ control_tower.py
│  ├─ inventory.py
│  ├─ simulation.py
│  ├─ analytics.py
│  ├─ advisor.py
│  └─ about.py
└─ src/
   ├─ data_loader.py
   ├─ inventory_engine.py
   ├─ metrics.py
   ├─ charts.py
   └─ utils.py""",
        language="text",
    )

    st.divider()

    # ---------------------------------------------------------
    # Design Principles
    # ---------------------------------------------------------
    st.subheader("🎯 Design Principles")

    st.markdown(
        """
- **Clarity first**: Executive-friendly layouts and KPI storytelling  
- **Actionability**: Every insight should lead to a decision  
- **Modularity**: Independent modules for easy iteration and scale  
- **Explainability**: Recommendations backed by transparent logic  
- **Scalability-ready**: Future integration with LLM copilots and external ERP data
"""
    )

    st.divider()

    # ---------------------------------------------------------
    # Roadmap
    # ---------------------------------------------------------
    st.subheader("🛣 Product Roadmap")

    r1, r2 = st.columns(2)

    with r1:
        st.info(
            """
**Near-term Enhancements**
- Excel export
- PDF executive report
- Saved simulation history
- KPI trend persistence
"""
        )

    with r2:
        st.info(
            """
**Future Enhancements**
- Forecasting module
- Multi-LLM AI copilot integration
- ERP/API connectors
- Role-based views and collaboration
"""
        )

    st.divider()

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------
    f0, f1, f2 = st.columns(3)

    with f0:
        st.caption("Built by Kashyapa.suta")
    with f1:
        st.caption("SentinelSC • Enterprise Supply Chain Intelligence")
    # with f2:
    #     st.caption("Built with Streamlit + Plotly")
    with f2:
        st.caption(f"Last Updated: {datetime.now().strftime('%d %b %Y • %H:%M:%S')}")