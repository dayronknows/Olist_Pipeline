from pathlib import Path
from typing import Dict
import duckdb
import pandas as pd


DB_PATH = Path("db") / "olist_dw.duckdb"
DB_PATH.parent.mkdir(exist_ok=True)


def load_to_duckdb(tables: Dict[str, pd.DataFrame]) -> Path:
    """
    Write cleaned tables into a DuckDB warehouse file.
    Overwrites the tables on each pipeline run.
    """
    print(f"[LOAD] Connecting to DuckDB → {DB_PATH} ...")
    con = duckdb.connect(DB_PATH.as_posix())

    try:
        for name, df in tables.items():
            print(f"[LOAD] Writing {name:<20} ({len(df):,} rows)")

            con.register("temp_df", df)
            con.execute(
                f"""
                CREATE OR REPLACE TABLE {name} AS
                SELECT * FROM temp_df
                """
            )
            con.unregister("temp_df")

        print("[LOAD] All tables written.")
    finally:
        con.close()
        print("[LOAD] Connection closed.")

    return DB_PATH
