import plotly.express as px


def inventory_value_chart(df):

    chart_df = df.copy()

    chart_df["Inventory Value"] = (
        chart_df["Current Inventory"]
        *
        chart_df["Unit Cost"]
    )

    fig = px.bar(

        chart_df,

        x="SKU",

        y="Inventory Value",

        color="Category",

        title="Inventory Value by SKU",

    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
    )

    return fig

def category_distribution(df):

    fig = px.pie(

        df,

        names="Category",

        values="Current Inventory",

        hole=0.6,

        title="Inventory Distribution"

    )

    fig.update_layout(

        template="plotly_dark"

    )

    return fig