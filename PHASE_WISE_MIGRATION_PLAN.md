# AgriSim Project - Phase-Wise Migration Plan
## Transforming Existing Project to AgriSim Specification

---

### Executive Summary

This document provides a comprehensive audit of the existing "AI-Driven Nutrient Recommendation System with Digital Twin & XAI Capabilities" project against the **AgriSim Project Idea & System Blueprint** PDF. The goal is to **preserve completed work**, **correct architectural direction**, **modernize ML components**, and **gradually transform** the project into the AgriSim system.

---

## 1. Phase-Wise Migration Matrix

| Phase | Existing Status | What Can Be Reused | What Needs Modification | What Must Be Added | Priority |
|-------|-----------------|-------------------|------------------------|-------------------|----------|
| **Phase 1**<br>Literature Survey & Problem Definition | 🟢 **COMPLETED**<br>• 12 papers surveyed (2023-2026)<br>• Research gap identified: "Predict Only" → "Predict + Simulate"<br>• Problem statement, objectives, methodology documented<br>• Resource vault, cheat sheets created | • All literature survey work<br>• Research gap analysis (aligned with AgriSim)<br>• Problem definition structure<br>• Academic documentation quality | • Update problem statement to explicitly include **geospatial/map-driven** workflow<br>• Add rainfall forecasting & spatial soil identification to objectives<br>• Expand scope to include budget estimation & farming roadmap | • Geospatial agricultural decision support context<br>• Localized rainfall analysis literature<br>• Regional soil database literature<br>• Farm planning/roadmap literature | **LOW**<br>(Already 90% aligned) |
 | **Phase 2**<br>System Architecture & Requirements | 🟢 **COMPLETED**<br>• Architecture diagram created (`Phase_2_Architecture_and_Requirements.md`)
• FastAPI backend skeleton with routers, OpenAPI spec
• React component stubs for map, rainfall, soil, crop, simulation, roadmap
• PostgreSQL + PostGIS schema defined, Docker Compose file ready
• CI workflow, documentation updated | • Existing FastAPI/React codebase (aligned) | • No further architectural changes required; focus now on data ingestion and model implementation in Phase 3 |
 | **Phase 3**<br>Data Collection, Preprocessing & EDA | ✅ **COMPLETED**<br>• All 5 real datasets ingested (rainfall, soil, crop production, crop recommendation, fertilizer)<br>• District‑monthly rainfall time‑series built and stored (`training_data/rainfall_processed.csv`)<br>• Soil spatial data imported via `agrisim_backend/data_import/soil_spatial_import.py` and seeded in DB (district geometry & soil type mapping)<br>• Crop economics dataset added (`datasets/04_crop_economics/crop_economics.csv`) and integrated into training pipeline (`prepare_training_data.py` task 7)<br>• Full EDA notebook (`notebooks/eda_and_preprocessing.ipynb`) covering rainfall trends, soil distribution, economics features, class balance, and feature correlations<br>• Feature config (`training_data/feature_config.json`) updated with new columns and types | • **All 5 real datasets** now aligned with AgriSim objectives<br>• `prepare_training_data.py` extended to include economics & soil‑region features<br>• New script `soil_spatial_import.py` loads GeoJSON districts and populates PostGIS tables<br>• EDA notebook fully completed and exported charts in `output/` | • No remaining data‑collection work for Phase 3. All required datasets are present and pre‑processed. | • Rainfall monthly TS ready for forecasting models<br>• Soil table with geometry and soil‑type percentages ready for queries<br>• Crop economics table ready for cost‑based recommendation<br>• Comprehensive EDA reports for model developers | **COMPLETED** |
