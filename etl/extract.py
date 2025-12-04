from pathlib import Path
import shutil
import pandas as pd
import kagglehub


RAW_DIR = Path("data_raw")

# All Olist CSVs you care about
CSV_FILES = [
    "olist_customers_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_geolocation_dataset.csv",
]


def extract_raw_files() -> dict:
    """
    Download raw CSVs from Kaggle (if not already downloaded)
    and return them as a dict of DataFrames.

    Returns
    -------
    dict[str, pd.DataFrame]
        Mapping of raw table name → DataFrame
    """
    print("[EXTRACT] Downloading Olist dataset via kagglehub...")
    dataset_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

    RAW_DIR.mkdir(exist_ok=True)

    # Copy only the CSVs we care about
    for name in CSV_FILES:
        src = Path(dataset_path) / name
        dst = RAW_DIR / name

        if not dst.exists():
            shutil.copy(src, dst)

    print("[EXTRACT] Raw files saved to data_raw/")

    # Load all into memory
    tables = {}
    for name in CSV_FILES:
        df = pd.read_csv(RAW_DIR / name)
        key = name.replace(".csv", "")  # e.g. "olist_customers_dataset"
        tables[key] = df
        print(f"[EXTRACT] Loaded {name} → {df.shape[0]:,} rows")

    return tables


if __name__ == "__main__":
    extract_raw_files()
