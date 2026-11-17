# AgriBrain - Smart Agriculture Platform

## Project Identity & Objectives

**Project Name:** AgriBrain (formerly AgriSim)
**Type:** Full-stack AI-powered agricultural intelligence platform
**Target Region:** India (pan-India coverage with district-level granularity)
**Status:** Active development - production build passing, Vercel-deployed frontend, Render-deployed backend

### Core Mission
Democratize precision agriculture for Indian farmers through:
1. **ML-based Crop Recommendations** - XGBoost model (22 crops) trained on Indian agro-climatic data
2. **Digital Twin Simulation** - Economics, water balance, risk assessment, cultivation timeline
3. **Expert AI Agronomist Chat** - Context-aware LLM (Groq Llama-3.3-70b) with vision capabilities
4. **Interactive Map & Spatial Intelligence** - India district mapping with soil/climate profiles

### Key Value Proposition
Farmers input location (map click or coordinates) → Get instant soil/climate profile → ML recommends top-5 crops → Run full-season digital twin simulation → Receive cultivation calendar → Chat with expert AI that knows their complete farm context
---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16.4)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Home Page   │  │ Simulate Page│  │ Calendar Page│             │
│  │  (Chat +     │  │ (MapUI +     │  │ (Weather +   │             │
│  │   Journey)   │  │  Crop Table) │  │  Alerts +    │             │
│  └──────┬───────┘  └──────┬───────┘  │  DigitalTwin)│             │
│         │                 │          └──────┬───────┘             │
│         └─────────────────┼────────────────┘                      │
│                           ▼                                       │
│              ┌────────────────────────┐                           │
│              │   FarmContext (React)  │  ◄── Global state mgmt   │
│              │  - selectedCrop        │                           │
│              │  - coordinates         │                           │
│              │  - soilParams          │                           │
│              │  - simulationResults   │                           │
│              │  - farmParams          │                           │
│              │  - calendarStages      │                           │
│              │  - chatHistory         │                           │
│              └───────────┬────────────┘                           │
│                          │                                         │
│              ┌───────────▼────────────┐                           │
│              │   ApiService (fetch)   │  ◄── Backend proxy layer  │
│              │  - sendChatMessage     │                           │
│              │  - getCropRecommendations                      │
│              │  - runSimulation       │                           │
│              │  - lookupDistrict      │                           │
│              └───────────┬────────────┘                           │
└──────────────────────────┼────────────────────────────────────────┘
                           │ HTTPS/JSON
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI 3.0)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  /spatial    │  │ /simulation  │  │    /chat     │             │
│  │  - reverse   │  │  - run       │  │  - troubleshoot      │
│  │  - geocode   │  │  - list      │  │  - troubleshoot-vision   │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│         │                │                   │                      │
│         └────────────────┼───────────────────┘                      │
│                          ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │              SimulationEngine (services)                    │      │
│  │  - Agronomic calculations (NPK, water, yield)              │      │
│  │  - Economic modeling (costs, MSP, market prices, ROI)      │      │
│  │  - Risk assessment (drought, pest, soil stress)            │      │
│  │  - Roadmap generation (5-stage cultivation timeline)       │      │
│  └────────────────────────┬────────────────────────────────────┘      │
│                           │                                           │
│        ┌──────────────────┼──────────────────┐                       │
│        ▼                  ▼                  ▼                       │
│  ┌───────────┐     ┌───────────────┐  ┌───────────┐                 │
│  │ ML Models │     │   Database    │  │   Groq    │                 │
│  │ - XGBoost │     │  (PostgreSQL/ │  │  LLM API  │                 │
│  │   Crop    │     │   SQLite dev) │  │ - llama-  │                 │
│  │ - Yield   │     │  - districts  │  │   3.3-70b │                 │
│  │   Predict │     │  - crops      │  │ - llama-  │                 │
│  └───────────┘     │  - rainfall   │  │   3.2-11b │                 │
│                    │  - costs      │  │   vision  │                 │
│                    │  - prices     │  └───────────┘                 │
│                    │  - simulations│                                 │
│                    └───────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend Framework** | Next.js | 16.4.6 | App Router, SSR/SSG, API routes |
| **React** | React | 19.3.0 | UI components |
| **Styling** | Tailwind CSS | 4.3.3 | Utility-first CSS |
| **UI Components** | Radix UI | 2.x | Accessible primitives |
| **Maps** | React-Leaflet | 5.0.0 | Interactive map (Leaflet 1.9.4) |
| **Charts/Visualization** | Custom + Lucide | - | Icons, progress bars |
| **Markdown** | React-Markdown | 10.1.0 | Chat rendering |
| **Backend Framework** | FastAPI | 0.109.0 | REST API |
| **Database ORM** | SQLAlchemy | 2.0.25 | Database models |
| **Database** | PostgreSQL (prod) / SQLite (dev) | - | Persistent storage |
| **ML Framework** | XGBoost + scikit-learn | 1.3.2 | Crop recommendation, yield prediction |
| **LLM Provider** | Groq | - | llama-3.3-70b-versatile, llama-3.2-11b-vision |
| **Geospatial** | GeoPandas, Shapely | 0.14.3 | Spatial operations |
| **Deployment** | Vercel (FE) + Render (BE) | - | Production hosting |