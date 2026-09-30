# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AgriSim: Geospatial Farming Simulator & Predictive AI Guide** — a map-driven agricultural decision-support platform targeting Indian smallholder farms. The system follows the pipeline: **MAP → RAINFALL → RAINFALL FORECAST → REGIONAL SOIL → CROP RECOMMENDATION → LAND/BUDGET → SIMULATION → YIELD/COST → FARMING ROADMAP**.

Core components:

- Interactive Leaflet.js map for location selection (lat/long → district via PostGIS)
- Historical rainfall analysis + time-series forecasting (Prophet, XGBoost, LSTM)
- Spatial soil database (PostGIS) with region→soil-type mappings
- ML-based crop recommendation (XGBoost/LightGBM) using rainfall forecast + soil + climate features
- Farm simulation engine: plant capacity, cost breakdown, yield estimation, market value, risk
- Farming roadmap generator: crop growth stages → interactive calendar
- SHAP explainability for all ML models
- Optional add-ons: soil image classification (CNN), AI chatbot, plant disease detection

## Commands

### Python Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Generate the synthetic dataset (10,000 rows, Indian crops + Digital Twin logic)
python data/generate_dataset.py

# Train all models (RF + XGBoost with GridSearchCV). Saves .pkl files to models/
python train_models.py

# Generate SHAP explainability plots (beeswarm, dependence, waterfall)
python shap_analysis.py

# Prepare train/val/test splits from raw datasets
python training_data/prepare_training_data.py

# Fix malformed CSV headers
python fix_header.py
```

### Frontend

The frontend is a static HTML/CSS SPA (no build step, no npm). It deploys to GitHub Pages via GitHub Actions.

```bash
# View the app locally — just open the file
open frontend/index.html    # macOS
# or
start frontend/index.html   # Windows
```

### CI/CD

- GitHub Actions workflow: `.github/workflows/static.yml` — auto-deploys `frontend/` to GitHub Pages on every push to `main`.
- To trigger manually: push to `main` branch or use "Run workflow" in the Actions tab.

### Running Tests

This project does not have a formal test suite. Validation is performed by:

1. Running `train_models.py` and confirming metrics print without errors.
2. Running `shap_analysis.py` and confirming SHAP plots save to `output/shap/`.
3. Opening `frontend/index.html` and verifying interactive NPK sliders and tab navigation render correctly.

### Linting

No formal linter is configured. Python style follows PEP 8. Frontend CSS uses BEM-style component naming with `kebab-case` and design tokens in `:root`.

## Project Architecture

```
FinalYearProject/
├── frontend/
│   ├── index.html        # Glassmorphism SPA (HTML only, no JS framework)
│   └── styles.css        # Neon-themed glassmorphism design system
├── data/
│   ├── generate_dataset.py          # Synthetic 10k-row dataset generator
│   ├── advanced_agri_dataset.csv    # Generated dataset (10k rows)
│   ├── preprocessed_agri_data.csv   # Preprocessed version
│   └── soil_health_data.csv         # Original synthetic dataset
├── notebooks/
│   ├── eda_and_preprocessing.ipynb  # Jupyter EDA notebook
│   └── eda_and_preprocessing.py     # Python export of EDA notebook
├── training_data/
│   ├── *.csv                        # Train/val/test splits per task
│   ├── feature_config.json          # Feature columns, target columns
│   ├── *_scaler.pkl                 # StandardScaler artifacts
│   ├── *_label_encoder.pkl          # Label encoder artifacts
│   └── prepare_training_data.py     # Data splitting script
├── datasets/                        # Raw downloaded datasets (5 sources)
│   ├── 01_crop_recommendation/
│   ├── 02_fertilizer_recommendation/
│   ├── 03_crop_production_india/
│   ├── 04_rainfall_india/
│   └── 05_crop_yield_prediction/
├── models/                          # Trained model artifacts (generated, not committed)
│   ├── best_*_model.pkl             # Best-per-task models
│   ├── rf_*_model.pkl               # Random Forest models
│   ├── xgb_*_model.pkl              # XGBoost models
│   └── model_evaluation_results.json
├── output/
│   ├── *.png                        # Distribution & correlation charts
│   └── shap/                        # SHAP explainability plots
├── train_models.py                  # Stage 4: Model training pipeline
├── shap_analysis.py                 # Stage 4: SHAP explainability analysis
├── requirements.txt                 # Python dependencies
├── .github/workflows/static.yml     # CI/CD — deploys frontend to Pages
├── PROJECT_ROADMAP.md               # 7-stage roadmap with learning resources
├── STAGE_1_*.md                     # Literature survey documents
├── STAGE_1_CheatSheet.md            # Self-study / viva / defense cheat sheet
├── fix_header.py                    # CSV header repair helper
├── runs.json, papers.json, parsed_papers.txt  # Research metadata
└── README.md                        # Minimal (contains only "FinalYearProject" title)
```

## Key Architecture Decisions

### Data Flow

1. Raw datasets are downloaded to `datasets/` (5 source datasets from Kaggle/ICAR).
2. `data/generate_dataset.py` creates `data/advanced_agri_dataset.csv` — a synthetic 10,000-row dataset where yield, irrigation demand, and crop failure risk are computed via explicit Digital Twin penalty formulas.
3. `training_data/prepare_training_data.py` splits data into task-specific train/val/test CSVs and saves feature configs to `feature_config.json`.
4. `train_models.py` trains RF and XGBoost models per task, selects the best on validation, and saves `.pkl` artifacts to `models/`.
5. `shap_analysis.py` loads best models and generates explainability plots to `output/shap/`.

### Model Tasks (4 total)

| Task                        | Type                            | Target                                      | Classes/Range                   |
| --------------------------- | ------------------------------- | ------------------------------------------- | ------------------------------- |
| `crop_recommendation`       | Classification (22 crops)       | Crop_Type                                   | 22 classes                      |
| `fertilizer_recommendation` | Classification (14 fertilizers) | Recommended_Fertilizer                      | 14 classes                      |
| `yield_prediction`          | Regression                      | Yield_tons_per_ha                           | 0.1–70 tons/ha                  |
| `advanced_yield`            | Multi-output                    | Yield, Irrigation Demand, Crop Failure Risk | 2 regressors + 1 classification |

### Digital Twin Logic

The Digital Twin simulation is embedded in the dataset generation formula and the frontend slider logic. Yield is modified by penalties (Nitrogen deficiency = 0.2, Phosphorus = 0.1, Potassium = 0.1, pH = 0.15, Temperature = 0.15, Rainfall = 0.3), capped at 95% loss. Irrigation demand is computed from rainfall and moisture deficits. Crop failure risk is binned: 2 (High > 0.6 penalty), 1 (Medium > 0.3 penalty or high irrigation), 0 (Low).

### Frontend SPA Structure

The SPA in `frontend/index.html` uses:

- A sidebar navigation with tabs (Overview, Field Status, AI Analytics, Digital Twin, Settings).
- Glassmorphism panels with neon-green (`#39ff14`) / neon-cyan (`#00ffff`) accent colors.
- Interactive NPK sliders (native HTML `range` inputs with custom styling).
- Digital Twin dial (`--neon-green` ring rotation) showing risk simulation.
- SHAP explainability section with bar charts and feature importance waterfall preview.
- A roadmap timeline visualization at the bottom of the Overview tab.
- Responsive design: two-column grid on desktop, single-column below 1024px.

