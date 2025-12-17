import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Data Analyzer v3 – SQL Lab",
    layout="wide"
)

st.title("🦆 Data Analyzer v3 – DuckDB SQL Lab")
st.caption("Upload data, query with SQL, and visualize results")

# -----------------------------
# Session state initialization
# -----------------------------
if "duckdb_con" not in st.session_state:
    st.session_state.duckdb_con = duckdb.connect(database=":memory:")

if "df" not in st.session_state:
    st.session_state.df = None

if "sql_result" not in st.session_state:
    st.session_state.sql_result = None

if "sql_query" not in st.session_state:
    st.session_state.sql_query = "SELECT * FROM data LIMIT 100"

# -----------------------------
# Helper functions
# -----------------------------


def register_dataframe(df: pd.DataFrame):
    con = st.session_state.duckdb_con

    # Safely unregister if it already exists
    try:
        con.unregister("data")
    except Exception:
        pass

    con.register("data", df)


def suggest_charts(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    suggestions = []

    if len(numeric_cols) >= 2:
        suggestions.append(("Scatter", numeric_cols[0], numeric_cols[1]))

    if categorical_cols and numeric_cols:
        suggestions.append(("Bar", categorical_cols[0], numeric_cols[0]))

    if len(numeric_cols) == 1:
        suggestions.append(("Histogram", numeric_cols[0], None))

    return suggestions


# -----------------------------
# Sidebar – File upload
# -----------------------------
st.sidebar.header("📂 Data Upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state.df = df
        register_dataframe(df)

        st.sidebar.success(
            f"Loaded {df.shape[0]} rows × {df.shape[1]} columns")

    except Exception as e:
        st.sidebar.error(f"Failed to load file: {e}")

# -----------------------------
# If no data loaded, stop here
# -----------------------------
if st.session_state.df is None:
    st.info("👈 Upload a CSV or Excel file to get started")
    st.stop()

df = st.session_state.df

# -----------------------------
# Tabs
# -----------------------------
sql_tab, viz_tab, preview_tab = st.tabs(
    ["🦆 SQL Lab", "📊 Visualize Results", "📄 Data Preview"]
)

# -----------------------------
# SQL LAB TAB
# -----------------------------
with sql_tab:
    st.subheader("🦆 DuckDB SQL Lab")
    st.caption("Table name: `data`")

    col_editor, col_templates = st.columns([3, 1])

    with col_templates:
        st.markdown("### SQL Templates")

        if st.button("Preview"):
            st.session_state.sql_query = "SELECT * FROM data LIMIT 100"

        if st.button("Describe"):
            st.session_state.sql_query = "DESCRIBE data"

        if st.button("Count Rows"):
            st.session_state.sql_query = "SELECT COUNT(*) AS total_rows FROM data"

        if st.button("Group By"):
            st.session_state.sql_query = """
SELECT
    column_name,
    COUNT(*) AS total
FROM data
GROUP BY column_name
ORDER BY total DESC
"""

    with col_editor:
        sql_query = st.text_area(
            "SQL Editor",
            value=st.session_state.sql_query,
            height=220
        )

        run_query = st.button("▶ Run Query")

    if run_query:
        try:
            con = st.session_state.duckdb_con
            result = con.execute(sql_query).df()

            st.session_state.sql_result = result
            st.session_state.sql_query = sql_query

            st.success(f"Query executed successfully – {len(result)} rows")

        except Exception as e:
            st.session_state.sql_result = None
            st.error(f"SQL Error: {e}")

    if st.session_state.sql_result is not None:
        st.markdown("### Result Preview")

        st.dataframe(
            st.session_state.sql_result,
            use_container_width=True,
            height=350
        )

        st.download_button(
            "⬇ Download Result as CSV",
            st.session_state.sql_result.to_csv(index=False),
            file_name="sql_result.csv",
            mime="text/csv"
        )

# -----------------------------
# VISUALIZATION TAB
# -----------------------------
with viz_tab:
    st.subheader("📊 Visualize Query Results")

    if st.session_state.sql_result is None:
        st.info("Run a SQL query first to visualize results.")
    else:
        df_plot = st.session_state.sql_result
        suggestions = suggest_charts(df_plot)

        if not suggestions:
            st.warning("No suitable chart suggestions found.")
        else:
            chart_type, x, y = suggestions[0]
            st.caption(f"Suggested chart: {chart_type}")

            if chart_type == "Scatter":
                fig = px.scatter(df_plot, x=x, y=y)
            elif chart_type == "Bar":
                fig = px.bar(df_plot, x=x, y=y)
            elif chart_type == "Histogram":
                fig = px.histogram(df_plot, x=x)

            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DATA PREVIEW TAB
# -----------------------------
with preview_tab:
    st.subheader("📄 Raw Data Preview")

    rows_per_page = 50
    if "page" not in st.session_state:
        st.session_state.page = 0

    start = st.session_state.page * rows_per_page
    end = start + rows_per_page

    st.dataframe(df.iloc[start:end], use_container_width=True)

    col_prev, col_next = st.columns(2)

    with col_prev:
        if st.button("⬅ Previous") and st.session_state.page > 0:
            st.session_state.page -= 1

    with col_next:
        if st.button("Next ➡") and end < len(df):
            st.session_state.page += 1
