"""
Data preprocessing: deduplication, imputation, and IQR outlier winsorization.

Mirrors notebook cells 7, 9, and 11.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from paths import DATA_RAW, DF_CLEAN_PATH


def preprocess(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Apply deduplication, imputation, and outlier clipping."""
    df = df_raw.drop_duplicates().reset_index(drop=True)
    df_clean = df.copy()

    num_cols_missing = df_clean.select_dtypes(include="number").columns[
        df_clean.select_dtypes(include="number").isnull().any()
    ].tolist()
    cat_cols_missing = df_clean.select_dtypes(include="object").columns[
        df_clean.select_dtypes(include="object").isnull().any()
    ].tolist()

    if num_cols_missing:
        num_imputer = SimpleImputer(strategy="median")
        df_clean[num_cols_missing] = num_imputer.fit_transform(df_clean[num_cols_missing])

    if cat_cols_missing:
        cat_imputer = SimpleImputer(strategy="most_frequent")
        df_clean[cat_cols_missing] = cat_imputer.fit_transform(df_clean[cat_cols_missing])

    print(f"Missing values after imputation: {df_clean.isnull().sum().sum()}")
    print(f"Numeric cols, corrected by adding median  : {num_cols_missing}")
    print(f"Categorical cols, corrected by adding mode: {cat_cols_missing}")

    numeric_features = df_clean.select_dtypes(include="number").columns.tolist()
    exclude_from_outlier = ["Employability_Score"]
    numeric_features = [c for c in numeric_features if c not in exclude_from_outlier]

    outlier_summary = {}
    for col in numeric_features:
        Q1, Q3 = df_clean[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        n_out = ((df_clean[col] < lower) | (df_clean[col] > upper)).sum()
        if n_out > 0:
            outlier_summary[col] = {"lower": lower, "upper": upper, "count": n_out}

    print(f"Columns with outliers: {len(outlier_summary)}")
    for col, bounds in outlier_summary.items():
        print(f"  {col:35s}: {bounds['count']} outliers")

    for col, bounds in outlier_summary.items():
        df_clean[col] = df_clean[col].clip(bounds["lower"], bounds["upper"])

    print("\nOutliers winsorized!")
    print(f"Rows after deduplication: {len(df_clean)}")
    return df_clean


def main() -> None:
    df_raw = pd.read_csv(DATA_RAW)
    df_clean = preprocess(df_raw)
    DF_CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(DF_CLEAN_PATH, index=False)
    print(f"Clean data saved to {DF_CLEAN_PATH}")


if __name__ == "__main__":
    main()
