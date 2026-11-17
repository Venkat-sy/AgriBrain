# Unified Crop Recommendation Service Specification

**Version:** 1.0
**Status:** Draft for Review
**Author:** AgriBrain Architecture Team
**Date:** 2026-11-16

---

## 1. Executive Summary

This specification consolidates three divergent crop recommendation systems into a single authoritative service:

| System | Crops | Algorithm | Endpoint | Status |
|--------|-------|-----------|----------|--------|
| **XGBoost (ML)** | 22 fruits/field crops | XGBoost Classifier (SMOTE) | `/api/v1/crop/recommend` | **Broken** — returns identical output |
| **Heuristic (DB)** | 9 crops (DB-backed) | Rule-based matching | `/api/v1/crop/profiles` (read-only) | Works but **unused** |
| **Simulation** | 40 crops (22 short + 18 long) | Penalty-based scoring | `/api/simulation/run` | **Production** — used by frontend |

**Goal:** Single source of truth for crop recommendations serving both the crop recommendation endpoint and the simulation engine.

---

## 2. Single Crop Database Source

### 2.1 File Location & Format

**Primary Source:** `agribrain_shared_pack/data/crops_master.yaml` (YAML for human readability + comments)

**Fallback/Generated:** `agribrain_shared_pack/data/crops_master.json` (auto-generated from YAML for runtime)

### 2.2 Schema Definition

```yaml
# crops_master.yaml
crops:
  - id: "rice"
    name: "Rice (Paddy)"
    category: "cereal"
    season: "Kharif"
    duration_days: 120
    # Agronomic optimals (from ICAR Package of Practices)
    opt_temp_c: 28
    opt_rainfall_mm: 210
    opt_ph: 6.0
    opt_n_kg_ha: 180
    opt_p_kg_ha: 60
    opt_k_kg_ha: 60
    # Economic
    base_yield_t_ha: 4.5
    msp_inr_per_t: 23000
    market_price_inr_per_t: 22000
    cultivation_cost_inr_per_ha: 45000
    water_requirement_mm: 1200
    # Suitability
    suitable_soils: ["Alluvial", "Clay Loam", "Silty Clay"]
    soil_ph_range: [5.5, 7.0]
    temp_range_c: [20, 35]
    rainfall_range_mm: [100, 300]
    # ML metadata
    ml_supported: true          # Present in XGBoost label_mapping
    legacy_rf_supported: true   # Present in legacy RandomForest training data
    simulation_tier: "short-term"  # or "long-term"
    data_source: "ICAR Package of Practices"
    last_updated: "2026-11-16"
```

### 2.3 Crop Inventory (42+ Crops)

