# ACTUAL IMPLEMENTATION AUDIT
## Technical Deep-Dive of AgriBrain Implementation

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  

---

## 1. NEXT.JS FRONTEND - ACTUAL IMPLEMENTATION

### 1.1 Architecture
- **Framework:** Next.js 14+ with App Router (`frontend_web/src/app/`)
- **State Management:** React Context (`FarmContext.tsx`) - global farm state
- **Styling:** Tailwind CSS with dark mode support
- **UI Components:** Radix UI primitives + custom components

### 1.2 Key Components

| Component | File | Functionality |
|-----------|------|---------------|
| MapUI | `src/components/MapUI.tsx` | Leaflet map with draggable pin, click handler, fly-to |
| MapSelector | `src/components/MapSelector.tsx` | Alternative map implementation |
| ChatAssistant | `src/components/ChatAssistant.tsx` | Text + vision chat with Groq |
| WeatherWidget | `src/components/WeatherWidget.tsx` | **MOCK DATA ONLY** - no live API |
| AlertsWidget | `src/components/AlertsWidget.tsx` | Visual alerts display |
| DigitalTwinWidget | `src/components/DigitalTwinWidget.tsx` | Metrics display |

### 1.3 Pages

| Page | Route | Purpose |
|------|-------|---------|
| Home | `/` | Landing with 3 nav cards + ChatAssistant |
| Simulate | `/simulate` | 3-step wizard: Map → Crop Selection → Parameters |
| Calendar | `/calendar` | Monthly cultivation timeline + widgets |
| Expert Chat | `/expert-chat` | AI agronomist with full farm context |

### 1.4 Local Fallback Engine (`simulate/page.tsx`)
**Location:** Lines 360-450 (400+ lines of simulation logic)

**Capabilites:**
- 45-crop database (CROP_DATABASE constant from engine_content.txt)
- 8 soil profiles with NPK/pH values
- Deterministic agro-zone mapping from lat/lon (inferRegionalProfile)
- Heuristic suitability scoring (penalty-based formula)
- Manual SHAP-style feature contributions
- Digital twin: yield, revenue, water, risk calculations
- 5-stage timeline generation
- What-if overrides (temp, rain, pH, N, P, K)

**Limitations:**
- Not automatic fallback - requires manual "Run Local Engine" button
- Different formulas than backend (e.g., score bounds 54-98.9 vs 52-98.8)
- Duplicate codebase - maintenance burden

---

## 2. FASTAPI BACKEND - ACTUAL IMPLEMENTATION

### 2.1 Architecture
- **Framework:** FastAPI with SQLAlchemy ORM
- **Database:** SQLite (dev) / PostgreSQL (prod) via config
- **Routers:** 3 mounted at both `/api/v1` and `/api` (double-mounted)
  - `/spatial` - Reverse geocoding + zone detection
  - `/simulation` - Digital twin simulation
  - `/chat` - Groq text + vision endpoints
  - `/crop` - ML-based crop recommendation

### 2.2 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/spatial/lookup` | POST | Reverse geocode + soil/weather |
| `/api/v1/spatial/autocomplete` | GET | District search |
| `/api/v1/simulation/run` | POST | Full simulation with overrides |
| `/api/v1/chat/troubleshoot` | POST | Groq text chat with context |
| `/api/v1/chat/vision` | POST | Groq vision (plant image) |
| `/api/v1/crop/recommend` | POST | XGBoost ML recommendation |

### 2.3 Services

| Service | File | Key Functions |
|---------|------|---------------|
| Weather Service | `services/weather_service.py` | `get_live_weather()`, `get_weather_for_district()` |
| Market Pricing | `services/market_pricing.py` | `fetch_live_market_price()`, fallback to baselines |
| Crop Recommendation | `services/crop_recommendation_service.py` | `recommend_crops()` - rule-based |
| Simulation Engine | `services/simulation_engine.py` | `run_simulation()` - DB-backed |

### 2.4 ML Inference (`ml/inference/crop_recommendation.py`)

**XGBoost Model:**
- Loads from `saved_models/xgboost_crop_model.pkl` (joblib)
- 22 crop classes (fruits: apple, banana, coconut, mango, papaya, etc.)
- Includes LabelEncoder, StandardScaler, feature names
- `predict_crop()` returns top-k with probabilities

**Yield Prediction (RandomForest):**
- `predict_yield()` function exists but **requires missing training data**
- Tries to load `crop_production_processed.csv` → **FILE NOT FOUND**
- Falls back to synthetic RandomForest on dummy data

---

## 3. SPATIAL & GEOCODING - ACTUAL IMPLEMENTATION

### 3.1 Nominatim Integration (`api/spatial.py`)

```python
# Lines 10-26: Actual API call
response = requests.get(
    "https://nominatim.openstreetmap.org/reverse",
    params={"lat": lat, "lon": lon, "format": "json", "addressdetails": 1},
    headers={"User-Agent": "AgriBrain-DigitalTwin/3.0"},
    timeout=5
)
```

### 3.2 Zone Detection (Deterministic - NOT from datasets)

