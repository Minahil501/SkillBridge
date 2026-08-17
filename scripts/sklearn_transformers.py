"""Custom sklearn transformers mirroring the SkillBridge notebook pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder


class DataCleaner(BaseEstimator, TransformerMixin):
    """Impute missing values and winsorize outliers using IQR (notebook section 2)."""

    def __init__(self, exclude_from_outlier=None):
        self.exclude_from_outlier = exclude_from_outlier or ["Employability_Score"]
        self.num_imputer_ = None
        self.cat_imputer_ = None
        self.outlier_bounds_ = {}

    def fit(self, X, y=None):
        X = pd.DataFrame(X).copy()
        num_cols = X.select_dtypes(include="number").columns
        cat_cols = X.select_dtypes(include=["object", "category"]).columns

        num_missing = num_cols[num_cols.isin(X.columns) & X[num_cols].isnull().any()].tolist()
        cat_missing = cat_cols[cat_cols.isin(X.columns) & X[cat_cols].isnull().any()].tolist()

        if num_missing:
            self.num_imputer_ = SimpleImputer(strategy="median")
            self.num_imputer_.fit(X[num_missing])

        if cat_missing:
            self.cat_imputer_ = SimpleImputer(strategy="most_frequent")
            self.cat_imputer_.fit(X[cat_missing])

        numeric_features = X.select_dtypes(include="number").columns.tolist()
        numeric_features = [c for c in numeric_features if c not in self.exclude_from_outlier]

        for col in numeric_features:
            Q1, Q3 = X[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            n_out = ((X[col] < lower) | (X[col] > upper)).sum()
            if n_out > 0:
                self.outlier_bounds_[col] = {"lower": lower, "upper": upper}

        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        num_cols = X.select_dtypes(include="number").columns
        cat_cols = X.select_dtypes(include=["object", "category"]).columns

        if self.num_imputer_ is not None:
            cols = self.num_imputer_.feature_names_in_.tolist()
            X[cols] = self.num_imputer_.transform(X[cols])

        if self.cat_imputer_ is not None:
            cols = self.cat_imputer_.feature_names_in_.tolist()
            X[cols] = self.cat_imputer_.transform(X[cols])

        for col, bounds in self.outlier_bounds_.items():
            if col in X.columns:
                X[col] = X[col].clip(bounds["lower"], bounds["upper"])

        return X


class CategoricalEncoder(BaseEstimator, TransformerMixin):
    """Ordinal encoding for Project_Complexity from notebook cell 14.

    Gender is intentionally not encoded into a model feature: an audit found
    it carried no meaningful predictive signal (absent from both top-25
    SelectKBest feature lists), so it was dropped as an unjustified basis for
    an employability/career decision. See README.md "Bias Audit".
    """

    def __init__(self):
        self.ord_enc_ = OrdinalEncoder(categories=[["Low", "Medium", "High"]])
        self.le_career_ = LabelEncoder()

    def fit(self, X, y=None):
        X = pd.DataFrame(X).copy()
        self.ord_enc_.fit(X[["Project_Complexity"]])
        if "Recommended_Career_Path" in X.columns:
            self.le_career_.fit(X["Recommended_Career_Path"])
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        X["Project_Complexity_Enc"] = self.ord_enc_.transform(X[["Project_Complexity"]])
        if "Recommended_Career_Path" in X.columns and hasattr(self.le_career_, "classes_"):
            X["Career_Label"] = self.le_career_.transform(X["Recommended_Career_Path"])
        return X

    @property
    def career_classes_(self):
        return self.le_career_.classes_


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Engineered features from notebook cell 18."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        X["Language_Index"] = (X["Python_Skill"] + X["JavaScript_Skill"]) / 2
        X["Academic_Index"] = X["CGPA"] * (X["Attendance_Percentage"] / 100)
        X["Industry_Readiness"] = (
            X["Internship_Experience"] * 25
            + X["Certifications_Count"] * 8
            + X["Workshops_Attended"] * 4
        )
        X["Competitive_Edge"] = (
            X["Hackathons_Participated"] * 10
            + X["Coding_Contest_Rating"] / 100
            + X["GitHub_Repo_Count"] * 2
        )
        X["Comm_Tech_Ratio"] = X["Soft_Skill_Index"] / (X["Technical_Skill_Index"] + 1e-5)
        X["DS_Python_Synergy"] = X["ML_Score"] * X["Python_Skill"] / 100
        X["Web_JS_Synergy"] = X["WebDev_Score"] * X["JavaScript_Skill"] / 100
        X["SE_Core_Strength"] = X["DSA_Score"] * X["Programming_Score"] / 100
        X["DA_Core_Strength"] = X["Database_Score"] * X["Python_Skill"] / 100
        X["Tech_Soft_Product"] = X["Technical_Skill_Index"] * X["Soft_Skill_Index"]
        return X


class ColumnSubset(BaseEstimator, TransformerMixin):
    """Select a fixed list of columns before feature selection."""

    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return pd.DataFrame(X)[self.columns]
