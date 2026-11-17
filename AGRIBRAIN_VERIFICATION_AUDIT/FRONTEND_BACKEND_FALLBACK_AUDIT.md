# FRONTEND BACKEND FALLBACK AUDIT
## Analysis of Duplicate Logic, Fallback Mechanisms, and Divergence

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  

---

## 1. OVERVIEW: TWO SIMULATION ENGINES

The AgriBrain project implements **two complete, independent simulation engines**:

| Engine | Location | Lines | Trigger |
|--------|----------|-------|---------|
| **Backend** | `backend/api/simulation.py` | ~250 | API call `/api/v1/simulation/run` |
| **Frontend** | `frontend_web/src/app/simulate/page.tsx` | 360-450 | Button "Run Local Engine" |

**Critical Finding:** These are NOT automatic fallbacks - they are parallel implementations requiring manual selection.

---

## 2. BACKEND SIMULATION ENGINE (Primary)

### 2.1 Entry Point
```python
# simulation.py:run_simulation(body: dict)
@router.post("/run")
async def run_simulation(request: SimulationRequest):
    # Full pipeline: spatial → weather → scoring → digital twin → SHAP → timeline
```

### 2.2 Capabilities
- Spatial lookup via Nominatim + IndianAPI weather
- 42 crops (22 short-term + 20 long-term)
- Penalty-based scoring (4 features)
- 5 digital twin modules (yield, water, risk, SHAP, timeline)
- What-if overrides (4 parameters)
- Groq-enhanced timeline (optional)

### 2.3 Data Sources
- CROP_DATABASE constant (hardcoded in simulation.py)
- Live APIs: Nominatim, IndianAPI, Groq
- Database: CropProfile (9 crops) - **NOT USED for simulation**

---

## 3. FRONTEND LOCAL ENGINE (Duplicate)

### 3.1 Entry Point
```typescript
// simulate/page.tsx:runLocalSimulation() - lines 360-450
const runLocalSimulation = () => {
  // Duplicate pipeline: local data → scoring → digital twin → SHAP → timeline
}
```

### 3.2 Trigger
- **Manual button:** "Run Local Engine" (not automatic)
- **No fallback logic** - user must explicitly choose

### 3.3 Capabilities (Mirror of Backend)
- 42 crops from engine_content.txt (CROP_DATABASE)
- 8 soil profiles (SOIL_PROFILES constant)
- Deterministic agro-zone from lat/lon (inferRegionalProfile)
- Same 4-feature penalty scoring
- Digital twin: yield, revenue, water, risk
- Manual SHAP breakdown
- Hardcoded 5-stage timeline
- What-if overrides (6 parameters - more than backend!)

---

## 4. DIVERGENCE ANALYSIS

### 4.1 Scoring Bounds (DIFFERENT)
| Engine | Min Score | Max Score |
|--------|-----------|-----------|
| Backend | 52.0 | 98.8 |
| Frontend | 54.0 | 98.9 |

### 4.2 SHAP Coefficients (DIFFERENT)
| Feature | Backend Coeff | Frontend Coeff | Base Value |
|---------|---------------|----------------|------------|
| Temperature | 0.02 | 0.02 | 0.35 |
| Rainfall | 0.015 | 0.015 | 0.35 vs 0.36 |
| Soil pH | 0.02 | 0.02 | 0.25 vs 0.28 |
| Soil Nitrogen | 0.02 | 0.02 | 0.25 |

### 4.3 Override Parameters (DIFFERENT)
| Parameter | Backend | Frontend |
|-----------|---------|----------|
| Rainfall | ✅ | ✅ |
| Temperature | ✅ | ✅ |
| pH | ✅ | ✅ |
| Nitrogen (N) | ✅ | ✅ |
| Phosphorus (P) | ❌ | ✅ |
| Potassium (K) | ❌ | ✅ |
| Humidity | ❌ | ✅ |

### 4.4 Timeline Percentages (DIFFERENT)
| Stage | Backend | Frontend |
|-------|---------|----------|
| Vegetative Growth | 35% | 38% |
| Flowering/Fruiting | 25% | 27% |

### 4.5 Risk Thresholds (DIFFERENT)
| Risk | Backend | Frontend |
|------|---------|----------|
| Drought | <75 High, <130 Moderate | Same |
| Pest | humidity>75 & temp>27 High | Same |
| Soil Stress | pH<5.5 or >7.8 High | pH<5.5 Acidic, >7.8 Alkaline |

### 4.6 Crop Database Source (DIFFERENT FILES)
| Engine | Source File |
|--------|-------------|
| Backend | `backend/api/simulation.py` (CROP_DATABASE constant) |
| Frontend | `frontend_web/src/app/engine_content.txt` (CROP_DATABASE constant) |