| **Phase 4**<br>Modern ML / AI Models & XAI | 🟡 **PARTIALLY COMPLETED**<br>• 4 tasks: crop rec, fertilizer rec, yield pred, advanced yield<br>• RF + XGBoost trained with GridSearchCV<br>• SHAP explainability implemented (bar, beeswarm, dependence, waterfall)<br>• Model evaluation saved (accuracy, F1, R²)<br>• Multi-output: yield, irrigation, risk | • **Training pipeline structure** (	rain_models.py) - well organized<br>• **SHAP/XAI infrastructure** (shap_analysis.py) - production ready<br>• Model evaluation methodology<br>• Feature config system<br>• Multi-output concept (yield + irrigation + risk) | • **Replace default RF/XGBoost with modern model evaluation**:<br>  - Rainfall Forecasting: SARIMA/Prophet → LSTM/GRU → TFT comparison<br>  - Crop Rec: XGBoost/LightGBM/CatBoost/HistGradientBoosting comparison<br>  - Yield: XGB/LGBM/CatBoost/NN regression comparison<br>  - Risk: Gradient boosting + calibration<br>• **Integrate XAI into NEW models** (not old ones)<br>• Remove fertilizer recommendation (not in AgriSim core) | • Rainfall forecasting models (time-series)<br>• Modern crop recommendation with soil+region features<br>• Yield prediction with economic features<br>• Irrigation demand model (if data supports)<br>• Crop failure risk classification (Low/Med/High)<br>• XAI for each selected model<br>• Model comparison & selection documentation | **CRITICAL**<br>(Core intelligence) |
| **Phase 5**<br>Digital Twin / Agricultural Simulation | 🟡 **PARTIALLY COMPLETED**<br>• Digital Twin concept embedded in synthetic data generator<br>• Frontend DigitalTwin.jsx component (UI only, mock data)<br>• Penalty-based yield/irrigation/risk formulas<br>• What-if scenario UI (Normal/Drought/Flood/Optimal) | • **Digital Twin concept** - core USP preserved<br>• Penalty-based simulation logic (formula-based)<br>• Frontend UI components (scenario selector, metrics, what-if actions)<br>• Simulation variables identified (rainfall, temp, nutrients, moisture, budget) | • **Connect simulation to REAL ML predictions** (not synthetic formulas)<br>• Input pipeline: Location + Rainfall + Forecast + Soil + Crop + Land + Budget<br>• Scenario engine: Modify rainfall, temperature, soil nutrients, irrigation, budget<br>• Output: Yield, cost, market value, risk, roadmap<br>• Remove hardcoded scenarios; make data-driven | • Simulation engine service (Python/FastAPI)<br>• Cost calculation module (seeds, fertilizer, irrigation, labor, etc.)<br>• Plant spacing calculator<br>• Market value estimation<br>• Farming roadmap/timeline generator<br>• User override capability for all assumptions | **HIGH**<br>(Unique differentiator) |
| **Phase 6**<br>Full-Stack Application Integration | 🟡 **PARTIALLY COMPLETED**<br>• React app with routing, context, components<br>• Pages: Dashboard, Farms, Crops, Weather, Alerts, Recommendations, Chat, Analytics, Settings<br>• UI components: Cards, Charts, Modals, Forms<br>• AI Chat component (UI only)<br>• Static HTML frontend also exists (glassmorphism SPA) | • **React frontend foundation** - modern, component-based<br>• AppContext state management<br>• Component library (common, charts, forms)<br>• Weather, Crops, Farms, Recommendations pages<br>• AI Chat UI (needs backend)<br>• Responsive design, design tokens | • **Complete UI redesign to match AgriSim user journey**:<br>  1. **Map View** (Leaflet.js) - PRIMARY entry point<br>  2. **Rainfall Dashboard** - historical + forecast charts<br>  3. **Soil Selection** - region-filtered dropdown<br>  4. **Crop Recommendation** - with reasoning<br>  5. **Simulation Setup** - land, budget, assumptions<br>  6. **Financial Dashboard** - cost, yield, revenue<br>  7. **Farming Roadmap** - interactive timeline<br>• Connect to FastAPI backend (not mock data)<br>• Deprecate static HTML frontend | • Interactive India map (Leaflet.js) with district boundaries<br>• Rainfall charts (historical + 12-month forecast)<br>• Soil type selector with region filtering<br>• Crop recommendation panel with XAI explanations<br>• Simulation parameter form<br>• Budget/cost breakdown dashboard<br>• Yield/revenue visualization<br>• Farming roadmap calendar/timeline<br>• Optional: Soil image upload, Plant disease detection, AI chatbot | **CRITICAL**<br>(User-facing product) |
| **Phase 7**<br>Testing, Validation & Final Documentation | 🔴 **NOT STARTED**<br>• No formal test suite<br>• Validation via manual runs only<br>• Some documentation (progress.md, roadmap)<br>• Deployment config (Vercel, GitHub Pages) | • Progress tracking documentation<br>• Deployment configs<br>• Project roadmap structure | • Implement comprehensive testing per AgriSim spec:<br>  - Geospatial, rainfall, ML, simulation, frontend<br>• Model validation with proper metrics<br>• End-to-end integration testing<br>• Academic documentation finalization | • Test suites (unit, integration, e2e)<br>• Geospatial validation (coordinates, regions, soil filtering)<br>• Rainfall forecast accuracy validation<br>• ML model comparison reports<br>• Simulation scenario testing<br>• Final thesis/report documentation<br>• API documentation | **HIGH**<br>(Academic requirement) |
---