| # | Crop ID | Name | Category | Season | ML (XGB) | Legacy RF | Simulation | Shared JSON |
|---|---------|------|----------|--------|----------|-----------|------------|-------------|
| 1 | rice | Rice (Paddy) | cereal | Kharif | ✅ | ✅ | ✅ (ST) | ✅ |
| 2 | wheat | Wheat | cereal | Rabi | ❌ | ✅ | ✅ (ST) | ✅ |
| 3 | maize | Maize (Hybrid) | cereal | Kharif/Rabi | ✅ | ✅ | ✅ (ST) | ✅ |
| 4 | blackgram | Blackgram (Urad) | pulse | Kharif/Zaid | ✅ | ❌ | ✅ (ST) | ❌ |
| 5 | mungbean | Mungbean (Moong) | pulse | Zaid/Kharif | ✅ | ❌ | ✅ (ST) | ❌ |
| 6 | chickpea | Chickpea (Bengal Gram) | pulse | Rabi | ✅ | ✅ | ✅ (ST) | ✅ |
| 7 | pigeonpea | Pigeonpea (Tur/Arhar) | pulse | Kharif | ✅ | ❌ | ✅ (ST) | ✅ |
| 8 | groundnut | Groundnut (Peanut) | oilseed | Kharif/Rabi | ❌ | ❌ | ✅ (ST) | ✅ |
| 9 | soybean | Soybean | oilseed | Kharif | ✅ | ✅ | ✅ (ST) | ✅ |
| 10 | mustard | Mustard (Rapeseed) | oilseed | Rabi | ❌ | ✅ | ✅ (ST) | ✅ |
| 11 | sunflower | Sunflower | oilseed | Rabi/Zaid | ❌ | ✅ | ✅ (ST) | ✅ |
| 12 | cotton | Cotton (Bt Hybrid) | fiber | Kharif | ✅ | ✅ | ✅ (ST) | ✅ |
| 13 | jute | Jute | fiber | Kharif | ✅ | ✅ | ✅ (ST) | ✅ |
| 14 | potato | Potato | tuber | Rabi | ❌ | ❌ | ✅ (ST) | ❌ |
| 15 | onion | Onion | vegetable | Rabi/Kharif | ❌ | ❌ | ✅ (ST) | ❌ |
| 16 | tomato | Tomato (Hybrid) | vegetable | All-Season | ❌ | ❌ | ✅ (ST) | ❌ |
| 17 | chilli | Chilli (Guntur/Byadgi) | spice | Kharif/Rabi | ❌ | ❌ | ✅ (ST) | ❌ |
| 18 | okra | Okra (Bhindi) | vegetable | Zaid/Kharif | ❌ | ❌ | ✅ (ST) | ❌ |
| 19 | watermelon | Watermelon | fruit | Zaid | ✅ | ❌ | ✅ (ST) | ❌ |
| 20 | muskmelon | Muskmelon | fruit | Zaid | ✅ | ❌ | ✅ (ST) | ❌ |
| 21 | ragi | Ragi (Finger Millet) | millet | Kharif | ❌ | ✅ | ✅ (ST) | ✅ |
| 22 | bajra | Bajra (Pearl Millet) | millet | Kharif | ❌ | ✅ | ✅ (ST) | ✅ |
| 23 | coconut | Coconut (Tall/Dwarf) | plantation | Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 24 | arecanut | Arecanut (Supari) | plantation | Perennial | ❌ | ❌ | ✅ (LT) | ❌ |
| 25 | mango | Mango (Alphonso/Kesar) | fruit | Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 26 | banana | Banana (Grand Naine) | fruit | Annual/Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 27 | pomegranate | Pomegranate (Bhagwa) | fruit | Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 28 | coffee | Coffee (Arabica/Robusta) | plantation | Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 29 | blackpepper | Black Pepper (Panniyur) | spice | Perennial | ❌ | ❌ | ✅ (LT) | ❌ |
| 30 | cashew | Cashew (Vengurla) | plantation | Perennial | ❌ | ❌ | ✅ (LT) | ❌ |
| 31 | papaya | Papaya (Red Lady) | fruit | Long-Duration | ❌ | ❌ | ✅ (LT) | ❌ |
| 32 | guava | Guava (Taiwan Pink) | fruit | Perennial | ❌ | ❌ | ✅ (LT) | ❌ |
| 33 | grapes | Grapes (Thompson) | fruit | Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 34 | sweetorange | Sweet Orange (Mosambi) | fruit | Perennial | ✅ | ❌ | ✅ (LT) | ❌ |
| 35 | apple | Apple (Gala/Delicious) | fruit | Temperate | ✅ | ❌ | ✅ (LT) | ❌ |
| 36 | sugarcane | Sugarcane (Co-86032) | commercial | Annual/Ratoon | ❌ | ✅ | ✅ (LT) | ✅ |
| 37 | turmeric | Turmeric (Prathibha) | spice | Long-Duration | ❌ | ❌ | ✅ (LT) | ❌ |
| 38 | ginger | Ginger (Rio-de-Janeiro) | spice | Long-Duration | ❌ | ❌ | ✅ (LT) | ❌ |
| 39 | rubber | Rubber (RRII 105) | plantation | Perennial | ❌ | ❌ | ✅ (LT) | ❌ |
| 40 | cardamom | Cardamom (Malabar) | spice | Highland | ❌ | ❌ | ✅ (LT) | ❌ |
| 41 | sorghum | Sorghum (Jowar) | cereal | Kharif | ❌ | ✅ | ❌ | ✅ |
| 42 | barley | Barley | cereal | Rabi | ❌ | ✅ | ❌ | ✅ |
| 43 | sesame | Sesame (Til) | oilseed | Kharif | ❌ | ❌ | ❌ | ✅ |
| 44 | castor | Castor | oilseed | Kharif | ❌ | ❌ | ❌ | ✅ |
| 45 | linseed | Linseed | oilseed | Rabi | ❌ | ❌ | ❌ | ✅ |
| 46 | greengram | Green Gram (Moong) | pulse | Kharif | ❌ | ❌ | ❌ | ✅ |
| 47 | kidneybeans | Kidney Beans (Rajma) | pulse | Rabi | ✅ | ❌ | ❌ | ❌ |
| 48 | lentil | Lentil (Masoor) | pulse | Rabi | ✅ | ❌ | ❌ | ❌ |
| 49 | mothbeans | Moth Beans (Matki) | pulse | Kharif | ✅ | ❌ | ❌ | ❌ |
| 50 | orange | Orange (Citrus) | fruit | Perennial | ✅ | ❌ | ❌ | ❌ |

**Total Unique Crops:** 50 (42 core + 8 extended from ML/Shared)

> **Note:** Crops marked `simulation_tier: "short-term"` (ST) or `"long-term"` (LT) are available in the simulation engine. Crops with `ml_supported: true` are in the XGBoost label_mapping (22 classes). Crops with `legacy_rf_supported: true` are in the legacy RandomForest training data.

### 2.4 Data Loading Contract

```python
# backend/services/crop_data_service.py
from pathlib import Path
import yaml
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class CropRecord(BaseModel):
    id: str
    name: str
    category: str
    season: str
    duration_days: int
    opt_temp_c: float
    opt_rainfall_mm: float
    opt_ph: float
    opt_n_kg_ha: float
    opt_p_kg_ha: float
    opt_k_kg_ha: float
    base_yield_t_ha: float
    msp_inr_per_t: float
    market_price_inr_per_t: float
    cultivation_cost_inr_per_ha: float
    water_requirement_mm: float
    suitable_soils: List[str]
    soil_ph_range: List[float]
    temp_range_c: List[float]
    rainfall_range_mm: List[float]
    ml_supported: bool = False
    legacy_rf_supported: bool = False
    simulation_tier: str  # "short-term" | "long-term"
    data_source: str
    last_updated: str

class CropDataService:
    _instance: Optional["CropDataService"] = None
    _crops: Dict[str, CropRecord] = {}
    _by_simulation_tier: Dict[str, List[CropRecord]] = {"short-term": [], "long-term": []}
    _ml_supported: List[CropRecord] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        path = Path(__file__).resolve().parents[2] / "agribrain_shared_pack" / "data" / "crops_master.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        for c in data["crops"]:
            record = CropRecord(**c)
            self._crops[record.id] = record
            self._by_simulation_tier[record.simulation_tier].append(record)
            if record.ml_supported:
                self._ml_supported.append(record)

    def get(self, crop_id: str) -> Optional[CropRecord]:
        return self._crops.get(crop_id)

    def all(self) -> List[CropRecord]:
        return list(self._crops.values())

    def by_tier(self, tier: str) -> List[CropRecord]:
        return self._by_simulation_tier.get(tier, [])

    def ml_supported_crops(self) -> List[CropRecord]:
        return self._ml_supported
```

---

## 3. Unified Scoring Algorithm

### 3.1 Architecture: ML Primary, Heuristic Fallback

```
┌─────────────────────────────────────────────────────────────┐
│                    recommend_crops()                          │
├─────────────────────────────────────────────────────────────┤
│  1. Validate input features (N, P, K, temp, humidity,       │
│     ph, rainfall, soil_type, district)                       │
│  2. Try ML Scoring (XGBoost)                                 │
│     ├─ Load XGBoost bundle                                   │
│     ├─ Run inference → probabilities per crop                │
│     ├─ Compute SHAP explanations                             │
│     └─ Map to unified response format                        │
│     │                                                         │
│     └─❌ On failure (model missing, inference error,         │
│         identical outputs detected) → FALLBACK               │
│  3. Heuristic Scoring (Penalty-based, simulation-compatible) │
│     ├─ For each crop in requested tier (or all)              │
│     ├─ Compute penalty = Σ |input - optimal| × weight        │
│     ├─ Score = clamp(100 - penalty × 0.42, 52, 98.8)        │
│     ├─ Generate match_reasons from top penalties             │
│     └─ Return top-K                                           │
│  4. Attach metadata: version, model_used, shap_data          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 ML Scoring (Primary)

**Input Features (7):**
| Feature | Key | Unit | Source |
|---------|-----|------|--------|
| Nitrogen | `N` | kg/ha | Soil test / API input |
| Phosphorus | `P` | kg/ha | Soil test / API input |
| Potassium | `K` | kg/ha | Soil test / API input |
| Temperature | `temperature` | °C | Weather API / API input |
| Humidity | `humidity` | % | Weather API / API input |
| Soil pH | `ph` | - | Soil test / API input |
| Rainfall | `rainfall` | mm | Weather API / API input |

**Output per Crop:**
```json
{
  "crop_id": "rice",
  "crop_name": "Rice (Paddy)",
  "confidence": 0.87,
  "match_reasons": ["Optimal temperature match", "Adequate rainfall"],
  "shap_values": [
    {"feature": "temperature", "value": 27.5, "shap_value": 0.23, "impact": "positive"},
    {"feature": "rainfall", "value": 200, "shap_value": 0.18, "impact": "positive"},
    {"feature": "ph", "value": 6.2, "shap_value": -0.05, "impact": "negative"}
  ],
  "model_version": "xgboost_v2.0",
  "expected_yield_t_ha": 4.2,
  "season": "Kharif"
}
```

**Identical-Output Detection (Circuit Breaker):**
```python
def _detect_identical_outputs(recommendations: List[Dict]) -> bool:
    """XGBoost model is broken — returns same confidence for all crops."""
    if len(recommendations) < 2:
        return False
    confidences = [r["confidence"] for r in recommendations]
    # If all confidences are identical (within epsilon) or top-3 are identical
    return len(set(round(c, 4) for c in confidences[:3])) == 1
