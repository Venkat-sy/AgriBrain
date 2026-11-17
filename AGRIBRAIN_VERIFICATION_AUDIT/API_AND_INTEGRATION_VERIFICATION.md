# API AND INTEGRATION VERIFICATION
## API Contracts, External Integrations, and Data Flow Analysis

**Audit Date:** 2026-11-16  
**Auditor:** Independent AI Coding Agent  

---

## 1. BACKEND API ENDPOINTS

### 1.1 Router Mounting (main.py lines 50-57)
```python
# DOUBLE MOUNTED - same routers at TWO paths:
app.include_router(spatial.router, prefix="/api/v1")  # /api/v1/spatial/*
app.include_router(simulation.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(crop.router, prefix="/api/v1")

app.include_router(spatial.router, prefix="/api")     # /api/spatial/*
app.include_router(simulation.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(crop.router, prefix="/api")
```
**Issue:** Duplicate routes, potential conflicts, no versioning strategy

### 1.2 Endpoint Inventory

| Endpoint | Method | Router | Request Model | Response Model |
|----------|--------|--------|---------------|----------------|
| `/api/v1/spatial/lookup` | POST | spatial | `SpatialLookupRequest` | `SpatialLookupResponse` |
| `/api/v1/spatial/autocomplete` | GET | spatial | query params | `AutocompleteResponse` |
| `/api/v1/simulation/run` | POST | simulation | `SimulationRequest` | `SimulationResponse` |
| `/api/v1/chat/troubleshoot` | POST | chat | `ChatRequest` | `ChatResponse` |
| `/api/v1/chat/vision` | POST | chat | FormData (image + prompt) | `ChatResponse` |
| `/api/v1/crop/recommend` | POST | crop | `CropRecommendationRequest` | `CropRecommendationResponse` |

---

## 2. REQUEST/RESPONSE MODELS (Pydantic)

### 2.1 Spatial Lookup
```python
# Request
class SpatialLookupRequest(BaseModel):
    latitude: float
    longitude: float

# Response
class SpatialLookupResponse(BaseModel):
    district: str
    state: str
    agro_zone: str
    soil: SoilProfile
    weather: WeatherData
```

### 2.2 Simulation Request/Response
```python
class SimulationRequest(BaseModel):
    district_id: int
    selected_crop: str
    land_area_ha: float
    budget_inr: Optional[float] = None
    confirmed_soil_type: Optional[str] = None
    planting_month: Optional[int] = None
    overrides: Optional[Dict] = None  # rainfall, temp, ph, N

class SimulationResponse(BaseModel):
    ranked_crops: List[RankedCrop]
    recommended_crop: str
    digital_twin: DigitalTwin
    shap_explanation: SHAPExplanation
    timeline: List[TimelineStage]
    simulation_parameters: Dict
    generated_at: str
```

### 2.3 Chat Request/Response
```python
class ChatRequest(BaseModel):
    message: str
    session_id: str = "agribrain_chat"  # HARDCODED DEFAULT
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model: str
    usage: Dict
```

### 2.4 Crop Recommendation Request/Response
```python
class CropRecommendationRequest(BaseModel):
    N: int
    P: int
    K: int
    temperature: float
    humidity: float
    ph: float
    rainfall: float

class CropRecommendationResponse(BaseModel):
    crop_name: str
    confidence: float
    probabilities: Dict[str, float]
    match_reasons: List[str]
```

---

## 3. FRONTEND API CLIENT (frontend_web/src/lib/api.ts)

