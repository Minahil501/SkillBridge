"""
Standard scaling of selected regression and classification feature sets.

Mirrors notebook cell 22. Saves scalers to models/scaler.pkl.
"""

from __future__ import annotations

import json
import pickle

import pandas as pd
from sklearn.preprocessing import StandardScaler

from paths import DATA_PROCESSED, DF_FEAT_PATH, MODELS_DIR


def scale_features(df_feat: pd.DataFrame) -> dict:
    """Fit StandardScaler on top-k feature subsets."""
    with open(DATA_PROCESSED / "feature_selection.json", encoding="utf-8") as f:
        feature_meta = json.load(f)

    top_reg_features = feature_meta["top_reg_features"]
    top_cls_features = feature_meta["top_cls_features"]

    scaler_reg = StandardScaler()
    scaler_cls = StandardScaler()

    X_reg = df_feat[top_reg_features].copy()
    X_cls = df_feat[top_cls_features].copy()

    X_reg_scaled = pd.DataFrame(scaler_reg.fit_transform(X_reg), columns=top_reg_features)
    X_cls_scaled = pd.DataFrame(scaler_cls.fit_transform(X_cls), columns=top_cls_features)

    print("Scaling complete.")
    print(f"X_reg shape: {X_reg_scaled.shape}")
    print(f"X_cls shape: {X_cls_scaled.shape}")

    return {
        "scaler_reg": scaler_reg,
        "scaler_cls": scaler_cls,
        "X_reg_scaled": X_reg_scaled,
        "X_cls_scaled": X_cls_scaled,
        "top_reg_features": top_reg_features,
        "top_cls_features": top_cls_features,
    }


def main() -> None:
    df_feat = pd.read_parquet(DF_FEAT_PATH)
    artifacts = scale_features(df_feat)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    artifacts["X_reg_scaled"].to_parquet(DATA_PROCESSED / "X_reg_scaled.parquet", index=False)
    artifacts["X_cls_scaled"].to_parquet(DATA_PROCESSED / "X_cls_scaled.parquet", index=False)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    scaler_path = MODELS_DIR / "scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(
            {
                "scaler_reg": artifacts["scaler_reg"],
                "scaler_cls": artifacts["scaler_cls"],
                "top_reg_features": artifacts["top_reg_features"],
                "top_cls_features": artifacts["top_cls_features"],
            },
            f,
        )

    print(f"Scaled matrices saved to {DATA_PROCESSED}")
    print(f"Scalers saved to {scaler_path}")


if __name__ == "__main__":
    main()
