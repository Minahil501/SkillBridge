"""Shared path constants for the SkillBridge ML project."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "DataSet_SkillBridge_modified.csv"
DATA_INTERIM = PROJECT_ROOT / "data" / "interim"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
PLOTS_DIR = PROJECT_ROOT / "data" / "plots"
MODELS_DIR = PROJECT_ROOT / "models"

DF_CLEAN_PATH = DATA_INTERIM / "df_clean.parquet"
DF_ENCODED_PATH = DATA_INTERIM / "df_encoded.parquet"
DF_FEAT_PATH = DATA_PROCESSED / "df_feat.parquet"
METADATA_PATH = DATA_PROCESSED / "metadata.json"

TARGET_REG = "Employability_Score"
TARGET_CLS = "Recommended_Career_Path"

BASE_FEATURES = [
    "CGPA",
    "Attendance_Percentage",
    "DSA_Score",
    "Programming_Score",
    "Database_Score",
    "WebDev_Score",
    "ML_Score",
    "Python_Skill",
    "JavaScript_Skill",
    "Project_Complexity_Enc",
    "Communication_Score",
    "Presentation_Score",
    "Problem_Solving_Score",
    "Leadership_Score",
    "Teamwork_Score",
    "Aptitude_Test_Score",
    "Projects_Count",
    "Certifications_Count",
    "Hackathons_Participated",
    "Internship_Experience",
    "GitHub_Repo_Count",
    "LinkedIn_Profile_Strength",
    "Volunteer_Activities",
    "Research_Papers",
    "Workshops_Attended",
    "Coding_Contest_Rating",
    "Mock_Interview_Score",
    "English_Proficiency_Score",
    "Technical_Skill_Index",
    "Soft_Skill_Index",
    "Experience_Index",
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

PALETTE = ["#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED", "#0891B2"]