## 2. Current Project Architecture

`
CURRENT ARCHITECTURE
FRONTEND: React App + Static HTML SPA
BACKEND: FastAPI (planned, not built)
ML: RF + XGBoost (4 tasks trained)
DATA: 5 Kaggle datasets + synthetic
DATABASE: CSV files only
MAPS: None
`

### Current Tech Stack
| Layer | Technology | Status |
|-------|------------|--------|
| Frontend | React 18 + Vite + Recharts + React Router | Built (UI only) |
| Frontend (Legacy) | Static HTML/CSS/JS (Glassmorphism) | Built |
| Backend | FastAPI (planned) | Not built |
| ML | Python, Scikit-learn, XGBoost, SHAP | Trained (4 tasks) |
| Data | 5 Kaggle datasets + synthetic 10k rows | Prepared |
| Database | None (CSV files) | Not implemented |
| Maps | None | Not implemented |
| Deployment | GitHub Pages (static), Vercel config | Partial |

---

## 3. AgriSim Target Architecture

`
AGRISIM TARGET ARCHITECTURE
FRONTEND: React + Leaflet.js (Map-first)
BACKEND: FastAPI with service layer
DATABASE: PostgreSQL + PostGIS
ML: Time-series (rainfall) + Tabular (crop/yield/risk)
`

### Target Tech Stack
| Layer | Technology | Justification |
|-------|------------|---------------|
| Frontend | React 18 + Vite + Leaflet.js + Recharts | Map-first, interactive charts |
| Backend | FastAPI (Python) | Async, auto-docs, ML integration |
| Database | PostgreSQL + PostGIS | Spatial queries for district/soil mapping |
| ML - Rainfall | Prophet / SARIMA to LSTM/GRU to TFT | Time-series forecasting |
| ML - Crop Rec | XGBoost / LightGBM / CatBoost / HistGradientBoosting | Tabular classification |
| ML - Yield | XGBoost / LightGBM / CatBoost / NN | Tabular regression |
| ML - Risk | Gradient Boosting + Calibration | Classification with probabilities |
| XAI | SHAP (TreeExplainer for tree models) | Consistent with existing work |
| Maps | Leaflet.js + GeoJSON (India districts) | Lightweight, no API key needed |
| Deployment | Docker + Cloud (AWS/Azure/GCP) | Production ready |

---

## 4. Major Differences

| Aspect | Current Project | AgriSim Target | Gap Severity |
|--------|-----------------|----------------|--------------|
| Entry Point | Dashboard with NPK sliders | Interactive India Map (Leaflet) | Critical |
| Location Input | Manual farm creation | Map click to lat/long to district | Critical |
| Rainfall | Single value input | Historical charts + 12-month forecast | Critical |
| Soil | Manual selection / NPK values | Region-filtered soil types from spatial DB | Critical |
| Crop Rec | NPK+pH+weather to 22 crops | Soil+Region+Rainfall+Climate to crops | High |
| Fertilizer Rec | Core feature (14 types) | REMOVED (not in AgriSim core) | Remove |
| Yield Prediction | Area+production+inputs | Crop+Land+Soil+Rainfall+Budget | High |
| Digital Twin | Penalty formulas + mock UI | Data-driven simulation engine | High |
| Budget/Cost | Not implemented | Full cost breakdown + market value | Critical |
| Farming Roadmap | Not implemented | Interactive timeline/calendar | Critical |
| Soil Image | Not implemented | Optional: Transfer learning | Optional |
| Plant Disease | Not implemented | Optional: Transfer learning | Optional |
| AI Chatbot | UI only | Optional: RAG-based farming assistant | Optional |
| Database | CSV files | PostgreSQL + PostGIS | Critical |

---

## 5. Phase-by-Phase Migration Plan

