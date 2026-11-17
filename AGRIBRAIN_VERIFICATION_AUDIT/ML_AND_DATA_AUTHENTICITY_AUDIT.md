# ML AND DATA AUTHENTICITY AUDIT
## Verification of ML Models, Training Data, and Explainability Claims

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  

---

## 1. CROP RECOMMENDATION ML MODEL (XGBoost)

### 1.1 Implementation Location
- File: `backend/ml/inference/crop_recommendation.py` (lines 49-66)
- Model artifacts: `ml_model.joblib`, `ml_scaler.joblib`, `ml_encoder.joblib`

### 1.2 Model Architecture
```python
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
```

### 1.3 Training Pipeline (crop_recommendation.py lines 13-47)
```python
def train_model():
    # 1. Load CSV: backend/datasets/crop_production.csv
    df = pd.read_csv("backend/datasets/crop_production.csv")
    
    # 2. Feature engineering
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[features]
    y = df['label']  # crop name
    
    # 3. Preprocessing
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    
    # 4. Train/val split
    X_train, X_val, y_train, y_val = train_test_split(X_scaled, y_encoded, test_size=0.2)
    
    # 5. Train XGBoost
    model.fit(X_train, y_train)
    
    # 6. Save artifacts (joblib)
    joblib.dump(model, "ml_model.joblib")
    joblib.dump(scaler, "ml_scaler.joblib")
    joblib.dump(encoder, "ml_encoder.joblib")
```

### 1.4 Inference Endpoint (/api/v1/crop/recommend)
```python
# Load artifacts at module level
model = joblib.load("ml_model.joblib")
scaler = joblib.load("ml_scaler.joblib")
encoder = joblib.load("ml_encoder.joblib")

# Predict
X_input = scaler.transform([[N, P, K, temp, humidity, ph, rainfall]])
probs = model.predict_proba(X_input)[0]
top_k = np.argsort(probs)[::-1][:5]
results = [{"crop": encoder.inverse_transform([i])[0], "confidence": probs[i]} for i in top_k]
```

### 1.5 Test Results (test_crop_rec.py)
```
❌ CRITICAL FAILURE: Model returns IDENTICAL output for ALL inputs
Test cases: 5 different (N,P,K,temp,humidity,ph,rainfall) combinations
Result: apple: 0.57, banana: 0.36, papaya: 0.05, coconut: 0.01, rice: 0.01
Model appears to IGNORE input features entirely
```

### 1.6 Training Data Verification
- **Source:** `backend/datasets/crop_production.csv` 
- **Status:** File EXISTS but contents unverified
- **Classes:** 22 fruit/crop labels (mostly fruits: apple, banana, coconut, mango, papaya, etc.)
- **Note:** Different from simulation crops (field crops: rice, wheat, maize, etc.)

---

## 2. YIELD PREDICTION ML MODEL

### 2.1 Implementation Location
- File: `backend/ml/inference/yield_prediction.py` (lines 1-60)
- Required training data: `crop_production_processed.csv`

### 2.2 Model Architecture
```python
# Attempts to load: yield_model.joblib, yield_scaler.joblib
# If not found, trains new model:
model = RandomForestRegressor(n_estimators=100, random_state=42)
```

### 2.3 Training Data Requirements
```python
# Features needed:
['State_Name', 'District_Name', 'Crop', 'Season', 'Area', 
 'Production', 'Yield', 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

# Target: Yield (tons/hectare)
```

### 2.4 Current Status: **BROKEN**
```
❌ MISSING FILE: crop_production_processed.csv
❌ Model artifacts NOT FOUND (yield_model.joblib, yield_scaler.joblib)
❌ Training pipeline cannot run without processed dataset
```

### 2.5 Error from Tests
```
test_sim.py → ML prediction failed: crop_production_processed.csv not found
Fallback: Uses heuristic simulation engine instead
```

---

## 3. CROP RECOMMENDATION SERVICE (Rule-Based/Heuristic)

### 3.1 Implementation Location
- File: `backend/services/crop_recommendation_service.py`
- Uses: Database `CropProfile` records (9 crops)

