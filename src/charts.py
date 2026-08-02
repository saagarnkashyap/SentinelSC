import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _safe_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(
            columns=["SKU", "Category", "Current Inventory", "Unit Cost", "Inventory Value"]
        )
    out = df.copy()
    if "Inventory Value" not in out.columns and {"Current Inventory", "Unit Cost"}.issubset(out.columns):
        out["Inventory Value"] = out["Current Inventory"] * out["Unit Cost"]
    return out


def inventory_value_chart(df: pd.DataFrame):
    d = _safe_df(df)
    if d.empty or "SKU" not in d.columns or "Inventory Value" not in d.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Inventory Value by SKU (no data)",
            template="plotly_white",
            height=360,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig

    top = d.sort_values("Inventory Value", ascending=False).head(15)

    fig = px.bar(
        top,
        x="SKU",
        y="Inventory Value",
        color="Inventory Value",
        color_continuous_scale="Blues",
        title="Top SKUs by Inventory Value",
    )
    fig.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=10, r=10, t=50, b=10),
        coloraxis_showscale=False,
        xaxis_title="SKU",
        yaxis_title="Inventory Value",
    )
    return fig


def category_distribution(df: pd.DataFrame):
    d = _safe_df(df)
    if d.empty or "Category" not in d.columns or "Inventory Value" not in d.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Category Distribution (no data)",
            template="plotly_white",
            height=360,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig

    g = d.groupby("Category", dropna=False)["Inventory Value"].sum().reset_index()

    fig = px.pie(
        g,
        names="Category",
        values="Inventory Value",
        hole=0.45,
        title="Inventory Value Distribution by Category",
    )
    fig.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig