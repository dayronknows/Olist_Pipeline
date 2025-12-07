# Notebooks – Olist ETL & Analytics

## Purpose

This folder contains Jupyter / Databricks notebooks used to:

- Validate that the **DuckDB warehouse** has been populated correctly.
- Perform **exploratory data analysis (EDA)** and build first-pass business insights.
- Demonstrate how the same data model can be queried from:
  - A **local development environment** (VS Code + Python virtual environment), and  
  - A **cloud analytics environment** (Databricks).

The notebooks are intentionally **separate** from the core ETL code (`etl/`), so the pipeline remains script-driven and reproducible, while this layer remains interactive and experiment-friendly.

---

## Notebook Inventory

Current notebooks in this folder:

1. `01_exploration.ipynb`  
   - First look at the DuckDB star schema.
   - Sanity checks on table row counts, key distributions, and null patterns.

2. `02_customer_behavior.ipynb`  
   - (Planned / in progress)  
   - Focused analysis of customer behavior, retention, and geographic patterns.

3. `duckdb_queries.sql.ipynb`  
   - Notebook wrapper for common SQL queries against `db/olist_dw.duckdb`.
   - Acts as a library of reusable analytics snippets.

On Databricks, these are mirrored by notebooks such as:

- `notebooks/01_exploration_db`  

which follow the same structure but are adapted to Databricks compute and workspace paths.

---

## Environments and Tooling

### 1. Local – VS Code + Jupyter

Local notebooks are developed and run in **Visual Studio Code** using:

- The **Python** and **Jupyter** extensions.
- The project’s virtual environment: `.venv`.

**Kernel selection**

From VS Code:

1. Open a notebook (e.g., `01_exploration.ipynb`).
2. In the top-right kernel picker, select the interpreter from `.venv`  
   (for example: `Python 3.12.1 ('.venv')`).

This ensures:

- The notebook uses the **same dependencies** as the ETL pipeline.
- Imports such as `duckdb` and `pandas` are available.

**Why VS Code and not PyCharm / others?**

- The project is **Git-centric**; VS Code integrates Git, terminals, and notebooks in a single workspace.
- The Jupyter experience is lightweight and closely aligned with how Databricks structures notebooks (cells, outputs, and Markdown).
- The rest of the project (ETL scripts, tests, `requirements.txt`) is Python-file heavy, which VS Code handles very well.
- PyCharm is an excellent alternative, but for this portfolio project the goal was:
  - Low setup friction,
  - Familiarity for most data / analytics teams,
  - And a UI that mirrors Databricks notebooks as closely as possible.

---

### 2. Databricks – Workspace Notebooks

The same analytical logic is mirrored into **Databricks notebooks** so that:

- Stakeholders can run analysis directly in the cloud.
- The project demonstrates realistic integration with a modern analytics platform.

**Key characteristics:**

- Location:  
  `Workspace / Users / <user_email> / Olist_Pipeline / notebooks/`
- Compute:  
  The notebooks are attached to **Serverless / General Compute**, **not** SQL Warehouses, because:
  - Python + DuckDB code must run on a general compute cluster.
  - SQL Warehouses are restricted to pure SQL cells.

---

## Connecting to DuckDB

All notebooks read from the DuckDB warehouse created by the ETL pipeline:

```text
db/olist_dw.duckdb
````

### Local (VS Code)

```python
import duckdb
import pandas as pd

con = duckdb.connect("db/olist_dw.duckdb")

customers = con.sql("SELECT * FROM dim_customer LIMIT 5").df()
customers.head()
```

### Databricks

In Databricks, the notebook lives under `notebooks/` and the DuckDB file is stored in a sibling `db/` folder in the workspace. The relative path becomes:

```python
import duckdb
import pandas as pd

con = duckdb.connect("../db/olist_dw.duckdb")

