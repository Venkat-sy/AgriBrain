# WORKFLOW VERIFICATION
## Real Execution Sequences Traced from Code

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  

---

## WORKFLOW 1: SELECTING A LOCATION ON THE MAP

### Frontend → Backend → External API → Response → UI

```
1. USER ACTION: Clicks on MapUI component (MapUI.tsx)
   └─ ClickHandler.onClick(event) → gets lat/lng from leaflet event
   
2. FRONTEND STATE UPDATE:
   └─ handlePinDrop({lat, lng}) in simulate/page.tsx (line 150)
   └─ setPin({lat, lng})
   
3. REVERSE GEOCODING (Parallel paths):
   
   PATH A - Frontend Direct (simulate/page.tsx lines 161-174):
   └─ fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
   └─ Parses: district, state from address components
   └─ Calls inferRegionalProfile(lat, lng) for zone/soil/weather
   
   PATH B - Backend API (api.ts line 142):
   └─ api.getLocation(lat, lng) → POST /api/v1/spatial/lookup
   └─ Backend: spatial.py lookup_spatial(lat, lng)
   └─ Calls Nominatim API (same as frontend)
   └─ Falls back to deterministic zone mapping
   └─ Returns: district, state, agro_zone, soil{}, weather{}
   
4. UI UPDATE:
   └─ Displays districtName, agroZone, selectedSoilType
   └─ Shows coordinates badge
   └─ Enables "Run Simulation" button
```

### Verification: **WORKING** - Both paths functional, but DUPLICATE implementation

---

## WORKFLOW 2: REVERSE GEOCODING

### Backend Implementation (spatial.py lines 6-75)

```
FUNCTION: lookup_spatial(lat, lng)
1. Nominatim API Call:
   └─ GET https://nominatim.openstreetmap.org/reverse
   └─ Params: lat, lon, format=json, addressdetails=1
   └─ Headers: User-Agent: "AgriBrain-DigitalTwin/3.0"
   └─ Timeout: 5 seconds
   
2. Address Parsing (Priority Order):
   └─ state_district → county → city → town → village → suburb
   └─ State from: state field
   
3. On Success:
   └─ Determine agro-zone via coordinate rules
   └─ Generate soil/weather via mathematical formulas
   └─ Return structured dict
   
4. On Failure (Exception):
   └─ Fallback to deterministic zone mapping
   └─ Same coordinate-based rules
   └─ Generate synthetic soil/weather
```

### Verification: **WORKING** - Real Nominatim API call with proper fallback

---

## WORKFLOW 3: OBTAINING ENVIRONMENTAL INFORMATION

### Backend: Spatial → Weather API → Response

```
1. SPATIAL LOOKUP (as above) returns base weather dict

2. LIVE WEATHER ENHANCEMENT (simulation.py lines 75-82):
   └─ If WEATHER_API_KEY exists AND district != "Regional District"
   └─ Calls: https://weather.indianapi.in/india/weather?city={district}
   └─ Headers: Authorization + x-api-key
   └─ Timeout: 3 seconds
   └─ Updates: weather.temp, weather.humidity from API response
   
3. WHAT-IF OVERRIDES (simulation.py lines 84-92):
   └─ If request.body.overrides provided:
   └─ rainfall → weather.rainfall
   └─ temp → weather.temp
   └─ ph → soil.pH
   └─ N → soil.N
   
4. FINAL WEATHER OBJECT:
   └─ temp, humidity, rainfall (from API or fallback or override)
   └─ Used for all downstream calculations
```

### Verification: **PARTIALLY WORKING** - Live API requires key; fallback to formulaic data

---

## WORKFLOW 4: SELECTING SOIL

### Frontend: User Selection Overrides Detected