### 3.2 Algorithm (Deterministic Scoring)
```python
def calculate_suitability(crop_profile, conditions):
    score = 0
    
    # Temperature match (0-25 pts)
    if crop.temp_min <= conditions.temp <= crop.temp_max: score += 25
    elif abs(conditions.temp - crop.temp_opt) <= 5: score += 15
    
    # pH match (0-20 pts)
    if crop.ph_min <= conditions.ph <= crop.ph_max: score += 20
    
    # Rainfall match (0-20 pts)
    if crop.rain_min <= conditions.rainfall <= crop.rain_max: score += 20
    
    # Soil type match (0-15 pts)
    if conditions.soil_type in crop.suitable_soils: score += 15
    
    # NPK suitability (0-20 pts)
    # ... complex NPK ratio calculations
    
    return min(score, 100)
```

### 3.3 Database Crops (9 profiles seeded)
| Crop | Temp Range | pH Range | Rainfall (mm) |
|------|------------|----------|---------------|
| Rice | 20-35 | 5.5-7.0 | 1000-2000 |
| Wheat | 12-25 | 6.0-7.5 | 300-600 |
| Maize | 18-32 | 5.5-7.5 | 500-1000 |
| Cotton | 20-35 | 5.5-8.0 | 500-1200 |
| Soybean | 20-30 | 6.0-7.5 | 600-1000 |
| Groundnut | 22-32 | 6.0-7.0 | 500-1000 |
| Sugarcane | 20-35 | 6.0-8.0 | 1000-2000 |
| Chickpea | 10-25 | 6.0-8.0 | 300-600 |

---

## 4. SIMULATION ENGINE (Penalty-Based Heuristic)

### 4.1 Implementation Location
- File: `backend/api/simulation.py` (lines 85-114)
- Crops: 42 (22 short-term + 20 long-term) from CROP_DATABASE

### 4.2 Scoring Algorithm
```python
# For each crop:
temp_diff = abs(weather.temp - c.opt_temp) * 2.1
rain_diff = abs(weather.rainfall - c.opt_rain) * 0.22
ph_diff = abs(soil.pH - c.opt_ph) * 11.5
n_diff = abs(soil.N - c.opt_n) * 0.14

total_penalty = temp_diff + rain_diff + ph_diff + n_diff
score_pct = max(52.0, min(98.8, 100 - total_penalty * 0.42))
```

### 4.3 Crop Database Structure
```python
CROP_DATABASE = [
    {"name": "Rice", "type": "short_term", "opt_temp": 28, "opt_rain": 1200, "opt_ph": 6.5, "opt_n": 120, "base_yield": 2.5, "msp": 23000, "water": 1200, "duration": 120},
    {"name": "Wheat", "type": "short_term", "opt_temp": 20, "opt_rain": 500, "opt_ph": 7.0, "opt_n": 150, "base_yield": 3.2, "msp": 24250, "water": 500, "duration": 130},
    # ... 40 more crops
]
```

---

## 5. FRONTEND LOCAL ENGINE (Duplicate Penalty-Based)

### 5.1 Implementation Location
- File: `frontend_web/src/app/simulate/page.tsx` (lines 360-450)
- Crops: Same 42 from `engine_content.txt` (CROP_DATABASE constant)

### 5.2 Scoring Algorithm (DIFFERENT from backend!)
```javascript
// Frontend weights differ from backend:
tempDiff = Math.abs(weather.temp - crop.temp) * 2.1      // Same
rainDiff = Math.abs(weather.rainfall - crop.rain) * 0.22  // Same
phDiff = Math.abs(soil.pH - crop.ph) * 11.5              // Same
nDiff = Math.abs(soil.N - crop.n) * 0.14                 // Same

penalty = tempDiff + rainDiff + phDiff + nDiff
score = Math.max(54.0, Math.min(98.9, 100 - penalty * 0.42))  // DIFFERENT BOUNDS!
// Backend: 52.0 - 98.8
// Frontend: 54.0 - 98.9
```

---

## 6. SHAP EXPLAINABILITY - VERIFICATION

### 6.1 Claim vs Reality