```

### 3.3 Heuristic Scoring (Fallback — Simulation Compatible)

**Penalty Weights (from simulation.py, calibrated):**
| Factor | Weight | Formula |
|--------|--------|---------|
| Temperature | 2.1 | `abs(temp - opt_temp) * 2.1` |
| Rainfall | 0.22 | `abs(rainfall - opt_rainfall) * 0.22` |
| Soil pH | 11.5 | `abs(ph - opt_ph) * 11.5` |
| Nitrogen (N) | 0.14 | `abs(N - opt_n) * 0.14` |

**Score Calculation:**
```python
def heuristic_score(crop: CropRecord, features: Dict) -> float:
    temp_diff = abs(features["temperature"] - crop.opt_temp_c) * 2.1
    rain_diff = abs(features["rainfall"] - crop.opt_rainfall_mm) * 0.22
    ph_diff = abs(features["ph"] - crop.opt_ph) * 11.5
    n_diff = abs(features["N"] - crop.opt_n_kg_ha) * 0.14
    total_penalty = temp_diff + rain_diff + ph_diff + n_diff
    score = max(52.0, min(98.8, round(100.0 - total_penalty * 0.42, 1)))
    return score
```

**Match Reasons Generation:**
```python
def generate_match_reasons(crop: CropRecord, features: Dict) -> List[str]:
    reasons = []
    diffs = {
        "temperature": (abs(features["temperature"] - crop.opt_temp_c), "°C"),
        "rainfall": (abs(features["rainfall"] - crop.opt_rainfall_mm), "mm"),
        "ph": (abs(features["ph"] - crop.opt_ph), "pH units"),
        "nitrogen": (abs(features["N"] - crop.opt_n_kg_ha), "kg/ha"),
    }
    # Sort by closeness (smallest diff first)
    sorted_factors = sorted(diffs.items(), key=lambda x: x[1][0])
    for factor, (diff, unit) in sorted_factors[:2]:
        if factor == "temperature" and diff <= 3:
            reasons.append(f"Optimal temperature ({features['temperature']:.1f}°C vs {crop.opt_temp_c}°C ideal)")
        elif factor == "rainfall" and diff <= 50:
            reasons.append(f"Adequate rainfall ({features['rainfall']:.0f}mm vs {crop.opt_rainfall_mm}mm ideal)")
        elif factor == "ph" and diff <= 0.5:
            reasons.append(f"Suitable soil pH ({features['ph']:.1f} vs {crop.opt_ph:.1f} ideal)")
        elif factor == "nitrogen" and diff <= 30:
            reasons.append(f"Good nitrogen availability ({features['N']:.0f} vs {crop.opt_n_kg_ha:.0f} kg/ha ideal)")
    return reasons or ["Moderate suitability for local conditions"]
```

### 3.4 Unified Scoring Interface

```python
# backend/services/unified_crop_service.py
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel
from backend.services.crop_data_service import CropDataService, CropRecord

class ScoringInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    soil_type: Optional[str] = None
    district_id: Optional[int] = None
    tier: Optional[Literal["short-term", "long-term", "all"]] = "all"
    top_k: int = 5
    include_shap: bool = True

class ScoredCrop(BaseModel):
    crop_id: str
    crop_name: str
    confidence: float          # 0.0 - 1.0 (normalized score_pct / 100)
    score_pct: float           # 0 - 100 (raw score for simulation compatibility)
    match_reasons: List[str]
    expected_yield_t_ha: Optional[float] = None
    season: str
    duration_days: int
    shap_values: Optional[List[Dict]] = None
    model_used: Literal["xgboost", "heuristic"]
    model_version: str

