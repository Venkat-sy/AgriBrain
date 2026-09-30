# Stage 1: Self-Study & Mentor Discussion Guide

This document is your personal knowledge base. Use these points for your own deeper understanding of the literature and to confidently tackle questions during meetings with your project mentor.

## 1. The Core Objective (The "Big Picture")
*   **What you are building (AgriSim):** "I am building AgriSim — a geospatial farming simulator and predictive AI guide. It's a map-driven agricultural decision-support platform that combines: interactive map location selection → historical rainfall analysis → rainfall forecasting → regional soil identification → ML-based crop recommendation → budget/land input → farm simulation (costs, yield, market value, risk) → interactive farming roadmap."
*   **Why it matters (The Problem):** "Currently, Indian farmers get static fertilizer/crop recommendations from disconnected sources. They check rainfall in one app, soil in another, crop prices in a third. No single platform connects location → rainfall → soil → crop → budget → roadmap in one unified geospatial workflow. Existing systems are 'Predict Only' — they don't forecast rainfall, don't use spatial soil data, don't simulate costs/yield, and don't generate a farming calendar."
*   **How you solve it (The Solution):** "AgriSim follows the pipeline: **MAP → RAINFALL → RAINFALL FORECAST → REGIONAL SOIL → CROP RECOMMENDATION → LAND/BUDGET → SIMULATION → YIELD/COST → FARMING ROADMAP**. It uses: (1) PostGIS for spatial queries, (2) Prophet/XGBoost for rainfall forecasting, (3) XGBoost/LightGBM for crop recommendation with soil+rainfall features, (4) a simulation engine for cost/yield/value/roadmap, (5) SHAP for explainability at every step, (6) React+Leaflet for the interactive map frontend."

## 2. Understanding Your Datasets (AgriSim-Aligned)
If asked by your mentor: *"Where are you getting your data?"* or *"How is this relevant to India?"*
*   **Rainfall Data:** "IMD district-level monthly rainfall (1901-2015) — used for historical analysis and time-series forecasting for the next 12 months."
*   **Soil Data:** "ICAR/NBSSLUP soil type mappings by region/state, aggregated from Soil Health Card data — stored in PostGIS as region→soil type spatial table."
*   **Crop Recommendation Data:** "Enhanced public datasets (Kaggle/UCI) with added soil type + region + rainfall forecast features."
*   **Crop Economics Data (NEW):** "Custom-built dataset: crop-specific spacing, input costs per hectare (seeds, fertilizer, labor, irrigation, plant protection), market prices (with source/date), growth stage durations."
*   **Crop Production Data:** "District-level historical production (1997-2020) for yield baseline assumptions by crop/region."
*   **Geospatial Data:** "District boundary GeoJSON from DataMeet/geojson-india for map rendering and spatial queries."

## 3. Grasping the Algorithms (In Simple Terms)
If asked by your mentor: *"What algorithms did you study?"*
*   **Rainfall Forecasting (Time-Series):** "Prophet (baseline, handles seasonality/holidays), XGBoost/LightGBM with lag features, LSTM for sequence modeling. Metrics: MAE, RMSE, MAPE."
*   **Crop Recommendation (Classification):** "XGBoost vs LightGBM vs HistGradientBoosting vs TabNet. Features: forecasted rainfall, soil type, climate, region. Metrics: F1-macro, Top-3 Accuracy."
*   **Yield Prediction (Regression):** "XGBoost vs LightGBM vs Random Forest vs HistGradientBoosting. Features: crop, soil, rainfall, land size, management. Metrics: R², MAE, RMSE."
*   **Crop Economics (Regression):** "LightGBM for cost per hectare by crop/region."
*   **Generative AI / NLP (Optional Chatbot):** "Used in recent 2025 papers to translate numerical predictions into multilingual farming advice."
*   **CNN (Optional Soil/Disease Image Classification):** "Lightweight CNN (MobileNet/EfficientNet) for soil image classification and plant disease detection."

## 4. Explaining the Advanced Tech (For Your Own Knowledge)
If you need to break down: *"What is Explainable AI or a Digital Twin or Geospatial Pipeline?"*
*   **Explainable AI (XAI - using SHAP):** "Shows exactly *why* the AI recommended a crop or predicted a yield. For crop recommendation: 'I recommended Rice because forecasted rainfall is high (contribution +35%), soil is clay (+25%), and region is coastal (+15%)'. This builds trust."
*   **Rainfall Forecasting (Time-Series):** "Predicts monthly rainfall for the next 12 months using historical patterns. Prophet decomposes trend + seasonality + holidays. Critical for kharif/rabi planning."
*   **Geospatial Pipeline (PostGIS + Leaflet):** "User drops pin on map → lat/long → PostGIS query finds containing district → district ID retrieves historical rainfall + soil types → feeds into ML models. All in SQL."
*   **Agricultural Simulation Engine:** "Pure Python functions: spacing × area = plant count; cost components summed; yield × price = market value; growth stages → calendar timeline. Testable, no ML involved — just agronomic formulas."
*   **Farming Roadmap:** "Converts crop growth stages (land prep, sowing, vegetative, flowering, grain filling, harvest) into interactive calendar with user-adjustable start date."

## 5. Anticipated Mentor Questions & How to Tackle Them

*   **Mentor:** *"Just to recap, why did we decide to exclude conference papers?"*
    *   **Your Answer:** "As per your instruction, we focused strictly on Journal and Transaction papers. This ensures that the foundation of our project relies on the highest standard of rigorously peer-reviewed and validated methodologies, avoiding preliminary or incomplete findings often found in conference proceedings."
*   **Mentor:** *"How is AgriSim different from existing agricultural apps?"*
    *   **Your Answer:** "Most existing apps take soil data and output a static NPK number or crop name. My literature survey identified that this 'Predict Only' model is flawed. AgriSim is a full **geospatial pipeline**: Map → Rainfall (history + forecast) → Regional Soil → Crop Recommendation (with SHAP reasoning) → Budget/Land Input → Simulation (costs, yield, value, risk) → Farming Roadmap. It connects disconnected silos into one workflow."
*   **Mentor:** *"Are Digital Twins practical for small Indian farms?"*
    *   **Your Answer:** "Full-scale IoT digital twins with sensors are expensive. However, AgriSim uses a **software simulation** approach — no sensors needed. It uses localized data (district rainfall, regional soil) + user inputs (land, budget) to run agronomic formulas. Highly scalable and cost-effective."
*   **Mentor:** *"How will you get spatial soil data for every district?"*
    *   **Your Answer:** "Primary source: ICAR/NBSSLUP published soil maps and Soil Health Card aggregates. Fallback: state-level soil type generalizations. The PostGIS schema allows starting with state-level and refining to district-level as data becomes available."
*   **Mentor:** *"Rainfall forecasting at district level — is that accurate enough?"*
    *   **Your Answer:** "District-level is the practical resolution for IMD data. We use ensemble (Prophet + XGBoost) and communicate uncertainty via confidence intervals. The simulation engine allows user override of rainfall assumptions. Accuracy is sufficient for planning decisions, not precision agriculture."
*   **Mentor:** *"What about the optional modules (soil image, disease, chatbot)?"*
    *   **Your Answer:** "Per AgriSim blueprint: core pipeline (Map→Rainfall→Soil→Crop→Sim→Roadmap) is MVP. Optional modules are add-ons developed ONLY after core pipeline is 100% working. They don't block the main deliverable."
