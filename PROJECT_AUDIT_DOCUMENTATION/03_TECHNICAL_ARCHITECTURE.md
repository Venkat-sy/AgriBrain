# Technical Architecture - AgriBrain

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend (Vercel)"
        A[Next.js App Router] --> B[FarmContext Provider]
        B --> C[MapUI - Leaflet Map]
        B --> D[ChatAssistant - AI Chat]
        B --> E[Simulation Workflow]
        B --> F[Calendar View]
        B --> G[Expert Chat Page]
        C --> H[/api/simulation/location]
        D --> I[/api/chat]
        E --> J[/api/simulate]
        E --> K[/api/recommend]
        F --> B
        G --> I
    end

    subgraph "Backend (Render)"
        L[FastAPI App] --> M[/spatial router]
        L --> N[/simulation router]
        L --> O[/chat router]
        L --> P[/crop router]
        M --> Q[Spatial Lookup Service]
        N --> R[SimulationEngine]
        O --> S[Groq LLM Client]
        P --> T[ML Inference Module]
        R --> U[Database - PostgreSQL]
        R --> V[Crop Profiles]
        R --> W[Market Prices]
        T --> X[XGBoost Model]
        T --> Y[Yield Model]
    end

    H -.->|HTTPS| M
    I -.->|HTTPS| O
    J -.->|HTTPS| N
    K -.->|HTTPS| P
## Data Flow Architecture

### 1. Farm Input Flow (Map → Parameters)
```
User clicks map → MapUI.onClick → /api/simulation/location → spatial.reverse_geocode 
→ Nominatim + Zone Mapping → District, Soil, AgroZone → FarmContext.soilParams
```

### 2. Crop Recommendation Flow
```
User selects crop → /api/recommend → crop_recommendation.recommend 
→ XGBoost.predict_proba → Top-5 crops with confidence → FarmContext.selectedCrop
```

### 3. Simulation Flow
```
User submits farm params → /api/simulate → simulation.run 
→ SimulationEngine.run_simulation → 
  1. Weather/soil lookup
  2. Crop suitability scoring (22 crops)
  3. Agronomic calculations (NPK, water)
  4. Economic modeling (costs, revenue, ROI)
  5. Risk assessment
  6. Timeline generation (Groq LLM)
→ SimulationResponse → FarmContext.simulationResults + calendarStages
```

### 4. Calendar Generation Flow
```
simulationResults.monthly_breakdown → CalendarPage.useEffect 
→ Maps months to growth stages → Generates tasks per stage
→ CalendarStage[] → FarmContext.calendarStages
```

### 5. Expert Chat Flow
```
User message + context → /api/chat → chat.troubleshoot 
→ Build system prompt with farm context 
→ Groq Llama-3.3-70b → Response → ChatAssistant UI
```

### 6. Vision Chat Flow
```
User uploads image → base64 encode → /api/chat (FormData) 
→ chat.troubleshoot_vision → Groq Llama-3.2-11b-vision 
→ Response → ChatAssistant UI
```
    L -.->|SQL| U
## Component Architecture

### Frontend State Management (FarmContext)
```typescript
interface FarmContextType {
  // Location & Soil
  coordinates: [number, number] | null;
  soilParams: SoilParams | null;
  selectedDistrict: District | null;
  
  // Farm Configuration
  farmParams: FarmParams | null;  // area, budget, season, soil_type, dates
  
  // Crop & Simulation
  selectedCrop: string | null;
  simulationResults: SimulationResults | null;
  
  // Calendar & Progress
  calendarStages: CalendarStage[] | null;
  currentStep: number;  // 1-5
  
  // Chat
  chatHistory: ChatMessage[];
  
  // Actions
  setCoordinates, setSoilParams, setFarmParams, 
  setSelectedCrop, setSimulationResults, setCalendarStages,
  setCurrentStep, addChatMessage, resetFarm
}
```

### Backend Service Layer

