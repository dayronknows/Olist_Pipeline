# Olist ETL Pipeline (DuckDB Warehouse)

## Overview

This project is an end-to-end ETL pipeline built on the  
[Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

**Goal:** Convert messy transactional CSVs into a clean, analytics-ready **star schema** inside a **DuckDB** data warehouse file.

The entire pipeline is fully reproducible and runs with a **single command**.

---

## Architecture

### **Source Layer**
- Kaggle dataset with multiple CSVs:
  - customers
  - sellers
  - products
  - geolocation
  - orders
  - items
  - payments
  - reviews

Files are downloaded automatically via `kagglehub` and stored in:

```

data_raw/

```

---

### **Pipeline Stages**

#### **1. Extract** (`etl/extract.py`)
- Uses `kagglehub` to download the latest Olist dataset  
- Copies all CSVs into a local **raw zone** (`data_raw/`)
- Ensures repeatability and stable inputs for transformations

---

#### **2. Transform** (`etl/transform.py`)
Responsible for cleaning data and shaping the star schema.

- Cleans text fields (city/state names)
- Removes duplicates where appropriate
- Converts data types (dates, numerics)
- Standardizes column names
- Builds the following **dimension tables**:

  - `dim_customer`  
  - `dim_seller`  
  - `dim_product`  
  - `dim_geolocation`

- And the following **fact tables**:

  - `fact_orders`
  - `fact_order_items`
  - `fact_payments`
  - `fact_reviews`

Outputs a dictionary:

```

{
"dim_customer": DataFrame,
"dim_seller": DataFrame,
"dim_product": DataFrame,
...
"fact_reviews": DataFrame
}

```

---

#### **3. Load** (`etl/load.py`)
Loads each table into a DuckDB warehouse file:

```

db/olist_dw.duckdb

````

For each table, executes:

```sql
CREATE OR REPLACE TABLE <table_name> AS
SELECT * FROM df_temp;
````

Features:

* Overwrites existing tables for consistent reproducibility
* Logs row counts for validation
* Closes the DB connection cleanly

---

#### **4. Orchestration** (`etl/pipeline.py`)

Runs the entire ETL in sequence:

```
extract_raw_files() → transform_all() → load_to_duckdb()
```

* Provides clean logs at each step
* One command to rebuild the warehouse
* Future-friendly design if lifted into Airflow or ADF

---

### **Warehouse Layer**

* Embedded OLAP database: `db/olist_dw.duckdb`

* Fully portable file — can be opened with:

  * DuckDB CLI
  * Python (`duckdb.connect("db/olist_dw.duckdb")`)
  * DBeaver / DuckDB Explorer

* Star schema designed for analytics:

  * Fast aggregations
  * Minimal joins
  * BI-ready tables

---

## Tech Stack

* **Python** — ETL logic
* **pandas** — cleaning & transformation
* **DuckDB** — analytics warehouse
* **kagglehub** — dataset download
* **requirements.txt** — dependency management

---

## How to Run the Pipeline Locally

### **1. Clone the Repository**

```bash
git clone https://github.com/<your-username>/olist-etl-project.git
cd olist-etl-project
```

### **2. Create a Virtual Environment**

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate      # Mac/Linux
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Run the Pipeline**

```bash
python etl/pipeline.py
```

This performs:

* Extract → download into `data_raw/`
* Transform → clean into DataFrames
* Load → populate `db/olist_dw.duckdb`

---

## Inspecting the Warehouse

### **Python**

```python
import duckdb
con = duckdb.connect("db/olist_dw.duckdb")
con.execute("SELECT * FROM dim_customer LIMIT 10").fetchdf()
```

### **DuckDB CLI**

```bash
duckdb db/olist_dw.duckdb
```

### **GUI Tools**

* DBeaver
* DuckDB Explorer
* DataGrip (with DuckDB plugin)

---

## Example Analytics Queries

### Top 10 Cities by Customer Count

```sql
SELECT customer_city, COUNT(*) AS customers
FROM dim_customer
GROUP BY customer_city
ORDER BY customers DESC
LIMIT 10;
```

### Monthly Order Volume

```sql
SELECT
  date_trunc('month', order_purchase_timestamp) AS month,
  COUNT(*) AS total_orders
FROM fact_orders
GROUP BY month
ORDER BY month;
```

---

## Project Roadmap

Planned upgrades:

* Add incremental pipelines
* Add dbt transformations
* Add Power BI dashboard layer
* Add Azure version using ADF + Synapse
* Add automated data quality tests (pytest + Great Expectations)
* Add scheduling with Prefect

---

## License

MIT License — free to use, modify, and learn from.

```

---

# ✅ Next Step
If you want, I can now:

### 🔹 Write the **portfolio case-study page** for your website  
### 🔹 Generate a **schema diagram (ASCII or PNG)**  
### 🔹 Add a **“Why DuckDB for this project?”** section  
### 🔹 Add screenshots and placeholders  

Just say **“case study page next”** or whichever piece you want.
```