customers = con.sql("SELECT * FROM dim_customer LIMIT 5").df()
display(customers)
```

This design keeps the **warehouse file portable**:

* Locally: `db/olist_dw.duckdb` is created by running `etl/pipeline.py`.
* In Databricks: the same file is uploaded into `Olist_Pipeline/db/` and referenced via a relative path from notebooks.

---

## Running the Notebooks

### A. Local – VS Code

1. Ensure the ETL has been run and the DuckDB file exists:

   ```bash
   python etl/pipeline.py
   # creates / refreshes db/olist_dw.duckdb
   ```

2. Open `notebooks/01_exploration.ipynb` in VS Code.

3. Select the `.venv` kernel.

4. Run cells sequentially (Shift+Enter) or use **Run All**.

---

### B. Databricks

1. In Databricks, navigate to:
   `Workspace → Users → <user_email> → Olist_Pipeline`.

2. Verify that the following exists:

   * `db/olist_dw.duckdb` (uploaded DuckDB file).
   * `notebooks/01_exploration_db`.

3. Open `01_exploration_db`.

4. Attach compute:

   * Top-left dropdown → choose a **Serverless** or **General Compute** cluster (not SQL Warehouse).

5. Install dependencies once per cluster (first cell):

   ```python
   %pip install duckdb pandas
   ```

   After the first run, **restart the kernel** so the new packages are available.

6. Run the notebook cells. They will connect to:

   ```python
   "../db/olist_dw.duckdb"
   ```

   and read the same tables produced by the ETL pipeline.

---

## Troubleshooting Log

This section documents key issues encountered while wiring notebooks to the DuckDB warehouse, and how they were resolved.

### 1. `ModuleNotFoundError: No module named 'duckdb'` (Databricks)

**Symptom**

A Python Databricks notebook raised:

```text
ModuleNotFoundError: No module named 'duckdb'
```

**Root Cause**

The default Databricks runtime did not include the `duckdb` library.

**Resolution**

1. At the top of the notebook, run:

   ```python
   %pip install duckdb pandas
   ```

2. Once installation completes, restart the notebook kernel (Databricks usually prompts for this).

3. Re-run the notebook.

---

### 2. “Unsupported cell during execution. SQL warehouses only support executing SQL cells.”

**Symptom**

Running Python code in a notebook attached to a **SQL Warehouse** produced an error indicating only SQL cells were allowed.

**Root Cause**

SQL Warehouses are designed for **SQL-only** workloads and do not execute Python.

**Resolution**

* Re-attach the notebook to a **Serverless / General Compute** cluster instead of a SQL Warehouse.
* After re-attaching, Python and `%pip` cells run as expected.

---

### 3. `IO Error: Cannot open file '../db/olist_dw.duckdb'`

**Symptom**

Databricks raised an `IOError` when trying to connect to DuckDB:

```text
IO Error: Cannot open file "../db/olist_dw.duckdb": No such file or directory
```

**Root Cause**

The DuckDB file was present locally but had not yet been uploaded to the Databricks `db/` folder, or the relative path from the notebook was incorrect.

**Resolution**

1. In Databricks:

   * Navigate to `Workspace → Users → <user_email> → Olist_Pipeline`.
   * Create a `db/` folder if it does not exist.
   * Upload `olist_dw.duckdb` into that folder.

2. Confirm the relative path from the notebook:

   * Notebook path: `Olist_Pipeline/notebooks/01_exploration_db`
   * DuckDB path:   `Olist_Pipeline/db/olist_dw.duckdb`
   * Connection string:

     ```python
     con = duckdb.connect("../db/olist_dw.duckdb")
     ```

---

### 4. Git and `.gitignore` Considerations

During setup, `.gitignore` initially excluded entire data directories:

```text
data_raw/
data_processed/
db/
```

This ensures large or regenerable data files are not committed.

However, for Databricks integration we needed to **decide whether to track the DuckDB file**:

* For a pure-ETL repository, the warehouse can be treated as a build artifact and excluded.
* For a portfolio / demo repository, including a small DuckDB file can make the project easier to run without reprocessing.

The current approach is:

* Keep **raw and processed CSVs** out of Git.
* Store the DuckDB file either:

  * As a local artifact built by running `etl/pipeline.py`, or
  * Uploaded manually to Databricks.
* The `.gitignore` file has been adjusted so this behavior can be changed easily (comment/uncomment the `db/` line depending on the desired strategy).

---

## Interpretation Philosophy

The notebooks are not meant to replace the ETL pipeline. Instead, they:

* Serve as **validation tools** for the warehouse (e.g., checking keys, row counts, logic).
* Provide a **narrative, portfolio-friendly view** of the analysis process.
* Demonstrate that the project can operate both:

  * As a local, file-based analytics stack (Python + DuckDB), and
  * Inside a modern cloud workspace (Databricks).

Future notebooks will extend this layer with:

* Customer segmentation and lifetime value analysis.
* Order funnel and conversion analysis.
* Visualizations for executive-level storytelling (e.g., Power BI / Databricks SQL dashboard alignment).

```
::contentReference[oaicite:0]{index=0}
```
