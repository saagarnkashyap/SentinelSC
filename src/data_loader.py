from pathlib import Path

import pandas as pd

from src.inventory_engine import optimize_inventory

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "inventory.csv"


def load_inventory():

    df = pd.read_csv(DATA_PATH)

    df = optimize_inventory(df)

    return df