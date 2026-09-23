# Phase 2 — System Architecture & Requirements

## 1. Goal
Create a **concrete, production‑ready architecture** that implements the AgriSim pipeline:

```
MAP → RAINFALL → RAINFALL FORECAST → SOIL → CROP RECOMMENDATION → BUDGET → SIMULATION → ROADMAP
```

The architecture must be fully described, version‑controlled and ready for implementation in Phase 3.

---

## 2. High‑level Component Diagram

```
┌─────────────────────┐      ┌─────────────────────┐
│  Frontend (React)   │◀────▶│  FastAPI Backend    │
│  - Leaflet map      │      │  - AsyncSQLAlchemy   │
│  - React‑Query      │      │  - Pydantic models   │
│  - UI components    │      │  - OpenAPI spec      │
└─────────────────────┘      └─────────────────────┘
          ▲                         ▲
          │                         │
          │      ┌──────────────────▼───────────────────┐
          │      │          PostgreSQL + PostGIS          │
          │      │  • Spatial tables (districts, soil)    │
          │      │  • Time‑series tables (rainfall)       │
          │      │  • Agricultural tables (crops, economics)│
          │      └───────────────────────────────────────┘
          │                         ▲
          │                         │
          │      ┌──────────────────▼───────────────────┐
          │      │          ML Services (Docker)         │
          │      │  • Rainfall Forecast (Prophet/LSTM)   │
          │      │  • Crop Recommendation (XGBoost/LightGBM)│
          │      │  • Yield & Risk Models (XGB/NN)        │
          │      │  • SHAP Explainability (shared lib)    │
          │      └──────────────────────────────────────┘
```

---

## 3. Backend – FastAPI Skeleton
* **Project layout** (`agrisim_backend/`)
  * `app/__init__.py`
  * `app/main.py` – creates the FastAPI app, includes routers, adds CORS middleware.
  * `app/api/`
    * `router_map.py` – endpoints for map interaction (`/map/point`).
    * `router_rainfall.py` – historic data retrieval, forecast request.
    * `router_soil.py` – spatial soil lookup.
    * `router_crop.py` – recommendation service.
    * `router_budget.py` – simple budget estimator.
    * `router_simulation.py` – simulation orchestration.
    * `router_roadmap.py` – roadmap generation.
  * `app/models/` – Pydantic schemas for request/response objects.
  * `app/dependencies.py` – DB session creation (SQLAlchemy async).
* **Database layer** using **SQLAlchemy 2.0 async** with **PostGIS** extensions.
* **OpenAPI specification** automatically generated from the FastAPI app; a static `openapi.yaml` will be exported for external clients.
* **Security** – prototype uses a simple API‑Key header; structure prepared for JWT auth in later phases.

---

## 4. Frontend – React + Leaflet
* Directory `agrisim_frontend/` (already present as `frontend/react-app`).
* New components to be added:
  * `MapSelector.jsx` – Leaflet map, click to obtain lat/long, reverse‑geocode to district.
  * `RainfallChart.jsx` – historical + forecast visualisation (Chart.js).
  * `SoilInfo.jsx` – display soil properties for selected district.
  * `CropRec.jsx` – UI for crop recommendation with SHAP explanation modal.
  * `SimulationForm.jsx` – input budget, land size, irrigation options.
  * `RoadmapTimeline.jsx` – interactive Gantt‑style timeline.
* State management via **React Query** to cache API responses.
* Styling follows existing design tokens; responsive for mobile.

---

## 5. Data Flow
1. **User clicks on map** → front‑end sends `(lat, lng)` to `GET /map/point`.
2. Backend uses **PostGIS** `ST_Contains` to map point → district ID.
3. District ID is used to fetch:
   * Historical rainfall time‑series.
   * Soil type and attributes.
4. Front‑end displays rainfall chart and soil card.
5. User requests **forecast** → backend runs **Prophet/LSTM** model (containerised) and returns forecast series.
6. User selects crops → recommendation endpoint uses **XGBoost/LightGBM** model, returns top‑N crops with SHAP values.
7. Budget & simulation services combine forecast, soil, crop yields to compute financial outcomes.
8. Roadmap service builds a timeline of recommended actions.

---

## 6. Deployment – Docker Compose
```yaml
version: "3.9"
services:
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_USER: agrisim
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: agrisim
    volumes:
      - pgdata:/var/lib/postgresql/data
  backend:
    build: ./agrisim_backend
    depends_on:
      - db
    env_file:
      - .env.backend
    ports:
      - "8000:8000"
  frontend:
    build: ./agrisim_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
volumes:
  pgdata:
```
* Separate Dockerfiles for backend (Python 3.11, `uvicorn` with `gunicorn`) and frontend (Node 20, `react‑scripts`).
* CI/CD pipeline (GitHub Actions) will run linting, unit tests, build images, and push to a container registry.

---

## 7. Requirements Checklist (Phase 2 Deliverables)
| Item | Description | Status |
|------|-------------|--------|
| Architecture diagram | Draw.io diagram (PNG & `.drawio`) | ✅ Created |
| Database schema | SQL script creating tables: `districts`, `soil`, `rainfall`, `crops`, `economics`, `simulation_inputs` | ✅ Drafted |
| OpenAPI spec | Exported `openapi.yaml` from FastAPI skeleton | ✅ Generated |
| FastAPI project skeleton | Directory structure, routers, DB connection, CORS, health endpoint | ✅ Implemented |
| React component stubs | Empty components with TypeScript interfaces, routing added | ✅ Added |
| Docker Compose file | Multi‑service compose for dev environment | ✅ Added |
| CI workflow | GitHub Actions lint + test + build stages | ✅ Added |
| Documentation update | `synopsis.md`, `PROJECT_ROADMAP.md`, `CLAUDE.md` reflect new architecture | ✅ Updated |

---

## 8. Success Criteria (Phase 2)
* `docker compose up` launches **Postgres+PostGIS**, **FastAPI**, and **React** without errors.
* `GET /health` returns `200 OK`.
* `GET /map/point?lat=...&lng=...` returns a valid district ID.
* Front‑end map loads and clicking a point displays district name.
* OpenAPI spec can be imported into Postman and all endpoints respond with example payloads.

---

## 9. Next Steps (Enter Phase 3)
* Populate the spatial tables with district GeoJSON and soil CSV.
* Train the rainfall‑forecast and crop‑recommendation models.
* Connect the front‑end components to the live API.

---

*Prepared by Cline – AI coding agent*
