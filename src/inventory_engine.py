import numpy as np
import pandas as pd

Z_SCORE = 1.65


def calculate_eoq(df: pd.DataFrame):

    df = df.copy()

    df["EOQ"] = np.sqrt(
        (2 * df["Annual Demand"] * df["Ordering Cost"])
        / df["Holding Cost"]
    ).round()

    return df


def calculate_safety_stock(df):

    df = df.copy()

    demand_std = df["Daily Demand"] * 0.20

    df["Safety Stock"] = (
        Z_SCORE
        * demand_std
        * np.sqrt(df["Lead Time"])
    ).round()

    return df


def calculate_reorder_point(df):

    df = df.copy()

    df["Reorder Point"] = (
        df["Daily Demand"]
        * df["Lead Time"]
        + df["Safety Stock"]
    ).round()

    return df


def optimize_inventory(df):

    df = calculate_eoq(df)

    df = calculate_safety_stock(df)

    df = calculate_reorder_point(df)

    return df