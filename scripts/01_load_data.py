"""
Load the SkillBridge dataset, detect column types, and persist raw metadata.

Mirrors notebook section 1 (Load Dataset).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from paths import DATA_PROCESSED, DATA_RAW, METADATA_PATH, TARGET_CLS, TARGET_REG


def load_raw_data(csv_path=DATA_RAW) -> pd.DataFrame:
    """Read the CSV and return the raw dataframe."""
    return pd.read_csv(csv_path)


def detect_column_types(df: pd.DataFrame) -> dict:
    """Detect numeric and categorical columns using notebook conventions."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    return {
        "target_regression": TARGET_REG,
        "target_classification": TARGET_CLS,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
    }


def main() -> None:
    df_raw = load_raw_data()
    print(f"Shape: {df_raw.shape}")
    print(f"\nCareer Distribution:\n{df_raw[TARGET_CLS].value_counts()}")
    print(f"\nEmployability Score stats:\n{df_raw[TARGET_REG].describe()}")
    print("\nFirst 5 rows:")
    print(df_raw.head(5).to_string())

    metadata = detect_column_types(df_raw)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nMetadata saved to {METADATA_PATH}")


if __name__ == "__main__":
    main()
