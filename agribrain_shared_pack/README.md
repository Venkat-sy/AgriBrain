# AgriBrain Shared Pack

This folder contains a shareable copy of the AgriBrain project assets:
datasets, trained ML models/scalers, and an environment configuration template.

All files here are **copies**. The original files in the source project were not
moved, renamed, modified, or deleted.

## Folder layout

```
agribrain_shared_pack/
├── data/            # Dataset CSVs and JSON manifests
├── models/          # Pre-trained ML models (.pkl) and scalers
└── config/          # Environment template (.env.example)
```

## Datasets (`data/`)

| File | Description |
|------|-------------|
| `india_soilgrids_subset.csv` | SoilGrids soil-property subset for Indian districts |
| `All_India_AgriSim_Master_Dataset.csv` | Master AgriSim dataset (all-India) |
| `master_agri_dataset.csv` | Master agriculture dataset |
| `master_agri_dataset_v2.csv` | Master agriculture dataset v2 |
| `master_agri_dataset_v2_fixed.csv` | Master agriculture dataset v2 (fixed headers) |
| `crop_production.csv` | District-level crop production data |
| `district_name_mapping.csv` | District name mappings |
| `district_rainfall_history.csv` | Historical district rainfall |
| `ICRISAT-District Level Data.csv` | ICRISAT district-level crop data |
| `crop_agronomy_base.json` | Crop agronomy base configuration |
| `district_rainfall_summary.json` | District rainfall summary |

## ML Feature Vector

The crop-recommendation model expects features in this exact order:

```
[N, P, K, temperature, humidity, ph, rainfall]
```

| Feature | Meaning |
|---------|---------|
| N | Nitrogen content |
| P | Phosphorus content |
| K | Potassium content |
| temperature | Temperature (°C) |
| humidity | Humidity (%) |
| ph | Soil pH |
| rainfall | Rainfall (mm) |

## Models (`models/`)

Pre-trained pickled models and scalers are included. Load them with
`pickle` / `joblib` and pair each model with its matching scaler before
inference.

## Quick placement instructions for collaborators

1. Unzip `agribrain_shared_pack.zip` into your project root.
2. Copy `config/.env.example` to `config/.env` and fill in your own API keys.
3. Place the `data/` CSVs where your loader expects them (default: `datasets/`).
4. Place the `models/` `.pkl` files where your inference code expects them
   (default: `ml/models/` or `models/`).
5. Run `pip install -r requirements.txt` to install Python dependencies.

## Safety note

No source file was altered during the creation of this pack. Every asset above
is a duplicate produced with `shutil.copy2` (read-only on the source).