### 3.1 API Base Configuration
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiClient {
  async request(endpoint, options) {
    const url = `${API_BASE}${endpoint}`
    const res = await fetch(url, { ... })
    return res.json()
  }
}
```

### 3.2 Method Mapping
```typescript
export const api = {
  // Spatial
  getLocation: (lat, lng) => apiClient.post("/api/v1/spatial/lookup", { latitude: lat, longitude: lng }),
  searchDistricts: (query) => apiClient.get(`/api/v1/spatial/autocomplete?q=${query}`),
  
  // Simulation
  run: (params) => apiClient.post("/api/v1/simulation/run", params),
  
  // Chat
  troubleshoot: (message, context) => apiClient.post("/api/v1/chat/troubleshoot", { 
    message, 
    session_id: "agribrain_chat",  // HARDCODED
    context 
  }),
  vision: (imageBase64, prompt) => {
    const form = new FormData()
    form.append("image", imageBase64)
    form.append("prompt", prompt)
    return apiClient.post("/api/v1/chat/vision", form)
  },
  
  // Crop
  recommend: (data) => apiClient.post("/api/v1/crop/recommend", data),
}
```

---

## 4. EXTERNAL API INTEGRATIONS

### 4.1 Nominatim (OpenStreetMap) - Reverse Geocoding
| Aspect | Details |
|--------|---------|
| **Endpoint** | `https://nominatim.openstreetmap.org/reverse` |
| **Usage** | Both frontend (direct) and backend (spatial.py) |
| **Rate Limit** | 1 req/sec (policy) - **No client-side throttling** |
| **Headers** | User-Agent: "AgriBrain-DigitalTwin/3.0" (backend only) |
| **Timeout** | 5 seconds (backend), no timeout (frontend) |
| **Error Handling** | Backend: graceful fallback to deterministic zones |

### 4.2 IndianAPI - Live Weather
| Aspect | Details |
|--------|---------|
| **Endpoint** | `https://weather.indianapi.in/india/weather?city={district}` |
| **Auth** | Header: `x-api-key` + `Authorization` |
| **Usage** | Backend only (simulation.py lines 75-82) |
| **Trigger** | Only if `WEATHER_API_KEY` set AND district != "Regional District" |
| **Timeout** | 3 seconds |
| **Fallback** | Formula-based weather (lat/lon math) |

### 4.3 DataGov - Market Prices
| Aspect | Details |
|--------|---------|
| **Endpoint** | DataGov API (not directly called - CSV file used) |
| **File** | `backend/datasets/market_prices.csv` |
| **Service** | `services/market_pricing.py` - `fetch_live_market_price()` |
| **Fallback** | Baseline MSP prices from CROP_DATABASE |

### 4.4 Groq - LLM Inference
| Aspect | Details |
|--------|---------|
| **Endpoint** | Groq Cloud API |
| **Models Used** | 
| Text Chat | `llama-3.3-70b-versatile` |
| Vision | `llama-3.2-11b-vision-preview` |
| Timeline | `llama-3.3-70b-versatile` |
| **Config** | 
| Text | temp=0.5, max_tokens=900 |
| Vision | temp=0.4, max_tokens=900 |
| Timeline | temp=0.3, max_tokens=600 |
| **Integration Points** | chat.py (text + vision), simulation.py (timeline) |
| **Fallback** | Hardcoded templates if API key missing or error |

---

## 5. DATA FLOW ANALYSIS

### 5.1 Simulation Request Flow
```
FRONTEND (simulate/page.tsx)
    │
    ├─ User selects: location, soil, crop, area, overrides
    │
    ▼
api.ts → POST /api/v1/simulation/run
    │
    ▼
BACKEND (simulation.py:run_simulation)
    │
    ├─ 1. spatial.lookup_spatial(lat, lng) → district, zone, soil, weather
    │       └─ Nominatim API call
    │
    ├─ 2. Live weather enhancement (if API key)
    │       └─ IndianAPI call
    │
    ├─ 3. Apply overrides from request
    │
    ├─ 4. Score 42 crops (penalty-based)
    │
    ├─ 5. Digital twin calculations (yield, water, risk)
    │
    ├─ 6. Manual SHAP breakdown
    │
    ├─ 7. Timeline (hardcoded or Groq)
    │
    ▼
Returns SimulationResponse
    │
    ▼
FRONTEND → Updates state, displays results
```

### 5.2 Chat Flow
```
FRONTEND (ChatAssistant.tsx)
    │
    ├─ Builds context: farm + simulation + calendar
    │
    ▼
api.ts → POST /api/v1/chat/troubleshoot {message, session_id, context}
    │
    ▼
BACKEND (chat.py:troubleshoot)
    │
    ├─ Constructs system prompt
    ├─ Injects context into user message
    ├─ Calls Groq API
    │
    ▼
Returns ChatResponse
    │
    ▼
FRONTEND → Streams response to UI
```