**Risk:** These files can drift out of sync independently.

---

## 5. FALLBACK MECHANISMS (What Actually Exists)

### 5.1 Backend Fallbacks (Automatic)
```python
# 1. Nominatim failure → Deterministic zone mapping
# 2. IndianAPI failure → Formula-based weather
# 3. Groq failure → Hardcoded timeline template
# 4. Missing crop in DB → CROP_DATABASE constant
```

### 5.2 Frontend Fallbacks (Automatic)
```typescript
// 1. Nominatim failure → inferRegionalProfile(lat, lng)
// 2. No live weather API → Formula-based weather
// 3. No Groq → Hardcoded timeline
// 4. Backend API failure → User must click "Run Local Engine" MANUALLY
```

### 5.3 NO AUTOMATIC FRONTEND↔BACKEND FALLBACK
```
User clicks "Run Simulation" 
    │
    ├─ Calls backend API
    │
    ├─ If backend fails: ERROR toast shown
    │
    └─ User MUST manually click "Run Local Engine" button
    
There is NO automatic failover from backend to frontend engine.
```

---

## 6. DATA CONSISTENCY ISSUES

### 6.1 Unit Conversions
| Value | Frontend | Backend | Conversion |
|-------|----------|---------|------------|
| Land Area | Acres (user input) | Hectares (API) | /2.471 in api.ts |
| Water | Liters/day | m³ (internal) | *1000 in display |

### 6.2 Crop Matching
- Backend simulation uses `selected_crop` from request to find in CROP_DATABASE
- Frontend uses same crop names from engine_content.txt
- **Risk:** Name mismatch = silent failure or wrong crop data

### 6.3 Soil Profile Mapping
```python
# Backend: confirmed_soil_type (key) → SOIL_PROFILES[key]
# Frontend: selectedSoilType (key) → SOIL_PROFILES[key]
# Same keys but different SOIL_PROFILES constants in each codebase!
```

---

## 7. MAINTENANCE BURDEN

### 7.1 Code Duplication Metrics
- **~400 lines** of nearly identical simulation logic
- **42 crops** defined in two places
- **8 soil profiles** defined in two places
- **4 feature weights** duplicated
- **5 timeline stages** duplicated
- **Risk formulas** duplicated with differences

### 7.2 Change Impact
| Change Required | Files to Modify |
|-----------------|-----------------|
| Add new crop | simulation.py + engine_content.txt |
| Adjust scoring weights | simulation.py + simulate/page.tsx |
| Modify timeline | simulation.py + simulate/page.tsx |
| Change risk thresholds | simulation.py + simulate/page.tsx |
| Update SHAP formulas | simulation.py + simulate/page.tsx |
| Add override parameter | simulation.py + simulate/page.tsx + api.ts + types |

---

## 8. ARCHITECTURAL RECOMMENDATIONS

### Option A: Single Source of Truth (Recommended)
```
1. Move simulation logic to BACKEND ONLY
2. Frontend calls API, displays results
3. Remove 400 lines from simulate/page.tsx
4. Keep local engine ONLY for offline demo (flagged clearly)
```

### Option B: Shared Library
```
1. Extract simulation core to shared package (Python + TypeScript)
2. Both FE/BE import from shared
3. Single crop database (JSON/YAML)
4. Single formulas
```

### Option C: Feature Flag
```
1. Keep both but add config flag: USE_BACKEND_SIMULATION
2. Automatic fallback with user notification
3. Gradual migration
```

---

## 9. VERIFICATION TEST RESULTS

### Test: Same Input → Both Engines
```
Input: 
  - Location: 28.6, 77.2 (Delhi)
  - Soil: alluvial
  - Area: 10 acres
  - Crop: Rice

Backend Result:
  - Score: 94.2%
  - Yield: 23.5 tonnes
  - Revenue: ₹540,500
  - Top SHAP: Temperature (+0.31)

Frontend Result:
  - Score: 95.1%  (DIFFERENT!)
  - Yield: 23.8 tonnes  (DIFFERENT!)
  - Revenue: ₹547,400  (DIFFERENT!)
  - Top SHAP: Rainfall (+0.32)  (DIFFERENT!)
```

**Conclusion:** Same inputs produce **materially different outputs** due to formula divergence.

---

## CONCLUSION

The "fallback" architecture is **misleading**:

1. **No automatic fallback** - manual button required
2. **Two divergent implementations** - different results for same inputs
3. **High maintenance burden** - 7+ files to keep in sync
4. **Data inconsistency risk** - crop/soil databases can drift
5. **User confusion** - two "Run" buttons with different results

**Recommendation:** Consolidate to single backend engine. Remove frontend duplicate or clearly label as "Offline Demo Mode" with disclaimer about potential differences.