# Olist ETL Pipeline – Local Development + Databricks Analytics

## Overview

This repository contains an end-to-end ETL pipeline built on the  
[Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

The project has **two complementary environments**:

1. **Local ETL & development** (Python, DuckDB, VS Code)  
2. **Cloud analytics workspace** (Databricks notebooks connected to the same DuckDB warehouse)

**Objective**

- Transform raw Olist CSV files into a **star-schema warehouse** in DuckDB  
- Keep the pipeline **fully reproducible** from a clean clone  
- Demonstrate the ability to work in both **traditional local tooling** and a **modern data platform (Databricks)**

---

## Architecture

### High-Level Flow

1. **Raw data**: Kaggle Olist CSVs → `data_raw/`
2. **ETL pipeline** (local Python modules in `etl/`)  
3. **Warehouse**: DuckDB file → `db/olist_dw.duckdb`
4. **Analytics**:
   - Local Jupyter notebook in `notebooks/`
   - Mirrored notebook in Databricks, connecting to the same schema

```text
Kaggle (CSVs)
   │
   ▼
data_raw/          (raw zone)
   │
   ▼
etl/               (Python: extract → transform → load)
   │
   ▼
db/olist_dw.duckdb (DuckDB star schema)
   │
   ├─ Local notebooks/ (exploration / validation)
   └─ Databricks notebooks (cloud analytics)
````

---

## Repository Structure

```text
olist_etl_project/
│
├─ etl/                    # ETL modules (pure Python)
│   ├─ extract.py
│   ├─ transform.py
│   └─ load.py
│
├─ data_raw/               # Raw CSVs from Kaggle (ignored by git)
├─ data_processed/         # (Optional) intermediate outputs (ignored by git)
│
├─ db/
│   └─ olist_dw.duckdb     # DuckDB warehouse file
│
├─ notebooks/
│   ├─ 01_exploration.ipynb        # Local exploratory analysis
│   └─ 02_customer_behavior.ipynb  # Additional analyses (optional)
│
├─ tests/                  # Placeholder for unit / data-quality tests
├─ requirements.txt        # Python dependencies
└─ README.md               # Project documentation
```

---

## ETL Pipeline

### 1. Extract – `etl/extract.py`

**Purpose:** Create a reproducible **raw zone** with the Olist dataset.

* Downloads the Olist dataset (e.g. via `kagglehub` or pre-placed CSVs)
* Copies all CSVs into:

```text
data_raw/
    olist_customers_dataset.csv
    olist_geolocation_dataset.csv
    olist_order_items_dataset.csv
    olist_order_payments_dataset.csv
    olist_order_reviews_dataset.csv
    olist_orders_dataset.csv
    olist_products_dataset.csv
    olist_sellers_dataset.csv
    product_category_name_translation.csv
```

* Guarantees that downstream transformations always start from a known, consistent input.

---

### 2. Transform – `etl/transform.py`

**Purpose:** Clean and model the source data into an analytics-friendly star schema.

Key responsibilities:

* Standardise text fields (cities, states, categories)
* Enforce data types (dates, numerics, identifiers)
* Handle duplicates and basic data-quality issues
* Derive surrogate keys and foreign-key relationships

Creates the following **dimension tables**:

* `dim_customer`
* `dim_seller`
* `dim_product`
* `dim_geolocation`

And the following **fact tables**:

* `fact_orders`
* `fact_order_items`
* `fact_payments`
* `fact_reviews`

The module returns an in-memory dictionary of DataFrames:

```python
{
    "dim_customer": df_dim_customer,
    "dim_seller": df_dim_seller,
    "dim_product": df_dim_product,
    "dim_geolocation": df_dim_geolocation,
    "fact_orders": df_fact_orders,
    "fact_order_items": df_fact_order_items,
    "fact_payments": df_fact_payments,
    "fact_reviews": df_fact_reviews,
}
```

---

### 3. Load – `etl/load.py`

**Purpose:** Persist the star schema into a **DuckDB warehouse file**.

Target file:

```text
db/olist_dw.duckdb
```

For each DataFrame in the dictionary above, the loader:

1. Opens a DuckDB connection to `db/olist_dw.duckdb`
2. Registers the DataFrame as a temporary table
3. Executes:

```sql
CREATE OR REPLACE TABLE <table_name> AS
SELECT * FROM df_temp;
```

Design decisions:

* **Idempotent loads**: `CREATE OR REPLACE` ensures the warehouse can be rebuilt from scratch without manual cleanup.
* **Logging**: row counts per table can be logged to verify completeness.
* **Clean teardown**: the database connection is always closed explicitly.

---

### 4. Orchestration – `etl/pipeline.py`

**Purpose:** Provide a **single entry point** to rebuild the warehouse.

Execution order:

```python
extract_raw_files()
tables = transform_all()
load_to_duckdb(tables)
```

Benefits:

* One command sets up the entire environment.
* Easy to lift into scheduled orchestration tools later (e.g. Airflow, ADF, Prefect).
* Clear separation of concerns between extract, transform, and load.

---

## Warehouse Layer – DuckDB

The central warehouse is a single DuckDB file:

```text
db/olist_dw.duckdb
```

Characteristics:

* **Embedded OLAP database** optimised for analytical workloads.
* **File-based and portable**:

  * Can be committed to Git for small demo projects or distributed together with the repo.
  * Can be opened from:

    * Python: `duckdb.connect("db/olist_dw.duckdb")`
    * DuckDB CLI
    * Desktop tools such as DBeaver or DuckDB Explorer.

Reasons for choosing DuckDB:

* Excellent performance on columnar analytics for medium-scale datasets like Olist.
* Zero-infrastructure: no server to manage, ideal for portfolio and local experimentation.
* Integrates naturally with both **pandas** and **SQL** workflows.

---

## Development Environment & Tooling

### Local Development – Why VS Code?

The local development environment is based on:

* **Python 3.12+**
* **Virtual environment** (`.venv/`)
* **VS Code** as the primary IDE

**Reasons for using VS Code:**

* Strong support for **Python** and **Jupyter notebooks** via extensions.
* Built-in **Git integration** (staging, commits, diffs) tightly aligned to how this repository is managed.
* Lightweight and highly configurable; suitable for both ETL scripting and exploratory data analysis.
* Cross-platform and widely adopted in data engineering and analytics teams.

**Why not PyCharm or other IDEs in this project?**

PyCharm and similar IDEs are excellent, especially for large application codebases.
For this project, VS Code was chosen because:

* The work is a blend of **scripts + notebooks**, where VS Code’s Jupyter experience is very smooth.
* The environment needed to match how many modern data teams actually work: Git + notebooks + Python scripts in a single interface.
* VS Code is easy to mirror conceptually with Databricks notebooks, making it simpler to explain in a portfolio context.

> The choice is not about one tool being objectively “better”, but about aligning the project with a realistic, productivity-focused data-engineering workflow.

---

### Databricks Workspace – What’s Different from VS Code?

Databricks introduces a **hosted compute and notebook environment** on top of the code in this repo.

Key concepts:

* **Workspace**: a folder structure in the Databricks UI where repos, notebooks, and data assets live (`Users/<email>/Olist_Pipeline/…`).
* **Databricks Repos**: a Git-backed copy of this GitHub repository inside the workspace, kept in sync via the Databricks UI.
* **Notebooks**: interactive documents similar to Jupyter notebooks, supporting Python, SQL, and other languages.
* **Compute**:

  * **All-purpose / Serverless compute**: used here to run Python + DuckDB inside the notebook.
  * **SQL Warehouses**: optimised for SQL only. They do not execute Python cells, which is why this project uses **serverless general compute** for analytic notebooks.

How it differs from VS Code:

| Aspect                | VS Code (Local)                         | Databricks (Cloud)                                         |
| --------------------- | --------------------------------------- | ---------------------------------------------------------- |
| Execution environment | Local machine, local Python interpreter | Managed clusters / serverless compute                      |
| Notebook type         | Jupyter (`.ipynb`)                      | Databricks notebooks (web UI)                              |
| Storage path          | Local filesystem (`db/olist_dw.duckdb`) | Workspace path (`/Workspace/Users/.../Olist_Pipeline/db/`) |
| Dependencies          | Installed via `pip` into `.venv/`       | Installed via `%pip` cells into the attached cluster       |
| Git integration       | Native Git / CLI within VS Code         | Databricks Repos with GitHub integration                   |

In practice:

* The **ETL pipeline** runs locally and writes `db/olist_dw.duckdb`.
* This file is then **uploaded to the Databricks `db/` folder** or committed and pulled via Databricks Repos, so analytic notebooks can connect to the same warehouse.

---

## Local vs Databricks Notebooks

### Local Notebook – `notebooks/01_exploration.ipynb`

Used to:

* Verify that tables in `db/olist_dw.duckdb` load correctly.
* Prototype analysis queries with `duckdb` + `pandas`.
* Serve as a template for the Databricks notebook.

Typical pattern:

```python
import duckdb
import pandas as pd

con = duckdb.connect("db/olist_dw.duckdb")
customers = con.sql("SELECT * FROM dim_customer LIMIT 5").df()
customers.head()
```

---

### Databricks Notebook – `01_exploration_db`

Mirrors the logic of the local exploration notebook, but runs inside Databricks.

Core connection pattern:

```python
import duckdb
import pandas as pd

# Path is relative to the Databricks workspace repo root
con = duckdb.connect("../db/olist_dw.duckdb")

customers = con.sql("SELECT * FROM dim_customer LIMIT 5").df()
display(customers)
```

Important points:

* The relative path `../db/olist_dw.duckdb` is **relative to the notebook’s folder inside the Databricks repo**, not to your local filesystem.
* Before running the notebook, ensure that `olist_dw.duckdb` exists in the `db/` folder in the Databricks workspace (either via Git sync or manual upload).
* Dependencies such as `duckdb` are installed via a cell:

  ```python
  %pip install duckdb
  ```

  and may require a kernel restart the first time.

---

## Version Control & Repository Hygiene

### What is `__pycache__` and Why Ignore It?

When Python imports modules, it generates compiled bytecode files (`*.pyc`) in `__pycache__/` directories.

* These files:

  * Are **machine-generated**, not hand-written code.
  * Are specific to a given Python version and environment.
  * Do **not** need to be tracked in Git.

Accordingly, the `.gitignore` includes:

```gitignore
# Python
__pycache__/
*.pyc

# Virtual env
.venv/
venv/

# IDEs
.idea/
.vscode/

# Data folders (local only)
data_raw/
data_processed/

# Databricks export bundles
*.dbc
```

### Handling Large / Local-Only Artifacts

* `data_raw/` and `data_processed/` can be large and are **environment-specific**, so they are ignored.
* The DuckDB file (`db/olist_dw.duckdb`) is small enough for this project to be:

  * **Kept locally** for development, and
  * **Copied or uploaded to Databricks** for analytics.

Git errors such as `Permission denied` when trying to `git add db/olist_dw.duckdb` usually indicate that a process (e.g., Python or DuckDB) still has the file open. Closing the connection or stopping the interpreter resolves this.

---

## Troubleshooting & Lessons Learned

This project intentionally documents the main issues encountered and how they were resolved.
These are valuable as a reference and demonstrate practical debugging in a realistic workflow.

### 1. Git Authentication – “Invalid username or token”

**Symptom**

```text
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed for 'https://github.com/...'
```

**Cause**

GitHub no longer allows password authentication over HTTPS; a **Personal Access Token (PAT)** is required.

**Resolution**

* Generated a PAT in GitHub with appropriate scopes (repo).

* Configured Git to use the Windows Credential Manager so the token is stored securely:

  ```bash
  git config --global credential.helper manager
  ```

* Pushed again, and credentials were stored for subsequent operations.

---

### 2. Unwanted Files in Git – `__pycache__`, `.idea`, `data_raw/`

**Symptom**

Git status showed many machine-generated or environment-specific files as modified or untracked.

**Cause**

Initial `.gitignore` was incomplete.

**Resolution**

* Added entries to `.gitignore` for:

  * Python caches (`__pycache__/`, `*.pyc`)
  * IDE folders (`.idea/`, `.vscode/`)
  * Data folders (`data_raw/`, `data_processed/`)

* Removed already-tracked files from the index (without deleting them locally):

  ```bash
  git rm -r --cached data_raw
  git rm -r --cached data_processed
  git rm -r --cached .idea
  ```

* Committed the cleaned-up repository.

---

### 3. Databricks: “SQL warehouses only support executing SQL cells”

**Symptom**

Python cells in a Databricks notebook failed with an error indicating that **SQL warehouses only support SQL**.

**Cause**

The notebook was attached to a **SQL Warehouse**, which is intended purely for SQL, not Python.

**Resolution**

* Switched the notebook to **Serverless / All-purpose compute (General Compute)**.
* Re-ran the notebook; Python and DuckDB executed correctly.

---

### 4. Databricks: `ModuleNotFoundError: No module named 'duckdb'`

**Symptom**

The first run in Databricks produced:

```text
ModuleNotFoundError: No module named 'duckdb'
```

**Cause**

The cluster’s Python environment did not yet have `duckdb` installed.

**Resolution**

* Added a cell at the top of the notebook:

  ```python
  %pip install duckdb
  ```

* After installation, restarted the kernel when prompted.

* Subsequent runs imported `duckdb` successfully.

---

### 5. Databricks: `IO Error: Cannot open file "../db/olist_dw.duckdb"`

**Symptom**

The Databricks notebook attempted to connect to DuckDB with:

```python
con = duckdb.connect("../db/olist_dw.duckdb")
```

but raised an `IO Error: Cannot open file` pointing to a workspace path.

**Cause**

* The DuckDB file did not yet exist in the Databricks workspace at the expected location, or
* The path was interpreted relative to the local filesystem instead of the repo root.

**Resolution**

1. Created a `db/` folder under the `Olist_Pipeline` repo inside the Databricks workspace.

2. Uploaded or synchronised `olist_dw.duckdb` into that folder.

3. Confirmed the relative path from the notebook to the DB file:

   ```text
   /Workspace/Users/<user>/Olist_Pipeline/notebooks/01_exploration_db
   /Workspace/Users/<user>/Olist_Pipeline/db/olist_dw.duckdb
   ```

   → `../db/olist_dw.duckdb` is the correct relative reference.

4. Re-ran the notebook; the connection succeeded and queries returned results.

---

### 6. General: “Permission denied” when `git add db/olist_dw.duckdb`

**Symptom**

Git reported:

```text
error: open("db/olist_dw.duckdb"): Permission denied
fatal: adding files failed
```

**Cause**

The DuckDB file was still open in a running Python process (local notebook / terminal), locking it for writes.

**Resolution**

* Closed the Python session or kernel using the DB.
* Ensured no other tools (e.g. DuckDB CLI) were holding locks.
* Re-ran `git add`, which then succeeded.

---

## How to Run the Pipeline Locally

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Olist_Pipeline.git
cd Olist_Pipeline
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Mac/Linux
# source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Execute the ETL Pipeline

```bash
python etl/pipeline.py
```

This will:

1. Populate `data_raw/` with the Olist CSVs.
2. Transform them into star-schema tables.
3. Write all dimension and fact tables into `db/olist_dw.duckdb`.

---

## Inspecting the Warehouse Locally

### Via Python

```python
import duckdb
con = duckdb.connect("db/olist_dw.duckdb")

con.sql("SELECT * FROM dim_customer LIMIT 10").fetchdf()
```

### Via DuckDB CLI

```bash
duckdb db/olist_dw.duckdb
```

### Via GUI Tools

* DBeaver
* DuckDB Explorer
* DataGrip (with DuckDB plugin)

---

## Using the Project in Databricks

High-level steps:

1. **Create a Databricks Repo**

   * In the Databricks UI, create a Repo pointing at the GitHub repository.
   * This will create a folder such as:

     ```text
     /Workspace/Users/<user>/Olist_Pipeline/
     ```

2. **Ensure the DuckDB File is Present**

   * Either:

     * Commit `db/olist_dw.duckdb` to Git and pull it into the Databricks repo, or
     * Manually upload the file into `/Workspace/Users/<user>/Olist_Pipeline/db/`.

3. **Attach the Notebook to Compute**

   * Open `notebooks/01_exploration_db` in Databricks.
   * Attach it to a **Serverless / All-purpose compute** cluster, not a SQL Warehouse.

4. **Install Dependencies (First Run)**

   * At the top of the notebook, run:

     ```python
     %pip install duckdb
     ```

   * Restart the kernel if prompted.

5. **Run the Exploration Notebook**

   * The notebook will:

     ```python
     import duckdb
     import pandas as pd

     con = duckdb.connect("../db/olist_dw.duckdb")
     customers = con.sql("SELECT * FROM dim_customer LIMIT 5").df()
     display(customers)
     ```

   * From there, additional analytics (e.g. churn, cohort analysis, revenue trends) can be built directly in Databricks.

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

These queries can be executed:

* Directly in DuckDB (CLI or local notebook), or
* Through Databricks notebooks using `con.sql(...).df()`.

---

## Roadmap / Possible Extensions

Future enhancements that would naturally extend this project:

* Add **incremental loading** rather than full rebuilds.
* Introduce **data-quality tests** (e.g. with `pytest` and Great Expectations).
* Add a **dbt layer** for declarative transformations on top of DuckDB.
* Build a **Power BI** or **Databricks SQL** dashboard on top of the warehouse.
* Migrate the ETL orchestration into **Prefect**, **Airflow**, or **Azure Data Factory** for scheduling and monitoring.

---

## License

MIT License – you are free to use, modify, and learn from this project.


