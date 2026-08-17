"""
PCA visualization on scaled classification features (2 components).

Mirrors notebook cell 24. Saves PCA model to models/pca.pkl.
"""

from __future__ import annotations

import pickle

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA

from paths import DATA_PROCESSED, DF_FEAT_PATH, MODELS_DIR, PALETTE, PLOTS_DIR


def run_pca(df_feat: pd.DataFrame) -> PCA:
    """Fit PCA on scaled classification features and save projection plot."""
    X_cls_scaled = pd.read_parquet(DATA_PROCESSED / "X_cls_scaled.parquet")
    y_cls = df_feat["Career_Label"].values

    with open(MODELS_DIR / "encoder.pkl", "rb") as f:
        encoders = pickle.load(f)
    career_classes = encoders["career_classes"]

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_cls_scaled)

    fig, ax = plt.subplots(figsize=(11, 7))
    for i, label in enumerate(career_classes):
        mask = y_cls == i
        ax.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            label=label,
            alpha=0.75,
            s=55,
            color=PALETTE[i % len(PALETTE)],
            edgecolors="white",
            linewidth=0.4,
        )

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}% variance)")
    ax.set_title("PCA — 2D Projection of Career Classes (v2.0 dataset)", fontweight="bold")
    ax.legend(loc="upper right", framealpha=0.85)
    plt.tight_layout()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(PLOTS_DIR / "pca_projection.png", bbox_inches="tight")
    plt.close()

    print(f"Total variance explained: {pca.explained_variance_ratio_.sum() * 100:.1f}%")
    return pca


def main() -> None:
    df_feat = pd.read_parquet(DF_FEAT_PATH)
    pca = run_pca(df_feat)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    pca_path = MODELS_DIR / "pca.pkl"
    with open(pca_path, "wb") as f:
        pickle.dump(pca, f)
    print(f"PCA model saved to {pca_path}")


if __name__ == "__main__":
    main()