### PHASE 1: Literature Survey & Problem Definition - MOSTLY DONE
Timeline: Already completed (Weeks 1-4)
Action Items:
1. Update synopsis.md problem statement to include geospatial/map-driven workflow
2. Add rainfall forecasting & spatial soil identification to objectives
3. Expand scope to include budget estimation & farming roadmap
4. Add 3-5 papers on: geospatial agri-DSS, rainfall forecasting, spatial soil databases
5. Update PROJECT_ROADMAP.md to reflect AgriSim phases

Files to Modify: synopsis.md, PROJECT_ROADMAP.md, STAGE_1_Survey.md

---

### PHASE 2: System Architecture & Requirements - CRITICAL - START HERE
Timeline: Weeks 1-2 (Immediate)
Action Items:
1. Create new system architecture diagram matching AgriSim pipeline
2. Design PostgreSQL + PostGIS schema
3. Define API contracts for each service
4. Select ML model candidates for each task
5. Update CLAUDE.md with new architecture

Deliverables: Architecture diagram, DB schema, API spec, ML model selection doc

---

### PHASE 3: Data Collection, Preprocessing & EDA - HIGH
Timeline: Weeks 2-4
Action Items:

#### 3.1 Rainfall Data (EXISTING to ENHANCE)
- Source: datasets/04_rainfall_india/rainfall in india 1901-2015.csv (528k rows)
- Current: Processed with monsoon features in prepare_training_data.py task4
- Needed: District-level monthly time series for forecasting
- Action: Map SUBDIVISION to District, create monthly time series per district

#### 3.2 Soil Data (MISSING - CRITICAL)
- Current: Soil type as categorical in fertilizer dataset only
- Needed: Spatial dataset mapping District to Predominant Soil Type(s)
- Sources: ICAR-NBSSLUP soil maps, Soil Health Card data, ISRIC World Soil Information
- Action: Create soil_types table with geometry

#### 3.3 Crop Recommendation Data (EXISTING to RESTRUCTURE)
- Source: datasets/01_crop_recommendation/Crop_recommendation.csv
- Current: 7 features, no soil type, no region
- Needed: Add Soil Type + Region/District features
- Action: Join with soil data, augment with regional climate normals

#### 3.4 Crop Economics Data (MISSING - CRITICAL)
- Needed: Per-crop spacing, seed cost, fertilizer cost, labor cost, expected yield, market price
- Sources: crop_production.csv for yield baselines, Government cost reports, AGMARKNET prices
- Action: Build crop_economics table

#### 3.5 Optional CV Data (MISSING)
- Soil Images: ICAR soil image dataset / collect own
- Plant Disease: PlantVillage dataset (public, 54k+ images)

#### 3.6 EDA Requirements
- Temporal rainfall patterns per district
- Regional soil distribution
- Crop recommendation class balance
- Feature correlation with yield
- Missing value analysis per dataset

Files to Modify: prepare_training_data.py (add soil/economics tasks), create new EDA notebook

---

### PHASE 4: Modern ML / AI Models & XAI - CRITICAL
Timeline: Weeks 4-8
Action Items:

#### 4.1 Rainfall Forecasting (NEW - Core AgriSim)
Candidate Models: SARIMA, Prophet, LSTM/GRU, Temporal Fusion Transformer, XGBoost/LightGBM with temporal features
Data: District-monthly time series (1901-2015) to forecast next 12 months
Evaluation: MAE, RMSE, MAPE on holdout last 2-3 years per district

#### 4.2 Crop Recommendation (UPGRADE)
Candidate Models: Random Forest (baseline), XGBoost, LightGBM, CatBoost, HistGradientBoosting
Features: N,P,K,pH,rainfall,temp,humidity, SOIL_TYPE, REGION
Evaluation: Accuracy, F1-macro, F1-weighted, per-class metrics
XAI: SHAP TreeExplainer for all

#### 4.3 Yield Prediction (UPGRADE)
Candidate Models: Random Forest Reg (baseline), XGBoost, LightGBM, CatBoost, MLP Regressor
Features: Crop, Soil, Rainfall (hist+forecast), Land Area, Budget to inputs
Target: Yield (tons/ha)
Evaluation: MAE, RMSE, R2, MAPE
XAI: SHAP for regression