| Claim | Reality |
|-------|---------|
| "SHAP-based explainability" | **FALSE** - No SHAP library imported anywhere |
| "Feature importance from SHAP" | Manual heuristic formulas with hardcoded coefficients |
| "SHAP values per prediction" | `max(-0.35, 0.35 - diff * coefficient)` calculations |

### 6.2 Evidence: No SHAP Dependency
```
grep -r "shap" backend/ --include="*.py"
# Returns ONLY: variable names "shap_breakdown", "shap_explanation"
# NO: import shap, shap.TreeExplainer, shap.Explanation, etc.

pip list | grep -i shap
# Not in requirements.txt or any installed packages
```

### 6.3 Backend Manual SHAP (simulation.py lines 100-113, 145-156)
```python
shap_breakdown = [
    {"feature": "Temperature", "impact": max(-0.35, 0.35 - temp_diff * 0.02)},
    {"feature": "Rainfall", "impact": max(-0.35, 0.35 - rain_diff * 0.015)},
    {"feature": "Soil pH", "impact": max(-0.25, 0.25 - ph_diff * 0.02)},
    {"feature": "Soil Nitrogen", "impact": max(-0.25, 0.25 - n_diff * 0.02)},
]
# Sorted by impact descending
# These are HEURISTIC FORMULAS, not SHAP values
```

### 6.4 Frontend Manual SHAP (simulate/page.tsx lines 397-405)
```javascript
// DIFFERENT COEFFICIENTS from backend!
shapBreakdown = [
  {feature: 'Seasonal Rainfall', impact: max(-0.35, 0.36 - rainDiff * 0.015)},  // 0.36 vs 0.35
  {feature: 'Temperature', impact: max(-0.35, 0.35 - tempDiff * 0.02)},
  {feature: 'Confirmed Soil pH', impact: max(-0.28, 0.28 - phDiff * 0.02)},    // 0.28 vs 0.25
  {feature: 'Soil Nitrogen (N)', impact: max(-0.25, 0.25 - nDiff * 0.02)},
].sort((a,b) => b.impact - a.impact)
```

---

## 7. THREE CROP RECOMMENDATION SYSTEMS COMPARISON

| Aspect | System A: ML (XGBoost) | System B: Heuristic (DB) | System C: Simulation | Frontend Local |
|--------|------------------------|-------------------------|---------------------|----------------|
| **Location** | `ml/inference/crop_rec.py` | `services/crop_rec_service.py` | `api/simulation.py` | `simulate/page.tsx` |
| **Crops** | 22 (fruits) | 9 (field crops) | 42 (mixed) | 42 (mixed) |
| **Method** | Trained XGBoost | Rule-based scoring | Penalty-based scoring | Penalty-based scoring |
| **Inputs** | N,P,K,temp,hum,ph,rain | temp,ph,rain,soil,NPK | temp,rain,ph,N (+overrides) | temp,rain,ph,N (+overrides) |
| **Output** | crop + confidence | crop + confidence + reasons | ranked + digital twin + SHAP | ranked + digital twin + SHAP |
| **Model File** | ml_model.joblib | DB (CropProfile) | Hardcoded CROP_DATABASE | engine_content.txt |
| **Test Status** | ❌ Same output for all inputs | ✅ Works (test_crop_reqs.py) | ✅ Works (test_sim.py) | Manual button only |

---

## 8. SPATIAL DATA AUTHENTICITY

### 8.1 Claim: "High-resolution soil maps, weather stations, agro-ecological zones"

### 8.2 Reality: **Mathematical Formulas, Not Datasets**

#### Agro-Zone Detection (spatial.py, simulate/page.tsx)
```python
# Backend: spatial.py lines 110-130
# Frontend: simulate/page.tsx inferRegionalProfile() lines 80-110

# LATITUDE/LONGITUDE → ZONE MAPPING:
if 8.0 <= lat <= 37.0 and 68.0 <= lng <= 97.0:  # India bounds
    if lat > 28: zone = "Trans-Gangetic Plains"      # Punjab, Haryana
    elif lat > 24: zone = "Upper Gangetic Plains"    # UP, Bihar
    elif lat > 20: zone = "Central Plateau"          # MP, Maharashtra
    elif lat > 16: zone = "Deccan Plateau"           # Karnataka, Telangana
    else: zone = "Southern Peninsula"                 # Tamil Nadu, Kerala
```

