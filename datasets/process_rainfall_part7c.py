import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 9. UPDATE DATA_COVERAGE_REPORT.md
# ============================================================
print("Updating DATA_COVERAGE_REPORT.md...")

# Read existing report
with open('DATA_COVERAGE_REPORT.md', 'r') as f:
    report = f.read()

# Add new section for rainfall data integration
new_section = """

## Rainfall Data Integration (2025-2026) - NEW

### Files Downloaded
| File | Size | Status |
|------|------|--------|
| `rainfall_districtwise_daily_imd.csv` | 9.00 MB | **Processed** - IMD district-wise daily observations |
| `RF25_indselect_rfp25.nc` | 0 KB | **INCOMPLETE - NOT PROCESSED** |
| `RF25_ind2025_rfp25.nc` | 24.25 MB | **Processed** - IMD gridded 0.25° NetCDF (2025 full year) |

### NetCDF: RF25_ind2025_rfp25.nc (Gridded 2025)
- **Variable**: RAINFALL (mm)
- **Date Range**: 2025-01-01 to 2025-12-31 (365 days, COMPLETE YEAR)
- **Spatial Extent**: 6.5°N–38.5°N, 66.5°E–100.0°E (India + surroundings)
- **Resolution**: 0.25° × 0.25° (approx. 25 km)
- **Grid Size**: 129 lat × 135 lon = 17,415 cells
- **Aggregation**: Spatial average of grid cells intersecting each district polygon
- **Districts Derived**: 641 (all canonical districts)

### CSV: rainfall_districtwise_daily_imd.csv (Observations 2026)
- **Variable**: Daily Actual (mm)
- **Date Range**: 2026-08-19 to 2026-11-06 (~80 days, monsoon season only)
- **Original Districts**: 728 across 39 states/UTs
- **Matched to Canonical**: 437 districts
- **Unmatched**: 291 districts (naming differences, e.g., new districts, spelling variants)
- **Records After Matching**: 34,523

### Combined Dataset
| Metric | Value |
|--------|-------|
| Total district-daily records | 268,488 |
| Unique districts covered | 641 |
| Years available | 2025 (gridded), 2026 (observations, partial) |
| NetCDF-derived records (2025) | 233,965 |
| IMD observation records (2026) | 34,523 |

### Output Files Generated
| File | Records | Description |
|------|---------|-------------|
| `district_rainfall_history.csv` | 1,078 | Annual rainfall per district per year per source |
| `district_rainfall_summary.json` | 641 | Per-district summary statistics |
| `rainfall_data_coverage.csv` | 641 | Coverage matrix for all districts |

### Critical Gaps Remaining
1. **2021–2024**: NO DATA whatsoever (historical target not met)
2. **2025**: Only gridded estimates — no ground-truth district observations
3. **2026**: Only Aug–Nov monsoon season, only 437/641 districts
4. **Phase 3 Requirement**: ≥500 genuine records per target variable — NOT MET

### Source Attribution
- **Direct observations**: `imd_district_observation` (CSV, 2026)
- **Gridded-derived estimates**: `netcdf_grid_derived` (NetCDF aggregated, 2025)
- **Preserved**: Original files unchanged in `datasets/`
- **Distinguished**: Every record tagged with `source` column

### Next Steps
1. Acquire IMD historical 2021–2024 district-wise rainfall via formal request
2. Acquire DES crop production/yield 2019–2023 via data.gov.in API key
3. Acquire ICAR/NBSS&LUP soil profiles via MoU
4. Only then re-run `build_geospatial_and_master.py` and retrain models
"""

# Append to report
updated_report = report + new_section

with open('DATA_COVERAGE_REPORT.md', 'w') as f:
    f.write(updated_report)
print("Updated DATA_COVERAGE_REPORT.md")

# ============================================================
# 10. PRINT FINAL VERIFICATION SUMMARY
# ============================================================
print("\n\n" + "="*80)
print("FINAL VERIFICATION SUMMARY")
print("="*80)

print(f"\n1. FILE VERIFICATION:")
print(f"   - rainfall_districtwise_daily_imd.csv: 9.00 MB, 57,465 records, 728 districts")
print(f"   - RF25_indselect_rfp25.nc: 0 KB (INCOMPLETE - NOT PROCESSED)")
print(f"   - RF25_ind2025_rfp25.nc: 24.25 MB, 365 days, 129x135 grid, 0.25° resolution")

print(f"\n2. NETCDF (RF25_ind2025_rfp25.nc):")
print(f"   - Variable: RAINFALL (mm)")
print(f"   - Date range: 2025-01-01 to 2025-12-31 (365 days, FULL YEAR)")
print(f"   - Spatial: 6.5°N to 38.5°N, 66.5°E to 100.0°E (India + surroundings)")
print(f"   - Resolution: 0.25° x 0.25° (approx 25km)")
print(f"   - Districts derived: 641 (all 641 canonical districts have grid cells)")

print(f"\n3. CSV (rainfall_districtwise_daily_imd.csv):")
print(f"   - Variable: Daily Actual (mm)")
print(f"   - Date range: 2026-08-19 to 2026-11-06 (~80 days, monsoon season)")
print(f"   - Original districts: 728 across 39 states")
print(f"   - Matched to canonical: 437 districts")
print(f"   - Unmatched (name differences): 291 districts")

print(f"\n4. COMBINED DATA:")
print(f"   - Total district-daily records: 268,488")
print(f"   - Unique districts covered: 641")
print(f"   - Years: 2025 (gridded, all 641 districts), 2026 (observations, 437 districts)")
print(f"   - Source breakdown:")
print(f"     - netcdf_grid_derived: 233,965 records")
print(f"     - imd_district_observation: 34,523 records")

print(f"\n5. OUTPUT FILES GENERATED:")
annual = pd.read_pickle('temp_annual.pkl')
coverage_df = pd.read_pickle('temp_coverage_df.pkl')
print(f"   - district_rainfall_history.csv: {len(annual)} annual records")
print(f"   - district_rainfall_summary.json: 641 districts with stats")
print(f"   - rainfall_data_coverage.csv: {len(coverage_df)} districts with coverage info")
print(f"   - dataset_source_manifest.json: UPDATED")
print(f"   - DATA_COVERAGE_REPORT.md: UPDATED")

print(f"\n6. DATA GAPS (STILL MISSING):")
print(f"   - Historical 2021-2024: NO DATA")
print(f"   - 2025: Only gridded estimates (no district observations)")
print(f"   - 2026: Only partial monsoon (Aug-Nov), only 437 districts")
print(f"   - Target 2021-2025 historical: ONLY 2025 available (gridded)")

print("\n" + "="*80)