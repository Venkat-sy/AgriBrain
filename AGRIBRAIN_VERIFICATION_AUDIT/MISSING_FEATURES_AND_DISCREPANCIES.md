# MISSING FEATURES AND DISCREPANCIES
## Gap Catalog: Documentation Claims vs. Implementation Reality

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  

---

## 1. CROP COUNT DISCREPANCIES

| Context | Claimed | Actual | Gap |
|---------|---------|--------|-----|
| Documentation | "45 crops" | - | **Baseline claim** |
| Simulation Engine | - | 42 crops | -3 |
| ML Model (XGBoost) | - | 22 crops | -23 |
| Database (CropProfile) | - | 9 crops | -36 |
| Heuristic Service | - | 9 crops | -36 |

**Impact:** Users expecting 45 crops get different subsets depending on which system they use.

---

## 2. SHAP EXPLAINABILITY - FALSE CLAIM

| Documentation Claim | Implementation Reality |
|---------------------|------------------------|
| "SHAP-based feature attribution" | **No SHAP library installed** |
| "Per-prediction SHAP values" | Manual heuristic formulas |
| "SHAP waterfall plots" | Text-based breakdown only |
| "Model-agnostic explanations" | Only for penalty-based scoring |

**Evidence:**
```bash
grep -r "import shap" backend/ --include="*.py"
# ZERO RESULTS

pip list | grep shap
# NOT INSTALLED
```

**Verdict:** SHAP is a **marketing term**, not an implementation.

---

## 3. YIELD PREDICTION ML - NON-FUNCTIONAL

| Component | Status | Details |
|-----------|--------|---------|
| Model file | ❌ Missing | `yield_model.joblib` not found |
| Scaler file | ❌ Missing | `yield_scaler.joblib` not found |
| Training data | ❌ Missing | `crop_production_processed.csv` not found |
| Training script | ✅ Exists | `yield_prediction.py` has training code |
| Inference endpoint | ❌ Not exposed | No API endpoint for yield ML |
| Test result | ❌ Failed | `test_sim.py`: "ML prediction failed" |

**Fallback:** System uses heuristic yield formula: `base_yield * (score/100)`

---

## 4. WEATHER WIDGET - MOCK ONLY

| Documentation Claim | Implementation Reality |
|---------------------|------------------------|
| "Live weather data" | **Hardcoded mock data** |
| "Current conditions" | Static temperature/humidity |
| "Forecast display" | Not implemented |
| "API integration" | No frontend weather API call |

**Code Evidence (WeatherWidget.tsx):**
```typescript
// Lines 15-30: MOCK DATA
const mockWeather = {
  temperature: 28,
  humidity: 65,
  rainfall: 120,
  condition: "Partly Cloudy"
}
// No fetch(), no API call, no useEffect for data loading
```

**Backend has live weather** (IndianAPI) but **frontend doesn't use it**.

---

## 5. SPATIAL DATA - FORMULAIC, NOT DATASET-DRIVEN

| Claimed Data Source | Actual Implementation |
|---------------------|----------------------|
| "High-resolution soil maps" | 8 hardcoded soil profiles |
| "Weather station data" | Lat/lon mathematical formulas |
| "Agro-ecological zones" | Latitude-based if/else rules |
| "District-level soil %" | Deterministic zone→soil mapping |

**No GeoJSON, no raster data, no shapefiles, no actual spatial datasets used.**

---

## 6. THREE DIVERGENT CROP RECOMMENDATION SYSTEMS

| System | Crops | Method | Status | Used in UI? |
|--------|-------|--------|--------|-------------|
| ML (XGBoost) | 22 fruits | Trained model | ❌ Broken (same output) | ❌ No |
| Heuristic (DB) | 9 field crops | Rule-based | ✅ Working | ❌ No |
| Simulation | 42 mixed | Penalty-based | ✅ Working | ✅ Yes (both FE/BE) |
| Frontend Local | 42 mixed | Penalty-based | ✅ Working | ✅ Manual button |

**User Impact:** Same farm gets different crop recommendations depending on which path taken.

---

## 7. FRONTEND/BACKEND LOGIC DIVERGENCE

| Component | Backend | Frontend | Divergence |
|-----------|---------|----------|------------|
| Score bounds | 52-98.8 | 54-98.9 | Different |
| SHAP coefficients | 4 features | 4 features | Different base values |
| Override params | 4 | 6 | Frontend has more |
| Timeline stages | 35%/25% | 38%/27% | Different % |
| Risk labels | "High/Moderate/Low" | "Acidic/Alkaline/Optimal" | Different schema |
| Crop database | simulation.py | engine_content.txt | Two sources |

---

## 8. DATABASE TABLES - UNSEDED/UNUSED