```
1. DETECTED SOIL: From spatial lookup (backend) or inferRegionalProfile (frontend)
   └─ Based on agro-zone → maps to one of 8 SOIL_PROFILES

2. USER OVERRIDE (simulate/page.tsx lines 177-183, 280-295):
   └─ Select dropdown with all 8 soil profiles
   └─ Each shows: name, pH, N, P, K values
   └─ onChange → setSelectedSoilType(key)
   
3. SIMULATION INPUT:
   └─ Frontend: Uses selectedSoilType for local engine
   └─ Backend: Sends confirmed_soil_type in SimulationRequest
   └─ Backend simulation.py: Overrides soil dict with user selection
```

### Verification: **WORKING** - Full user override capability

---

## WORKFLOW 5: ENTERING FARM ACREAGE

### Frontend → Simulation Request

```
1. INPUT FIELD (simulate/page.tsx line 267):
   └─ Input type="number" min="0.1" max="1000" step="0.1"
   └─ value={areaAcres} → setAreaAcres(Number(e.target.value))
   
2. LOCAL ENGINE: Uses areaAcres directly in calculations
   
3. BACKEND REQUEST (api.ts line 155):
   └─ simulation.run({
       district_id, selected_crop, land_area_ha: areaAcres/2.471,
       budget_inr, confirmed_soil_type, planting_month, overrides
     })
   └─ Note: Frontend uses ACRES, Backend converts to HECTARES (/2.471)
```

### Verification: **WORKING** - Unit conversion handled (acres ↔ hectares)

---

## WORKFLOW 6: RUNNING CROP RECOMMENDATIONS

### Three Divergent Paths Exist

#### PATH A: Frontend Local Engine (simulate/page.tsx lines 360-450)

```
1. TRIGGER: User clicks "Run Local Engine" button
2. GET DATA: 
   └─ weather from pin + inferRegionalProfile
   └─ soil from selectedSoilType (SOIL_PROFILES)
   └─ areaAcres from input
   
3. SCORE ALL CROPS (CROP_DATABASE from engine_content.txt):
   FOR each crop in 42 crops:
   └─ tempDiff = |weather.temp - crop.temp| * 2.1
   └─ rainDiff = |weather.rainfall - crop.rain| * 0.22
   └─ phDiff = |soil.pH - crop.ph| * 11.5
   └─ nDiff = |soil.N - crop.n| * 0.14
   └─ penalty = tempDiff + rainDiff + phDiff + nDiff
   └─ score = clamp(100 - penalty * 0.42, 54.0, 98.9)
   └─ shapBreakdown = manual 4-feature impacts
   └─ digital_twin = yield, revenue, water, risk
   └─ timeline = 5-stage hardcoded
   
4. SORT by score_pct descending
5. SET STATE: data = {ranked_crops, recommended_crop, timeline...}
6. SAVE to localStorage
```

#### PATH B: Backend Simulation API (/api/v1/simulation/run)

```
1. REQUEST: SimulationRequest with overrides
2. SPATIAL: lookup_spatial(lat, lng) → district, zone, soil, weather
3. LIVE WEATHER: Enhance with IndianAPI if key available
4. APPLY OVERRIDES: Modify weather/soil from request
5. SELECT POOL: LONG_TERM_CROPS or SHORT_TERM_CROPS (42 total)
6. SCORE ALL CROPS (simulation.py lines 85-114):
   FOR each crop in pool:
   └─ temp_diff = |weather.temp - c.opt_temp| * 2.1
   └─ rain_diff = |weather.rainfall - c.opt_rain| * 0.22
   └─ ph_diff = |soil.pH - c.opt_ph| * 11.5
   └─ n_diff = |soil.N - c.opt_n| * 0.14
   └─ total_penalty = sum
   └─ score = clamp(100 - total_penalty * 0.42, 52.0, 98.8)
   └─ shap_breakdown = 4 features with impact formulas
   
7. DIGITAL TWIN MODULES:
   └─ Module 1: Yield = base_yield * (score/100) * acres
   └─ Module 2: Water = (crop_water - 0.75*rain) * 4.047 * acres
   └─ Module 3: Risk = threshold-based rules
   └─ Module 4: SHAP = manual breakdown sorted by impact
   └─ Module 5: Timeline = hardcoded or Groq LLM
   
8. RETURN: Full response with ranked_crops, digital_twin, shap, timeline
```

