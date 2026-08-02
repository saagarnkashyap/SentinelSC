import streamlit as st

import pandas as pd

from pathlib import Path

from src.inventory import optimize_inventory

from src.metrics import *

from src.charts import *

DATA = Path("data/inventory.csv")

df = pd.read_csv(DATA)

df = optimize_inventory(df)

st.set_page_config(

    page_title="Sentinel",

    page_icon="📦",

    layout="wide",
)

st.title("📦 Sentinel")

st.caption(
    "Enterprise Supply Chain Intelligence Platform"
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(

        "Inventory Value",

        f"${total_inventory_value(df):,.0f}"

    )

with c2:

    st.metric(

        "Average EOQ",

        round(average_eoq(df))

    )

with c3:

    st.metric(

        "Critical SKUs",

        critical_skus(df)

    )

with c4:

    st.metric(

        "Average Lead Time",

        f"{average_lead_time(df):.1f} Days"

    )

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

st.subheader("Inventory")

st.dataframe(df)