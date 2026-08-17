"""
Feature engineering: create synergy and composite indices used by the models.

Mirrors notebook cell 18. Depends on 04_encoding.py output.
"""

from __future__ import annotations

import pandas as pd

from paths import BASE_FEATURES, DF_ENCODED_PATH, DF_FEAT_PATH


def engineer_features(df_encoded: pd.DataFrame) -> pd.DataFrame:
    """Create engineered columns from the encoded dataframe."""
    df_feat = df_encoded.copy()

    df_feat["Language_Index"] = (df_feat["Python_Skill"] + df_feat["JavaScript_Skill"]) / 2
    df_feat["Academic_Index"] = df_feat["CGPA"] * (df_feat["Attendance_Percentage"] / 100)
    df_feat["Industry_Readiness"] = (
        df_feat["Internship_Experience"] * 25
        + df_feat["Certifications_Count"] * 8
        + df_feat["Workshops_Attended"] * 4
    )
    df_feat["Competitive_Edge"] = (
        df_feat["Hackathons_Participated"] * 10
        + df_feat["Coding_Contest_Rating"] / 100
        + df_feat["GitHub_Repo_Count"] * 2
    )
    df_feat["Comm_Tech_Ratio"] = df_feat["Soft_Skill_Index"] / (df_feat["Technical_Skill_Index"] + 1e-5)
    df_feat["DS_Python_Synergy"] = df_feat["ML_Score"] * df_feat["Python_Skill"] / 100
    df_feat["Web_JS_Synergy"] = df_feat["WebDev_Score"] * df_feat["JavaScript_Skill"] / 100
    df_feat["SE_Core_Strength"] = df_feat["DSA_Score"] * df_feat["Programming_Score"] / 100
    df_feat["DA_Core_Strength"] = df_feat["Database_Score"] * df_feat["Python_Skill"] / 100
    df_feat["Tech_Soft_Product"] = df_feat["Technical_Skill_Index"] * df_feat["Soft_Skill_Index"]

    new_feats = [
        "Language_Index",
        "Academic_Index",
        "Industry_Readiness",
        "Competitive_Edge",
        "Comm_Tech_Ratio",
        "DS_Python_Synergy",
        "Web_JS_Synergy",
        "SE_Core_Strength",
        "DA_Core_Strength",
        "Tech_Soft_Product",
    ]
    print("New & enhanced features:")
    print(df_feat[new_feats].describe().round(2).to_string())
    print(f"\nBase feature count: {len(BASE_FEATURES)}")
    return df_feat


def main() -> None:
    if not DF_ENCODED_PATH.exists():
        raise FileNotFoundError(f"{DF_ENCODED_PATH} not found. Run 04_encoding.py first.")

    df_encoded = pd.read_parquet(DF_ENCODED_PATH)
    df_feat = engineer_features(df_encoded)
    DF_FEAT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_feat.to_parquet(DF_FEAT_PATH, index=False)
    print(f"Feature dataset saved to {DF_FEAT_PATH}")


if __name__ == "__main__":
    main()
