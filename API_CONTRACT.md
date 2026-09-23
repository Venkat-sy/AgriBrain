# AgriSim API Contract

This document describes the public REST API exposed by the **FastAPI** backend. All endpoints are prefixed with `/api/v1/`.

## 1. District Lookup

### Request
```
GET /api/v1/map/districts
```
*No query parameters.*

### Response (200 OK)
```json
[
  {
    "id": 1,
    "name": "Alipurduar",
    "state": "West Bengal",
    "geometry": { "type": "Polygon", "coordinates": [...] }
  },
  { ... }
]
```
Each object contains the district identifier, human‑readable name, state and optional GeoJSON geometry used for map rendering.

---

## 2. Crop Profiles

### Request
```
GET /api/v1/crop/profiles
```
*No query parameters.*

### Response (200 OK)
```json
[
  {
    "id": 10,
    "name": "Wheat",
    "category": "Cereal",
    "season": "Rabi",
    "ideal_temperature_c": 20,
    "ideal_rainfall_mm": 350,
    "optimal_soil_type": "Loam"
  },
  { ... }
]
```

---

## 3. Run Simulation (Digital Twin)

### Request
```
POST /api/v1/simulation/run
Content-Type: application/json

{
  "district_id": 1,
  "selected_crop": "Wheat",
  "land_area_ha": 2.5,
  "budget_inr": 50000,
  "confirmed_soil_type": "Loam",
  "rainfall_override_mm": 400   // optional
}
```

### Response (200 OK)
```json
{
  "total_cost_inr": 48000,
  "estimated_yield_tons": 12.34,
  "market_value_inr": 75000,
  "net_profit_inr": 27000,
  "roi_percentage": 56.25,
  "risk_level": "low",
  "estimated_yield_tons_per_ha": 4.94,
  "soil_temp": "28.4°C",
  "moisture": "67%",
  "nitrogen_level": "85ppm",
  "cost_breakdown": [
    {"activity": "Seeds", "unit": "kg", "unit_cost": 100, "quantity": 5, "total_cost": 500},
    {"activity": "Fertiliser", "unit": "kg", "unit_cost": 150, "quantity": 20, "total_cost": 3000}
  ]
}
```

Fields:
* `total_cost_inr` – aggregated cost of all inputs.
* `estimated_yield_tons` – predicted yield for the given land area.
* `market_value_inr` – revenue estimate based on current market price.
* `net_profit_inr` – revenue minus total cost.
* `roi_percentage` – return on investment.
* `risk_level` – qualitative risk (low/medium/high) derived from scenario.
* `cost_breakdown` – itemised list of activities used for the simulation.

---

## Error Handling

All error responses follow the FastAPI default format:
```json
{
  "detail": "<human readable error message>"
}
```

Typical HTTP status codes and example payloads for each endpoint are listed below.

### 1. District Lookup – `GET /api/v1/map/districts`
* **400 Bad Request** – malformed query parameters (e.g., invalid `state` value).
```json
{
  "detail": "value is not a valid enumeration member; permitted: 'West Bengal', 'Maharashtra', ..."
}
```
* **500 Internal Server Error** – unexpected database failure.
```json
{
  "detail": "Failed to retrieve district data due to a server error."
}
```

### 2. Crop Profiles – `GET /api/v1/crop/profiles`
* **500 Internal Server Error** – unable to load crop data.
```json
{
  "detail": "Crop profile data could not be loaded."
}
```

### 3. Run Simulation – `POST /api/v1/simulation/run`
* **400 Bad Request** – validation errors for request body fields.
```json
{
  "detail": [
    {
      "loc": ["body", "district_id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    },
    {
      "loc": ["body", "land_area_ha"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```
* **404 Not Found** – referenced district or crop does not exist.
```json
{
  "detail": "District with id 999 not found."
}
```
* **500 Internal Server Error** – simulation engine raised an exception.
```json
{
  "detail": "Simulation failed due to internal error: <error details>"
}
```

---

*Last updated: 2026‑09‑23*
