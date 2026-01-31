import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px
from datetime import datetime

# -------------------------
# App Config
# -------------------------
st.set_page_config(
    page_title="Data Analyzer v3 – DuckDB SQL Lab",
    layout="wide"
)

st.title("📊 Data Analyzer v4 – DuckDB SQL Lab")

MAX_VIZ_ROWS = 50_000

# -------------------------
# Session State Init
# -------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "con" not in st.session_state:
    st.session_state.con = duckdb.connect(database=":memory:")

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "last_query_result" not in st.session_state:
    st.session_state.last_query_result = None


# -------------------------
# Sidebar – File Upload
# -------------------------
st.sidebar.header("📂 Data Source")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state.df = df

        con = st.session_state.con
        con.execute("DROP TABLE IF EXISTS data")
        con.register("data", df)

        st.sidebar.success("Dataset loaded successfully")

    except Exception as e:
        st.sidebar.error(f"Failed to load file: {e}")


# -------------------------
# Sidebar – Dataset Info
# -------------------------
if st.session_state.df is not None:
    df = st.session_state.df
    st.sidebar.subheader("📄 Dataset Info")
    st.sidebar.write(f"Rows: {len(df):,}")
    st.sidebar.write(f"Columns: {df.shape[1]}")
    st.sidebar.write(
        f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")


# -------------------------
# Tabs
# -------------------------
tabs = st.tabs([
    "📌 Overview",
    "🔍 Raw Data Explorer",
    "🧠 DuckDB SQL Lab",
    "📈 Query Visualization"
])

# ======================================================
# TAB 1 — OVERVIEW
# ======================================================
with tabs[0]:
    if st.session_state.df is None:
        st.info("Upload a dataset to begin.")
    else:
        df = st.session_state.df

        st.subheader("Dataset Preview")
        st.dataframe(df.head(100))

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Column Types")
            st.dataframe(df.dtypes.astype(str))

        with col2:
            st.subheader("Missing Values")
            st.dataframe(df.isnull().sum())


# ======================================================
# TAB 2 — RAW DATA EXPLORER
# ======================================================
with tabs[1]:
    if st.session_state.df is None:
        st.info("Upload a dataset to explore.")
    else:
        df = st.session_state.df

        st.subheader("Filter Columns")
        selected_cols = st.multiselect(
            "Choose columns",
            df.columns,
            default=list(df.columns)
        )

        filtered_df = df[selected_cols]
        st.dataframe(filtered_df.head(500))

        st.subheader("Raw Data Visualization")

        chart_type = st.selectbox(
            "Chart Type",
            ["Histogram", "Bar", "Box", "Scatter", "Line"]
        )

        x_col = st.selectbox("X axis", filtered_df.columns)
        y_col = None

        if chart_type in ["Scatter", "Line", "Bar", "Box"]:
            y_col = st.selectbox("Y axis", filtered_df.columns)

        if len(filtered_df) > MAX_VIZ_ROWS:
            st.warning(
                "Too many rows for visualization. Apply filters or use SQL.")
        else:
            if chart_type == "Histogram":
                fig = px.histogram(filtered_df, x=x_col)
            elif chart_type == "Bar":
                fig = px.bar(filtered_df, x=x_col, y=y_col)
            elif chart_type == "Box":
                fig = px.box(filtered_df, x=x_col, y=y_col)
            elif chart_type == "Scatter":
                fig = px.scatter(filtered_df, x=x_col, y=y_col)
            else:
                fig = px.line(filtered_df, x=x_col, y=y_col)

            st.plotly_chart(fig, use_container_width=True)


# ======================================================
# TAB 3 — DUCKDB SQL LAB
# ======================================================
with tabs[2]:
    if st.session_state.df is None:
        st.info("Upload a dataset to run SQL queries.")
    else:
        st.subheader("SQL Editor")

        query = st.text_area(
            "Write SQL (table name: data)",
            height=150,
            placeholder="SELECT * FROM data LIMIT 10;"
        )

        if st.button("▶ Run Query"):
            try:
                result_df = st.session_state.con.execute(query).fetchdf()

                if len(result_df) > MAX_VIZ_ROWS:
                    st.warning("Query result too large. Limited to 50k rows.")
                    result_df = result_df.head(MAX_VIZ_ROWS)

                st.session_state.last_query_result = result_df

                st.session_state.query_history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "query": query,
                    "rows": len(result_df),
                    "data": result_df
                })

                st.success("Query executed successfully")
                st.dataframe(result_df)

            except Exception as e:
                st.error(f"Query failed: {e}")

        if st.session_state.query_history:
            st.subheader("Query History")
            for i, q in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                st.markdown(
                    f"**{i}. [{q['timestamp']}] Rows: {q['rows']}**\n\n```sql\n{q['query']}\n```"
                )


# ======================================================
# TAB 4 — QUERY VISUALIZATION
# ======================================================
with tabs[3]:
    result_df = st.session_state.last_query_result

    if result_df is None:
        st.info("Run a SQL query first.")
    else:
        st.subheader("Visualize Query Result")

        chart_type = st.selectbox(
            "Chart Type",
            ["Bar", "Line", "Scatter", "Histogram"]
        )

        x_col = st.selectbox("X axis", result_df.columns)
        y_col = None

        if chart_type != "Histogram":
            y_col = st.selectbox("Y axis", result_df.columns)

        if len(result_df) > MAX_VIZ_ROWS:
            st.warning("Result too large to visualize.")
        else:
            if chart_type == "Histogram":
                fig = px.histogram(result_df, x=x_col)
            elif chart_type == "Bar":
                fig = px.bar(result_df, x=x_col, y=y_col)
            elif chart_type == "Line":
                fig = px.line(result_df, x=x_col, y=y_col)
            else:
                fig = px.scatter(result_df, x=x_col, y=y_col)

            st.plotly_chart(fig, use_container_width=True)