#### 4.4 Irrigation Demand (NEW - If Data Supports)
- Use rainfall deficit + crop water requirement + soil moisture
- Gradient boosting regression or physics-informed ML

#### 4.5 Crop Failure Risk (ENHANCE)
- Current: 3-class from penalty formula
- New: Probabilistic classification (Low/Medium/High) with calibrated probabilities

#### 4.6 XAI Integration
- Preserve shap_analysis.py infrastructure
- Adapt for new models (TreeExplainer works for all tree-based)
- Generate per-prediction explanations for frontend

Files to Create: 
- models/rainfall_forecasting.py
- models/crop_recommendation_v2.py
- models/yield_prediction_v2.py
- models/risk_prediction.py
- models/model_comparison.py
- Update train_models.py to new pipeline

---

### PHASE 5: Digital Twin / Agricultural Simulation - HIGH
Timeline: Weeks 6-9 (Overlaps with Phase 4)
Action Items:

#### 5.1 Simulation Engine Service (FastAPI)
Input: SimulationRequest with location, crop, land_area_ha, budget_inr, soil_type, rainfall_forecast, assumptions
Output: SimulationResult with plant_capacity, cost_breakdown, total_cost, yield_estimate, market_value, net_profit, risk_level, risk_probability, roadmap

#### 5.2 Cost Calculation Module
- Seeds: plants * seed_cost_per_plant
- Fertilizer: land_area * recommended_rate * price_per_kg
- Irrigation: irrigation_demand_mm * land_area * cost_per_mm
- Labor: land_area * labor_cost_per_ha * crop_duration_factor
- Land Prep: land_area * prep_cost_per_ha
- Plant Protection: land_area * protection_cost_per_ha
- Other: Contingency (5-10%)

#### 5.3 Yield Estimation
- Base yield from ML model (tons/ha)
- Adjust for: rainfall adequacy, soil suitability, management level
- final_yield = base_yield * rainfall_factor * soil_factor * management_factor

#### 5.4 Farming Roadmap Generator
- Crop-specific growth stages from literature
- Map to calendar dates based on planting date
- Activities: Land prep, sowing, fertilizer applications, irrigation, weeding, pest control, harvesting

#### 5.5 User Override
- Allow modifying: rainfall forecast, fertilizer rate, irrigation, budget allocation
- Re-run simulation instantly

Files to Create: simulation/engine.py, simulation/costs.py, simulation/roadmap.py, FastAPI endpoints

---

### PHASE 6: Full-Stack Application Integration - CRITICAL
Timeline: Weeks 8-12
Action Items:

#### 6.1 Backend (FastAPI) - NEW
agrisim/
  main.py
  api/map.py, rainfall.py, soil.py, crop_rec.py, simulation.py, roadmap.py
  services/rainfall_forecaster.py, crop_recommender.py, yield_predictor.py, risk_predictor.py, simulation_engine.py
  db/models.py, database.py
  core/config.py, security.py

#### 6.2 Frontend (React) - RESTRUCTURE
New Page Flow:
/ to MapView (Leaflet India map)
/rainfall/:districtId to RainfallDashboard
/soil/:districtId to SoilSelector
/crop-rec/:districtId to CropRecommendation
/simulation to SimulationSetup
/simulation/:id/results to FinancialDashboard
/roadmap/:id to FarmingRoadmap

#### 6.3 Key Frontend Components to Build
- MapView.jsx - Leaflet map with district boundaries, click handler
- RainfallCharts.jsx - Historical + Forecast charts
- SoilSelector.jsx - Dropdown with soil descriptions
- CropRecPanel.jsx - Ranked crops with SHAP bar charts
- SimulationForm.jsx - Land, budget, assumption sliders
- FinancialDashboard.jsx - Cost breakdown, yield gauge, revenue
- RoadmapTimeline.jsx - Calendar view with activities
- SHAPExplanation.jsx - Reusable waterfall/bar for any prediction

#### 6.4 State Management
- Replace AppContext with React Query / TanStack Query for server state
- Keep local UI state in context
- API client service layer

Files to Modify: Entire frontend/react-app/src/ restructure

---

### PHASE 7: Testing, Validation & Final Documentation - HIGH
Timeline: Weeks 12-14
Action Items:

#### 7.1 Testing
| Category | Tests |
|----------|-------|
| Geospatial | Valid/invalid coords, district lookup, soil filtering |
| Rainfall | Historical retrieval, forecast generation, missing data, accuracy |
| ML | Classification (acc, F1, cm), Regression (MAE, RMSE, R2), TS (MAE, MAPE) |
| Simulation | Budget/land/rainfall/soil/crop variations, edge cases |
| Frontend | API failures, loading, empty states, invalid inputs, responsive |

#### 7.2 Validation
- Model comparison reports (baseline vs modern)
- Forecast accuracy on holdout years
- Simulation sanity checks (costs > 0, yield reasonable)
- End-to-end user journey testing

#### 7.3 Documentation
- Final thesis/report
- API documentation (auto from FastAPI)
- Database schema docs
- Model cards (performance, limitations, intended use)
- User guide

---

## 6. Modern ML Model Candidates

### 6.1 Rainfall Forecasting (Time-Series)
| Model | Pros | Cons | Suitability |
|-------|------|------|-------------|
| SARIMA | Interpretable, statistical baseline, handles seasonality | Manual order selection, univariate, slow for many districts | Baseline |
| Prophet | Automatic seasonality, handles holidays/missing, interpretable | Less flexible, univariate by default | Baseline |
| LSTM/GRU | Captures long dependencies, multivariate, scalable | Needs more data, black box, tuning effort | Strong candidate |
| Temporal Fusion Transformer | SOTA for TS, interpretability, handles static covariates | Complex, needs large data, heavy compute | If data justifies |
| XGBoost/LightGBM + Features | Fast, handles tabular features, feature importance | Requires feature engineering | Strong candidate |

Recommendation: Start with Prophet + XGBoost (temporal features) as baselines, then LSTM/GRU if district-level data sufficient.

### 6.2 Crop Recommendation (Tabular Classification)
| Model | Pros | Cons | Suitability |
|-------|------|------|-------------|
| Random Forest | Baseline, robust, handles mixed features | Lower ceiling than boosting | Baseline |
| XGBoost | High accuracy, speed, SHAP support | Tuning sensitive | Primary |
| LightGBM | Faster, handles categorical, leaf-wise | Can overfit small data | Primary |
| CatBoost | Best categorical handling, ordered boosting | Slower training | Primary |
| HistGradientBoosting | Native missing value handling, fast | Less tuning control | Candidate |

Recommendation: Compare XGBoost vs LightGBM vs CatBoost with 5-fold CV. Select best F1-macro. Use SHAP for all.

### 6.3 Yield Prediction (Tabular Regression)
| Model | Pros | Cons | Suitability |
|-------|------|------|-------------|
| Random Forest Reg | Baseline, robust | Lower ceiling | Baseline |
| XGBoost Reg | High accuracy, SHAP | Tuning | Primary |
| LightGBM Reg | Fast, categorical | Overfit risk | Primary |
| CatBoost Reg | Categorical native | Slower | Primary |
| MLP Regressor | Non-linear interactions | Needs scaling, tuning | If tree models plateau |

Recommendation: Same as crop rec - compare XGBoost/LightGBM/CatBoost on MAE/RMSE/R2.

### 6.4 Crop Failure Risk (Classification with Probabilities)
| Model | Pros | Cons | Suitability |
|-------|------|------|-------------|
| XGBoost/LightGBM/CatBoost | Probability outputs, SHAP, calibrated | Need calibration (Platt/Isotonic) | Primary |
| CalibratedClassifierCV | Guarantees calibrated probs | Extra CV step | Use with above |

Recommendation: Best tree model + CalibratedClassifierCV to Low/Med/High with confidence.

---

## 7. Features That Should Be Preserved

| Feature | Location | Reason |
|---------|----------|--------|
| Literature survey & research gap | STAGE_1_*.md, synopsis.md | Academic foundation, well done |
| 5 Kaggle datasets | datasets/ | Real data, already downloaded & organized |
| Data preparation pipeline | training_data/prepare_training_data.py | Modular, reproducible, feature config system |
| SHAP explainability infrastructure | shap_analysis.py | Production-ready, generates all plot types |
| Model training framework | train_models.py | GridSearchCV, multi-task, evaluation, serialization |
| Digital Twin concept | generate_dataset.py, DigitalTwin.jsx | Core USP, formula logic reusable |
| React frontend foundation | frontend/react-app/src/ | Modern stack, component library, routing, context |
| UI component library | frontend/react-app/src/components/common/ | Reusable: Card, Button, ChartCard, Modal, etc. |
| AI Chat UI | frontend/react-app/src/components/chat/ | Good foundation for optional chatbot |
| Deployment configs | vercel.json, .github/workflows/ | CI/CD ready |
| Progress documentation | progress.md, Comprehensive_Project_Review.md | Academic tracking |