class RecommendationResult(BaseModel):
    recommendations: List[ScoredCrop]
    model_used: Literal["xgboost", "heuristic"]
    model_version: str
    fallback_triggered: bool
    generated_at: str

def recommend_crops(input: ScoringInput) -> RecommendationResult:
    crop_service = CropDataService()
    pool = crop_service.all() if input.tier == "all" else crop_service.by_tier(input.tier)
    
    # Try ML first
    ml_result = _try_ml_scoring(input, pool)
    if ml_result and not _detect_identical_outputs(ml_result.recommendations):
        return ml_result
    
    # Fallback to heuristic
    heuristic_result = _heuristic_scoring(input, pool)
    heuristic_result.fallback_triggered = True
    return heuristic_result
```

---

## 4. API Contract: `/api/v1/crop/recommend`

### 4.1 Request

```http
POST /api/v1/crop/recommend
Content-Type: application/json
```

```json
{
  "district_id": 123,
  "soil_type": "Alluvial",
  "rainfall_mm": 200,
  "temperature_c": 27.5,
  "humidity_percent": 65,
  "ph": 6.2,
  "n": 180,
  "p": 60,
  "k": 60,
  "top_k": 5,
  "tier": "all",
  "include_shap": true,
  "include_economics": true,
  "include_digital_twin": false
}
```

**Field Definitions:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| district_id | int | ✅ | — | District ID for weather fallback |
| soil_type | string | ✅ | — | Soil type name (e.g., "Alluvial") |
| rainfall_mm | float | ✅ | — | Rainfall in mm |
| temperature_c | float | ❌ | weather API | Air temperature °C |
| humidity_percent | float | ❌ | weather API | Relative humidity % |
| ph | float | ❌ | soil default | Soil pH |
| n | float | ❌ | soil default | Nitrogen kg/ha |
| p | float | ❌ | soil default | Phosphorus kg/ha |
| k | float | ❌ | soil default | Potassium kg/ha |
| top_k | int | ❌ | 5 | Number of recommendations (1-10) |
| tier | enum | ❌ | "all" | "short-term" \| "long-term" \| "all" |
| include_shap | bool | ❌ | true | Include SHAP explanations |
| include_economics | bool | ❌ | false | Include yield, revenue, cost estimates |
| include_digital_twin | bool | ❌ | false | Full digital twin output (simulation parity) |

### 4.2 Response (Success: 200)

```json
{
  "district_id": 123,
  "soil_type": "Alluvial",
  "rainfall_mm": 200,
  "recommendations": [
    {
      "crop_id": "rice",
      "crop_name": "Rice (Paddy)",
      "confidence": 0.87,
      "score_pct": 87.2,
      "match_reasons": [
        "Optimal temperature (27.5°C vs 28°C ideal)",
        "Adequate rainfall (200mm vs 210mm ideal)"
      ],
      "expected_yield_t_ha": 4.2,
      "season": "Kharif",
      "duration_days": 120,
      "shap_values": [
        {"feature": "temperature", "value": 27.5, "shap_value": 0.23, "impact": "positive"},
        {"feature": "rainfall", "value": 200, "shap_value": 0.18, "impact": "positive"},
        {"feature": "ph", "value": 6.2, "shap_value": -0.05, "impact": "negative"}
      ],
      "model_used": "xgboost",
      "model_version": "xgboost_v2.0",
      "economics": {
        "base_yield_t_ha": 4.5,
        "predicted_yield_t_ha": 4.2,
        "msp_inr_per_t": 23000,
        "market_price_inr_per_t": 22000,
        "cultivation_cost_inr_per_ha": 45000,
        "estimated_revenue_inr_per_ha": 92400,
        "estimated_profit_inr_per_ha": 47400
      }
    }
  ],
  "model_used": "xgboost",
  "model_version": "xgboost_v2.0",
  "fallback_triggered": false,
  "generated_at": "2026-11-16T10:30:00Z",
  "version": "unified_v1.0"
}
```

### 4.3 Response (Fallback Indicated)

```json
{
  "recommendations": [...],
  "model_used": "heuristic",
  "model_version": "penalty_v1.0",
  "fallback_triggered": true,
  "fallback_reason": "identical_outputs_detected",
  "generated_at": "2026-11-16T10:30:00Z",
  "version": "unified_v1.0"
}
```

### 4.4 Error Responses

| Code | Condition | Body |
|------|-----------|------|
| 400 | Invalid input (missing required, out of range) | `{ "detail": "temperature_c must be between -10 and 50" }` |
| 404 | District not found | `{ "detail": "District 999 not found" }` |
| 500 | Internal error (both ML and heuristic failed) | `{ "detail": "Recommendation service unavailable" }` |

---

## 5. Integration with Simulation Endpoint

### 5.1 Current Simulation Flow

```
/api/simulation/run
  → lookup_spatial(lat, lng) → district, soil, weather
  → Select pool: SHORT_TERM_CROPS or LONG_TERM_CROPS (inline arrays)
  → For each crop: penalty_score = f(temp, rain, ph, N)
  → Sort by score_pct descending
  → Digital Twin: yield, revenue, irrigation, risk, timeline
  → SHAP from XGBoost (per-crop, for explanation only)
  → Return full simulation response
