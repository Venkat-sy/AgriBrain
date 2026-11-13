## Rainfall Data Integration (2021-2026) - UPDATED

### Files Downloaded
| File | Size | Status |
|------|------|--------|
| `rainfall_districtwise_daily_imd.csv` | 9.00 MB | **Processed** - IMD district-wise daily observations |
| `RF25_indselect_rfp25.nc` | 0 KB | **INCOMPLETE - NOT PROCESSED** |
| `RF25_ind2021_rfp25.nc` | 24.25 MB | **Processed** - IMD gridded 0.25° NetCDF (2021 full year) |
| `RF25_ind2022_rfp25.nc` | 24.25 MB | **Processed** - IMD gridded 0.25° NetCDF (2022 full year) |
| `RF25_ind2023_rfp25.nc` | 24.25 MB | **Processed** - IMD gridded 0.25° NetCDF (2023 full year) |
| `RF25_ind2024_rfp25.nc` | 24.37 MB | **Processed** - IMD gridded 0.25° NetCDF (2024 full year - leap year) |
| `RF25_ind2025_rfp25.nc` | 24.25 MB | **Processed** - IMD gridded 0.25° NetCDF (2025 full year) |

### NetCDF: RF25_ind{{YYYY}}_rfp25.nc (Gridded 2021-2025)
- **Variable**: RAINFALL (mm)
- **Date Range**: 2021-01-01 to 2025-12-31 (5 full years: 2021=365d, 2022=365d, 2023=365d, 2024=366d leap, 2025=365d)
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
| Total district-daily records | {total_records} |
| Unique districts covered | 641 |
| Years available | 2021-2025 (gridded, complete), 2026 (observations, partial) |
| NetCDF-derived records (2021) | {y2021} |
| NetCDF-derived records (2022) | {y2022} |
| NetCDF-derived records (2023) | {y2023} |
| NetCDF-derived records (2024) | {y2024} |
| NetCDF-derived records (2025) | 233,965 |
| IMD observation records (2026) | 34,523 |

### Output Files Generated
| File | Records | Description |
|------|---------|-------------|
| `district_rainfall_history.csv` | {annual_records} | Annual rainfall per district per year per source |
| `district_rainfall_summary.json` | {coverage_districts} | Per-district summary statistics |
| `rainfall_data_coverage.csv` | {coverage_districts} | Coverage matrix for all districts |

### Critical Gaps Remaining
1. **2026**: Only Aug–Nov monsoon season, only 437/641 districts
2. **Phase 3 Requirement**: ≥500 genuine records per target variable — NOT MET (all 2021-2025 are gridded estimates)
3. **Ground Truth**: No direct district-level observations for 2021-2025

### Source Attribution
- **Direct observations**: `imd_district_observation` (CSV, 2026)
- **Gridded-derived estimates**: `netcdf_grid_derived` (NetCDF aggregated, 2021-2025)
- **Preserved**: Original files unchanged in `datasets/`
- **Distinguished**: Every record tagged with `source` column

### Next Steps
1. Acquire IMD historical 2021–2024 district-wise rainfall via formal request (to replace gridded estimates)
2. Acquire DES crop production/yield 2019–2023 via data.gov.in API key
3. Acquire ICAR/NBSS&LUP soil profiles via MoU
4. Only then re-run `build_geospatial_and_master.py` and retrain models