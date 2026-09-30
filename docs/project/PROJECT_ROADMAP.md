# Final Year Project: Complete Roadmap & Learning Guide

**Project Title:** AgriSim: Geospatial Farming Simulator & Predictive AI Guide  
**Domain:** Precision Agriculture / Artificial Intelligence / Geospatial Decision Support  
**Target Context:** Indian Agriculture (Smallholder Farms, Monsoonal Climate, District-Level Planning)

As your guide, I have structured this roadmap to take you from the theoretical research phase all the way to a fully deployed software application. Since this project is a massive learning opportunity, every stage includes **Learning Resources** tailored to be fully accessible from India, using direct links to popular, free Indian tech educators.

The project follows the **AgriSim Pipeline**:
**MAP → RAINFALL → RAINFALL FORECAST → REGIONAL SOIL → CROP RECOMMENDATION → LAND/BUDGET → SIMULATION → YIELD/COST → FARMING ROADMAP**

---

## Phase 1: Literature Survey & Problem Definition (Weeks 1–4) ✅ *COMPLETED*
*   **Tasks:** Study existing systems, identify the research gap (Predict Only → Predict + Simulate + Geospatial). Align problem statement with AgriSim's map-driven workflow.
*   **Deliverables:** Literature Table, Research Gap Identification, Survey Paper Draft, Updated Synopsis (AgriSim-aligned).
*   **Learning Resources:** 
    *   *You have already completed this! Refer to your `STAGE_1_Resource_Vault.md` and `STAGE_1_CheatSheet.md` for a recap of the theories.*

---

## Phase 2: System Architecture & Requirements (Weeks 5–8) 🔴 *NEEDS REWORK*
Before writing any code, you must define the "blueprint" of your project aligned with AgriSim pipeline.

*   **Software Requirements Stack:**
    *   **Machine Learning:** Python, Scikit-Learn, XGBoost, LightGBM, Prophet, SHAP, (optional: PyTorch/TensorFlow for CNN).
    *   **Backend / API:** FastAPI (async) with SQLAlchemy + PostGIS.
    *   **Database:** PostgreSQL + PostGIS (spatial queries), Redis (caching).
    *   **Frontend (User Interface):** React + Leaflet.js (interactive maps), Recharts/Chart.js (visualizations).
    *   **Geospatial:** GeoPandas, Shapely, district boundary GeoJSON.
*   **Deliverable:** 
    *   System Architecture Diagram matching AgriSim pipeline
    *   PostgreSQL + PostGIS database schema
    *   OpenAPI/Swagger specification for all endpoints
    *   FastAPI project skeleton with router structure