```

### 5.2 New Unified Flow

```
/api/simulation/run
  → lookup_spatial(lat, lng) → district, soil, weather
  → Build ScoringInput from spatial + overrides
  → Call unified recommend_crops(ScoringInput)
  → Get ScoredCrop[] with score_pct, confidence, shap_values
  → Digital Twin modules consume ScoredCrop[] directly
  → Return simulation response (unchanged format)
```

### 5.3 Shared Data Contract

```python
# backend/services/simulation_adapter.py
from backend.services.unified_crop_service import recommend_crops, ScoringInput
from backend.api.spatial import lookup_spatial

def build_scoring_input_from_simulation(
    lat: float, lng: float, area_acres: float,
    tier: str, overrides: Dict
) -> ScoringInput:
    spatial = lookup_spatial(lat, lng)
    soil = spatial["soil"]
    weather = spatial["weather"]
    
    # Apply digital twin overrides
    if overrides.get("rainfall") is not None:
        weather["rainfall"] = float(overrides["rainfall"])
    if overrides.get("temp") is not None:
        weather["temp"] = float(overrides["temp"])
    if overrides.get("ph") is not None:
        soil["pH"] = float(overrides["ph"])
    if overrides.get("N") is not None:
        soil["N"] = int(overrides["N"])
    
    return ScoringInput(
        N=soil.get("N", 100),
        P=soil.get("P", 40),
        K=soil.get("K", 150),
        temperature=weather["temp"],
        humidity=weather["humidity"],
        ph=soil["pH"],
        rainfall=weather["rainfall"],
        soil_type=soil["type"],
        district_id=spatial["district"]["id"],
        tier=tier,
        top_k=10,
        include_shap=True,
        include_economics=True,
        include_digital_twin=True
    )

def run_simulation_unified(request: Dict) -> Dict:
    # ... existing setup ...
    input = build_scoring_input_from_simulation(lat, lng, area_acres, pref, overrides)
    result = recommend_crops(input)
    
    # Convert to simulation response format
    scored_crops = []
    for rec in result.recommendations:
        scored_crops.append({
            "crop": rec.crop_name,
            "season": rec.season,
            "duration_days": rec.duration_days,
            "confidence": rec.confidence,
            "score_pct": rec.score_pct,
            "base_yield_t_acre": rec.expected_yield_t_ha / 2.471,  # ha → acre
            "msp_inr_t": crop_service.get(rec.crop_id).msp_inr_per_t,
            "water_mm": crop_service.get(rec.crop_id).water_requirement_mm,
            "shap_breakdown": rec.shap_values or []
        })
    
    # ... existing digital twin modules using scored_crops ...
    return simulation_response
