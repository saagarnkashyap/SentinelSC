from __future__ import annotations

import random
from pathlib import Path
import pandas as pd

random.seed(42)

PRODUCTS = [
    ("MCU-001", "Automotive MCU", "MCU"),
    ("MCU-002", "Industrial MCU", "MCU"),
    ("SOC-001", "Mobile SoC", "SoC"),
    ("SOC-002", "AI Edge SoC", "SoC"),
    ("FPGA-001", "High-Speed FPGA", "FPGA"),
    ("FPGA-002", "Embedded FPGA", "FPGA"),
    ("ASIC-001", "AI Accelerator", "ASIC"),
    ("ASIC-002", "Networking ASIC", "ASIC"),
    ("MEM-001", "DDR5 Memory", "Memory"),
    ("MEM-002", "LPDDR5 Memory", "Memory"),
    ("RF-001", "RF Front-End", "RF"),
    ("RF-002", "5G RF Module", "RF"),
    ("PMIC-001", "Power IC", "Analog"),
    ("PMIC-002", "Power Controller", "Analog"),
    ("SEN-001", "Image Sensor", "Sensor"),
    ("SEN-002", "Temperature Sensor", "Sensor"),
    ("DSP-001", "DSP Processor", "DSP"),
    ("DSP-002", "Audio DSP", "DSP"),
    ("GPU-001", "Embedded GPU", "GPU"),
    ("NPU-001", "Neural Processing Unit", "AI"),
]

SUPPLIERS = [
    "Supplier A",
    "Supplier B",
    "Supplier C",
    "Supplier D",
    "Supplier E",
]

WAREHOUSES = [
    "Singapore DC",
    "Taiwan Hub",
    "Germany DC",
]

def generate_inventory_dataset() -> pd.DataFrame:

    rows = []

    for sku, desc, category in PRODUCTS:

        annual_demand = random.randint(4000, 25000)

        daily_demand = annual_demand / 365

        lead_time = random.randint(5, 21)

        ordering_cost = random.randint(200, 600)

        holding_cost = round(random.uniform(8, 20), 2)

        unit_cost = random.randint(40, 500)

        inventory = random.randint(200, 2500)

        supplier = random.choice(SUPPLIERS)

        warehouse = random.choice(WAREHOUSES)

        rows.append(
            {
                "SKU": sku,
                "Description": desc,
                "Category": category,
                "Supplier": supplier,
                "Warehouse": warehouse,
                "Annual Demand": annual_demand,
                "Daily Demand": round(daily_demand, 2),
                "Lead Time": lead_time,
                "Ordering Cost": ordering_cost,
                "Holding Cost": holding_cost,
                "Unit Cost": unit_cost,
                "Current Inventory": inventory,
                "Service Level": 0.95,
            }
        )

    return pd.DataFrame(rows)

if __name__ == "__main__":

    df = generate_inventory_dataset()

    print(df.head())

    DATA_DIR = Path(__file__).resolve().parent.parent / "data"

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(DATA_DIR / "inventory.csv", index=False)