| Table | Defined | Seeded | Used | Status |
|-------|---------|--------|------|--------|
| User | ✅ | ❌ | ❌ | **Orphaned** |
| District | ✅ | ❌* | ✅ (spatial) | **Empty** |
| SoilType | ✅ | ❌* | ✅ (spatial) | **Empty** |
| DistrictSoilType | ✅ | ❌* | ❌ | **Empty** |
| CropProfile | ✅ | ✅ (9) | ✅ (heuristic) | **Partial** |
| CropCost | ✅ | ❌ | ❌ | **Empty** |
| RainfallMonthly | ✅ | ❌ | ❌ | **Empty** |
| RainfallDaily | ✅ | ❌ | ❌ | **Empty** |
| MarketPrice | ✅ | ❌ | ✅ (service) | **Empty** |
| SimulationResult | ✅ | ❌ | ❌ | **Never persisted** |

*Import script exists (`soil_spatial_import.py`) but no evidence of execution.

---

## 9. MISSING PRODUCTION FEATURES

| Feature | Documentation | Implementation | Gap |
|---------|---------------|----------------|-----|
| Authentication | "User management" | User model only | **No auth endpoints, no JWT, no sessions** |
| Rate Limiting | "API protection" | None | **Open to abuse** |
| Caching | "Redis for performance" | Config only | **Upstash configured but unused** |
| Audit Logging | "Traceability" | None | **No request/response logging** |
| Data Validation | "Input sanitization" | Pydantic only | **No business rule validation** |
| API Versioning | "Stable contracts" | Double-mounted | **No versioning strategy** |
| Monitoring | "Observability" | None | **No metrics, no health checks** |
| Backup/Restore | "Data safety" | None | **No backup strategy** |

---

## 10. SECURITY VULNERABILITIES

| Vulnerability | Location | Severity | Exploitability |
|---------------|----------|----------|----------------|
| CORS: `["*"]` | `config.py:23` | HIGH | Any origin can call API |
| No Auth | All endpoints | HIGH | Anonymous access to all data |
| Hardcoded session_id | `chat.py:24`, `api.ts:95` | MEDIUM | Session fixation |
| No Rate Limit | All endpoints | MEDIUM | DoS, API abuse |
| API Keys in .env | `config.py` | MEDIUM | Rotation not enforced |
| SQL Injection Risk | Raw SQL in imports | LOW | Parameterized mostly |

---

## 11. TEST COVERAGE GAPS

| Test File | Coverage | Issues |
|-----------|----------|--------|
| `test_crop_recommendation.py` | Unit (ML training) | Uses synthetic data, passes but model broken |
| `test_crop_rec.py` | Integration (ML inference) | **Reveals model returns same output** |
| `test_crop_reqs.py` | Integration (heuristic) | Passes, but only 9 crops |
| `test_sim.py` | Integration (simulation) | ML fails, falls back to heuristic |
| `test_simulation.py` | Unit (simulation engine) | Tests internal functions |

**Missing:** E2E tests, API contract tests, load tests, security tests, frontend tests.

---

## 12. DOCUMENTATION VS REALITY MATRIX

| Feature Area | Docs Claim | Reality | Severity |
|--------------|------------|---------|----------|
| Crop Recommendations | 45 crops, ML-powered | 3 systems, 1 broken, 2 heuristic | HIGH |
| SHAP Explainability | Full SHAP integration | Manual formulas, no SHAP lib | HIGH |
| Yield Prediction | ML model | Missing data, no model | HIGH |
| Weather Data | Live + forecast | Backend only, frontend mock | MEDIUM |
| Spatial Data | High-res datasets | Mathematical formulas | MEDIUM |
| Market Prices | Live API | CSV fallback only | MEDIUM |
| Offline Support | Local engine fallback | Manual button, divergent logic | MEDIUM |
| Multi-user | Session support | Hardcoded single session | HIGH |
| Production Ready | "Deployable" | No auth, no rate limit, open CORS | CRITICAL |

---

## 13. PRIORITIZED FIX LIST

### CRITICAL (Security/Production Blockers)
1. Implement authentication (JWT/OAuth)
2. Fix CORS: restrict to known origins
3. Add rate limiting (per IP, per endpoint)
4. Remove hardcoded session_id
5. Add API key rotation strategy

### HIGH (Core Functionality)
6. Fix XGBoost crop model (retrain with proper data)
7. Implement yield prediction ML (get processed CSV)
8. Replace fake SHAP with real SHAP or remove claim
9. Consolidate 3 crop systems → 1 authoritative system
10. Fix frontend/backend divergence (single source of truth)

### MEDIUM (Data/Features)
11. Seed database tables (run import scripts)
12. Connect frontend WeatherWidget to backend weather API
13. Implement real spatial datasets or remove claim
14. Add market price API integration
15. Implement automatic backend→frontend fallback

### LOW (Quality/Observability)
16. Add comprehensive test suite
17. Add monitoring/health endpoints
18. Add audit logging
19. Document API contracts (OpenAPI)
20. Add backup/restore procedures

---

## CONCLUSION

The AgriBrain project has **significant gaps between documentation and implementation**:

- **3 HIGH-severity** functional gaps (SHAP, Yield ML, Crop systems)
- **1 CRITICAL** security gap (no auth, open CORS)
- **Multiple MEDIUM** data integrity gaps (spatial, weather, market)
- **Architectural debt**: Duplicate engines, divergent logic, unseeded DB

**Not production-ready.** Suitable as prototype/demo with clear disclaimers.