```

### 5.4 Backward Compatibility

- **Response format unchanged** — simulation frontend consumes identical JSON structure
- **Scoring parity** — heuristic mode uses exact same penalty weights as current simulation
- **SHAP parity** — ML mode returns authentic SHAP; heuristic mode returns simulated breakdown (same format)
- **No frontend changes required**

---

## 6. Deprecation Plan: Orphaned XGBoost Endpoint

### 6.1 Current Orphaned Endpoint

| Endpoint | File | Status |
|----------|------|--------|
| `POST /api/v1/crop/recommend` | `backend/api/crop_recommendation.py` | **Active but broken** — uses XGBoost directly, returns identical outputs |

### 6.2 Deprecation Timeline

| Phase | Date | Action |
|-------|------|--------|
| **Phase 0** | Week 0 | Deploy unified service behind feature flag `UNIFIED_CROP_SERVICE=true` |
| **Phase 1** | Week 1 | Route `/api/v1/crop/recommend` to unified service (shadow mode: log both old/new) |
| **Phase 2** | Week 2 | Validate parity: compare unified vs simulation heuristic for 1000 random inputs |
| **Phase 3** | Week 3 | Enable unified as primary; old XGBoost code path disabled but kept |
| **Phase 4** | Week 4 | Remove `backend/api/crop_recommendation.py` and `backend/services/crop_recommendation_service.py` |
| **Phase 5** | Week 5 | Remove XGBoost bundle loading from `backend/ml/inference/crop_recommendation.py` (keep for SHAP in simulation) |
| **Phase 6** | Week 6 | Archive legacy training code (`backend/ml/crop_recommendation.py`, `backend/ml/train_crop_model.py`) |

### 6.3 Migration Checklist

- [ ] Create `crops_master.yaml` with all 50 crops (merge simulation + XGBoost + shared JSON)
- [ ] Implement `CropDataService` singleton
- [ ] Implement `unified_crop_service.py` with ML + heuristic scoring
- [ ] Add identical-output detection circuit breaker
- [ ] Update `/api/v1/crop/recommend` to call unified service
- [ ] Update `/api/simulation/run` to call unified service via adapter
- [ ] Add feature flag `UNIFIED_CROP_SERVICE`
- [ ] Integration tests: unified service vs simulation heuristic parity
- [ ] Load test: 100 concurrent recommendations < 200ms p95
- [ ] Documentation update: API docs, architecture decision record

### 6.4 Rollback Plan

If unified service introduces regressions:
1. Flip feature flag `UNIFIED_CROP_SERVICE=false`
2. Old `/api/v1/crop/recommend` (XGBoost) and `/api/simulation/run` (inline heuristic) resume immediately
3. No data migration needed (stateless)

---

## 7. Feature Parity Matrix

| Feature | XGBoost (Old) | Heuristic DB (Old) | Simulation (Old) | Unified (New) |
|---------|---------------|--------------------|------------------|---------------|
| **Crop Coverage** | 22 crops | 9 crops (DB) | 40 crops | **50 crops** (master) |
| **ML Inference** | ✅ XGBoost | ❌ | ❌ (SHAP only) | ✅ Primary (XGBoost) |
| **Heuristic Fallback** | ❌ | ✅ Rule-based | ✅ Penalty-based | ✅ Penalty-based (sim-compatible) |
| **Identical-Output Detection** | ❌ | N/A | N/A | ✅ Circuit breaker |
| **SHAP Explanations** | ✅ Per-crop | ❌ | ✅ Per-crop (authentic) | ✅ Per-crop (authentic or simulated) |
| **Match Reasons** | ❌ Empty array | ❌ | ❌ | ✅ Generated from penalties |
| **Yield Estimates** | ❌ None | ✅ DB field | ✅ base_yield × suitability | ✅ From master data |
| **Economic Data** | ❌ | ✅ Cost/Price tables | ✅ MSP, water, revenue | ✅ From master data |
| **Season Info** | ❌ None | ✅ DB field | ✅ Inline | ✅ From master data |
| **Duration** | ❌ None | ✅ DB field | ✅ Inline | ✅ From master data |
| **Soil Suitability** | ❌ | ✅ JSON array | ❌ | ✅ From master data |
| **Digital Twin Modules** | ❌ | ❌ | ✅ Yield, irrigation, risk, timeline | ✅ Via simulation adapter |
| **Tier Filtering** | ❌ | ❌ (all 9) | ✅ short/long | ✅ short/long/all |
| **District Weather Fallback** | ✅ | ❌ | ✅ | ✅ |
| **Overrides Support** | ❌ | ❌ | ✅ Rain, temp, pH, N | ✅ Passed through |
| **API Versioning** | `xgboost_v2.0` | N/A | N/A | `unified_v1.0` |
| **Frontend Consumers** | Crop Rec page | None | Dashboard/Map | **Both** |

---

## 8. Implementation Files Summary

### New Files
```
backend/services/
├── crop_data_service.py          # Singleton loader for crops_master.yaml
├── unified_crop_service.py       # Core scoring logic (ML + heuristic)
└── simulation_adapter.py         # Bridge for simulation endpoint

agribrain_shared_pack/data/
└── crops_master.yaml             # Single source of truth (50 crops)
```

### Modified Files
```
backend/api/
├── crop_recommendation.py        # → delegates to unified_crop_service
└── simulation.py                 # → uses simulation_adapter

