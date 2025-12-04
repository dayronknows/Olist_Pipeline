from pathlib import Path
import pandas as pd


def clean_string_cols(df, cols):
    """Utility: strip whitespace on selected columns."""
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


def transform_all(raw_tables: dict) -> dict:
    """
    Apply cleaning + modeling rules to raw Olist tables.

    Parameters
    ----------
    raw_tables : dict[str, pd.DataFrame]

    Returns
    -------
    dict[str, pd.DataFrame]
        Cleaned, analytics-ready tables
    """
    print("[TRANSFORM] Starting transformations...")

    out = {}

    # ------------------------------
    # DIM_CUSTOMER
    # ------------------------------
    customers = raw_tables["olist_customers_dataset"].copy()
    customers = clean_string_cols(customers, ["customer_city", "customer_state"])
    customers = customers.drop_duplicates(subset=["customer_id"])
    out["dim_customer"] = customers
    print("[TRANSFORM] dim_customer ✔")

    # DIM_SELLER
    sellers = raw_tables["olist_sellers_dataset"].copy()
    sellers = clean_string_cols(sellers, ["seller_city", "seller_state"])
    out["dim_seller"] = sellers
    print("[TRANSFORM] dim_seller ✔")

    # DIM_PRODUCT
    products = raw_tables["olist_products_dataset"].copy()
    out["dim_product"] = products
    print("[TRANSFORM] dim_product ✔")

    # DIM_GEOLOCATION
    geo = raw_tables["olist_geolocation_dataset"].copy()
    out["dim_geolocation"] = geo
    print("[TRANSFORM] dim_geolocation ✔")

    # FACT_ORDER
    orders = raw_tables["olist_orders_dataset"].copy()
    out["fact_orders"] = orders
    print("[TRANSFORM] fact_orders ✔")

    # FACT_ORDER_ITEM
    order_items = raw_tables["olist_order_items_dataset"].copy()
    out["fact_order_items"] = order_items
    print("[TRANSFORM] fact_order_items ✔")

    # FACT_PAYMENT
    payments = raw_tables["olist_order_payments_dataset"].copy()
    out["fact_payments"] = payments
    print("[TRANSFORM] fact_payments ✔")

    # FACT_REVIEW
    reviews = raw_tables["olist_order_reviews_dataset"].copy()
    out["fact_reviews"] = reviews
    print("[TRANSFORM] fact_reviews ✔")

    print(f"[TRANSFORM] Complete. Produced {len(out)} tables.")
    return out


if __name__ == "__main__":
    raise SystemExit("Run via pipeline.py")
