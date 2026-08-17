"""
Load trained pipelines and run inference on a single student record.

Mirrors notebook evaluation/prediction logic. Provides predict(input_dict).
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import shap

sys.path.insert(0, str(Path(__file__).resolve().parent))

from paths import BASE_FEATURES, MODELS_DIR, TARGET_CLS, TARGET_REG
import sklearn_transformers  # noqa: F401 — register custom transformers for pickle

TOP_REG_FEATURES = [
    "Technical_Skill_Index", "Python_Skill", "DA_Core_Strength", "SE_Core_Strength",
    "DSA_Score", "Tech_Soft_Product", "Comm_Tech_Ratio", "Project_Complexity_Enc",
]
TOP_CLS_FEATURES = [
    "Project_Complexity_Enc", "Web_JS_Synergy", "DS_Python_Synergy", "Technical_Skill_Index",
    "JavaScript_Skill", "ML_Score", "SE_Core_Strength", "DA_Core_Strength",
]

# Derived features FeatureEngineer computes from the raw inputs (sklearn_transformers.py).
# Not directly editable — each is a fixed function of raw fields already submitted —
# but surfaced here so a user can see exactly what the pipeline computed internally.
ENGINEERED_FEATURE_KEYS = [
    "Language_Index", "Academic_Index", "Industry_Readiness", "Competitive_Edge",
    "Comm_Tech_Ratio", "DS_Python_Synergy", "Web_JS_Synergy", "SE_Core_Strength",
    "DA_Core_Strength", "Tech_Soft_Product",
]

_FEATURE_STATS = None
_PIPELINE_BUNDLE = None
_SHAP_EXPLAINERS = None


def _load_feature_stats() -> dict:
    global _FEATURE_STATS
    if _FEATURE_STATS is None:
        with open(MODELS_DIR / "feature_stats.json", encoding="utf-8") as f:
            _FEATURE_STATS = json.load(f)
    return _FEATURE_STATS


def _percentile_label(z: float) -> str:
    if z > 1.5:
        return "significantly above average"
    if z > 0.5:
        return "above average"
    if z >= -0.5:
        return "typical"
    if z >= -1.5:
        return "below average"
    return "significantly below average"


def _reasoning(engineered_row: pd.Series, feature_names: list[str]) -> list[dict]:
    stats = _load_feature_stats()
    reasons = []
    for name in feature_names:
        if name not in stats:
            continue
        mean, std = stats[name]["mean"], stats[name]["std"]
        value = float(engineered_row[name])
        z = (value - mean) / std if std > 1e-9 else 0.0
        reasons.append(
            {
                "feature": name,
                "value": round(value, 2),
                "population_mean": round(mean, 2),
                "z_score": round(z, 2),
                "assessment": _percentile_label(z),
            }
        )
    return reasons


def _get_shap_explainers(reg_pipeline, cls_pipeline):
    """SHAP TreeExplainers on each pipeline's XGBoost sub-model (real per-prediction
    attribution, distinct from the population-relative z-scores in _reasoning). XGBoost
    is one of three equally-weighted base learners in each ensemble, so this explains
    that component's view of the prediction — not the full stacked/voted model, which
    has no exact SHAP decomposition. Cached after first build (TreeExplainer construction
    isn't free)."""
    global _SHAP_EXPLAINERS
    if _SHAP_EXPLAINERS is None:
        reg_xgb = reg_pipeline.named_steps["model"].named_estimators_["xgb"]
        cls_xgb = cls_pipeline.named_steps["model"].named_estimators_["xgb"]
        _SHAP_EXPLAINERS = (shap.TreeExplainer(reg_xgb), shap.TreeExplainer(cls_xgb))
    return _SHAP_EXPLAINERS


def _shap_reasoning(feature_names, shap_values, top_n: int = 6) -> list[dict]:
    pairs = sorted(zip(feature_names, shap_values), key=lambda p: abs(p[1]), reverse=True)[:top_n]
    return [
        {
            "feature": name,
            "impact": round(float(val), 3),
            "direction": "increases" if val > 0 else "decreases",
        }
        for name, val in pairs
    ]


def _shap_waterfall(feature_names, shap_values, base_value: float, top_n: int = 6) -> dict:
    """Cumulative baseline -> feature contributions -> final value, for a step/line
    chart. Remaining (non-top-N) features are folded into one 'Other features' bucket
    so the steps always sum exactly to the total."""
    pairs = sorted(
        zip(feature_names, (float(v) for v in shap_values)), key=lambda p: abs(p[1]), reverse=True
    )
    shown = pairs[:top_n]
    shown_names = {name for name, _ in shown}
    other_sum = sum(val for name, val in pairs if name not in shown_names)

    steps = list(shown)
    if abs(other_sum) > 1e-6:
        steps.append(("Other features", other_sum))

    running = base_value
    points = [{"label": "Baseline", "impact": 0.0, "value": round(running, 2)}]
    for name, val in steps:
        running += val
        points.append({"label": name, "impact": round(val, 3), "value": round(running, 2)})

    return {"base_value": round(base_value, 2), "points": points, "total": round(running, 2)}


def load_pipelines(model_path=None):
    """Load bundled regression and classification pipelines (cached after first call)."""
    global _PIPELINE_BUNDLE
    if _PIPELINE_BUNDLE is not None and model_path is None:
        return _PIPELINE_BUNDLE
    resolved_path = model_path or MODELS_DIR / "ml_pipeline.pkl"
    with open(resolved_path, "rb") as f:
        bundle = pickle.load(f)
    if model_path is None:
        _PIPELINE_BUNDLE = bundle
    return bundle


def predict(input_dict: dict, model_path=None) -> dict:
    """
    Predict employability score and recommended career path for one student,
    with class probabilities, a confidence estimate, and feature-level reasoning.

    Parameters
    ----------
    input_dict : dict
        Raw feature dictionary matching dataset columns (excluding Student_ID
        and target columns unless provided).

    Returns
    -------
    dict
        employability_score, employability_range, recommended_career_path,
        career_class_index, career_probabilities, confidence, reasoning
    """
    bundle = load_pipelines(model_path)
    reg_pipeline = bundle["regression_pipeline"]
    cls_pipeline = bundle["classification_pipeline"]
    career_classes = bundle["career_classes"]

    row = pd.DataFrame([input_dict])
    feature_row = row.drop(columns=[TARGET_REG, TARGET_CLS], errors="ignore")

    employability_score = float(reg_pipeline.predict(feature_row)[0])

    # Base-estimator spread (RF / XGB / GBM) inside the StackingRegressor as an
    # uncertainty proxy: pushed through the fitted pre-model steps, then read
    # via StackingRegressor.transform(), which returns each base learner's
    # raw prediction (pre meta-model).
    pre_model = feature_row
    for step_name in ("clean", "encode", "engineer", "subset", "select", "scale"):
        pre_model = reg_pipeline.named_steps[step_name].transform(pre_model)
    base_preds = reg_pipeline.named_steps["model"].transform(pre_model)[0]
    score_spread = float(base_preds.std())

    proba = cls_pipeline.predict_proba(feature_row)[0]
    career_idx = int(proba.argmax())
    recommended_career = career_classes[career_idx]
    career_probabilities = {
        career_classes[i]: round(float(p), 4) for i, p in enumerate(proba)
    }

    engineered = feature_row
    for step_name in ("clean", "encode", "engineer", "subset"):
        engineered = reg_pipeline.named_steps[step_name].transform(engineered)
    engineered_row = engineered.iloc[0]
    engineered_features = {
        key: round(float(engineered_row[key]), 3) for key in ENGINEERED_FEATURE_KEYS
    }

    # Real per-prediction SHAP attribution from each pipeline's XGBoost sub-model,
    # computed on the same pre-model (scaled, top-25) representation the models see.
    reg_explainer, cls_explainer = _get_shap_explainers(reg_pipeline, cls_pipeline)
    reg_feature_names = reg_pipeline.named_steps["select"].get_feature_names_out(BASE_FEATURES)
    reg_shap_values = reg_explainer.shap_values(pre_model)[0]
    reg_base_value = float(np.ravel(reg_explainer.expected_value)[0])

    pre_model_cls = feature_row
    for step_name in ("clean", "encode", "engineer", "subset", "select", "scale"):
        pre_model_cls = cls_pipeline.named_steps[step_name].transform(pre_model_cls)
    cls_feature_names = cls_pipeline.named_steps["select"].get_feature_names_out(BASE_FEATURES)
    cls_shap_values = cls_explainer.shap_values(pre_model_cls)[0, :, career_idx]
    cls_base_value = float(np.ravel(cls_explainer.expected_value)[career_idx])

    return {
        "employability_score": round(employability_score, 2),
        "employability_range": [
            round(employability_score - score_spread, 2),
            round(employability_score + score_spread, 2),
        ],
        "recommended_career_path": recommended_career,
        "career_class_index": career_idx,
        "career_probabilities": career_probabilities,
        "confidence": round(float(proba.max()), 4),
        "reasoning": {
            "employability": _reasoning(engineered_row, TOP_REG_FEATURES),
            "career": _reasoning(engineered_row, TOP_CLS_FEATURES),
        },
        "engineered_features": engineered_features,
        "shap_reasoning": {
            "employability": _shap_reasoning(reg_feature_names, reg_shap_values),
            "career": _shap_reasoning(cls_feature_names, cls_shap_values),
        },
        "shap_waterfall": {
            "employability": _shap_waterfall(reg_feature_names, reg_shap_values, reg_base_value),
            "career": _shap_waterfall(cls_feature_names, cls_shap_values, cls_base_value),
        },
    }


def evaluate_on_holdout(model_path=None) -> dict:
    """Run a quick holdout evaluation using saved pipelines (smoke test)."""
    from paths import DATA_RAW

    df = pd.read_csv(DATA_RAW).drop_duplicates().reset_index(drop=True)
    sample = df.drop(columns=["Student_ID"]).iloc[2].to_dict()
    y_true_reg = float(df.iloc[2][TARGET_REG])
    y_true_cls = df.iloc[2][TARGET_CLS]

    preds = predict(sample, model_path=model_path)
    preds["actual_employability_score"] = y_true_reg
    preds["actual_career_path"] = y_true_cls
    return preds


def main() -> None:
    parser = argparse.ArgumentParser(description="SkillBridge inference")
    parser.add_argument(
        "input_json",
        nargs="?",
        default=None,
        help="JSON string with student feature dictionary",
    )
    args = parser.parse_args()

    if args.input_json:
        input_dict = json.loads(args.input_json)
        result = predict(input_dict)
        print(json.dumps(result, indent=2))
    else:
        result = evaluate_on_holdout()
        print("Sample prediction (first dataset row):")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