backend/ml/inference/
└── crop_recommendation.py        # → keep for SHAP only; remove XGBoost bundle loading
```

### Removed Files (Phase 4+)
```
backend/api/crop_recommendation.py           # Old XGBoost endpoint
backend/services/crop_recommendation_service.py  # Old shim
backend/ml/crop_recommendation.py            # Legacy training shim
backend/ml/train_crop_model.py               # Legacy training script
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
```python
# tests/test_unified_crop_service.py
def test_heuristic_scoring_matches_simulation():
    """Heuristic scores must match simulation.py penalty formula exactly."""
    input = ScoringInput(N=180, P=60, K=60, temperature=28, humidity=70, ph=6.0, rainfall=210)
    result = recommend_crops(input)
    # Verify rice scores ~87-90 (same as simulation)
    rice = next(r for r in result.recommendations if r.crop_id == "rice")
    assert 85 <= rice.score_pct <= 92

def test_identical_output_detection():
    """Circuit breaker triggers when ML returns identical confidences."""
    with patch("backend.ml.inference.crop_recommendation.recommend") as mock:
        mock.return_value = [{"crop_name": c, "confidence": 0.5, "match_reasons": []} for c in ["rice", "wheat", "maize"]]
        result = recommend_crops(valid_input)
        assert result.fallback_triggered == True
        assert result.model_used == "heuristic"

def test_tier_filtering():
    input = ScoringInput(..., tier="short-term")
    result = recommend_crops(input)
    assert all(r.season != "Perennial" for r in result.recommendations)
```

### 9.2 Integration Tests
```python
# tests/test_api_crop_recommend.py
async def test_recommend_endpoint_returns_unified_format(client):
    resp = await client.post("/api/v1/crop/recommend", json=valid_request)
    assert resp.status_code == 200
    data = resp.json()
    assert "model_used" in data
    assert data["model_used"] in ("xgboost", "heuristic")
    assert "fallback_triggered" in data
    assert all("crop_id" in r for r in data["recommendations"])
    assert all("score_pct" in r for r in data["recommendations"])

async def test_simulation_parity(client):
    """Simulation and crop/recommend must agree on top-3 for same input."""
    sim_resp = await client.post("/api/simulation/run", json=sim_request)
    rec_resp = await client.post("/api/v1/crop/recommend", json=rec_request)
    sim_top3 = [c["crop"] for c in sim_resp.json()["alternatives"][:3]]
    rec_top3 = [r["crop_name"] for r in rec_resp.json()["recommendations"][:3]]
    assert sim_top3 == rec_top3
```

### 9.3 Load Tests
```bash
# Locust script: 100 users, 10 req/s, 5 min
# Target: p95 < 200ms, p99 < 500ms, 0% errors
locust -f load_test.py --users 100 --spawn-rate 10 --run-time 5m
```

---

## 10. Open Questions / Decisions Needed

| # | Question | Recommendation |
|---|----------|----------------|
| 1 | Should `crops_master.yaml` live in `agribrain_shared_pack` or `backend/data`? | `agribrain_shared_pack/data/` — shared across backend, frontend, ML training |
| 2 | Retrain XGBoost on full 50 crops or keep 22-class model? | **Keep 22-class** for now; `ml_supported` flag gates ML path. Retrain as separate effort. |
| 3 | Include P/K in heuristic scoring? | **No** — simulation only uses N, temp, rain, pH. Keep parity. |
| 4 | Expose `crop_id` (stable key) vs `crop_name` (display) in API? | **Both** — `crop_id` for programmatic use, `crop_name` for display. |
| 5 | Versioning strategy for `crops_master.yaml`? | Git-tracked; `last_updated` field per crop; API returns `version: "unified_v1.0-{git_sha}"` |
| 6 | Handle crops in master but not in ML label_mapping? | Heuristic-only path; `model_used: "heuristic"` for those crops even if ML succeeds for others. |

---

## 11. Appendix: Penalty Weight Derivation

Current simulation weights (from `simulation.py` lines 95-101):
```python
temp_diff = abs(weather["temp"] - c["opt_temp"]) * 2.1
rain_diff = abs(weather["rainfall"] - c["opt_rain"]) * 0.22
ph_diff = abs(soil["pH"] - c["opt_ph"]) * 11.5
n_diff = abs(soil["N"] - c["opt_n"]) * 0.14
total_penalty = temp_diff + rain_diff + ph_diff + n_diff
score = max(52.0, min(98.8, round(100.0 - total_penalty * 0.42, 1)))
```

**Unified heuristic uses identical formula** — ensures 1:1 parity between `/api/v1/crop/recommend` (fallback mode) and `/api/simulation/run`.

---

*End of Specification*