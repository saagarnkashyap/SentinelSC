import pandas as pd


def total_inventory_value(df: pd.DataFrame):

    return (
        df["Current Inventory"] *
        df["Unit Cost"]
    ).sum()


def average_eoq(df):

    return df["EOQ"].mean()


def critical_skus(df):

    return (
        df["Current Inventory"]
        <
        df["Reorder Point"]
    ).sum()


def average_lead_time(df):

    return df["Lead Time"].mean()

