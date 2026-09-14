import pandas as pd


def detect_semantic_type(series: pd.Series) -> str:
    """
    Detect the semantic type of a pandas Series.
    """

    if pd.api.types.is_bool_dtype(series):
        return "Boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "Numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "Datetime"

    if pd.api.types.is_object_dtype(series):
        unique_ratio = series.nunique(dropna=True) / max(len(series), 1)

        if unique_ratio <= 0.05:
            return "Categorical"

        return "Text"

    return "Text"

def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate basic dataset-level and column-level profiling statistics.
    """

    profile = {
        "dataset": {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": df.memory_usage(deep=True).sum() / 1e6,
            "duplicate_rows": int(df.duplicated().sum()),
        },
        "columns": [],
        "numeric": []
    }

    for column in df.columns:
        null_count = int(df[column].isna().sum())
        unique_count = int(df[column].nunique(dropna=True))

        column_profile = {
            "column": column,
            "dtype": str(df[column].dtype),
            "null_count": null_count,
            "null_percentage": (null_count / len(df)) * 100,
            "unique_count": unique_count,
            "unique_percentage": (unique_count / len(df)) * 100,
            "semantic_type": detect_semantic_type(df[column]),
        }

        profile["columns"].append(column_profile)

    # Numeric profiling
    numeric_columns = df.select_dtypes(include="number").columns

    for column in numeric_columns:
        series = df[column].dropna()

        numeric_profile = {
            "column": column,
            "min": series.min(),
            "q1": series.quantile(0.25),
            "median": series.median(),
            "mean": series.mean(),
            "q3": series.quantile(0.75),
            "p95": series.quantile(0.95),
            "p99": series.quantile(0.99),
            "max": series.max(),
            "zero_count": int((series == 0).sum()),
            "negative_count": int((series < 0).sum()),
        }

        profile["numeric"].append(numeric_profile)

    return profile