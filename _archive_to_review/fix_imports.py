with open('build_geospatial_and_master.py', 'r') as f:
    lines = f.readlines()

# Fix imports
# Line 6 should be 'import json\n'
# Line 7 should be 'import pandas as pd\n'
# Line 8 should be 'import numpy as np\n'
# Line 9 should be 'from pathlib import Path\n'
# Line 10 should be 'from thefuzz import fuzz, process\n'
# Line 11 should be 'import warnings\n'
# Line 12 should be "warnings.filterwarnings('ignore')\n"

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
    '\n'
] + lines[20:]

with open('build_geospatial_and_master.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed imports')