#### SimulationEngine (Core Business Logic)
```python
class SimulationEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def run_simulation(self, request, district, crop) -> SimulationResponse:
        # 1. Get weather & soil
        weather = self._get_weather(district)
        soil = self._get_soil(district, request.confirmed_soil_type)
        
        # 2. Score all 22 crops
        scored_crops = self._score_crops(weather, soil, request)
        
        # 3. Calculate agronomics for selected crop
        agronomics = self._calculate_agronomics(crop, weather, soil, request)
        
        # 4. Economic modeling
        economics = self._calculate_economics(crop, request, agronomics)
        
        # 5. Risk assessment
        risks = self._assess_risks(weather, soil, crop)
        
        # 6. Generate timeline (with Groq)
        timeline = self._generate_timeline(crop, request, agronomics, risks)
        
        return SimulationResponse(...)
```

#### ML Inference Module (XGBoost)
```python
# Primary: XGBoost for crop recommendation (22 classes)
def recommend(input_features: Dict, top_k=5) -> List[Dict]:
    # Load model bundle (lazy)
    bundle = _get_xgboost_bundle()
    # Prepare features in correct order
    X = pd.DataFrame([input_features])[FEATURE_COLUMNS]
## Database Schema (ER Diagram)

```mermaid
erDiagram
    DISTRICT ||--o{ DISTRICT_SOIL_TYPE : has
    DISTRICT ||--o{ RAINFALL_MONTHLY : has
    DISTRICT ||--o{ RAINFALL_FORECAST : has
    DISTRICT ||--o{ CROP_COST : has
    SOIL_TYPE ||--o{ DISTRICT_SOIL_TYPE : in
    CROP_PROFILE ||--o{ CROP_COST : has
    CROP_PROFILE ||--o{ CROP_PRICE : has
    CROP_PROFILE ||--o{ SIMULATION_RESULT : used_in
    DISTRICT ||--o{ SIMULATION_RESULT : located_in
    USER ||--o{ SIMULATION_RESULT : owns
    USER ||--o{ SOIL_IMAGE_RESULT : uploads

    DISTRICT {
        int id PK
        string name
        string state
        float latitude
        float longitude
        string soil_type
        string agro_climatic_zone
        text geometry
    }
    
    CROP_PROFILE {
        int id PK
        string name
        string season
        float ph_min, ph_max
        float rainfall_min_mm, rainfall_max_mm
        float temp_min_c, temp_max_c
        float n_requirement, p_requirement, k_requirement
        int duration_days
        float expected_yield_tons_per_ha
        float water_requirement_mm
    }
    
    SIMULATION_RESULT {
        int id PK
        string user_id
        int district_id FK
        string selected_crop
        float land_area_ha
        float budget_inr
        string confirmed_soil_type
        float total_cost_inr
        float estimated_yield_tons
        float market_value_inr
        float net_profit_inr
        float roi_percentage
        string risk_level
        text farming_roadmap
        datetime created_at
    }
```

## API Contracts

### Simulation Request
```json
POST /api/v1/simulation/run
{
  "district_id": 1,
  "selected_crop": "Rice",
  "land_area_ha": 2.0,
  "budget_inr": 100000,
  "confirmed_soil_type": "Alluvial Soil",
  "rainfall_override_mm": 800,
  "planting_season": "Kharif",
  "planned_start_date": "2024-06-15"
}
```

### Simulation Response (Key Fields)
```json
{
  "selected_crop": "Rice",
  "land_area_ha": 2.0,
  "total_cost_inr": 85000,
  "estimated_yield_tons": 8.4,
  "estimated_yield_tons_per_ha": 4.2,
  "market_value_inr": 193200,
  "net_profit_inr": 108200,
  "roi_percentage": 127.3,
  "risk_level": "medium",
  "risk_factors": ["Moderate drought risk", "Pest pressure during flowering"],
  "digital_twin": {
    "yield_per_acre_tonnes": 1.7,
    "total_yield_tonnes": 8.4,
    "estimated_revenue_inr": 193200,
    "net_irrigation_mm": 250.5,
    "daily_water_liters": 150000,
    "risks": {"drought": "medium", "pest_disease": "high", "soil_reaction": "low"}
  },
  "shap_data": {"crop": "Rice", "score_pct": 87.3, "explanation": "..."},
  "timeline": [{"stage_name": "Land Preparation", "days": 15, "agronomy_advice": "..."}]
}
```

## Security Architecture

| Layer | Implementation |
|-------|---------------|
| **Transport** | HTTPS enforced (Vercel + Render) |
| **CORS** | `ALLOWED_ORIGINS: ["*"]` (dev) - needs restriction for prod |
| **Authentication** | None (session_id only) - **CRITICAL GAP** |
| **Input Validation** | Pydantic models on all endpoints |
| **Rate Limiting** | None implemented |
| **Secrets** | Environment variables (GROQ_API_KEY, DATABASE_URL) |
| **SQL Injection** | SQLAlchemy ORM (parameterized queries) |
| **XSS** | React auto-escaping, react-markdown sanitization |

## Deployment Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Developer     │────▶│   GitHub Main   │────▶│   Vercel (FE)   │
│   (Local)       │     │   (CI/CD)       │     │   Next.js 16    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌─────────────────┐        │
                              │   Render (BE)   │◀───────┘
                              │   FastAPI       │
                              │   PostgreSQL    │
                              └─────────────────┘
```

### Vercel Config (`vercel.json`)
```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

### Render Config (`render.yaml`)
```yaml
services:
  - type: web
    name: agribrain-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        fromDatabase: agribrain-db
      - key: GROQ_API_KEY
        sync: false
```

## Scalability Considerations

| Component | Current | Bottleneck | Scale Path |
|-----------|---------|------------|------------|
| **Frontend** | Static + SSR | None | CDN edge caching |
| **API Gateway** | FastAPI single process | CPU-bound ML inference | Horizontal scaling + model server |
| **ML Inference** | In-process joblib load | Model loading latency | TorchServe/Triton / ONNX Runtime |
| **Database** | SQLite (dev) / PG (prod) | Connection pooling | PgBouncer, read replicas |
| **LLM Calls** | Direct Groq API | Rate limits, latency | Caching, batching, fallback models |
| **GeoJSON** | Served from API | Large payload (2MB+) | CDN, vector tiles, simplification |

## Monitoring & Observability (Current State)

| Aspect | Status | Tool |
|--------|--------|------|
| **Frontend Errors** | ❌ None | - |
| **Backend Logs** | ✅ Console | Render logs |
| **API Metrics** | ❌ None | - |
| **Database Metrics** | ❌ None | - |
| **LLM Usage** | ❌ None | Groq dashboard |
| **Uptime** | ❌ None | - |
| **User Analytics** | ❌ None | - |

---

## Integration Points

### External Services
| Service | Purpose | Integration Method | Status |
|---------|---------|-------------------|--------|
| **Groq API** | LLM inference (chat + vision) | REST API (Python client) | ✅ Active |
| **Nominatim** | Reverse geocoding | HTTP requests | ✅ Active (with fallback) |
| **OpenWeather** | Weather data | Not integrated | ❌ Planned |
| **IMD API** | Indian meteorological data | Not integrated | ❌ Planned |
| **Upstash Redis** | Caching/sessions | Not integrated | ❌ Configured only |

### Internal Data Dependencies
| Data Source | Used By | Update Frequency |
|-------------|---------|------------------|
| `india_districts.geojson` | MapUI, spatial API | Static (manual update) |
| `crop_agronomy_base.json` | Simulation engine | Static |
| `master_agri_dataset_v2.csv` | ML training | One-time |
| `xgboost_crop_model.joblib` | Crop recommendation | Model retraining |
| District rainfall data | Simulation engine | Seasonal (needs seeding) |
| Market prices | Economic modeling | Daily (needs integration) |

### Chat Request
```json
POST /api/v1/chat/troubleshoot
{
  "session_id": "uuid",
  "user_question": "When should I apply nitrogen?",
  "context": {
    "selected_crop": "Rice",
    "farm_params": {...},
    "simulation_results": {...},
    "calendar_stages": [...],
    "coordinates": [28.6, 77.2],
    "soil_params": {...},
    "annual_rainfall": 800
  }
}
```