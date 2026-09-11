# SkillBridge

Turn a student's academic and technical profile into an **employability score**, a **recommended career path** across 6 options, and a plan to close the gap — with real model confidence, per-prediction explainability (SHAP), and a chat assistant for follow-up questions.

Full-stack ML portfolio project: a trained scikit-learn/XGBoost pipeline served through FastAPI, with a React dashboard on top.

---

## Contents

- [What it does](#what-it-does)
- [Tech stack](#tech-stack)
- [Getting started](#getting-started)
- [How the code works](#how-the-code-works)
- [Model performance](#model-performance)
- [Bias audit](#bias-audit)
- [API reference](#api-reference)
- [Project structure](#project-structure)
- [Deploying](#deploying)
- [Known limitations / next steps](#known-limitations--next-steps)

## What it does

1. **You fill in a profile** — 33 fields across academics, technical skills, soft skills, and activity/experience (or load a sample profile with one click).
2. **The model predicts**:
   - An **employability score** (0–100) with an uncertainty range
   - A **recommended career path** (Machine Learning Engineer, Web Developer, Data Analyst, Software Engineer, UI/UX Designer, or Cybersecurity Analyst), with confidence across _all six_, not just the winner
3. **You get a dashboard**: score gauge, confidence chart, a skill radar, category-strength breakdown, and the raw internally-computed metrics — all on one low-scroll Results page.
4. **You get an Insights page**: personalized recommendations, "why this result" reasoning toggleable between _population comparison_ (how your values compare to other students) and _real SHAP model attribution_ (how much each feature actually moved the model's output) — including a SHAP waterfall chart.
5. **You can ask follow-up questions** via a chat widget, grounded in your actual prediction, powered by a free-tier LLM.

## Tech stack

**Backend / ML**

| Tech                 | Role                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------- |
| Python               | Server-side language                                                                   |
| FastAPI + Uvicorn    | REST API (`/predict`, `/chat`)                                                         |
| Pydantic             | Request validation                                                                     |
| scikit-learn         | Pipelines, `StackingRegressor`, `VotingClassifier`, `SelectKBest`, custom transformers |
| XGBoost              | One of three members in each ensemble                                                  |
| SHAP                 | Real per-prediction explainability (`TreeExplainer`)                                   |
| pandas / numpy       | Data handling                                                                          |
| pyarrow              | Parquet I/O for pipeline intermediates                                                 |
| matplotlib / seaborn | EDA plots                                                                              |
| huggingface_hub      | Free LLM inference for the chat feature                                                |

**Frontend**

| Tech                   | Role                                                                   |
| ---------------------- | ---------------------------------------------------------------------- |
| React 19 + Vite        | UI + dev/build tooling                                                 |
| Tailwind CSS v4        | Styling / theme tokens                                                 |
| Framer Motion          | All animation                                                          |
| Hand-rolled inline SVG | Every chart (gauge, bars, radar, SHAP waterfall) — no charting library |

No database — the trained model is a static pickled artifact (`models/ml_pipeline.pkl`); no auth/session layer; no state-management library (plain `useState` lifted to `App.jsx` is enough at this size).

---

## Getting started

```powershell
# 1. Backend — from the project root
.\menv1\Scripts\Activate.ps1        # or create your own venv: python -m venv menv1
pip install -r requirements.txt      # only needed on a fresh venv
python run.py

# 2. Frontend — in a second terminal
cd frontend
npm install
npm run dev
```

Open the printed `localhost` URL (usually `5173`). The Vite dev server proxies `/predict` and `/chat` to `http://127.0.0.1:8000` (`frontend/vite.config.js`), and the backend has CORS enabled for local Vite ports.

**Chat setup (optional):** get a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) (no payment method required), then create a `.env` file in the project root:

```
HF_TOKEN=hf_...
```

`chat_api.py` loads it automatically via `python-dotenv` — no need to set it in every new terminal. Without it, everything else works — the chat endpoint just returns a clear error explaining what's missing.

**If you edit backend code:** `run.py` uses `--reload`, which is normally sufficient, but if responses seem stale after an edit (a field missing, old behavior persisting), fully close the terminal and restart rather than trusting the auto-reload — it's occasionally gotten stuck mid-session.

---

## How the code works

### Request lifecycle — a prediction

```
Browser (React)
      │  POST /predict  { 33 raw fields }
      ▼
backend/main.py            FastAPI route, Pydantic-validates the body
      │
      ▼
scripts/predict_api.py::predict()
      │
      ├─ loads models/ml_pipeline.pkl (pickled, cached after first request)
      ├─ runs the row through BOTH fitted sklearn pipelines (see below)
      ├─ reads StackingRegressor.transform() → base-learner spread → uncertainty range
      ├─ reads VotingClassifier.predict_proba() → confidence across all 6 careers
      ├─ runs shap.TreeExplainer on each pipeline's XGBoost sub-model → real attribution
      └─ compares engineered features to precomputed population stats → z-score reasoning
      │
      ▼
JSON response → React renders the Results + Insights pages
```

Only `scripts/predict_api.py`, `scripts/sklearn_transformers.py`, and `backend/main.py` execute at request time. Nothing from the training pipeline (`scripts/01`–`09`) runs live — those produced the static `models/ml_pipeline.pkl` this endpoint loads.

### The two trained models

Both are ensembles of the same three model families, so each cross-checks the others rather than relying on one algorithm's blind spots — extra insurance on a small (303-row) dataset.

- **Regression** (`StackingRegressor`): `RandomForestRegressor` + `XGBRegressor` + `GradientBoostingRegressor` as base learners, blended by a `Ridge` meta-learner fit via 5-fold CV.
- **Classification** (`VotingClassifier`, soft voting): `RandomForestClassifier` + `XGBClassifier` + `GradientBoostingClassifier`, averaging class probabilities rather than hard-voting labels — this is what makes real per-class confidence possible.

### The pipeline every row passes through

Both models sit behind an identical 6-step sklearn `Pipeline` (`scripts/sklearn_transformers.py`), fit independently per target:

```
raw input → clean → encode → engineer → subset → select(k=25) → scale → model
```

| Step                 | What it does                                                                                                                                                                                     |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `DataCleaner`        | Median/mode imputation, IQR-based outlier winsorization (bounds learned from training data)                                                                                                      |
| `CategoricalEncoder` | Ordinally encodes `Project_Complexity` (Low/Medium/High)                                                                                                                                         |
| `FeatureEngineer`    | Computes 10 derived features from raw scores — e.g. `DS_Python_Synergy = ML_Score × Python_Skill / 100`, capturing that _combinations_ of skills (not just individual scores) predict career fit |
| `ColumnSubset`       | Narrows to a fixed 41-feature set (raw + engineered)                                                                                                                                             |
| `SelectKBest`        | Statistical selection down to the top 25 features (`f_regression` / `f_classif` — different per target)                                                                                          |
| `StandardScaler`     | Zero-mean/unit-variance normalization                                                                                                                                                            |

### Training pipeline (offline, produces the artifacts above)

Run these **in this order** — the numbered filenames don't match the true dependency order at a glance, so it's worth knowing:

| Step | Script                              | Produces                                                         |
| ---- | ----------------------------------- | ---------------------------------------------------------------- |
| 1    | `scripts/01_load_data.py`           | `data/processed/metadata.json`                                   |
| 2    | `scripts/02_preprocessor.py`        | `data/interim/df_clean.parquet`                                  |
| 3    | `scripts/03_eda.py` (optional)      | `data/plots/*.png`                                               |
| 4    | `scripts/04_encoding.py`            | `data/interim/df_encoded.parquet`, `models/encoder.pkl`          |
| 5    | `scripts/05_feature_engineering.py` | `data/processed/df_feat.parquet`                                 |
| 6    | `scripts/06_feature_selection.py`   | `data/processed/feature_selection.json`, `feature_selectors.pkl` |
| 7    | `scripts/07_scaler.py`              | `data/processed/X_*_scaled.parquet`, `models/scaler.pkl`         |
| 8    | `scripts/08_pca.py`                 | `models/pca.pkl`, `data/plots/pca_projection.png`                |
| 9    | `scripts/09_train.py`               | `models/ml_pipeline.pkl`, `models/training_metrics.json`         |

Steps 4–8 mirror the exploratory notebook and **aren't required to serve predictions** — `09_train.py` is fully self-contained, re-implementing clean → encode → engineer inline rather than depending on steps 4–8's intermediate files. Only its output (`models/ml_pipeline.pkl`) is loaded at inference time.

### Request lifecycle — chat

```
Browser → POST /chat { messages[], context: {score, career, probabilities} }
      → scripts/chat_api.py::chat()
      → builds a system prompt grounded in the actual prediction
      → huggingface_hub.InferenceClient.chat_completion() against Qwen/Qwen2.5-7B-Instruct
      → { reply }
```

No conversation state is stored server-side — the frontend resends the full message history each turn (same statelessness as the Messages API pattern).

---

## Model performance

| Regression model                 | R²     | MAE   | RMSE  |
| -------------------------------- | ------ | ----- | ----- |
| Ridge Regression                 | 0.9315 | 2.490 | 2.896 |
| Random Forest                    | 0.9401 | 2.160 | 2.708 |
| XGBoost                          | 0.9484 | 2.025 | 2.514 |
| **Stacking Ensemble (deployed)** | 0.9442 | 2.142 | 2.613 |

| Classification model           | Accuracy | F1 (macro) | Precision | Recall |
| ------------------------------ | -------- | ---------- | --------- | ------ |
| **Voting Ensemble (deployed)** | 0.9508   | 0.9519     | 0.9577    | 0.95   |

Career classes: `0 Cybersecurity Analyst`, `1 Data Analyst`, `2 Machine Learning Engineer`, `3 Software Engineer`, `4 UI/UX Designer`, `5 Web Developer`.

## Bias audit

The raw dataset includes `Gender`. The original pipeline encoded and fed it to both models — a demographic attribute has no legitimate causal relationship to employability or career fit, so using it as a model input was an unjustified basis for a decision that could affect a real student.

**Finding:** `Gender_Enc` never appeared in either model's top-25 `SelectKBest` list, even before removal.

**Action:** removed `Gender` from the encoder, the trained feature set, and the API schema entirely. The API no longer asks for or uses gender in any way.

**Result:** retrained metrics are **identical to 4 decimal places** — removing it cost zero accuracy, confirming it was dead weight both statistically and ethically.

---

## API reference

### `POST /predict`

```json
{
  "employability_score": 80.98,
  "employability_range": [80.38, 81.59],
  "recommended_career_path": "Cybersecurity Analyst",
  "career_class_index": 0,
  "career_probabilities": {
    "Cybersecurity Analyst": 0.5365,
    "Data Analyst": 0.221,
    "...": "..."
  },
  "confidence": 0.5365,
  "reasoning": { "employability": ["..."], "career": ["..."] },
  "engineered_features": { "Language_Index": 57.5, "...": "..." },
  "shap_reasoning": { "employability": ["..."], "career": ["..."] },
  "shap_waterfall": {
    "employability": { "base_value": 83.7, "points": ["..."], "total": 94.48 },
    "career": ["..."]
  }
}
```

| Field                                 | What it is                                                                                                                                                                                                                             |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `employability_range`                 | Uncertainty band from how much the 3 base regressors disagree                                                                                                                                                                          |
| `career_probabilities` / `confidence` | Real `predict_proba` across all 6 careers, not just the top pick                                                                                                                                                                       |
| `reasoning`                           | Top-weighted features vs. the training population (z-score + label), from `models/feature_stats.json`                                                                                                                                  |
| `engineered_features`                 | The 10 derived scores `FeatureEngineer` computes internally — shown for transparency; each is a fixed function of the raw fields already submitted, not independently editable                                                         |
| `shap_reasoning`                      | Real per-prediction SHAP attribution from each pipeline's XGBoost sub-model — explains that component specifically, not the full ensemble (no exact SHAP decomposition exists for a `StackingRegressor`/`VotingClassifier` as a whole) |
| `shap_waterfall`                      | Same SHAP contributions as a baseline → feature-by-feature → final-value cumulative sequence, for the Insights-page line chart. Non-top-6 features fold into "Other features" so it always sums exactly                                |

### `POST /chat`

```json
{
  "messages": [{ "role": "user", "content": "How can I improve my score?" }],
  "context": {
    "employability_score": 80.98,
    "recommended_career_path": "Cybersecurity Analyst",
    "confidence": 0.54,
    "career_probabilities": { "...": 0.0 }
  }
}
```

→ `{"reply": "..."}`. Model defaults to `meta-llama/Llama-3.1-8B-Instruct:cheapest`, overridable via `HF_CHAT_MODEL`. The `:cheapest` suffix routes to the lowest-priced provider serving that model; a free Hugging Face account gets $0.10 of inference credit per month, and once it runs out `/chat` returns **503** with a plain-language message while the rest of the app keeps working.

Limits: 1–10 messages per request, each 1–3000 characters, roles `user` / `assistant` only — anything else returns **422**. Too many requests returns **429**: 8 per minute per client, 50 per day across all clients. The frontend sends only the last 10 messages of a conversation.

---

## Project structure

```
backend/main.py          FastAPI app — POST /predict, POST /chat, serves frontend/dist for everything else
scripts/
  01_load_data.py … 09_train.py   numbered training pipeline (see table above)
  paths.py                 path constants, target names, BASE_FEATURES
  sklearn_transformers.py  custom Pipeline steps (DataCleaner, CategoricalEncoder, FeatureEngineer, ColumnSubset)
  predict_api.py           predict() — loads models/ml_pipeline.pkl (cached), runs inference + SHAP
  chat_api.py              Hugging Face Inference integration for the chat
frontend/src/
  components/               LandingPage, InputForm, ResultView, InsightsView, ChatWidget, charts (SVG)
  data/                      form field definitions, sample profiles, feature label maps
  lib/api.js                 fetch wrappers for /predict and /chat
data/                     raw → interim → processed parquet files, EDA plots
models/                   trained artifacts (ml_pipeline.pkl + feature_stats.json are used at inference time)
run.py                    uvicorn launcher
```

## Deploying

The model only runs inside the FastAPI backend — React can't run scikit-learn/XGBoost in the browser, so the frontend stays a thin client calling `/predict` and `/chat` over HTTP.

Deployed as a single Docker web service on Render: a multi-stage build compiles the React
frontend (`npm run build`) and copies the static output into a Python/FastAPI image, which serves
`/predict` and `/chat` as API routes and everything else as the built SPA — same origin, no CORS
needed in production. See `Dockerfile`. The `HF_TOKEN` used by `/chat` is set as a Render
environment variable, not committed.

`render.yaml` defines the service as a Render Blueprint: in the Render dashboard, **New → Blueprint** → pick this repo, and Render asks for the `HF_TOKEN` value on the first deploy. On the free plan the service sleeps after 15 minutes without traffic, and the first visit after that takes about a minute to wake it.

## Known limitations / next steps

- Dataset is small (303 rows after dedup) — treat performance numbers as indicative, not production-grade.
- No auth or request logging. `/chat` is rate-limited in memory (8 messages per minute per client, 50 per day in total — sized to keep a month of demo traffic inside the $0.10 free inference credit) — enough for a demo, but the limits reset on every restart, and the per-client key comes from `X-Forwarded-For`, which a client can fake. `/predict` has no rate limit.
- No automated tests yet.
- Mobile responsiveness hasn't been thoroughly tested below ~640px.