### 5.3 Vision Flow
```
FRONTEND (ChatAssistant.tsx)
    │
    ├─ FileReader → base64 string
    │
    ▼
api.ts → POST /api/v1/chat/vision (FormData: image, prompt)
    │
    ▼
BACKEND (chat.py:vision)
    │
    ├─ Validates base64 image
    ├─ Constructs pathologist prompt
    ├─ Calls Groq Vision API
    │
    ▼
Returns ChatResponse
```

---

## 6. INTEGRATION ISSUES IDENTIFIED

### 6.1 Double Router Mounting
- **Issue:** All routers mounted at both `/api/v1` and `/api`
- **Impact:** Duplicate endpoints, potential routing conflicts
- **Fix:** Choose one prefix strategy

### 6.2 Hardcoded Session ID
- **Location:** `chat.py` line 24, `api.ts` line 95
- **Value:** `"agribrain_chat"`
- **Impact:** All users share same session, no conversation isolation
- **Fix:** Generate unique session IDs per user

### 6.3 Duplicate Nominatim Calls
- **Frontend:** Direct call in `simulate/page.tsx` lines 161-174
- **Backend:** Call in `spatial.py` `lookup_spatial()`
- **Impact:** 2x API calls, rate limit risk, inconsistent results possible
- **Fix:** Use single source (prefer backend)

### 6.4 Frontend/Backend Parameter Mismatch
| Parameter | Frontend | Backend | Issue |
|-----------|----------|---------|-------|
| Area | acres | hectares | Conversion in api.ts (/2.471) |
| Soil | selectedSoilType (key) | confirmed_soil_type (key) | Matching but undocumented |
| Overrides | 6 fields (temp, humidity, rain, ph, N, P, K) | 4 fields (rainfall, temp, ph, N) | P, K, humidity ignored by backend |

### 6.5 Crop Recommendation API Disconnect
- **Frontend** doesn't call `/api/v1/crop/recommend` at all
- **Simulate page** uses local engine OR backend simulation
- **Expert chat** context doesn't include ML crop recommendations
- **Result:** ML endpoint exists but is **unused in frontend**

### 6.6 Missing Error Boundaries
- No global error handling in frontend API client
- Backend returns 500 on external API failures (Nominatim, Groq)
- No retry logic for transient failures
- No user-facing error messages for API failures

---

## 7. API SECURITY GAPS

| Issue | Location | Severity |
|-------|----------|----------|
| CORS: `ALLOWED_ORIGINS = ["*"]` | `config.py` line 23 | HIGH |
| No authentication | All endpoints | HIGH |
| No rate limiting | All endpoints | MEDIUM |
| API keys in .env | `config.py` | MEDIUM |
| Hardcoded session_id | `chat.py`, `api.ts` | MEDIUM |
| No request validation beyond Pydantic | All endpoints | LOW |
| No API versioning strategy | Double-mounted routers | LOW |

---

## 8. CONTRACT COMPLIANCE CHECK

| Endpoint | Frontend Call Matches? | Backend Implements? | Notes |
|----------|----------------------|---------------------|-------|
| `/spatial/lookup` | ✅ | ✅ | Duplicate frontend call |
| `/spatial/autocomplete` | ✅ | ✅ | Used in MapSelector |
| `/simulation/run` | ✅ | ✅ | Main simulation path |
| `/chat/troubleshoot` | ✅ | ✅ | Context injection works |
| `/chat/vision` | ✅ | ✅ | Base64 upload works |
| `/crop/recommend` | ❌ **NOT CALLED** | ✅ | ML endpoint orphaned |

---

## CONCLUSION

The API layer is **functional but has significant integration debt**:

1. **Double-mounted routers** create maintenance burden
2. **Frontend bypasses ML crop recommendation** entirely
3. **Hardcoded session_id** breaks multi-user support
4. **Duplicate external API calls** (Nominatim) waste quota
5. **Parameter mismatches** between FE/BE (area units, override fields)
6. **No authentication/rate limiting** - not production-ready
7. **Orphaned ML endpoint** - trained model not integrated into UI

The system works as a demo but requires API governance for production.