# Project Synopsis

**Title:** AgriSim: Geospatial Farming Simulator & Predictive AI Guide — A Map-Driven Agricultural Decision Support Platform

## Problem Statement
Agriculture in India is increasingly affected by climate variability, soil degradation, water scarcity, and inefficient resource utilization. Existing intelligent farming systems primarily focus on predicting crop yield or recommending fertilizers using static soil datasets. However, they lack the capability to combine **geospatial location intelligence**, **localized rainfall analysis and forecasting**, **regional soil identification**, and **end-to-end farm planning** into a unified decision-support workflow.

Farmers and agricultural planners need to combine information from multiple disconnected sources — historical rainfall patterns, soil characteristics, crop suitability, input costs, spacing requirements, and expected yields — to decide what to grow, when to perform farming activities, and how much money may be required. These factors are not presented together in a single geospatial decision-support platform.

AgriSim addresses this gap by creating an **interactive, map-driven agricultural simulation platform** that connects localized environmental data (via map-based location selection) with historical rainfall analysis, rainfall forecasting, spatial soil filtering, machine-learning-based crop recommendation, financial planning, yield estimation, and a practical farming activity roadmap — all in one unified workflow.

## Objectives
- To develop a **geospatial location selection interface** using an interactive India map for precise latitude/longitude capture.
- To build a **historical rainfall analysis module** that retrieves and visualizes accumulated rainfall history for the selected region/district.
- To implement a **rainfall forecasting engine** using time-series models (Prophet/XGBoost/LSTM) to predict monthly rainfall accumulation for the upcoming 12 months.
- To create a **spatial soil database** (PostGIS-enabled) that identifies soil types naturally associated with the selected region, with manual confirmation override.
- To develop an **AI-based crop recommendation model** using rainfall forecasts, soil type, climate parameters, and agricultural features.
- To design a **farm simulation engine** that accepts land size and budget, and generates: plant capacity (via crop-specific spacing), cost breakdown (seeds, fertilizer, irrigation, labor, land preparation, plant protection), yield estimation, market value projection, and risk assessment.
- To generate an **interactive farming roadmap/timeline** converting crop growth stages into a practical calendar of activities (land preparation, sowing, irrigation, fertilization, harvesting).
- To build an **explainable AI layer** (SHAP) providing feature importance and reasoning for crop recommendations and yield predictions.
- To implement **optional add-on modules**: soil image classification (CNN), AI chatbot for farming queries, and plant disease detection (post-planting).

## Methodology
The proposed work follows the **AgriSim Geospatial Pipeline**: **MAP → RAINFALL → RAINFALL FORECAST → REGIONAL SOIL → CROP RECOMMENDATION → LAND/BUDGET → SIMULATION → YIELD/COST → FARMING ROADMAP**.

**Phase 1 — Geospatial Data Infrastructure:** District boundary GeoJSON (DataMeet/geojson-india) is loaded into PostgreSQL + PostGIS. IMD district-level monthly rainfall (1901–2015) is structured as time-series per district. ICAR/NBSSLUP soil type mappings and Soil Health Card aggregates are stored as a spatial region→soil-type table with geometry.

**Phase 2 — Rainfall Intelligence:** Historical rainfall dashboards visualize accumulated rainfall per district. A time-series forecasting engine (Prophet baseline, XGBoost/LightGBM with lag features, LSTM) predicts monthly rainfall for the next 12 months with confidence intervals.

**Phase 3 — Spatial Soil Filtering:** PostGIS spatial queries (`ST_Contains`) map the user's map pin (lat/long) to a district, which retrieves associated soil types. The user confirms or overrides the soil type manually (optional: soil image CNN classification).

**Phase 4 — ML-Based Crop Recommendation:** A multi-class classifier (XGBoost / LightGBM / HistGradientBoosting) uses forecasted rainfall, confirmed soil type, climate parameters, and region to recommend suitable crops. SHAP (TreeExplainer) provides feature-level reasoning for each recommendation.

**Phase 5 — Farm Simulation Engine:** Given selected crop, land size (hectares), and budget (INR), pure-Python agronomic functions compute: plant capacity (crop-specific spacing × area), cost breakdown (seeds, fertilizer, irrigation, labor, land prep, plant protection), yield estimation (base yield × area × adjustment factors for rainfall adequacy, soil suitability), market value (yield × price assumption with source/date), and risk indicators (rainfall deficit probability, price volatility).

**Phase 6 — Farming Roadmap Generator:** Crop growth stages (land preparation, sowing, vegetative, flowering, grain filling, harvest) are converted into an interactive calendar timeline with user-adjustable start date.

**Phase 7 — Full-Stack Integration (React + FastAPI):** Interactive Leaflet.js map for location selection. Rainfall dashboard (historical + forecast charts). Soil selector (region-filtered). Crop recommendation panel with SHAP explanations. Simulation form with adjustable assumptions. Financial dashboard (costs, yield, value, risk). Roadmap timeline. Optional modules: soil image classification, AI chatbot, plant disease detection — developed only after core pipeline is stable.

**Evaluation:** Rainfall forecasting (MAE, RMSE, MAPE), crop recommendation (F1-macro, Top-3 Accuracy), yield prediction (R², MAE, RMSE), simulation accuracy (vs. historical norms), geospatial lookup correctness, end-to-end user journey testing.

<br><br><br>

---

**Project Guide**  
Mr. Krishna Prasad D S  
Assistant Professor Gd-II  

**Project Coordinator**  
Dr. Radhakrishna  
Professor & Head