```python
# Lines 28-33: Coordinate-based rules
if lat > 29.8: return "Himalayan"
elif lon < 76.2 and lat < 19.5: return "West Coast"
elif lon > 79.8 and lat < 21.0: return "East Coast"
elif lat > 25.5 and lon > 74.5: return "Northern Plains"
elif lon < 74.5 and lat > 22.0: return "Arid West"
else: return "Deccan Plateau"
```

### 3.3 Soil/Weather Generation (Mathematical Formulas)

```python
# Lines 38-59: Formulaic generation
pH = 6.5 + (lat - 20) * 0.02 + (lon - 78) * 0.01 + noise
N = 120 + (lat - 20) * 1.5 + noise
# ... similar for P, K, temp, humidity, rainfall
```

**Key Finding:** All spatial data is **mathematically generated**, not sourced from real geospatial datasets.

---

## 4. CROP RECOMMENDATION - ACTUAL IMPLEMENTATION

### 4.1 Backend: Three Different Systems

**System A: ML-Based (XGBoost)** - `api/crop_recommendation.py`
- 22 fruit/crop classes (mostly fruits)
- Requires: N, P, K, temperature, humidity, pH, rainfall
- Returns: crop_name, confidence, probabilities, match_reasons

**System B: Heuristic (Rule-Based)** - `services/crop_recommendation_service.py`
- Uses 9 CropProfile DB records (Rice, Wheat, Maize, Cotton, Soybean, Groundnut, Sugarcane, Chickpea)
- Scores based on: temp range, pH range, rainfall range, soil type match, NPK suitability
- Returns: crop_name, confidence, match_reasons array

**System C: Simulation Engine** - `api/simulation.py`
- 42 crops (22 short-term + 20 long-term)
- Penalty-based scoring with 4 features (temp, rain, pH, N)
- Returns: ranked crops with digital twin, SHAP, timeline

### 4.2 Frontend: Local Engine (`simulate/page.tsx`)
- Same 42 crops as backend simulation
- Different penalty weights and bounds
- Independent implementation

### 4.3 Database Crops (`models/__init__.py` → `CropProfile`)
Only 9 crops seeded:
| Crop | N_req | P_req | K_req | Temp Range | pH Range | Rainfall Range |
|------|-------|-------|-------|------------|----------|----------------|
| Rice | 120 | 60 | 40 | 20-35 | 5.5-7.0 | 1000-2000 |
| Wheat | 150 | 60 | 40 | 12-25 | 6.0-7.5 | 300-600 |
| Maize | 180 | 70 | 50 | 18-32 | 5.5-7.5 | 500-1000 |
| Cotton | 120 | 60 | 60 | 20-35 | 5.5-8.0 | 500-1200 |
| Soybean | 20 | 60 | 40 | 20-30 | 6.0-7.5 | 600-1000 |
| Groundnut | 20 | 40 | 40 | 22-32 | 6.0-7.0 | 500-1000 |
| Sugarcane | 250 | 100 | 200 | 20-35 | 6.0-8.0 | 1000-2000 |
| Chickpea | 20 | 50 | 30 | 10-25 | 6.0-8.0 | 300-600 |

---

## 5. SIMULATION ENGINE - ACTUAL IMPLEMENTATION

### 5.1 Digital Twin Modules

**Module 1: Yield & Revenue** (`simulation.py` lines 125-130)
```
suitability_factor = score_pct / 100.0
predicted_yield_per_acre = base_yield_t_acre * suitability_factor
total_yield_tonnes = predicted_yield_per_acre * area_acres
estimated_revenue_inr = total_yield_tonnes * msp_inr_t
```

**Module 2: Irrigation Water Demand** (lines 131-135)
```
effective_rain_mm = rainfall * 0.75
net_irrigation_mm = max(120.0, crop_water_mm - effective_rain_mm)
total_water_m3 = net_irrigation_mm * 4.047 * area_acres
daily_water_liters = (total_water_m3 * 1000) / max(60, duration_days)
```

**Module 3: Multi-Hazard Risk** (lines 138-141)
```
drought_risk = "High" if rainfall < 75 else "Moderate" if rainfall < 130 else "Low"
pest_risk = "High" if (humidity > 75 and temp > 27) else "Moderate" if humidity > 60 else "Low"
soil_stress = "High (Acidic/Alkaline Alert)" if (pH < 5.5 or pH > 7.8) else "Optimal"
```

**Module 4: SHAP Explanation** (lines 100-113, 145-156) - **MANUAL, NOT REAL SHAP**
```python
shap_breakdown = [
    {"feature": "Temperature", "impact": max(-0.35, 0.35 - temp_diff * 0.02)},
    {"feature": "Rainfall", "impact": max(-0.35, 0.35 - rain_diff * 0.015)},
    {"feature": "Soil pH", "impact": max(-0.25, 0.25 - ph_diff * 0.02)},
    {"feature": "Soil Nitrogen", "impact": max(-0.25, 0.25 - n_diff * 0.02)},
]
```

**Module 5: Timeline** (lines 171-201)
- Hardcoded 5-stage template
- **Optional:** Groq LLM override if `GROQ_API_KEY` set

