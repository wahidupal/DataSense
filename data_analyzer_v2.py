import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------
# App config
# --------------------------------------------------
st.set_page_config(
    page_title="Data Analyzer v2",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Data Analyzer v2")
st.caption("Modern interactive data exploration tool")

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None

# --------------------------------------------------
# Data loading
# --------------------------------------------------


@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)


# --------------------------------------------------
# Sidebar – Upload
# --------------------------------------------------
st.sidebar.header("📂 Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

if uploaded_file:
    df = load_data(uploaded_file)
    st.session_state.df = df
    st.session_state.filtered_df = df.copy()

# --------------------------------------------------
# Guard clause
# --------------------------------------------------
if st.session_state.df is None:
    st.info("👈 Upload a dataset to get started")
    st.stop()

df = st.session_state.df
filtered_df = st.session_state.filtered_df

# --------------------------------------------------
# Tabs
# --------------------------------------------------
tab_overview, tab_filter, tab_viz, tab_stats = st.tabs(
    ["📋 Overview", "🔍 Filter", "📈 Visualize", "🧪 Stats"]
)

# ==================================================
# 📋 OVERVIEW
# ==================================================
with tab_overview:
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", len(df))
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing values", int(df.isna().sum().sum()))

    st.subheader("Column Summary")

    summary = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing %": (df.isna().mean() * 100).round(2),
        "unique values": df.nunique()
    })

    st.dataframe(summary, use_container_width=True)

    with st.expander("Preview data"):
        st.dataframe(df.head(100), use_container_width=True)

# ==================================================
# 🔍 FILTER
# ==================================================
with tab_filter:
    st.subheader("Filter dataset")

    temp_df = df.copy()

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val, max_val = st.slider(
                f"{col}",
                float(df[col].min()),
                float(df[col].max()),
                (float(df[col].min()), float(df[col].max()))
            )
            temp_df = temp_df[temp_df[col].between(min_val, max_val)]

        else:
            values = st.multiselect(
                f"{col}",
                options=df[col].dropna().unique(),
                default=df[col].dropna().unique()
            )
            temp_df = temp_df[temp_df[col].isin(values)]

    st.session_state.filtered_df = temp_df

    st.success(f"Filtered rows: {len(temp_df)}")
    st.dataframe(temp_df.head(100), use_container_width=True)

    st.download_button(
        "⬇ Download filtered data",
        temp_df.to_csv(index=False),
        file_name="filtered_data.csv"
    )

# ==================================================
# 📈 VISUALIZATION
# ==================================================
with tab_viz:
    st.subheader("Create charts")

    chart_type = st.selectbox(
        "Chart type",
        ["Scatter", "Line", "Bar", "Box", "Histogram"]
    )

    x_col = st.selectbox("X-axis", filtered_df.columns)
    y_col = None

    if chart_type != "Histogram":
        y_col = st.selectbox("Y-axis", filtered_df.columns)

    color_col = st.selectbox(
        "Color (optional)",
        [None] + list(filtered_df.columns)
    )

    if chart_type == "Scatter":
        fig = px.scatter(filtered_df, x=x_col, y=y_col, color=color_col)

    elif chart_type == "Line":
        fig = px.line(filtered_df, x=x_col, y=y_col, color=color_col)

    elif chart_type == "Bar":
        fig = px.bar(filtered_df, x=x_col, y=y_col, color=color_col)

    elif chart_type == "Box":
        fig = px.box(filtered_df, x=x_col, y=y_col, color=color_col)

    else:
        fig = px.histogram(filtered_df, x=x_col, color=color_col)

    st.plotly_chart(fig, use_container_width=True)

# ==================================================
# 🧪 STATS
# ==================================================
with tab_stats:
    st.subheader("Statistical analysis")

    st.markdown("### Describe dataset")
    st.dataframe(filtered_df.describe(include="all").transpose())

    st.markdown("### Correlation matrix")
    numeric_cols = filtered_df.select_dtypes(include=np.number)

    if len(numeric_cols.columns) > 1:
        corr = numeric_cols.corr()
        fig = px.imshow(corr, text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough numeric columns for correlation")
