# FINAL VERIFIED PROJECT CONTEXT
## AgriBrain - Independent Audit Handoff Document

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  
**Purpose:** Single source of truth for future developers, auditors, stakeholders  

---

## EXECUTIVE SUMMARY

AgriBrain is a **prototype agricultural decision support system** with a React/Next.js frontend and FastAPI/Python backend. While the system **runs end-to-end** and produces plausible outputs, **multiple core claims are unverified or false**:

| Claim | Verification | Reality |
|-------|-------------|---------|
| "45 crops supported" | ❌ False | 3 systems: 22/9/42 crops |
| "SHAP explainability" | ❌ False | Manual formulas, no SHAP lib |
| "ML yield prediction" | ❌ False | Missing data, no model artifacts |
| "Live weather data" | ⚠️ Partial | Backend only, frontend mock |
| "High-res spatial data" | ❌ False | Mathematical formulas only |
| "Production ready" | ❌ False | No auth, open CORS, no rate limit |

**Verdict:** Functional demo with **significant technical debt and claim gaps**. Not production-ready.

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │
│  │ Simulate    │ │ Expert      │ │ Crops       │ │ Weather   │  │
│  │ (dual eng)  │ │ Chat        │ │ Page        │ │ (MOCK)    │  │
│  └──────┬──────┘ └──────┬──────┘ └─────────────┘ └───────────┘  │
│         │               │                                       │
│         ▼               ▼                                       │
│  ┌─────────────────────────────────────────────┐               │
│  │           API Client (api.ts)               │               │
│  │  - Hardcoded session_id: "agribrain_chat"   │               │
│  │  - No error boundaries                      │               │
│  └──────────────────┬──────────────────────────┘               │
└─────────────────────│───────────────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ /spatial │ │ /sim     │ │ /chat    │ │ /crop    │           │
│  │ lookup   │ │ run      │ │trouble/  │ │ recommend│           │
│  │autocompl │ │          │ │vision    │ │ (ORPHAN) │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                  │
│       ▼            ▼            ▼            ▼                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              CORE SERVICES (Actual Logic)                 │  │
│  │  • simulation.py (42 crops, penalty scoring)             │  │
│  │  • crop_recommendation.py (ML: 22 fruits, BROKEN)        │  │
│  │  • crop_requirements.py (heuristic: 9 crops, WORKS)      │  │
│  │  • spatial.py (Nominatim + deterministic zones)          │  │
│  │  • weather.py (IndianAPI + formula fallback)             │  │
│  │  • market_prices.py (CSV fallback only)                  │  │
│  │  • chat.py (Groq + hardcoded session)                    │  │
│  │  • yield_prediction.py (MISSING DATA/MODEL)              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    ┌─────────┐ ┌──────────┐ ┌──────────┐
    │ SQLite  │ │ Groq API │ │ Nominatim│
    │ (local) │ │ (LLM)    │ │ (Geo)    │
    └─────────┘ └──────────┘ └──────────┘