### Model Selection

- Classification: best model selected by validation `f1_macro`.
- Regression: best model selected by validation `r2`.
- Hyperparameter tuning uses `GridSearchCV` with `cv=3`.
- Both models are saved as `.pkl` (e.g., `rf_crop_recommendation_model.pkl`, `xgb_yield_prediction_model.pkl`).
- The selected best model is also saved with a `best_` prefix for downstream compatibility.

## Environment Notes

- All Python scripts use `BASE_DIR = r"c:\Users\USER\Downloads\FinalYearProject"` (hardcoded Windows path). Update scripts if moving the project.
- Python scripts use `matplotlib.use('Agg')` for non-interactive figure saving — no display required.
- The `shap` library requires `xgboost` or `scikit-learn` tree models; `TreeExplainer` is used first with fallback to `shap.Explainer`.
- Frontend uses Google Fonts (`Orbitron`, `Rajdhani`) — requires internet access to render.
- `.gitignore` excludes `models/`, `output/`, and `__pycache__/`.

## Important File References

- `feature_config.json` in `training_data/` — defines `input_features`, `target_column` (or `target_columns` for multi-output) per task. All training and SHAP scripts read this.
- `train_models.py` lines 56-78 — hyperparameter grids for RF and XGBoost.
- `frontend/index.html` — the SPA HTML. CSS is in `frontend/styles.css` (no `<style>` block in the HTML file itself — it's linked via `<link rel="stylesheet">`).

## Recent Uncommitted Changes

As of the latest git status, these files are modified or untracked:

- Modified: `frontend/index.html`, `frontend/styles.css`, `requirements.txt`
- Untracked: `datasets/`, `progress.md`, `shap_analysis.py`, `train_models.py`, `training_data/`
