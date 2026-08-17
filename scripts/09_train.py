"""
Train regression and classification models with full sklearn Pipelines.

Mirrors notebook cells 26 and 30. Builds Pipeline + preprocessing transformers,
trains all models, evaluates metrics, and saves models/ml_pipeline.pkl.
"""

from __future__ import annotations

import json
import pickle
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
    StackingRegressor,
    VotingClassifier,
)
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor

sys.path.insert(0, str(Path(__file__).resolve().parent))

from paths import BASE_FEATURES, DATA_RAW, MODELS_DIR, TARGET_CLS, TARGET_REG
from sklearn_transformers import CategoricalEncoder, ColumnSubset, DataCleaner, FeatureEngineer

warnings.filterwarnings("ignore")


import importlib.util

_preprocessor_path = Path(__file__).resolve().parent / "02_preprocessor.py"
_spec = importlib.util.spec_from_file_location("preprocessor", _preprocessor_path)
_preprocessor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_preprocessor)
preprocess = _preprocessor.preprocess


def build_regression_pipeline() -> Pipeline:
    """Full regression pipeline matching notebook hyperparameters."""
    return Pipeline(
        [
            ("clean", DataCleaner()),
            ("encode", CategoricalEncoder()),
            ("engineer", FeatureEngineer()),
            ("subset", ColumnSubset(BASE_FEATURES)),
            ("select", SelectKBest(f_regression, k=25)),
            ("scale", StandardScaler()),
            (
                "model",
                StackingRegressor(
                    estimators=[
                        (
                            "rf",
                            RandomForestRegressor(
                                n_estimators=300, max_depth=15, random_state=42, n_jobs=-1
                            ),
                        ),
                        (
                            "xgb",
                            XGBRegressor(
                                n_estimators=300,
                                max_depth=6,
                                learning_rate=0.05,
                                random_state=42,
                                verbosity=0,
                            ),
                        ),
                        (
                            "gbm",
                            GradientBoostingRegressor(
                                n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42
                            ),
                        ),
                    ],
                    final_estimator=Ridge(alpha=1.0),
                    cv=5,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def build_classification_pipeline() -> Pipeline:
    """Full classification pipeline matching notebook hyperparameters."""
    return Pipeline(
        [
            ("clean", DataCleaner()),
            ("encode", CategoricalEncoder()),
            ("engineer", FeatureEngineer()),
            ("subset", ColumnSubset(BASE_FEATURES)),
            ("select", SelectKBest(f_classif, k=25)),
            ("scale", StandardScaler()),
            (
                "model",
                VotingClassifier(
                    estimators=[
                        (
                            "rf",
                            RandomForestClassifier(
                                n_estimators=300, max_depth=12, random_state=42, n_jobs=-1
                            ),
                        ),
                        (
                            "xgb",
                            XGBClassifier(
                                n_estimators=300,
                                max_depth=5,
                                learning_rate=0.05,
                                eval_metric="mlogloss",
                                random_state=42,
                                verbosity=0,
                            ),
                        ),
                        (
                            "gb",
                            GradientBoostingClassifier(
                                n_estimators=200, max_depth=4, random_state=42
                            ),
                        ),
                    ],
                    voting="soft",
                ),
            ),
        ]
    )


def reg_metrics(name, y_true, y_pred):
    return {
        "Model": name,
        "R2": round(r2_score(y_true, y_pred), 4),
        "MAE": round(mean_absolute_error(y_true, y_pred), 3),
        "RMSE": round(mean_squared_error(y_true, y_pred) ** 0.5, 3),
    }


def cls_metrics(name, y_true, y_pred):
    return {
        "Model": name,
        "Accuracy": round(accuracy_score(y_true, y_pred), 4),
        "F1 (macro)": round(f1_score(y_true, y_pred, average="macro"), 4),
        "Precision": round(precision_score(y_true, y_pred, average="macro"), 4),
        "Recall": round(recall_score(y_true, y_pred, average="macro"), 4),
    }


def prepare_raw_features(df: pd.DataFrame) -> pd.DataFrame:
    """Drop identifiers and targets; keep columns needed for preprocessing."""
    drop_cols = ["Student_ID", TARGET_REG, TARGET_CLS]
    return df.drop(columns=[c for c in drop_cols if c in df.columns])


def train_and_evaluate(df_raw: pd.DataFrame) -> dict:
    """Train both pipelines and print notebook-style metrics."""
    df = preprocess(df_raw)
    X = prepare_raw_features(df)
    y_reg = df[TARGET_REG]
    y_cls = df[TARGET_CLS]

    reg_pipeline = build_regression_pipeline()
    cls_pipeline = build_classification_pipeline()

    X_tr, X_te, y_tr, y_te = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    print(f"Regression train: {X_tr.shape[0]}  |  test: {X_te.shape[0]}")

    reg_pipeline.fit(X_tr, y_tr)
    y_pred_stack = reg_pipeline.predict(X_te)

    ridge_reg = Ridge(alpha=1.0)
    rf_reg = RandomForestRegressor(
        n_estimators=500,
        max_depth=20,
        min_samples_leaf=1,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )
    xgb_reg = XGBRegressor(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        random_state=42,
        verbosity=0,
        n_jobs=-1,
    )

    X_tr_scaled = reg_pipeline.named_steps["scale"].transform(
        reg_pipeline.named_steps["select"].transform(
            reg_pipeline.named_steps["subset"].transform(
                reg_pipeline.named_steps["engineer"].transform(
                    reg_pipeline.named_steps["encode"].transform(
                        reg_pipeline.named_steps["clean"].transform(X_tr)
                    )
                )
            )
        )
    )
    X_te_scaled = reg_pipeline.named_steps["scale"].transform(
        reg_pipeline.named_steps["select"].transform(
            reg_pipeline.named_steps["subset"].transform(
                reg_pipeline.named_steps["engineer"].transform(
                    reg_pipeline.named_steps["encode"].transform(
                        reg_pipeline.named_steps["clean"].transform(X_te)
                    )
                )
            )
        )
    )

    ridge_reg.fit(X_tr_scaled, y_tr)
    rf_reg.fit(X_tr_scaled, y_tr)
    xgb_reg.fit(X_tr_scaled, y_tr)

    y_pred_ridge = ridge_reg.predict(X_te_scaled)
    y_pred_rf = rf_reg.predict(X_te_scaled)
    y_pred_xgb = xgb_reg.predict(X_te_scaled)

    reg_results = pd.DataFrame(
        [
            reg_metrics("Ridge Regression", y_te, y_pred_ridge),
            reg_metrics("Random Forest", y_te, y_pred_rf),
            reg_metrics("XGBoost", y_te, y_pred_xgb),
            reg_metrics("Stacking Ensemble", y_te, y_pred_stack),
        ]
    )
    print("\n---------------------- Regression Model Comparison -------------------------")
    print(reg_results.to_string(index=False))

    le_career = LabelEncoder()
    y_cls_encoded = le_career.fit_transform(df[TARGET_CLS])
    career_classes = le_career.classes_
    X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(
        X, y_cls_encoded, test_size=0.2, stratify=y_cls_encoded, random_state=42
    )
    print(f"\nClassification train: {X_tr_c.shape[0]}  |  test: {X_te_c.shape[0]}")

    cls_pipeline.fit(X_tr_c, y_tr_c)
    y_pred_vote = cls_pipeline.predict(X_te_c)

    cls_results = pd.DataFrame([cls_metrics("Voting Ensemble", y_te_c, y_pred_vote)])
    print("\n------------------------- Classification Model Comparison ------------------------")
    print(cls_results.to_string(index=False))
    print(
        f"\n{classification_report(y_te_c, y_pred_vote, target_names=career_classes)}"
    )

    return {
        "regression_pipeline": reg_pipeline,
        "classification_pipeline": cls_pipeline,
        "career_classes": career_classes,
        "reg_results": reg_results.to_dict(orient="records"),
        "cls_results": cls_results.to_dict(orient="records"),
        "top_reg_features": reg_pipeline.named_steps["select"].get_feature_names_out(
            BASE_FEATURES
        ).tolist(),
        "top_cls_features": cls_pipeline.named_steps["select"].get_feature_names_out(
            BASE_FEATURES
        ).tolist(),
    }


def main() -> None:
    df_raw = pd.read_csv(DATA_RAW)
    artifacts = train_and_evaluate(df_raw)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    pipeline_path = MODELS_DIR / "ml_pipeline.pkl"
    with open(pipeline_path, "wb") as f:
        pickle.dump(
            {
                "regression_pipeline": artifacts["regression_pipeline"],
                "classification_pipeline": artifacts["classification_pipeline"],
                "career_classes": artifacts["career_classes"],
                "reg_results": artifacts["reg_results"],
                "cls_results": artifacts["cls_results"],
                "top_reg_features": artifacts["top_reg_features"],
                "top_cls_features": artifacts["top_cls_features"],
            },
            f,
        )

    metrics_path = MODELS_DIR / "training_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "regression": artifacts["reg_results"],
                "classification": artifacts["cls_results"],
                "top_reg_features": artifacts["top_reg_features"],
                "top_cls_features": artifacts["top_cls_features"],
            },
            f,
            indent=2,
        )

    print(f"\nFull pipelines saved to {pipeline_path}")
    print(f"Training metrics saved to {metrics_path}")


if __name__ == "__main__":
    main()