#### Soil Profile Generation (Mathematical)
```python
# 8 SOIL_PROFILES with fixed NPK/pH values
SOIL_PROFILES = {
    "alluvial": {"pH": 7.2, "N": 280, "P": 25, "K": 180},
    "black_cotton": {"pH": 7.8, "N": 220, "P": 18, "K": 320},
    "red_loam": {"pH": 6.2, "N": 180, "P": 22, "K": 150},
    # ... 5 more
}

# Zone → Soil mapping (deterministic)
zone_to_soil = {
    "Trans-Gangetic Plains": "alluvial",
    "Upper Gangetic Plains": "alluvial",
    "Central Plateau": "black_cotton",
    "Deccan Plateau": "red_loam",
    "Southern Peninsula": "laterite",
}
```

#### Weather Generation (Mathematical + Optional Live API)
```python
# Base formula (simulation.py lines 50-70):
base_temp = 28 - (lat - 20) * 0.4
base_rain = 1000 + (20 - lat) * 30
humidity = 65 + (20 - lat) * 1.2

# Live API enhancement (if WEATHER_API_KEY):
# https://weather.indianapi.in/india/weather?city={district}
```

### 8.3 District/Soil Import Script (NOT RUN)
- File: `backend/data_import/soil_spatial_import.py`
- Requires: GeoJSON boundaries + CSV soil data
- Status: Script exists but **no evidence it was executed**
- Database tables: `District`, `SoilType`, `DistrictSoilType` - likely empty

---

## 9. DATA SOURCES VERIFICATION

| Data Type | Claimed Source | Actual Status |
|-----------|----------------|---------------|
| Crop Production | ICAR / Government datasets | `crop_production.csv` exists; `crop_production_processed.csv` MISSING |
| Soil Maps | NBSS&LUP / ISRIC | **NOT USED** - mathematical formulas only |
| Weather | IMD / IndianAPI | IndianAPI integration exists but **key required** |
| Market Prices | DataGov / AGMARKNET | CSV file exists; import status unknown |
| Agro-Zones | ICAR Classification | **FORMULA-BASED** from lat/lon only |
| MSP Rates | Government announcements | Hardcoded in CROP_DATABASE |

---

## 10. AUTHENTICITY SCORECARD

| Component | Authentic ML/Data? | Evidence |
|-----------|-------------------|----------|
| Crop Rec ML (XGBoost) | ❌ **BROKEN** | Same output for all inputs; model ignores features |
| Yield Prediction ML | ❌ **MISSING** | Training data file not found; model not trained |
| Heuristic Crop Rec | ✅ **WORKING** | Rule-based, deterministic, tested |
| Simulation Engine | ✅ **WORKING** | Penalty-based heuristic, consistent results |
| SHAP Explainability | ❌ **FAKE** | No SHAP library; manual formulas with different coeffs |
| Spatial/Soil Data | ❌ **FORMULAIC** | Mathematical rules, no real geospatial datasets |
| Weather Data | ⚠️ **PARTIAL** | Live API code exists but fallback to formulas |
| Market Prices | ⚠️ **UNKNOWN** | Data file exists, import unconfirmed |

---

## CONCLUSION

**The AgriBrain project does NOT use authentic ML models or real geospatial datasets for its core agricultural intelligence.**

1. **Only ONE working ML model exists** (XGBoost crop rec) but it's **non-functional** (ignores inputs)
2. **Yield prediction ML is completely missing** (no training data, no model)
3. **SHAP explainability is entirely fabricated** - manual heuristic formulas
4. **Spatial/soil/weather data is mathematical fiction** - coordinate-based formulas
5. **Three different crop recommendation systems** exist with different crops, methods, outputs
6. **Frontend duplicates backend logic** with divergent parameters

The system functions as a **deterministic rule-based prototype**, not an ML-driven agricultural intelligence platform.