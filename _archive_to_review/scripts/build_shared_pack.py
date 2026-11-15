"""Build agribrain_shared_pack/ - a non-destructive, copy-only shareable package.

Safety: uses shutil.copy2 only. Never moves, renames, or deletes any source file.
"""
import shutil
import zipfile
import os
from pathlib import Path

ROOT = Path(r"C:\Users\USER\Downloads\FinalYearProject")
PACK = ROOT / "agribrain_shared_pack"

DATA_SRC = ROOT / "datasets"
ML_MODELS_SRC = ROOT / "ml" / "models"
ROOT_MODELS_SRC = ROOT / "models"

# ---------------------------------------------------------------------------
# 1. Create destination directories
# ---------------------------------------------------------------------------
(PACK / "data").mkdir(parents=True, exist_ok=True)
(PACK / "models").mkdir(parents=True, exist_ok=True)
(PACK / "config").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 2. Copy data files (copy-only, read-only on source)
# ---------------------------------------------------------------------------
data_files = [
    # Explicitly requested
    DATA_SRC / "india_soilgrids_subset.csv",
    DATA_SRC / "All_India_AgriSim_Master_Dataset.csv",
    # Other master dataset CSVs
    DATA_SRC / "master_agri_dataset.csv",
    DATA_SRC / "master_agri_dataset_v2.csv",
    DATA_SRC / "master_agri_dataset_v2_fixed.csv",
    # Crop production CSVs
    DATA_SRC / "03_crop_production_india" / "crop_production.csv",
    # District / soil CSVs
    DATA_SRC / "district_name_mapping.csv",
    DATA_SRC / "district_rainfall_history.csv",
    DATA_SRC / "ICRISAT-District Level Data.csv",
    DATA_SRC / "crop_agronomy_base.json",
    DATA_SRC / "district_rainfall_summary.json",
]

for src in data_files:
    if src.exists():
        shutil.copy2(str(src), str(PACK / "data" / src.name))
        print(f"[data] copied: {src.name}")
    else:
        print(f"[data] SKIPPED (not found): {src}")

# ---------------------------------------------------------------------------
# 3. Copy ML models and scalers (copy-only)
# ---------------------------------------------------------------------------
model_files = []
if ML_MODELS_SRC.exists():
    model_files.extend(sorted(ML_MODELS_SRC.glob("*.pkl")))
    model_files.extend(sorted(ML_MODELS_SRC.glob("*.json")))
if ROOT_MODELS_SRC.exists():
    model_files.extend(sorted(ROOT_MODELS_SRC.glob("*.pkl")))

# De-duplicate while preserving order
seen = set()
unique_models = []
for m in model_files:
    if m.name not in seen:
        seen.add(m.name)
        unique_models.append(m)

for src in unique_models:
    shutil.copy2(str(src), str(PACK / "models" / src.name))
    print(f"[model] copied: {src.name}")

# ---------------------------------------------------------------------------
# 4. Create config/.env.example (new template file, not touching any source)
# ---------------------------------------------------------------------------
env_example_content = """# AgriBrain shared pack - environment configuration template
# Copy this file to .env and fill in your own values before running.

DATAGOV_API_KEY="579b464db66ec23bdd0000014d3afe0a938b4b43421cca1205b38d6a"
DATAGOV_RESOURCE_ID="9ef84268-d588-465a-a308-a864a43d0070"
GEMINI_API_KEY="your_gemini_api_key_here"
PORT=8000
"""
env_path = PACK / "config" / ".env.example"
env_path.write_text(env_example_content, encoding="utf-8")
print(f"[config] created: .env.example")

# ---------------------------------------------------------------------------
# 5. Create README.md
# ---------------------------------------------------------------------------
readme_content = """# AgriBrain Shared Pack

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
"""
readme_path = PACK / "README.md"
readme_path.write_text(readme_content, encoding="utf-8")
print(f"[readme] created: README.md")

# ---------------------------------------------------------------------------
# 6. Compress to zip (standalone copy in root)
# ---------------------------------------------------------------------------
zip_path = ROOT / "agribrain_shared_pack.zip"
if zip_path.exists():
    zip_path.unlink()  # remove stale zip so we build fresh (zip itself, not source data)

with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
    for file_path in PACK.rglob("*"):
        if file_path.is_file():
            arcname = file_path.relative_to(PACK)
            zf.write(str(file_path), str(arcname))
            print(f"[zip] added: {arcname}")

print(f"\nDone. Created {zip_path}")
print(f"Pack folder: {PACK}")
print("\nVerification: source files remain untouched (read-only copies only).")