#### PATH C: ML Crop Recommendation API (/api/v1/crop/recommend)

```
1. REQUEST: CropRecommendationRequest with NPK, temp, humidity, pH, rainfall
2. ML INFERENCE (crop_recommendation.py lines 49-66):
   └─ Load XGBoost model + scaler + encoder (joblib)
   └─ Transform input features
   └─ predict_proba → top_k indices
   └─ Map indices to crop names via label_encoder
   └─ Return: crop_name, confidence, probabilities, match_reasons
3. MODEL: 22 fruit classes (apple, banana, coconut, mango, papaya, etc.)
```

### Verification: **THREE DIVERGENT IMPLEMENTATIONS** - Different crops, formulas, results

---

## WORKFLOW 7: RUNNING WHAT-IF SCENARIOS

### Frontend UI → Backend Overrides → Recalculation

```
1. FRONTEND TOGGLE (simulate/page.tsx lines 297-330):
   └─ Checkbox: "Enable Environmental Overrides"
   └─ Shows 6 input fields: Temp, Humidity, Rainfall, pH, N, P, K
   └─ State: overrides = {temp, humidity, rainfall, ph, N, P, K}
   
2. LOCAL ENGINE: Applies overrides before scoring (lines 370-380)
   └─ weather.temp = overrides.temp || weather.temp
   └─ weather.rainfall = overrides.rainfall || weather.rainfall
   └─ soil.pH = overrides.ph || soil.pH
   └─ soil.N = overrides.N || soil.N
   
3. BACKEND API: Passes overrides in request body
   └─ simulation.run({..., overrides: {...}})
   └─ simulation.py lines 84-92: Applies to weather/soil dicts
   
4. RECALCULATION: Not real-time - requires "Run Simulation" button click
```

### Verification: **WORKING** - Manual trigger, not real-time sliders

---

## WORKFLOW 8: CALCULATING YIELD AND REVENUE

### Formula Trace (Both FE/BE)

```
YIELD CALCULATION:
1. suitability_factor = score_pct / 100.0
2. yield_per_acre = base_yield_t_acre * suitability_factor
3. total_yield_tonnes = yield_per_acre * area_acres

REVENUE CALCULATION:
4. estimated_revenue_inr = total_yield_tonnes * msp_inr_t
   └─ msp_inr_t = Minimum Support Price per ton (from crop data)
   
COST CALCULATION (Backend only - simulation_engine.py):
5. cost_breakdown = Σ (quantity × unit_cost) for each activity
   └─ Activities: Land Prep, Seeds, Fertilizer, Irrigation, Labor, etc.
6. total_cost_inr = Σ cost_breakdown

PROFIT & ROI:
7. net_profit_inr = estimated_revenue_inr - total_cost_inr
8. roi_percentage = (net_profit_inr / total_cost_inr) * 100

FRONTEND SIMPLIFICATION:
- Uses MSP directly, no cost breakdown
- grossRev = totalYield * c.msp (no costs)
```

### Verification: **WORKING** - Backend has full cost model, frontend simplified

---

## WORKFLOW 9: CALCULATING IRRIGATION DEMAND

### Backend (simulation.py lines 131-135) & Frontend (simulate/page.tsx lines 410-413)

```
1. effective_rain_mm = rainfall * 0.75  (75% effective)
2. net_irrigation_mm = max(120, crop_water_mm - effective_rain_mm)
   └─ Minimum 120mm floor
3. total_water_m3 = net_irrigation_mm * 4.047 * area_acres
   └─ 1mm over 1 acre = 4.047 m³ (CORRECT conversion)
4. daily_water_liters = (total_water_m3 * 1000) / max(60, duration_days)
   └─ Assumes minimum 60 days or crop duration
```

### Verification: **WORKING** - Simplified arithmetic, not FAO-56 methodology

---

## WORKFLOW 10: DISPLAYING RISK ANALYSIS

### Backend (simulation.py lines 138-141) vs Frontend (simulate/page.tsx lines 415-422)