---

## 8. Features That Should Be Reworked

| Feature | Current State | Required Change |
|---------|---------------|-----------------|
| System Architecture | NPK-slider to ML predictions | Map to Rainfall to Soil to Crop to Budget to Simulation to Roadmap |
| Crop Recommendation Features | NPK+pH+temp+humidity+rainfall (7) | Add Soil Type + Region/District |
| Yield Prediction Features | Area+Production+Inputs+Encoded | Use Crop+Soil+Rainfall+Land+Budget to inputs |
| Fertilizer Recommendation | Core 14-class task | Remove (not in AgriSim core pipeline) |
| Rainfall Data Usage | Single annual value feature | Monthly time-series per district for forecasting |
| Soil Data | Categorical in fertilizer data only | Spatial dataset: District to Geometry to Soil Type(s) |
| Digital Twin Logic | Penalty formulas on synthetic data | Data-driven: ML predictions + economic calculations |
| Frontend Entry Point | Dashboard with NPK sliders | Interactive Map (Leaflet) as primary view |
| Database | CSV files | PostgreSQL + PostGIS for spatial queries |
| Backend | Not implemented | FastAPI with service layer for each ML model |

---

## 9. Features That Should Become Optional

| Feature | Current Priority | New Priority | Reason |
|---------|------------------|--------------|--------|
| Fertilizer Recommendation | Core (14 classes) | Remove from core | Not in AgriSim pipeline; keep as separate module if desired |
| Soil Image Classification | Not started | Optional (Phase 6+) | Transfer learning (MobileNetV3/EfficientNet); user must confirm |
| Plant Disease Detection | Not started | Optional (Phase 6+) | PlantVillage + MobileNetV3; isolated add-on |
| AI Chatbot | UI only | Optional (Phase 6+) | RAG-based farming assistant; don't block core pipeline |
| Advanced Yield Multi-output | Yield+Irrigation+Risk | Split into separate models | Cleaner architecture; each optimized independently |

---

## 10. Features That Are Missing

| Feature | Description | Phase | Effort |
|---------|-------------|-------|--------|
| Interactive India Map | Leaflet.js with district boundaries, click to lat/long | 2, 6 | Medium |
| District Geometry Data | GeoJSON/PostGIS for 700+ districts | 2, 3 | Medium (download) |
| Rainfall Forecasting Models | Time-series per district (12-month horizon) | 3, 4 | High |
| Spatial Soil Database | District to Soil Type(s) with percentages | 2, 3 | High (data acquisition) |
| Crop Economics Database | Spacing, costs, yield, price per crop | 3 | Medium |
| Simulation Engine | Cost + Yield + Value + Risk + Roadmap | 5 | High |
| Farming Roadmap Generator | Timeline from crop stages + planting date | 5, 6 | Medium |
| FastAPI Backend | All API endpoints + service layer | 2, 6 | High |
| PostgreSQL + PostGIS | Spatial database setup | 2 | Medium |
| SHAP for New Models | Adapt existing infra to new models | 4 | Low (infra exists) |
| Model Comparison Framework | Systematic baseline to modern comparison | 4 | Medium |
| End-to-End Tests | Geospatial, ML, simulation, frontend | 7 | Medium |

---

## 11. Recommended Development Order

WEEK 1-2: FOUNDATION (Phase 2)
- Design PostgreSQL + PostGIS schema
- Create new architecture diagram
- Define API contracts (OpenAPI spec)
- Set up FastAPI project structure
- Load district GeoJSON into PostGIS
- Update PROJECT_ROADMAP.md, CLAUDE.md

WEEK 2-4: DATA PIPELINE (Phase 3)
- Process rainfall: district-monthly time series
- Acquire/build spatial soil dataset (District to Soil)
- Build crop economics table (spacing, costs, prices)
- Augment crop rec data with soil + region features
- Create train/val/test splits (temporal for rainfall)
- EDA notebook for AgriSim data categories

