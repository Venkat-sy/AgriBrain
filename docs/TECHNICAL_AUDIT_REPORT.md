# AgriSim Legacy Project - Technical Audit & Data Extraction Report

**Date:** 2026-11-12  
**Auditor:** Senior Technical Auditor & Data Analyst  
**Repository:** `C:\Users\USER\Downloads\FinalYearProject` (Read-Only Reference)  
**Mode:** Comprehensive Review - Dataset Schema, ML Pipeline, Backend/API, Frontend

---

## Table of Contents
1. [Dataset Schema & Column Audit](#1-dataset-schema--column-audit)
2. [Machine Learning Pipeline & Feature Vector Audit](#2-machine-learning-pipeline--feature-vector-audit)
3. [Backend & API Logic Extraction](#3-backend--api-logic-extraction)
4. [Legacy UI & Frontend Review](#4-legacy-ui--frontend-review)

---

## 1. Dataset Schema & Column Audit

### 1.1 Core Data Files Located

| File Path | Description | Size/Rows | Key Columns |
|-----------|-------------|-----------|-------------|
| `agribrain_shared_pack/data/india_soilgrids_subset.csv` | SoilGrids data for India (lat/long + soil properties) | ~5 sample rows shown | `latitude`, `longitude`, `soc_0_5cm_dg_kg` (organic carbon), `phh2o_0_5cm` (pH), `clay_0_5cm_g_kg` |
| `agribrain_shared_pack/data/crop_production.csv` | ICRISAT district-level crop production data | Historical (2000+) | `State_Name`, `District_Name`, `Crop_Year`, `Season`, `Crop`, `Area`, `Production` |
| `agribrain_shared_pack/data/master_agri_dataset.csv` | Master agricultural dataset v1 | 30+ columns | `district_name`, `state_name`, `district_id`, `crop`, `year`, `area_ha`, `production_tonnes`, `yield_tons_per_ha`, `annual_rainfall_mm`, `soil_type`, `temperature`, **N/P/K/pH/EC/OC** baselines |
| `agribrain_shared_pack/data/master_agri_dataset_v2.csv` | Master agricultural dataset v2 (larger) | 187MB | `canonical_key`, `district_name`, `state_name`, `crop`, `year`, **soil_ph**, **soil_organic_carbon_percent**, **soil_nitrogen_kg_per_ha**, **soil_phosphorus_kg_per_ha**, **soil_potassium_kg_per_ha**, `soil_texture`, `cultivation_cost_inr_per_ha`, `market_price_inr_per_ton`, `yield_range_tons_per_ha` |
| `agribrain_shared_pack/data/master_agri_dataset_v2_fixed.csv` | Fixed version of v2 | Same schema | Identical to v2 with numeric type fixes |
| `agribrain_shared_pack/data/ICRISAT-District Level Data.csv` | Raw ICRISAT district data | 100+ columns | District codes, crop-wise area/production/yield for 50+ crops (Rice, Wheat, Sorghum, Millet, Maize, Pulses, Oilseeds, etc.) |
| `agribrain_shared_pack/data/district_rainfall_history.csv` | Historical rainfall by district/year | Sparse data | `district_name`, `state_name`, `year`, `annual_rainfall_mm` |
| `agribrain_shared_pack/data/district_rainfall_summary.json` | Rainfall statistics per district | JSON | `mean_annual_rainfall_mm`, `std`, `min`, `max`, `years_with_data` |
| `agribrain_shared_pack/data/crop_agronomy_base.json` | Crop agronomy parameters | 22+ crops | Per-crop: `season`, `duration_days`, `n_kg_per_ha`, `p_kg_per_ha`, `k_kg_per_ha`, `water_requirement_mm`, `optimal_temp_c`, `soil_ph_range`, `cultivation_cost_inr_per_ha`, `market_price_inr_per_ton`, `yield_range_tons_per_ha`, `suitable_soils` |
| `agribrain_shared_pack/data/district_name_mapping.csv` | District ID mapping | ~600+ rows | `district_name`, `state_name`, `district_id` |

### 1.2 Training Data Files (Processed)

| File Path | Description | Columns |
|-----------|-------------|---------|
| `training_data/crop_recommendation_train.csv` | Training split (scaled) | `n,p,k,temperature,humidity,ph,rainfall,label,label_encoded` (all **StandardScaler**-normalized) |
| `training_data/crop_recommendation_val.csv` | Validation split | Same as train |
| `training_data/crop_recommendation_test.csv` | Test split | Same as train |
| `training_data/crop_recommendations.csv` | Model output predictions | `district_id`, `rainfall_mm`, `crop_name`, `confidence` |
| `training_data/crop_label_mapping.json` | Label encoding map | 22 crops → 0-21 (apple=0, banana=1, blackgram=2, chickpea=3, coconut=4, coffee=5, cotton=6, grapes=7, jute=8, kidneybeans=9, lentil=10, maize=11, mango=12, mothbeans=13, mungbean=14, muskmelon=15, orange=16, papaya=17, pigeonpeas=18, pomegranate=19, rice=20, watermelon=21) |
| `training_data/crop_scaler.pkl` | StandardScaler artifact | Fitted on 7 features: `[n, p, k, temperature, humidity, ph, rainfall]` |
| `training_data/feature_config.json` | Feature configuration | Documents input features, types, target, scaler reference |
| `training_data/crop_economics_processed.csv` | Processed crop economics | Cost, price, yield data |
| `training_data/crop_production_processed.csv` | Processed production data | Cleaned ICRISAT data |
| `training_data/rainfall_processed.csv` | Processed rainfall data | With `Monsoon_Ratio`, `Rainfall_Variability` engineered features |
### 1.3 Key Agronomic Columns Verification

| Category | Columns Found | Status |
|----------|---------------|--------|
| **Soil Nutrients (NPK)** | `soil_nitrogen_kg_per_ha`, `soil_phosphorus_kg_per_ha`, `soil_potassium_kg_per_ha`, `baseline_N_kg_per_ha`, `baseline_P_kg_per_ha`, `baseline_K_kg_per_ha`, `n_kg_per_ha`, `p_kg_per_ha`, `k_kg_per_ha` | ✅ **Present** in master datasets & crop_agronomy_base.json |
| **Soil pH** | `phh2o_0_5cm` (SoilGrids), `soil_ph`, `baseline_pH`, `ph_min`, `ph_max`, `soil_ph_range` | ✅ **Present** across all datasets |
| **Organic Carbon** | `soc_0_5cm_dg_kg` (SoilGrids), `soil_organic_carbon_percent`, `baseline_OC_percent` | ✅ **Present** |
| **Yield** | `yield_tons_per_ha`, `production_tonnes/area_ha`, `expected_yield_tons_per_ha`, `yield_range_tons_per_ha` | ✅ **Present** |
| **Cost/Economics** | `cultivation_cost_inr_per_ha`, `market_price_inr_per_ton`, `estimated_cost_inr_per_ha`, `estimated_revenue_inr_per_ha` | ✅ **Present** in master v2, crop_agronomy_base.json, simulation defaults |
| **Mandi Prices** | Via DataGov API integration (not in static CSV) - `BASELINE_PRICES_PER_QUINTAL` dict in `market_pricing.py` | ✅ **API Integration** with 70+ crop fallback prices |
| **Rainfall** | `annual_rainfall_mm`, `rainfall_mm`, monthly `JAN-DEC`, `Monsoon_Ratio`, `Rainfall_Variability` | ✅ **Present** with engineered features |
| **Temperature/Humidity** | `average_temperature_c`, `optimal_temp_c`, `temperature`, `humidity` | ✅ **Present** |

### 1.4 Data Quality Observations
- **SoilGrids data**: Limited to lat/long + 3 soil properties (SOC, pH, Clay) - no NPK directly
- **Master datasets v2/v2_fixed**: Most comprehensive with 30+ columns including all agronomic parameters
- **ICRISAT data**: Raw district-level production stats (1978+) but no soil/climate - requires joining
- **Rainfall history**: Very sparse (mostly NaN in summary JSON)
- **Crop agronomy JSON**: Well-structured reference for 22 crops with all parameters needed for simulation
- **Training data**: Already **StandardScaler**-normalized (mean=0, std=1) - raw values not preserved in CSV

---

## 2. Machine Learning Pipeline & Feature Vector Audit

### 2.1 Model Artifacts

| Artifact | Path | Type | Description |
|----------|------|------|-------------|
| **Crop Recommendation Model** | `models/crop_recommendation_model.pkl` | `RandomForestClassifier` | 100 estimators, random_state=42 |
| **Crop Scaler** | `training_data/crop_scaler.pkl` | `StandardScaler` | Fitted on 7 features |
| **Label Mapping** | `training_data/crop_label_mapping.json` | JSON | 22 crop classes → integers 0-21 |
| **Feature Config** | `training_data/feature_config.json` | JSON | Documents feature order, types, target |
| **Fertilizer Model** | `training_data/fertilizer_scaler.pkl`, `fertilizer_label_mapping.json` | Scaler + LabelEncoder | Separate fertilizer recommendation task |
| **Yield Model** | `training_data/yield_scaler.pkl`, `yield_label_encoders.pkl` | Scaler + encoders | Yield prediction task |

### 2.2 Exact Feature Vector (CRITICAL FOR INFERENCE)

**Feature Order (must match training exactly):**
```python
FEATURE_COLUMNS = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]
```

**Expected Input Format (raw values, NOT scaled):**
```python
{
    "n": float,           # Nitrogen kg/ha
    "p": float,           # Phosphorus kg/ha  
    "k": float,           # Potassium kg/ha
    "temperature": float, # °C
    "humidity": float,    # % relative humidity
---

## 3. Backend & API Logic Extraction

### 3.1 Technology Stack
- **Framework:** FastAPI (Python 3.11+)
- **Database:** SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod) - `DATABASE_URL` in config
- **ML Inference:** `joblib` + `scikit-learn` (RandomForest + StandardScaler)
- **External APIs:** DataGov Mandi Pricing (`api.data.gov.in`), IMD, OpenWeather (keys in `.env`)
- **CORS:** Configured for localhost:3000, localhost:8080, wildcard

### 3.2 Key API Endpoints

#### Crop Recommendation (`/api/v1/crop`)
| Endpoint | Method | Description | Implementation |
|----------|--------|-------------|----------------|
| `/recommend` | POST | Rule-based crop scoring (NOT ML) | Scores crops by soil match (40%), rainfall (25%), temp (15%), pH (10%), nutrients (10%) |
| `/costs/{crop_id}` | GET | Input costs for crop | Queries `CropCost` table |
| `/prices/{crop_id}` | GET | Market prices for crop | Queries `CropPrice` table with date/market filters |

> **Critical Finding:** The `/api/v1/crop/recommend` endpoint uses a **rule-based scoring system**, NOT the trained ML model. The ML model is only accessible via the service layer (`crop_recommendation_service.py` → `ml.inference.crop_recommendation.recommend()`).

#### ML Inference Service (Internal)
| Function | Module | Description |
|----------|--------|-------------|
| `recommend_crops(input_features)` | `backend/services/crop_recommendation_service.py` | Bridges API → ML; maps N/P/K → n/p/k; calls `ml.inference.crop_recommendation.recommend()` |
| `recommend(input_features, top_k=5)` | `ml/inference/crop_recommendation.py` | Loads model/scaler/label_map; scales input; returns top-k predictions with confidence |

#### Soil API (`/api/v1/soil`)
| Endpoint | Description |
|----------|-------------|
| `/types` | List all reference soil types |
| `/types/{id}` | Get soil type by ID |
| `/district/{district_id}` | Get soil composition for district (percentages, predominant) |
| `/analyze` | **POST** - Upload soil image → ML classification (currently **mock/placeholder**) |

#### Rainfall API (`/api/v1/rainfall`)
| Endpoint | Description |
|----------|-------------|
| `/history/{district_id}` | Historical monthly rainfall with yearly summaries |
| `/forecast/{district_id}` | ML-generated forecast (requires model_version) |

#### Simulation API (`/api/v1/simulation`)
| Endpoint | Description |
|----------|-------------|
| `/run` | **POST** - Execute simulation with `SimulationRequest` params |
| `/save` | **POST** - Run + save simulation result to DB with roadmap |

#### Other APIs
- `/api/v1/map` - District/state geometry data
### 3.3 Simulation Engine Logic (`backend/services/simulation_engine.py`)

**Core Calculation Flow:**
```python
SimulationEngine.run_simulation(request, district, crop) → SimulationResult
```

**Key Calculations:**

1. **Rainfall Calculation** (`get_rainfall_for_district`):
   - Queries `RainfallMonthly` table by district_id
   - If crop_duration > 30 days: sums monthly averages over growing season
   - Defaults to 100mm if no data

2. **Market Price Lookup - 3-Tier Fallback** (`get_latest_market_price`):
   ```
   Tier 1: Database (CropPrice table) → ₹/Ton (stored)
   Tier 2: Live DataGov API → fetch_live_market_price() → modal_price ₹/Quintal × 10 = ₹/Ton
   Tier 3: Hardcoded fallback dict → ₹/Ton (pre-multiplied)
   ```

3. **Yield Estimation** (`calculate_yield`):
   - Base yield from `crop.expected_yield_tons_per_ha`
   - Rainfall factor: 0.5-1.1 based on min/max rainfall requirements
   - Soil factor: 1.1 (ideal), 1.05 (acceptable), 0.8 (unsuitable)
   - Capped at 1.5× base yield

4. **Cost Calculation** (`calculate_costs`):
   - Sums `unit_cost × quantity_per_ha × land_area_ha` for all `CropCost` items
   - Default costs per crop if DB empty (rice, cotton have specific defaults)

5. **Risk Assessment** (`assess_risk`):
   - Budget risk: cost/budget ratio >1.0 = high, >0.9 = medium
   - Rainfall risk: <70% of crop minimum = high risk
   - Returns `RiskLevel` enum: LOW/MEDIUM/HIGH

### 3.4 Market Pricing Service - DataGov Integration (`backend/services/market_pricing.py`)

**API Endpoint:** `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`

**Request Parameters:**
```python
params = {
    "api-key": os.getenv("DATAGOV_API_KEY"),
    "format": "json",
    "filters[commodity]": crop_name,
    "filters[state]": normalized_state_name,
    "limit": 100
}
```

**State Name Mapping:** Comprehensive dict mapping 36 states/UTs to API-expected names (e.g., "Delhi" → "NCT of Delhi")

**Price Conversion:** API returns `modal_price` in **₹/Quintal** → multiply by 10 for **₹/Ton**

**Fallback Baseline Prices:** 70+ crops with prices in ₹/Quintal (e.g., Rice=2000, Wheat=2200, Cotton=5500, Sugarcane=300)

### 3.5 Configuration & Hardcoded Values (`backend/core/config.py`)

| Setting | Value | Notes |
|---------|-------|-------|
| `DATABASE_URL` | `sqlite:///./agrisim_dev.db` | Dev default; PostgreSQL for prod |
| `ALLOWED_ORIGINS` | `["http://localhost:3000", "http://localhost:8080", "*"]` | CORS |
| `SOIL_CLASSIFIER_MODEL_PATH` | `models/soil_classifier.pkl` | Placeholder |
| `DISEASE_DETECTOR_MODEL_PATH` | `models/disease_detector.pkl` | Placeholder |
| `RAINFALL_FORECAST_MODEL_PATH` | `models/rainfall_forecast.pkl` | Placeholder |
| `MAX_UPLOAD_SIZE` | 10 MB | File uploads |
| `UPLOAD_DIR` | `uploads` | Local storage |

**Environment Variables (`.env`):**
- `DATAGOV_API_KEY` - Required for live mandi prices
- `IMD_API_KEY` - Weather data
- `OPENWEATHER_API_KEY` - Weather data

### 3.6 Database Models (Referenced in APIs)

Key SQLAlchemy models (from `backend/models/__init__.py`):
- `District` - id, name, state, geometry
- `CropProfile` - id, name, common_name, category, season, soil requirements, NPK needs, yield, costs
- `CropCost` - crop_id, activity, unit, unit_cost, quantity_per_ha, region
### 4.3 Component Analysis

#### InputPanel.tsx - Farmer Input Form
**State Fields:**
```typescript
{
  district_id: number,        // Dropdown: 10 predefined districts (Tamil Nadu, Punjab, Haryana, Maharashtra)
  soil_type: string,          // Dropdown: 8 soil types (Alluvial, Black, Red, Laterite, Desert, Mountain, Peaty)
  land_area_ha: number,       // Default: 2.0
  budget_inr: number,         // Default: 100,000
  rainfall_mm: number,        // Auto-filled from district selection
  temperature_c: number,      // Default: 28
  humidity_percent: number,   // Default: 65
  ph: number,                 // Default: 6.5
  n: number,                  // Default: 120 (Nitrogen)
  p: number,                  // Default: 40 (Phosphorus)
  k: number,                  // Default: 150 (Potassium)
  planting_season: string,    // Kharif/Rabi/Zaid/Annual
  planned_start_date: string  // Date picker
}
```

**Advanced Toggle:** Shows/hides NPK, pH, temperature, humidity, season, date fields

**District-Rainfall Mapping:** Hardcoded 10 districts with preset rainfall_mm values

**Submission:** Calls `onSubmit` callback with filtered fields (district_id, soil_type, rainfall_mm, temperature_c, humidity_percent, ph, n, p, k)

#### CropCard.tsx - Recommendation Display
**Props Interface:**
```typescript
CropRecommendation {
  crop_id: number;
  crop_name: string;
  confidence_score: number;      // 0-1
  expected_yield_tons_per_ha: number;
  water_requirement_mm: number;
  fertilizer_requirement_kg_per_ha: {N, P, K};
  estimated_cost_inr_per_ha: number;
  estimated_revenue_inr_per_ha: number;
  risk_score: number;            // 1 - confidence
  sustainability_score: number;  // = confidence
  reason: string;                // Match reasons joined by "; "
  land_area_ha?: number;
}
```

**Visual Elements:**
- Crop name + ID
- Confidence bar (green, 0-100%)
- 4-metric grid: Yield, Water, Cost/ha, Revenue/ha
- Risk & Sustainability bars (red/green)
- "Why this crop" callout box with reasons
- **Simulate button** → triggers simulation flow

#### SimulationResults.tsx - Detailed Results View
**SimulationResult Interface:**
```typescript
{
  crop_name: string;
  land_area_ha: number;
  water_availability_liters: number;
  water_requirement_liters: number;
  water_sufficiency: boolean;
  fertilizer_requirement_kg: {N, P, K};
  fertilizer_cost_inr: number;
  total_cost_inr: number;
  expected_yield_tons: number;
  expected_revenue_inr: number;
  expected_profit_inr: number;
### 4.4 Feature Parity Checklist for Next.js Frontend

| Feature | Backend Support | Frontend Implementation | Status |
|---------|----------------|------------------------|--------|
| District selection | ✅ DB + API | ✅ Hardcoded 10 districts | ⚠️ Need dynamic district loading |
| Soil type selection | ✅ DB + API | ✅ Hardcoded 8 types | ⚠️ Need dynamic soil types |
| NPK/pH/temp/humidity inputs | ✅ ML model expects these | ✅ Advanced toggle | ✅ Complete |
| ML-based recommendations | ✅ Service layer exists | ❌ Uses rule-based `/recommend` | 🔴 **Critical Gap** |
| Rule-based recommendations | ✅ `/api/v1/crop/recommend` | ✅ Via proxy | ✅ Working |
| Simulation engine | ✅ Full engine | ✅ Proxy + results view | ✅ Complete |
| Market price integration | ✅ 3-tier fallback | ❌ Not displayed | ⚠️ Missing |
| Rainfall data display | ✅ History + forecast | ❌ Not shown | ⚠️ Missing |
| Soil analysis (image) | ⚠️ Mock only | ❌ Not implemented | 🔴 Placeholder |
| Chat/LLM interface | ✅ Multiple endpoints | ❌ Not implemented | 🔴 Missing |
| Roadmap/calendar | ✅ API exists | ❌ Not implemented | 🔴 Missing |
| Multi-language | ❌ No | ❌ No | - |
| Offline/PWA | ❌ No | ❌ No | - |

### 4.5 Critical Gaps to Address

1. **ML Model Not Used in Primary Flow**: The `/api/v1/crop/recommend` endpoint uses rule-based scoring. The trained RandomForest model is only accessible via internal service. Frontend should call a new `/api/v1/ml/recommend` endpoint.

2. **Hardcoded District/Soil Data**: Frontend has 10 districts and 8 soil types hardcoded. Should fetch from `/api/v1/soil/types` and `/api/v1/map/districts` (or similar).

3. **Missing Economic Data Display**: Simulation results show profit/ROI but frontend doesn't display market price source (live API vs fallback) or cost breakdown details.

4. **No Rainfall Visualization**: Backend has rich rainfall history/forecast APIs; frontend shows only single rainfall_mm input.

5. **Soil Image Analysis**: Backend endpoint exists but returns mock data; frontend has no upload component.

---

## Summary & Recommendations

### High Priority
1. **Expose ML Model via API**: Create `/api/v1/ml/crop-recommend` endpoint that uses `crop_recommendation_service.recommend_crops()` for true ML-based recommendations.

2. **Dynamic Reference Data**: Add API endpoints to fetch districts, soil types, crops from database for frontend dropdowns.

3. **Integrate Market Price Display**: Show live vs fallback price source in simulation results with timestamps.

4. **Complete Soil Analysis**: Implement actual ML model for soil image classification or remove placeholder.

### Medium Priority
5. **Rainfall Charts**: Add historical rainfall charts and forecast visualization to frontend.

6. **Farming Roadmap UI**: Implement calendar/timeline view for `/api/v1/roadmap` data.

7. **Chat Interface**: Integrate LLM chat endpoints into frontend.

### Low Priority
8. **PWA/Offline Support**: For field usage.

9. **Multi-language**: Hindi/Tamil/Telugu support for farmer accessibility.

10. **Advanced Analytics**: SHAP explanations for ML recommendations, sensitivity analysis in simulation.

---

## Appendix: Key File Paths Reference

| Category | Path |
|----------|------|
| **Main Backend Entry** | `backend/main.py` |
| **ML Inference Module** | `ml/inference/crop_recommendation.py` |
| **Crop Recommendation Service** | `backend/services/crop_recommendation_service.py` |
| **Rule-Based Crop API** | `backend/api/crop_recommendation.py` |
| **Simulation Engine** | `backend/services/simulation_engine.py` |
| **Market Pricing Service** | `backend/services/market_pricing.py` |
| **Model Artifacts** | `models/crop_recommendation_model.pkl`, `training_data/crop_scaler.pkl`, `training_data/crop_label_mapping.json` |
| **Training Scripts** | `ml/training/train_crop_recommendation.py`, `ml/training/training_data/prepare_training_data.py` |
| **Master Datasets** | `agribrain_shared_pack/data/master_agri_dataset_v2_fixed.csv`, `agribrain_shared_pack/data/crop_agronomy_base.json` |
| **Frontend Components** | `frontend_web/src/components/{InputPanel,CropCard,SimulationResults}.tsx` |
| **Frontend API Proxies** | `frontend_web/src/app/api/{recommend,simulate}/route.ts` |
| **Configuration** | `backend/core/config.py`, `.env` (not in repo) |

---

*Report generated from read-only inspection of `C:\Users\USER\Downloads\FinalYearProject`. No files were modified during this audit.*
  roi_percent: number;
  sustainability_index: number;
  risk_level: string;  // "low"/"medium"/"high"
  monthly_breakdown: Array<{
    month: number;
    rainfall_mm: number;
    irrigation_needed_mm: number;
    water_available_liters: number;
    water_used_liters: number;
    growth_stage: string;
  }>
}
```

**Display Features:**
- Currency formatting (INR, en-IN locale)
- Risk level color coding (green/amber/red badges)
- Monthly breakdown table with growth stages
- Water sufficiency indicator
- ROI percentage display

#### API Routes (Next.js Proxy Layer)
**`/api/recommend/route.ts`:**
- Proxies POST to `BACKEND_URL/api/v1/crop/recommend`
- Transforms backend response to frontend-expected format
- Adds computed fields: `crop_id`, `fertilizer_requirement`, `estimated_cost`, `estimated_revenue`, `risk_score`, `sustainability_score`

**`/api/simulate/route.ts`:**
- Proxies to `BACKEND_URL/api/v1/simulation/run`
- Passes through simulation request/response
- `CropPrice` - crop_id, market, price_per_ton (₹/Ton), price_date, source
- `SoilType` - id, name, properties
- `DistrictSoilType` - district_id, soil_type_id, percentage, is_predominant
- `RainfallMonthly` - district_id, year, month, rainfall_mm
- `RainfallForecast` - district_id, forecast_date, predicted_mm, model_version
- `SimulationResult` - user_id, all simulation inputs + outputs + roadmap (JSON)

---

## 4. Legacy UI & Frontend Review

### 4.1 Frontend Architecture

**New Production Frontend:** `frontend_web/` - **Next.js 16.4.6 + React 19.3 + TypeScript + TailwindCSS 4.3**

**Key Dependencies:**
```json
{
  "next": "16.4.6",
  "react": "19.3.0",
  "react-dom": "19.3.0",
  "tailwindcss": "4.3.3",
  "typescript": "^5"
}
```

**No legacy Streamlit frontend found** - `frontend_streamlit/` directory exists but is empty.

### 4.2 Next.js Frontend Structure (`frontend_web/src`)

```
src/
├── app/
│   ├── layout.tsx          # Root layout with Geist font
│   ├── globals.css         # Tailwind + custom styles
│   ├── api/
│   │   ├── recommend/route.ts   # Proxy to backend /api/v1/crop/recommend
│   │   └── simulate/route.ts    # Proxy to backend /api/v1/simulation/run
│   └── page.tsx            # Main page (not yet inspected)
├── components/
│   ├── InputPanel.tsx      # Form input for crop recommendation
│   ├── CropCard.tsx        # Display crop recommendation with metrics
│   └── SimulationResults.tsx  # Detailed simulation results view
├── context/
│   └── SelectedCropContext.tsx  # React context for selected crop state
```
- `/api/v1/roadmap` - Farming activity calendar
- `/api/v1/chat` - LLM chat interface (multiple versions)
- `/api/v1/baseline` - Baseline data endpoints
    "ph": float,          # Soil pH
    "rainfall": float     # mm annual/seasonal
}
```

**Preprocessing Pipeline:**
1. Extract features in exact order above
2. Convert to numpy array: `X_raw = np.array([[input_features[col] for col in FEATURE_COLUMNS]])`
3. Apply **StandardScaler** (loaded from `crop_scaler.pkl`): `X_scaled = scaler.transform(X_raw)`
4. Predict probabilities: `probs = model.predict_proba(X_scaled)[0]`
5. Sort by probability, return top-k with crop names from reverse label mapping

### 2.3 Algorithm & Training Details

| Aspect | Specification |
|--------|---------------|
| **Algorithm** | `RandomForestClassifier(n_estimators=100, random_state=42)` |
| **Target Variable** | `label_encoded` (integer 0-21 representing crop class) |
| **Number of Classes** | 22 crops |
| **Training Data Source** | `datasets/01_crop_recommendation/Crop_recommendation.csv` (Kaggle standard dataset) |
| **Train/Val/Test Split** | 70% / 15% / 15% (stratified by label) |
| **Feature Scaling** | `StandardScaler` fit on training data only |
| **Label Encoding** | `LabelEncoder` on crop name strings |
| **Model Persistence** | `joblib.dump(model, "crop_recommendation_model.pkl")` |
| **Training Script** | `ml/training/train_crop_recommendation.py` (calls `ml.inference.crop_recommendation.merge_data`, `train_model`) |
| **Data Preparation** | `ml/training/training_data/prepare_training_data.py` - `task1()` handles crop recommendation |

### 2.4 Other ML Models in Repository

| Model | Algorithm | Features | Target |
|-------|-----------|----------|--------|
| **Fertilizer Recommendation** | RandomForest (implied) | Temperature, Humidity, Moisture, N, P, K, Soil Type (OHE), Crop Type (OHE) | Fertilizer Name (encoded) |
| **Yield Prediction** | Not fully inspected | Advanced features from `advanced_yield_train.csv` | Yield (continuous) |
| **Rainfall Forecast** | Referenced in config (`RAINFALL_FORECAST_MODEL_PATH`) | Monthly historical | Future rainfall |
| **Soil Classifier** | Referenced in config (`SOIL_CLASSIFIER_MODEL_PATH`) | Image-based (placeholder) | Soil type from image |
| **Disease Detector** | Referenced in config (`DISEASE_DETECTOR_MODEL_PATH`) | Image-based (placeholder) | Plant disease |