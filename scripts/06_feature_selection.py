"""
Feature selection using SelectKBest (k=25) for regression and classification targets.

Mirrors notebook cell 20. Saves selectors and top feature lists.
"""

from __future__ import annotations

import json
import pickle

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_selection import SelectKBest, f_classif, f_regression

from paths import BASE_FEATURES, DATA_PROCESSED, DF_FEAT_PATH, PALETTE, PLOTS_DIR, TARGET_REG

plt.rcParams.update({"figure.dpi": 120})
sns.set_palette(PALETTE)


def select_features(df_feat: pd.DataFrame) -> dict:
    """Run SelectKBest for both targets and return artifacts."""
    X = df_feat[BASE_FEATURES]
    y_reg = df_feat[TARGET_REG]
    y_cls = df_feat["Career_Label"]

    selector_reg = SelectKBest(f_regression, k=25)
    selector_reg.fit(X, y_reg)
    scores_reg = pd.Series(selector_reg.scores_, index=BASE_FEATURES).sort_values(ascending=False)

    selector_cls = SelectKBest(f_classif, k=25)
    selector_cls.fit(X, y_cls)
    scores_cls = pd.Series(selector_cls.scores_, index=BASE_FEATURES).sort_values(ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    for ax, scores, title, color in zip(
        axes,
        [scores_reg[:20], scores_cls[:20]],
        [
            "SelectKBest — Regression (Employability Score)",
            "SelectKBest — Classification (Career Path)",
        ],
        [PALETTE[0], PALETTE[4]],
    ):
        ax.barh(scores.index[::-1], scores.values[::-1], color=color, edgecolor="white", alpha=0.85)
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("F-Statistic Score")
    plt.tight_layout()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(PLOTS_DIR / "feature_selection.png", bbox_inches="tight")
    plt.close()

    top_reg_features = scores_reg[:25].index.tolist()
    top_cls_features = scores_cls[:25].index.tolist()
    print(f"Top regression features ({len(top_reg_features)}): {top_reg_features[:10]} ...")
    print(f"Top classification features ({len(top_cls_features)}): {top_cls_features[:10]} ...")

    return {
        "selector_reg": selector_reg,
        "selector_cls": selector_cls,
        "top_reg_features": top_reg_features,
        "top_cls_features": top_cls_features,
        "scores_reg": scores_reg.to_dict(),
        "scores_cls": scores_cls.to_dict(),
    }


def main() -> None:
    df_feat = pd.read_parquet(DF_FEAT_PATH)
    artifacts = select_features(df_feat)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    feature_meta_path = DATA_PROCESSED / "feature_selection.json"
    with open(feature_meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "top_reg_features": artifacts["top_reg_features"],
                "top_cls_features": artifacts["top_cls_features"],
            },
            f,
            indent=2,
        )

    selector_path = DATA_PROCESSED / "feature_selectors.pkl"
    with open(selector_path, "wb") as f:
        pickle.dump(
            {
                "selector_reg": artifacts["selector_reg"],
                "selector_cls": artifacts["selector_cls"],
            },
            f,
        )

    print(f"Feature metadata saved to {feature_meta_path}")
    print(f"Selectors saved to {selector_path}")


if __name__ == "__main__":
    main()