### 5.2 What-If Overrides (lines 80-90)
```python
overrides = body.get("overrides") or {}
if overrides.get("rainfall"): weather["rainfall"] = float(overrides["rainfall"])
if overrides.get("temp"): weather["temp"] = float(overrides["temp"])
if overrides.get("ph"): soil["pH"] = float(overrides["ph"])
if overrides.get("N"): soil["N"] = int(overrides["N"])
```

---

## 6. GROQ INTEGRATION - ACTUAL IMPLEMENTATION

### 6.1 Text Chat (`api/chat.py` lines 75-88)
```python
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
comp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "system", "content": system_prompt}, 
              {"role": "user", "content": user_message}],
    temperature=0.5,
    max_tokens=900
)
```

### 6.2 Vision Chat (`api/chat.py` lines 44-63)
```python
comp = client.chat.completions.create(
    model="llama-3.2-11b-vision-preview",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]
    }],
    temperature=0.4,
    max_tokens=900
)
```

### 6.3 Timeline Generation (`simulation.py` lines 179-201)
```python
prompt = f"Generate 5-stage timeline for {area_acres} acres of {top_crop}..."
comp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=600
)
```

---

## 7. DATABASE - ACTUAL STATE

### 7.1 Models Defined (10 tables)
1. `User` - Basic auth (unused)
2. `District` - Geometry + metadata
3. `SoilType` - 8 standard types
4. `DistrictSoilType` - Many-to-many with percentages
5. `CropProfile` - 9 crops seeded
6. `CropCost` - Cost items per crop (fertilizer, seed, etc.)
7. `RainfallMonthly` - Historical monthly data
8. `RainfallDaily` - Daily records
9. `MarketPrice` - Price records
10. `SimulationResult` - **Defined but NEVER persisted**

### 7.2 Data Seeding Status
- **District/Soil:** Import script exists (`soil_spatial_import.py`) but needs GeoJSON/CSV files
- **Crops:** 9 profiles seeded (test_crop_reqs.py confirms)
- **Costs:** Unknown if seeded
- **Rainfall:** Multiple CSV files in datasets/ but import status unknown
- **Market Prices:** DataGov CSV present but import status unknown

---

## 8. TEST RESULTS - ACTUAL EXECUTION

### 8.1 Unit Tests Passed
```bash
$ python -m pytest tests/test_crop_recommendation.py -v
# 3 passed: merge_data, train_model, recommend (synthetic data)
```

### 8.2 Integration Tests - Issues Found
```bash
$ python tests/test_crop_rec.py
# ML model loads but returns SAME recommendations for ALL test cases
# apple: 0.57, banana: 0.36, papaya: 0.05, coconut: 0.01, rice: 0.01
# Model appears to ignore input features
```

```bash
$ python tests/test_sim.py
# ML prediction failed: crop_production_processed.csv not found
# Simulation engine works with DB crops (9 crops)
# Shows yield, cost, revenue, ROI calculations
# Risk levels calculated correctly
```

---

## 9. SECURITY & OPERATIONAL GAPS

| Issue | Location | Severity |
|-------|----------|----------|
| CORS: `ALLOWED_ORIGINS: ["*"]` | `config.py` line 23 | HIGH |
| No authentication/authorization | Entire API | HIGH |
| No rate limiting | All endpoints | MEDIUM |
| Hardcoded session_id "agribrain_chat" | `chat.py` line 24, `api.ts` line 95 | MEDIUM |
| API keys in .env (not rotated) | `config.py` | MEDIUM |
| Upstash Redis configured but unused | `config.py` lines 40-41 | LOW |
| SimulationResult model unused | `models/__init__.py` | LOW |

---

## 10. DEPLOYMENT CONFIGURATION

### 10.1 Frontend (Vercel-ready)
- `next.config.ts`: `output: "standalone"` for container deployment
- Environment variables via `.env.local`

### 10.2 Backend (Render-ready)
- `render.yaml` documented in TECHNICAL_ARCHITECTURE.md
- SQLite for dev, PostgreSQL for prod
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 10.3 Environment Variables Required
```
DATABASE_URL
GROQ_API_KEY
WEATHER_API_KEY (IndianAPI)
DATAGOV_API_KEY (Market prices)
OPENWEATHER_API_KEY (Alternative weather)
IMD_API_KEY (Alternative weather)
UPSTASH_REDIS_REST_URL
UPSTASH_REDIS_REST_TOKEN
```

---

## CONCLUSION

The AgriBrain project has a **substantial codebase with working components**, but significant gaps exist between documentation claims and reality:

1. **SHAP is NOT implemented** - manual heuristics only
2. **45 crops claimed, 42 in simulation, 22 in ML, 9 in DB**
3. **WeatherWidget is mock-only** - no live API in frontend
4. **Yield ML model non-functional** - missing training data
5. **Frontend/Backend duplicate but divergent logic**
6. **No authentication, open CORS** - not production-ready
7. **Spatial data is formulaic, not dataset-driven**
8. **Database largely unseeded** - import scripts exist but not run

The system works as a **demonstration/prototype** but requires substantial work for production use.