```
BACKEND RISK:
drought_risk = "High" if rainfall < 75 
             else "Moderate" if rainfall < 130 
             else "Low"

pest_risk = "High" if (humidity > 75 AND temp > 27)
          else "Moderate" if humidity > 60
          else "Low"

soil_stress = "High (Acidic/Alkaline Alert)" if (pH < 5.5 OR pH > 7.8)
            else "Optimal"

FRONTEND RISK (DIFFERENT THRESHOLDS):
drought = rainfall < 75 ? 'High (Drip Required)' 
        : rainfall < 130 ? 'Moderate' : 'Low'

pest_disease = humidity > 75 && temp > 27 ? 'High (Fungal/Pest Alert)'
             : 'Moderate-Low'

soil_reaction = pH < 5.5 ? 'Acidic (Add Lime)'
              : pH > 7.8 ? 'Alkaline (Add Gypsum)'
              : 'Optimal pH Balance'
```

### Verification: **INCONSISTENT** - Different thresholds between FE/BE

---

## WORKFLOW 11: VIEWING SHAP EXPLANATIONS

### Backend (Manual) vs Frontend (Manual) - NO REAL SHAP

```
BACKEND (simulation.py lines 100-113, 145-156):
shap_breakdown = [
  {"feature": "Temperature", "value": weather.temp, "optimal": c.opt_temp,
   "impact": max(-0.35, 0.35 - temp_diff * 0.02)},
  {"feature": "Rainfall", "value": weather.rainfall, "optimal": c.opt_rain,
   "impact": max(-0.35, 0.35 - rain_diff * 0.015)},
  {"feature": "Soil pH", "value": soil.pH, "optimal": c.opt_ph,
   "impact": max(-0.25, 0.25 - ph_diff * 0.02)},
  {"feature": "Soil Nitrogen", "value": soil.N, "optimal": c.opt_n,
   "impact": max(-0.25, 0.25 - n_diff * 0.02)},
]
SORTED by impact descending

shap_explanation = {
  "top_feature": breakdown[0].feature,
  "contribution": breakdown[0].impact,
  "breakdown": breakdown,
  "reasoning": f"In {district} ({agro_zone}), {crop} achieved {score}% suitability. 
                Primary positive driver: {breakdown[0].feature}..."
}

FRONTEND (simulate/page.tsx lines 397-405):
shapBreakdown = [
  {feature: 'Seasonal Rainfall', impact: max(-0.35, 0.36 - rainDiff * 0.015)},
  {feature: 'Temperature', impact: max(-0.35, 0.35 - tempDiff * 0.02)},
  {feature: 'Confirmed Soil pH', impact: max(-0.28, 0.28 - phDiff * 0.02)},
  {feature: 'Soil Nitrogen (N)', impact: max(-0.25, 0.25 - nDiff * 0.02)},
].sort((a,b) => b.impact - a.impact)
```

### Verification: **FALSE CLAIM** - Not SHAP framework, manual heuristics with DIFFERENT formulas

---

## WORKFLOW 12: GENERATING CULTIVATION TIMELINES

### Backend (Hardcoded + Optional Groq) vs Frontend (Hardcoded)

```
BACKEND TIMELINE (simulation.py lines 171-201):
DEFAULT (Hardcoded 5 stages):
1. Land Preparation & Basal Nutrition (15 days)
2. Sowing / Orchard Transplanting (20 days)
3. Vegetative Growth & Irrigation (35% of duration)
4. Reproductive / Flowering & Pest Shield (25% of duration)
5. Maturity & Harvest Realization (20 days)

GROQ OVERRIDE (if GROQ_API_KEY):
- Prompt: "Generate 5-stage timeline for {acres} acres of {crop}..."
- Model: llama-3.3-70b-versatile, temp=0.3, max_tokens=600
- Parses JSON array from response
- Falls back to default on error

FRONTEND TIMELINE (simulate/page.tsx lines 425-440):
1. Land Prep & Soil Amendment (15 days)
2. Sowing / Transplanting (20 days)
3. Vegetative Growth & Irrigation (38% of duration)
4. Flowering, Fruiting & Pest Shield (27% of duration)
5. Maturity & Market Harvest (20 days)
- Different day percentages!
- Different agronomy advice text
```

