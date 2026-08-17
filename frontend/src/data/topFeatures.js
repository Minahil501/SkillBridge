// Top features by F-score, from data/processed/feature_selection.json (see README "Model performance").
// Global feature importance, not a per-prediction explanation.

export const LABELS = {
  Technical_Skill_Index: 'Technical Skill Index',
  Python_Skill: 'Python Skill',
  DA_Core_Strength: 'Data-Analysis Core Strength',
  SE_Core_Strength: 'Software-Engineering Core Strength',
  DSA_Score: 'DSA Score',
  Tech_Soft_Product: 'Technical × Soft Skill Product',
  Comm_Tech_Ratio: 'Communication/Technical Ratio',
  Project_Complexity_Enc: 'Project Complexity',
  Programming_Score: 'Programming Score',
  Coding_Contest_Rating: 'Coding Contest Rating',
  Web_JS_Synergy: 'Web Dev × JavaScript Synergy',
  DS_Python_Synergy: 'ML × Python Synergy',
  JavaScript_Skill: 'JavaScript Skill',
  ML_Score: 'ML Score',
  Language_Index: 'Language Index',
  Academic_Index: 'Academic Index',
  Industry_Readiness: 'Industry Readiness',
  Competitive_Edge: 'Competitive Edge',
  WebDev_Score: 'Web Dev Score',
  Aptitude_Test_Score: 'Aptitude Test Score',
  Database_Score: 'Database Score',
  CGPA: 'CGPA',
}

export const TOP_REG_FEATURES = [
  'Technical_Skill_Index', 'Python_Skill', 'DA_Core_Strength', 'SE_Core_Strength',
  'DSA_Score', 'Tech_Soft_Product', 'Comm_Tech_Ratio', 'Project_Complexity_Enc',
].map((key) => ({ key, label: LABELS[key] ?? key }))

export const TOP_CLS_FEATURES = [
  'Project_Complexity_Enc', 'Web_JS_Synergy', 'DS_Python_Synergy', 'Technical_Skill_Index',
  'JavaScript_Skill', 'ML_Score', 'SE_Core_Strength', 'DA_Core_Strength',
].map((key) => ({ key, label: LABELS[key] ?? key }))
