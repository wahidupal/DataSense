# 📊 Data Analyzer v4 – DuckDB SQL Lab

A modern, interactive data analysis web app built with **Streamlit**, **DuckDB**, and **Plotly**.  
This project is designed for fast data exploration, SQL-based analytics, and flexible visualization, all in one place.

The app allows you to upload a dataset, explore it visually, run powerful SQL queries using DuckDB, and instantly visualize query results.

---

## 🚀 Key Features

### 📂 Data Upload
- Upload **CSV** or **Excel** files
- Data is loaded into an **in-memory DuckDB table**
- No external database required

---

### 📌 Dataset Overview
- Preview the dataset
- Inspect column data types
- View missing value counts
- Quick dataset statistics (rows, columns, memory usage)

---

### 🔍 Raw Data Explorer
- Select and filter columns
- Preview data interactively
- Create visualizations directly from raw data:
  - Histogram
  - Bar chart
  - Box plot
  - Scatter plot
  - Line chart
- Built-in safety limit for large datasets (50k rows)

---

### 🧠 DuckDB SQL Lab
- Run SQL queries directly on your dataset
- Table name is always `data`
- Supports:
  - Filtering
  - Aggregations
  - Joins
  - Window functions
- Query results are displayed instantly
- Last queries are stored in session history

Example:
```sql
SELECT category, COUNT(*) AS total
FROM data
GROUP BY category
ORDER BY total DESC;
```
### 📈 Query-Based Visualization

- Visualize queried data only
- Choose chart types:
  - Bar
  - Line
  - Scatter
  - Histogram
- Select X and Y axes dynamically
- Designed to encourage SQL-first analysis

### 🧩 Design Philosophy

- SQL-first analytics using DuckDB
- In-memory processing for speed and simplicity
- Interactive visualizations with Plotly
- Session-based query history (no disk usage)
- Safe defaults to prevent memory issues

This app is ideal for:
- Data analysts
- Data science learners
- SQL practice
- Portfolio projects
- Quick exploratory data analysis

### 🛠 Tech Stack
- Streamlit – Web app framework
- DuckDB – Analytical SQL engine
- Pandas – Data handling
- Plotly – Interactive visualizations

### 📌 Notes
- Query and visualization results are capped at 50,000 rows for stability
- All data is processed locally in memory
- No external services or APIs are required
