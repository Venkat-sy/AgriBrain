# Project Structure & Codebase Audit

## Complete Directory Tree

```
FinalYearProject/
├── .github/                              # GitHub workflows
├── _archive_to_review/                   # Legacy/experimental code (excluded from build)
├── backend/                              # FastAPI Backend
│   ├── api/                              # API route modules
│   │   ├── __init__.py
│   │   ├── baseline.py
│   │   ├── chat.py                       # Groq LLM chat (text + vision)
│   │   ├── crop_recommendation.py        # ML crop recommendations
│   │   ├── map.py                        # District GeoJSON
│   │   ├── rainfall.py                   # Rainfall data
│   │   ├── roadmap.py                    # Cultivation roadmap
│   │   ├── simulation.py                 # Digital twin simulation
│   │   ├── soil.py                       # Soil data
│   │   └── spatial.py                    # Reverse geocoding + zones
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                     # Settings, DB connection
│   ├── database/
│   │   ├── __init__.py
│   │   └── init_db.py
│   ├── ml/
│   │   ├── inference/
│   │   │   ├── __init__.py
│   │   │   └── crop_recommendation.py    # XGBoost inference
│   │   ├── saved_models/
│   │   │   ├── xgboost_crop_model.joblib
│   │   │   └── xgboost_crop_model_info.json
│   │   └── training/
│   ├── models/
│   │   ├── __init__.py                   # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── simulation.py                 # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── calendar_generator.py
│   │   ├── crop_recommendation_service.py
│   │   ├── data_lookup.py
│   │   ├── market_pricing.py
│   │   ├── simulation_engine.py
│   │   └── weather_service.py
│   ├── main.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── alembic.ini
│
├── datasets/                             # Training & reference data
│   ├── master_agri_dataset_v2.csv
│   ├── india_districts.geojson
│   ├── crop_agronomy_base.json
│   ├── soil_types.json
│   ├── processed/
│   │   ├── crop_recommendation_train.csv
│   │   └── crop_production_processed.csv
│
├── docs/
├── frontend_web/                         # Next.js 16 Frontend
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── simulate/page.tsx
│   │   │   ├── calendar/page.tsx
│   │   │   ├── expert-chat/page.tsx
│   │   │   └── api/
│   │   ├── components/
│   │   │   ├── MapUI.tsx
│   │   │   ├── ChatAssistant.tsx
│   │   │   ├── HomeChatbot.tsx
│   │   │   ├── WeatherWidget.tsx
│   │   │   ├── AlertsWidget.tsx
│   │   │   ├── DigitalTwinWidget.tsx
│   │   │   ├── CropCard.tsx
│   │   │   ├── InputPanel.tsx
│   │   │   ├── SimulationPanel.tsx
│   │   │   ├── SimulationResults.tsx
│   │   │   ├── SimulationCalendar.tsx
│   │   │   ├── IndiaMapSelector.tsx
│   │   │   └── ui/
│   │   ├── context/FarmContext.tsx
│   │   ├── lib/utils.ts
│   │   ├── services/api.ts
│   │   └── hooks/
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── vercel.json
│   └── .eslintrc.json
│
├── tests/
│   ├── conftest.py
│   ├── test_crop_recommendation.py       # ✅ PASSING
│   ├── test_db.py                        # Script
│   ├── test_simulation.py                # Script
│   └── ...
│
├── PROJECT_AUDIT_DOCUMENTATION/
└── README.md
```