```
---

## VERIFIED WORKING FEATURES

| Feature | Endpoint | Status | Notes |
|---------|----------|--------|-------|
| Spatial Lookup | `/api/v1/spatial/lookup` | ✅ | Nominatim + deterministic fallback |
| Autocomplete | `/api/v1/spatial/autocomplete` | ✅ | Nominatim |
| Simulation (Backend) | `/api/v1/simulation/run` | ✅ | 42 crops, full digital twin |
| Simulation (Frontend) | Local engine | ✅ | 42 crops, **divergent results** |
| Expert Chat (Text) | `/api/v1/chat/troubleshoot` | ✅ | Groq + context injection |
| Expert Chat (Vision) | `/api/v1/chat/vision` | ✅ | Base64 image + Groq |
| Crop Heuristic | `/api/v1/crop/requirements` | ✅ | 9 crops, rule-based |
| Market Prices | `/api/v1/market/prices` | ⚠️ | CSV fallback only |

---

## CONFIRMED BROKEN/NON-EXISTENT FEATURES

| Feature | Issue | Evidence |
|---------|-------|----------|
| ML Crop Recommendation | Returns identical output for all inputs | `test_crop_rec.py` |
| ML Yield Prediction | Missing CSV, no model files | `test_sim.py` fails |
| SHAP Explainability | No shap library, manual formulas | `grep -r "import shap"` = 0 |
| Frontend Weather | Hardcoded mock data | `WeatherWidget.tsx` lines 15-30 |
| Spatial Datasets | Mathematical formulas only | No GeoJSON/rasters |
| User Authentication | Model exists, no endpoints | `models.py` has User only |
| Rate Limiting | Not implemented | No middleware |
| Crop ML Endpoint | Implemented but **never called by frontend** | `/api/v1/crop/recommend` |

---

## THREE DIVERGENT CROP RECOMMENDATION SYSTEMS

| System | File | Crops | Method | Used? |
|--------|------|-------|--------|-------|
| **ML (XGBoost)** | `crop_recommendation.py` | 22 fruits | Trained model | ❌ No (broken) |
| **Heuristic (DB)** | `crop_requirements.py` | 9 field | Rule-based | ❌ No (API only) |
| **Simulation** | `simulation.py` | 42 mixed | Penalty scoring | ✅ Primary |
| **Frontend Local** | `simulate/page.tsx` | 42 mixed | Penalty scoring | ✅ Manual |

**Critical:** Same input → Different outputs across systems.

---

## FRONTEND/BACKEND DIVERGENCE (SIMULATION ENGINE)

| Metric | Backend | Frontend | Diff |
|--------|---------|----------|------|
| Score Range | 52-98.8 | 54-98.9 | Yes |
| SHAP Base Values | 0.35/0.35/0.25/0.25 | 0.35/0.36/0.28/0.25 | Yes |
| Override Params | 4 (rain, temp, ph, N) | 6 (+P, +K, +humidity) | Yes |
| Timeline % | 35%/25% | 38%/27% | Yes |
| Risk Labels | High/Mod/Low | Acidic/Alkaline/Optimal | Yes |
| Crop DB Source | `simulation.py` | `engine_content.txt` | **Two files** |

---

## DATABASE STATE

| Table | Rows | Used By |
|-------|------|---------|
| User | 0 | Nothing |
| District | 0* | Spatial (empty) |
| SoilType | 0* | Spatial (empty) |
| DistrictSoilType | 0 | Nothing |
| CropProfile | 9 | Heuristic service |
| CropCost | 0 | Nothing |
| RainfallMonthly | 0 | Nothing |
| RainfallDaily | 0 | Nothing |
| MarketPrice | 0 | Service (falls to CSV) |
| SimulationResult | 0 | Never written |

*Import script exists but not run.

---

## SECURITY POSTURE

| Control | Status | Risk |
|---------|--------|------|
| Authentication | ❌ None | HIGH |
| Authorization | ❌ None | HIGH |
| CORS | `["*"]` (open) | HIGH |
| Rate Limiting | ❌ None | MEDIUM |
| Session Management | Hardcoded ID | MEDIUM |
| API Key Rotation | Not enforced | MEDIUM |
| Input Validation | Pydantic only | LOW |
| Audit Logging | ❌ None | LOW |

---

## EXTERNAL DEPENDENCIES

| Service | Purpose | Fallback | Status |
|---------|---------|----------|--------|
| Nominatim | Geocoding | Deterministic zone | ✅ Works |
| IndianAPI | Weather | Formula-based | ✅ Works |
| Groq | LLM (chat/timeline) | Hardcoded template | ✅ Works |
| Agmarknet | Market prices | CSV file | ⚠️ CSV only |
| Upstash Redis | Caching | Not used | ❌ Configured only |

---

## TEST RESULTS SUMMARY

| Test | Pass | Fail | Key Finding |
|------|------|------|-------------|
| `test_crop_recommendation.py` | ✅ | | Trains on synthetic data |
| `test_crop_rec.py` | | ✅ | **ML returns same output** |
| `test_crop_reqs.py` | ✅ | | Heuristic works (9 crops) |
| `test_sim.py` | | ✅ | ML fails, uses heuristic |
| `test_simulation.py` | ✅ | | Unit tests pass |

---

## KNOWN BUGS (Reproducible)

1. **ML Crop Model:** `python test_crop_rec.py` → All crops get same probability
2. **Yield ML:** `python test_sim.py` → "ML prediction failed"
3. **Double Mount:** All endpoints at `/api/v1/*` AND `/api/*`
4. **Session Fixation:** All users share `session_id="agribrain_chat"`
5. **FE/BE Divergence:** Same simulation input → different scores/SHAP
6. **Orphan Endpoint:** `/api/v1/crop/recommend` implemented, never called
7. **Mock Weather:** Frontend WeatherWidget shows static data
8. **Unseeded DB:** 9/10 tables empty

---

## FILES OF INTEREST

### Backend Core
```
backend/api/
├── simulation.py          # 42-crop penalty engine (PRIMARY)
├── crop_recommendation.py # XGBoost 22-fruit (BROKEN)
├── crop_requirements.py   # Heuristic 9-crop (WORKS)
├── spatial.py             # Nominatim + zones
├── weather.py             # IndianAPI + formulas
├── market_prices.py       # CSV fallback
├── chat.py                # Groq + hardcoded session
├── yield_prediction.py    # MISSING DATA
└── config.py              # CORS=["*"], API keys
```

### Frontend Core
```
frontend_web/src/app/
├── simulate/page.tsx      # DUAL ENGINE (360+ lines duplicate)
├── expert-chat/page.tsx   # Chat + vision
├── crops/page.tsx         # Crop catalog
├── components/
│   ├── WeatherWidget.tsx  # HARDCODED MOCK
│   └── MapSelector.tsx    # Nominatim autocomplete
└── lib/api.ts             # Hardcoded session_id
```

---

## RECOMMENDED NEXT STEPS (Priority Order)

### Phase 1: Security & Stability (Week 1-2)
- [ ] Implement JWT authentication
- [ ] Restrict CORS to known origins
- [ ] Add rate limiting middleware
- [ ] Generate unique session IDs per user
- [ ] Remove double router mounting

### Phase 2: Core Functionality (Week 3-4)
- [ ] Fix XGBoost model (retrain with real data)
- [ ] Obtain `crop_production_processed.csv` for yield ML
- [ ] Install SHAP library OR remove SHAP claims
- [ ] Consolidate 3 crop systems → 1 authoritative service
- [ ] Connect frontend WeatherWidget to backend API

### Phase 3: Data Integrity (Week 5)
- [ ] Run `soil_spatial_import.py` to seed District/SoilType
- [ ] Seed MarketPrice, CropCost, Rainfall tables
- [ ] Implement SimulationResult persistence
- [ ] Add database migration strategy

### Phase 4: Architecture Cleanup (Week 6)
- [ ] Remove frontend duplicate simulation engine
- [ ] Single source of truth for crop/soil data (JSON/YAML)
- [ ] Add OpenAPI documentation
- [ ] Implement health check endpoints
- [ ] Add integration tests

---

## VERIFICATION ARTIFACTS (This Audit)

| Document | Purpose |
|----------|---------|
| `ACTUAL_IMPLEMENTATION_AUDIT.md` | 10-section implementation review |
| `WORKFLOW_VERIFICATION.md` | 14 workflows traced end-to-end |
| `ML_AND_DATA_AUTHENTICITY_AUDIT.md` | ML models, SHAP, spatial data analysis |
| `API_AND_INTEGRATION_VERIFICATION.md` | API contracts, security, integration issues |
| `FRONTEND_BACKEND_FALLBACK_AUDIT.md` | Dual engine divergence analysis |
| `MISSING_FEATURES_AND_DISCREPANCIES.md` | Gap catalog vs documentation |
| `FINAL_VERIFIED_PROJECT_CONTEXT.md` | **This document** - handoff summary |

---

## CONTACT / ESCALATION

For questions on this audit, reference the specific document and section. All findings are reproducible using the test commands and file paths documented above.

**Audit Complete:** 2026-11-16  
**Next Review Recommended:** After Phase 1 fixes implemented