### Verification: **DIVERGENT** - Different percentages, different text, Groq optional

---

## WORKFLOW 13: INTERACTING WITH AI AGRONOMIST (TEXT)

### Frontend ChatAssistant → Backend /chat/troubleshoot → Groq

```
1. USER TYPES MESSAGE in ChatAssistant.tsx
2. BUILD CONTEXT (ChatAssistant.tsx lines 65-84):
   └─ Farm context: crop, location, soil, area, season, dates
   └─ Simulation results: yield, revenue, cost, ROI, risk
   └─ Calendar stages: current stage, tasks
   └─ Formats as structured text block
   
3. API CALL (api.ts lines 86-105):
   └─ POST /api/v1/chat/troubleshoot
   └─ Body: {message, session_id: "agribrain_chat", context}
   
4. BACKEND (chat.py lines 75-88):
   └─ system_prompt = "You are an expert AI agronomist..."
   └─ user_content = f"Farm Context:\n{context}\n\nUser Question: {message}"
   └─ Groq API: llama-3.3-70b-versatile, temp=0.5, max_tokens=900
   └─ Returns: {response, model, usage}
   
5. UI UPDATE: Streams response, adds to message history
```

### Verification: **WORKING** - Full context injection, Groq integration functional

---

## WORKFLOW 14: SUBMITTING PLANT IMAGES FOR ANALYSIS

### Frontend Upload → Backend /chat/vision → Groq Vision

```
1. USER SELECTS IMAGE (ChatAssistant.tsx lines 27, 315-344):
   └─ input type="file" accept="image/*"
   └─ onChange → FileReader.readAsDataURL → base64 string
   └─ Preview shown before submit
   
2. API CALL (api.ts lines 73-92):
   └─ POST /api/v1/chat/vision
   └─ FormData: image (base64), prompt (optional)
   
3. BACKEND (chat.py lines 44-63):
   └─ Decodes base64, validates image
   └─ prompt = "You are an expert plant pathologist... {user_prompt}"
   └─ Groq API: llama-3.2-11b-vision-preview, temp=0.4, max_tokens=900
   └─ Messages: [{role: user, content: [text + image_url]}]
   └─ Returns: {response, model, usage}
   
4. UI UPDATE: Displays analysis response
```

### Verification: **WORKING** - Groq vision integration functional

---

## SUMMARY: WORKFLOW INTEGRITY

| Workflow | Frontend | Backend | Consistent? | Notes |
|----------|----------|---------|-------------|-------|
| Map Pin Selection | ✅ | ✅ | ✅ | Duplicate Nominatim calls |
| Reverse Geocoding | ✅ | ✅ | ✅ | Real API + fallback |
| Environmental Data | ✅ | ✅ | ⚠️ | Backend has live API option |
| Soil Selection | ✅ | ✅ | ✅ | User override works |
| Acreage Input | ✅ | ✅ | ✅ | Acres↔Hectares conversion |
| Crop Recommendations | ✅ | ✅ | ❌ | **3 different systems** |
| What-If Scenarios | ✅ | ✅ | ✅ | Manual trigger |
| Yield/Revenue | ✅ | ✅ | ⚠️ | Backend has costs, FE doesn't |
| Irrigation Demand | ✅ | ✅ | ✅ | Same formulas |
| Risk Analysis | ✅ | ✅ | ❌ | Different thresholds |
| SHAP Explainability | ✅ | ✅ | ❌ | Different formulas, not real SHAP |
| Cultivation Timeline | ✅ | ✅ | ❌ | Different percentages |
| AI Agronomist Chat | ✅ | ✅ | ✅ | Full context injection |
| Plant Image Analysis | ✅ | ✅ | ✅ | Groq vision working |

**Critical Finding:** Crop recommendation has **three divergent implementations** producing different results for same inputs.