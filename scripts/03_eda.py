"""
Exploratory data analysis and visualization for the SkillBridge dataset.

Mirrors notebook EDA cells: info/describe, outlier plots, correlation heatmap,
distributions, 3D plots, and career skill profiles.
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from paths import DF_CLEAN_PATH, PALETTE, PLOTS_DIR

warnings.filterwarnings("ignore")

plt.rcParams.update(
    {
        "figure.dpi": 120,
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)
sns.set_palette(PALETTE)


def run_eda(df_clean: pd.DataFrame, plots_dir=PLOTS_DIR) -> None:
    """Generate EDA outputs and save plots."""
    plots_dir.mkdir(parents=True, exist_ok=True)

    print("-------------------------------------Dataset Info--------------------------------")
    df_clean.info()
    print("\n---------------------------------Basic Statistics------------------------------")
    print(df_clean.describe().round(2).to_string())

    missing = df_clean.isnull().sum()
    missing_pct = (missing / len(df_clean) * 100).round(2)
    missing_df = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
    missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values("Missing %", ascending=False)
    if missing_df.empty:
        print("\nNo missing values in the dataset.")
    else:
        print("\nMissing values:\n", missing_df.to_string())

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

    outlier_cols = list(outlier_summary.keys())
    if outlier_cols:
        n_cols = 3
        n_rows = int(np.ceil(len(outlier_cols) / n_cols))
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4.5 * n_rows))
        axes = np.array(axes).flatten()
        for i, col in enumerate(outlier_cols):
            ax = axes[i]
            ax.boxplot([df_clean[col]], labels=["After"], patch_artist=True, boxprops=dict(facecolor="lightblue"))
            ax.set_title(f"{col}\n({outlier_summary[col]['count']} outliers)", fontsize=9, pad=10)
        for j in range(len(outlier_cols), len(axes)):
            axes[j].axis("off")
        plt.suptitle("Outlier Treatment (IQR Method)", fontsize=14, fontweight="bold", y=1.0)
        plt.tight_layout(rect=[0, 0, 1, 1])
        plt.savefig(plots_dir / "outlier_boxplots.png", bbox_inches="tight")
        plt.close()

    drop_cols = ["Student_ID", "Gender", "Project_Complexity", "Recommended_Career_Path"]
    df_corr = df_clean.drop(columns=drop_cols, errors="ignore")
    corr_matrix = df_corr.corr()
    fig, ax = plt.subplots(figsize=(22, 18))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(
        corr_matrix,
        mask=mask,
        cmap="coolwarm",
        center=0,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 5.5},
        linewidths=0.3,
        ax=ax,
        vmin=-1,
        vmax=1,
    )
    ax.set_title("Feature Correlation Heatmap", fontsize=16, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(plots_dir / "correlation_heatmap.png", bbox_inches="tight")
    plt.close()

    dist_cols = [
        "CGPA",
        "Employability_Score",
        "Technical_Skill_Index",
        "Soft_Skill_Index",
        "Mock_Interview_Score",
        "Experience_Index",
    ]
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    axes = axes.flatten()
    for ax, col, color in zip(axes, dist_cols, PALETTE):
        data = df_clean[col].dropna()
        ax.hist(data, bins=25, color=color, alpha=0.8, edgecolor="white")
        ax.axvline(data.mean(), color="black", linestyle="--", linewidth=1.2, label=f"Mean={data.mean():.1f}")
        ax.set_title(col.replace("_", " "), fontweight="bold")
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")
        ax.legend(fontsize=8)
    plt.suptitle("Distribution of Key Features", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(plots_dir / "distributions.png", bbox_inches="tight")
    plt.close()

    careers = df_clean["Recommended_Career_Path"].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(careers)))
    color_map = dict(zip(careers, colors))
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")
    for career in careers:
        subset = df_clean[df_clean["Recommended_Career_Path"] == career]
        ax.scatter(
            subset["Programming_Score"],
            subset["DSA_Score"],
            subset["ML_Score"],
            s=subset["Employability_Score"] * 2,
            c=[color_map[career]],
            alpha=0.5,
            edgecolors="w",
            linewidth=0.3,
            label=career,
        )
    ax.set_xlabel("Programming Score", fontweight="bold", labelpad=10)
    ax.set_ylabel("DSA Score", fontweight="bold", labelpad=10)
    ax.set_zlabel("ML Score", fontweight="bold", labelpad=10)
    ax.set_title("3D Bubble Plot: Skills vs Employability", fontsize=14, fontweight="bold", pad=20)
    ax.legend(loc="upper left", fontsize=8, bbox_to_anchor=(1.05, 1))
    ax.view_init(elev=20, azim=135)
    plt.tight_layout()
    plt.savefig(plots_dir / "3d_bubble_plot.png", bbox_inches="tight", dpi=150)
    plt.close()

    skill_cols = [
        "ML_Score",
        "WebDev_Score",
        "DSA_Score",
        "Programming_Score",
        "JavaScript_Skill",
        "Python_Skill",
        "Database_Score",
    ]
    career_skill_means = df_clean.groupby("Recommended_Career_Path")[skill_cols].mean()
    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(skill_cols))
    width = 0.13
    for i, (career, row) in enumerate(career_skill_means.iterrows()):
        ax.bar(
            x + i * width,
            row.values,
            width,
            label=career,
            color=PALETTE[i % len(PALETTE)],
            alpha=0.85,
            edgecolor="white",
        )
    ax.set_xticks(x + width * 2.5)
    ax.set_xticklabels([c.replace("_", " ") for c in skill_cols], rotation=20, ha="right")
    ax.set_title("Domain Skill Profiles per Career Path", fontweight="bold", fontsize=14)
    ax.set_ylabel("Average Score")
    ax.legend(loc="upper right", framealpha=0.85)
    plt.tight_layout()
    plt.savefig(plots_dir / "skill_profiles_by_career.png", bbox_inches="tight")
    plt.close()

    print(f"\nEDA plots saved to {plots_dir}")


def main() -> None:
    df_clean = pd.read_parquet(DF_CLEAN_PATH)
    run_eda(df_clean)


if __name__ == "__main__":
    main()
