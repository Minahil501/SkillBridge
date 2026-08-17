"""
Categorical encoding: OrdinalEncoder for Project_Complexity and a LabelEncoder
for career path. Saves encoders to models/encoder.pkl.

Gender is deliberately NOT encoded into a model feature — see README.md
"Bias Audit". Mirrors notebook cell 14. Run after 02_preprocessor.py.
"""

from __future__ import annotations

import pickle

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder

from paths import DF_CLEAN_PATH, DF_ENCODED_PATH, MODELS_DIR


def encode(df_clean: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Apply encodings and return encoded dataframe plus encoder artifacts."""
    df_encoded = df_clean.copy()

    ord_enc = OrdinalEncoder(categories=[["Low", "Medium", "High"]])
    df_encoded["Project_Complexity_Enc"] = ord_enc.fit_transform(df_encoded[["Project_Complexity"]])

    le_career = LabelEncoder()
    df_encoded["Career_Label"] = le_career.fit_transform(df_encoded["Recommended_Career_Path"])
    career_classes = le_career.classes_

    print("Career class mapping:")
    for i, career in enumerate(career_classes):
        print(f"  {i} -> {career}")

    encoders = {
        "ord_enc": ord_enc,
        "le_career": le_career,
        "career_classes": career_classes,
    }
    return df_encoded, encoders


def main() -> None:
    df_clean = pd.read_parquet(DF_CLEAN_PATH)
    df_encoded, encoders = encode(df_clean)

    DF_ENCODED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_encoded.to_parquet(DF_ENCODED_PATH, index=False)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    encoder_path = MODELS_DIR / "encoder.pkl"
    with open(encoder_path, "wb") as f:
        pickle.dump(encoders, f)

    print(f"\nEncoded data saved to {DF_ENCODED_PATH}")
    print(f"Encoders saved to {encoder_path}")


if __name__ == "__main__":
    main()