WEEK 4-7: ML MODELS (Phase 4)
- Rainfall: Prophet + XGBoost(temporal) to LSTM comparison
- Crop Rec: XGBoost/LightGBM/CatBoost with soil+region
- Yield: XGBoost/LightGBM/CatBoost with economic features
- Risk: Best tree + calibration to Low/Med/High + prob
- Model comparison reports
- SHAP analysis for all selected models

WEEK 6-9: SIMULATION ENGINE (Phase 5)
- Cost calculation module
- Yield estimation with ML predictions
- Market value estimation
- Roadmap generator (crop stages to calendar)
- User override capability
- FastAPI endpoints: /simulation/run, /roadmap/{id}

WEEK 8-11: FULL-STACK INTEGRATION (Phase 6)
- Backend: All API endpoints connected to services
- Frontend: MapView (Leaflet) as new entry point
- Frontend: RainfallDashboard (historical + forecast charts)
- Frontend: SoilSelector (region-filtered)
- Frontend: CropRecPanel (with SHAP explanations)
- Frontend: SimulationForm + FinancialDashboard
- Frontend: RoadmapTimeline (interactive calendar)
- Optional: SoilImage, Disease, Chat modules
- React Query for server state management

WEEK 12-14: TESTING & DOCS (Phase 7)
- Unit tests for each service
- Integration tests for API
- E2E tests for user journey
- Geospatial validation
- ML model validation reports
- Simulation scenario testing
- Final thesis/documentation
- Deployment preparation

---

## 12. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Spatial soil data unavailable | Medium | High | Use ICAR/NBSSLUP publications; aggregate Soil Health Card data; fallback to state-level |
| Rainfall forecasting accuracy low | Medium | High | Use ensemble (Prophet + XGBoost); communicate uncertainty; show confidence intervals |
| District GeoJSON hard to find | Low | Medium | Use geojson-india npm package or DataMeet GitHub repo |
| ML training time too long | Low | Medium | Use HistGradientBoosting (fast); limit hyperparameter search; use subsampling |
| Frontend map performance | Low | Medium | Simplify GeoJSON (topojson); cluster districts at zoom levels |
| Scope creep from optional modules | High | Medium | Strict rule: Core pipeline must be 100% working before optional modules |
| Academic deadline pressure | High | High | Prioritize: Map to Rainfall to Soil to Crop to Simulation to Roadmap (in order) |

---

## 13. Success Criteria per Phase

| Phase | Success Criteria |
|-------|------------------|
| Phase 1 | Problem statement explicitly references geospatial, rainfall forecasting, spatial soil, farming roadmap |
| Phase 2 | Architecture diagram matches AgriSim pipeline; DB schema created; API spec complete; FastAPI skeleton runs |
| Phase 3 | District-monthly rainfall TS ready; Soil spatial table populated; Crop economics table built; EDA complete |
| Phase 4 | All 4 model types trained with modern candidates; comparison reports; best models selected; SHAP working |
| Phase 5 | Simulation engine returns cost/yield/value/risk/roadmap for given inputs; user overrides work |
| Phase 6 | Full user journey works: Map click to Rainfall to Soil to Crop to Sim to Roadmap; no mock data |
| Phase 7 | All test categories pass; model validation documented; thesis complete; deployed |

---

## 14. Immediate Next Steps (This Week)

1. Create Phase 2 deliverables:
   - New system architecture diagram (draw.io/Figma)
   - PostgreSQL + PostGIS schema SQL
   - OpenAPI spec for all endpoints
   - FastAPI project skeleton with router structure

2. Acquire spatial soil data:
   - Download district boundaries GeoJSON (DataMeet/geojson-india)
   - Research ICAR soil type per district mapping
   - Create soil_types CSV for import

3. Update documentation:
   - Modify synopsis.md problem statement
   - Update PROJECT_ROADMAP.md with AgriSim phases
   - Update CLAUDE.md with new architecture

4. Set up development environment:
   - PostgreSQL + PostGIS (Docker)
   - FastAPI with async SQLAlchemy
   - React + Leaflet map prototype

---

This migration plan preserves ~60% of existing work (literature, data pipeline, ML infra, frontend components, XAI) while redirecting the remaining 40% toward the AgriSim specification. The key is executing Phase 2 (Architecture) and Phase 3 (Data) correctly first, as they enable everything downstream.
