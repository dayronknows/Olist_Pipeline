from extract import extract_raw_files
from transform import transform_all
from load import load_to_duckdb


def run_pipeline():
    print("=== Olist ETL Pipeline (DuckDB Version) ===")

    # 1. Extract
    raw_tables = extract_raw_files()

    # 2. Transform
    cleaned_tables = transform_all(raw_tables)

    # 3. Load
    warehouse_path = load_to_duckdb(cleaned_tables)

    print(f"=== Pipeline complete. Warehouse at: {warehouse_path.resolve()} ===")


if __name__ == "__main__":
    run_pipeline()