*   **Learning Resources:**
    *   **[Video]** [CampusX System Architecture for Machine Learning Projects](https://www.youtube.com/watch?v=bHK1fE_BUms)
    *   **[Video]** [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
    *   **[Video]** [Leaflet.js Interactive Maps Tutorial](https://www.youtube.com/watch?v=ZB1Rl51Y7uQ)
    *   **[Article]** [PostGIS Tutorial](https://postgis.net/workshops/postgis-intro/)

---

## Phase 3: Data Collection, Preprocessing & EDA (Weeks 9–12) 🟡 *PARTIALLY COMPLETED - NEEDS REALIGNMENT*
Redirect existing datasets to AgriSim objectives.

*   **Tasks:**
    *   **Rainfall Data:** Process district-level monthly time-series (1901-2015) for forecasting — focus on Prophet/XGBoost-ready format.
    *   **Soil Data:** Acquire/create region→soil type mapping (ICAR/NBSSLUP publications, Soil Health Card aggregates) — build spatial table with geometry.
    *   **Crop Recommendation Data:** Enhance existing datasets with soil type + region as features.
    *   **Crop Economics Data:** **NEW** — Build crop economics dataset (spacing, input costs per hectare, market prices, growth stages).
    *   **Crop Production Data:** Use district-level historical production for yield baseline assumptions.
    *   **Geospatial Data:** Download district boundaries GeoJSON (DataMeet/geojson-india).
*   **Deliverable:** 
    *   District-monthly rainfall time-series ready for forecasting
    *   Soil spatial table (PostGIS) populated with region→soil mappings
    *   Crop economics table built
    *   Comprehensive EDA notebook per AgriSim data category
*   **Learning Resources:**
    *   **[Video]** [CodeWithHarry Pandas Tutorial in Hindi](https://www.youtube.com/watch?v=RhEjmHeDNoA) 
    *   **[Video]** [Krish Naik Exploratory Data Analysis (EDA)](https://www.youtube.com/watch?v=ioN1jcWxbv8)
    *   **[Video]** [Prophet Time Series Forecasting Tutorial](https://www.youtube.com/watch?v=BfZaizlQ8sY)
    *   **[Article]** [GeoPandas Documentation](https://geopandas.org/en/stable/docs/user_guide.html)

---

## Phase 4: Modern ML / AI & XAI (Weeks 13–17) 🟡 *PARTIALLY COMPLETED - NEEDS MODERNIZATION*
Train four model types with modern candidates; SHAP explainability for all.

*   **Tasks:**
    *   **Model 1 — Rainfall Forecasting (Time-Series Regression):** Prophet (baseline) vs XGBoost-Lag vs LightGBM-Lag vs LSTM. Metrics: MAE, RMSE, MAPE. District-level monthly prediction.
    *   **Model 2 — Crop Recommendation (Multi-class Classification):** XGBoost vs LightGBM vs HistGradientBoosting vs TabNet. Features: rainfall forecast, soil type, climate, region. Metrics: F1-macro, Top-3 Accuracy.
    *   **Model 3 — Yield Prediction (Regression):** XGBoost vs LightGBM vs Random Forest vs HistGradientBoosting. Features: crop, soil, rainfall, land size, management. Metrics: R², MAE, RMSE.
    *   **Model 4 — Crop Economics / Cost Estimation (Regression):** LightGBM for cost per hectare by crop/region.
    *   **XAI Layer:** SHAP (TreeExplainer) for all models — beeswarm, dependence, waterfall plots. Save explainers for API serving.
*   **Deliverable:** 
    *   4 trained model artifacts (.pkl/.joblib) with comparison reports
    *   SHAP explainers saved for production
    *   Model cards documenting features, metrics, limitations
*   **Learning Resources:**
    *   **[Video]** [Krish Naik Random Forest Algorithm Explained](https://www.youtube.com/watch?v=nxFG5xdpDto)
    *   **[Video]** [Krish Naik XGBoost Algorithm Intuition](https://www.youtube.com/watch?v=gPciUPwWJQQ) 
    *   **[Video]** [CampusX Explainable AI SHAP Tutorial](https://www.youtube.com/watch?v=8EQwpmK49sk)
    *   **[Video]** [Prophet Time Series Forecasting](https://www.youtube.com/watch?v=BfZaizlQ8sY)
    *   **[Article]** [LightGBM Documentation](https://lightgbm.readthedocs.io/en/latest/)

---

## Phase 5: Agricultural Simulation Engine (Weeks 18–21) 🔴 *NOT STARTED*
Core simulation logic: budget → costs → yield → value → roadmap.

*   **Tasks:**
    *   **Plant Capacity Calculator:** Crop-specific spacing × land area → plant count.
    *   **Cost Engine:** Seeds/seedlings + fertilizer + irrigation + labor + land prep + plant protection + misc. Regional cost assumptions table.
    *   **Yield Engine:** Base yield × area × adjustment factors (rainfall adequacy, soil suitability, management level).
    *   **Market Value Engine:** Yield × price assumption (with source/date metadata).
    *   **Risk Engine:** Rainfall deficit probability, price volatility, pest/disease pressure indicators.
    *   **Roadmap Generator:** Crop growth stages → calendar timeline (land prep → sowing → irrigation → fertilization → harvesting). User-adjustable start date.
    *   **User Override:** Allow modification of rainfall assumptions, cost assumptions, yield assumptions before finalizing.
*   **Deliverable:** 
    *   Simulation Python module (pure functions, testable)
    *   Integrated into FastAPI as `/simulate` endpoint
    *   Unit tests for each calculation
*   **Learning Resources:**
    *   **[Article]** [Crop Growth Stages Reference](https://www.icar.org.in/)
    *   **[Video]** [Software Design Patterns for Business Logic](https://www.youtube.com/watch?v=NuHxG2VcQ4A)

---

## Phase 6: Full-Stack Application Integration (Weeks 22–26) 🔴 *NOT STARTED*
End-to-end user journey: Map → Rainfall → Soil → Crop → Sim → Roadmap.

*   **Tasks:**
    *   **Backend (FastAPI):** 
        *   Router structure: `/map`, `/rainfall`, `/soil`, `/crop`, `/simulate`, `/roadmap`, `/chat` (optional)
        *   PostGIS spatial queries for district lookup & soil filtering
        *   Async model inference with cached SHAP explainers
        *   OpenAPI docs auto-generated
    *   **Frontend (React + Leaflet):**
        *   MapView: Interactive India map, pin drop, district highlight
        *   RainfallDashboard: Historical charts + 12-month forecast with confidence intervals
        *   SoilSelector: Region-filtered dropdown + manual override + optional image upload
        *   CropRecPanel: Ranked recommendations with SHAP reasoning
        *   SimulationForm: Crop, land size, budget, adjustable assumptions
        *   FinancialDashboard: Cost breakdown, yield, market value, risk indicators
        *   RoadmapTimeline: Interactive calendar with activity cards
        *   Optional: SoilImage, Disease, Chat modules
    *   **State Management:** React Query for server state, local state for form wizard.
*   **Deliverable:** 
    *   Working full-stack application (local)
    *   Complete user journey functional without mock data
*   **Learning Resources:**
    *   **[Video]** [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
    *   **[Video]** [React + Leaflet Tutorial](https://www.youtube.com/watch?v=ZB1Rl51Y7uQ)
    *   **[Video]** [React Query (TanStack Query) Tutorial](https://www.youtube.com/watch?v=seU46c6of5A)

---

## Phase 7: Testing, Validation & Final Documentation (Weeks 27–29) 🔴 *NOT STARTED*
Polishing the diamond before final submission.

*   **Tasks:**
    *   Unit tests for each service (backend + simulation engine)
    *   Integration tests for API endpoints
    *   E2E tests for user journey (Playwright/Cypress)
    *   Geospatial validation (district lookup accuracy)
    *   ML model validation reports (drift, fairness, robustness)
    *   Simulation scenario testing (different budgets, land sizes, rainfall scenarios, soil types, crops)
    *   Final thesis/documentation
    *   Deployment preparation (Docker, cloud deployment)
*   **Deliverable:** 
    *   All test suites passing
    *   Model validation documented
    *   Final thesis complete
    *   Deployed application (cloud)
*   **Learning Resources:**
    *   **[Video]** [Krish Naik End to End Machine Learning Deployment](https://www.youtube.com/watch?v=S_F_c9e2bz4)
    *   **[Video]** [Docker for ML Applications](https://www.youtube.com/watch?v=gAkwW2tuIqE)
    *   **[Video]** [Playwright E2E Testing](https://www.youtube.com/watch?v=Y7yCr4GcJyU)
