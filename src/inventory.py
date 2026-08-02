import numpy as np
import pandas as pd

Z_SCORE = 1.65

#eoq section
def calculate_eoq(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["EOQ"] = np.sqrt(
        (2 * df["Annual Demand"] * df["Ordering Cost"])
        / df["Holding Cost"]
    ).round(0)

    return df

#safety stock
def calculate_safety_stock(df: pd.DataFrame):

    df = df.copy()

    demand_std = df["Daily Demand"] * 0.20

    df["Safety Stock"] = (
        Z_SCORE
        * demand_std
        * np.sqrt(df["Lead Time"])
    ).round()

    return df

#reorder point
def calculate_reorder_point(df):

    df = df.copy()

    df["Reorder Point"] = (
        df["Daily Demand"] * df["Lead Time"]
        + df["Safety Stock"]
    ).round()

    return df

#pipeline
def optimize_inventory(df):

    df = calculate_eoq(df)

    df = calculate_safety_stock(df)

    df = calculate_reorder_point(df)

    return df

if __name__ == "__main__":

    from dataset import generate_inventory_dataset

    df = generate_inventory_dataset()

    df = optimize_inventory(df)

    print(df.head())