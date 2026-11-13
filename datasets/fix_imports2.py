with open('build_geospatial_and_master.py', 'r') as f:
    lines = f.readlines()

# The OUTPUTS dict is missing its opening - let me restore lines 1-30 properly
new_lines = [
    '#!/usr/bin/env python\n',
    '"""\n',
    'Build India-wide geospatial agricultural dataset from genuine sources.\n',
    'Synchronizes all datasets against canonical GeoJSON district names.\n',
    '"""\n',
    'import json\n',
    'import pandas as pd\n',
    'import numpy as np\n',
    'from pathlib import Path\n',
    'from thefuzz import fuzz, process\n',
    'import warnings\n',
    "warnings.filterwarnings('ignore')\n",
    '\n',
    '# ============================================================\n',
    '# CONFIGURATION\n',
    '# ============================================================\n',
    'DATASETS_DIR = Path(__file__).parent\n',
    'PROCESSED_DIR = DATASETS_DIR / "processed"\n',
    'RAW_DIR = DATASETS_DIR / "raw"\n',
    'GEOJSON_PATH = DATASETS_DIR / "india_districts.geojson"\n',
    '\n',
    '# Output files\n',
    'OUTPUTS = {\n',
    '    "district_metadata": DATASETS_DIR / "district_metadata.json",\n',
    '    "district_rainfall_summary": DATASETS_DIR / "district_rainfall_summary.json",\n',
    '    "crop_agronomy_base": DATASETS_DIR / "crop_agronomy_base.json",\n',
    '    "master_agri_dataset": DATASETS_DIR / "master_agri_dataset.csv",\n',
    '    "district_rainfall_history": DATASETS_DIR / "district_rainfall_history.csv",\n',
    '    "district_name_mapping": DATASETS_DIR / "district_name_mapping.csv",\n',
    '    "dataset_source_manifest": DATASETS_DIR / "dataset_source_manifest.json",\n',
    '    "data_coverage_report": DATASETS_DIR / "DATA_COVERAGE_REPORT.md",\n',
    '}\n',
    '\n',
    '# 21 major Indian crops (for reference)\n',
    'MAJOR_CROPS = [\n',
    '    "Rice", "Wheat", "Maize", "Cotton", "Soybean", "Groundnut", "Sugarcane",\n',
    '    "Chickpea", "Sorghum", "Pearl Millet", "Finger Millet", "Barley",\n',
    '    "Sunflower", "Sesame", "Castor", "Linseed", "Mustard", "Pigeon Pea",\n',
    '    "Green Gram", "Black Gram", "Jute"\n',
    ']\n',
    '\n',
    '# ============================================================\n',
    '# UTILITY FUNCTIONS\n',
    '# ============================================================\n'
] + lines[38:]

with open('build_geospatial_and_master.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed OUTPUTS dict')