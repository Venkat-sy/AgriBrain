# Data Coverage Report

## Executive Summary
This report documents the data coverage for the India Agricultural Forecasting Project after the validation and reconciliation pass (Phase 2 completion).

---

## Rainfall Data (IMD - India Meteorological Department)

### GENUINE DATA - Successfully Integrated
| Period | Source | Districts | Records | Provenance |
|--------|--------|-----------|---------|------------|
| 2021-2025 | IMD NetCDF Grid (RF25_indYYYY_rfp25.nc) | 631 canonical | ~631/yr | netcdf_grid_derived |
| 2026 | IMD District-wise Daily Observations | 437 canonical | 437 | imd_district_observation |

**Total Genuine Rainfall Records:** 3,642 (5 years x 631 + 1 year x 437)
**Coverage:** 631 districts (98.4% of canonical 641 district list)
**Years:** 2021, 2022, 2023, 2024, 2025, 2026
**Files preserved:** 5 NetCDF files (RF25_ind2021_rfp25.nc through RF25_ind2025_rfp25.nc) + rainfall_districtwise_daily_imd.csv

### SYNTHETIC/PLACEHOLDER DATA - REMOVED
- Previous build incorrectly used rainfall_district_annual.csv (synthetic placeholder for 10 districts)
- This has been REPLACED with genuine IMD data in the current build
- The synthetic file remains in raw/ for reference but is NOT used in master dataset

### Key Files
- temp_annual.pkl - Processed genuine IMD annual rainfall (2021-2026)
- district_rainfall_history.csv - Long-form district-year rainfall history (contains NaN for 1978-2017 due to no overlap)
- district_rainfall_summary.json - Summary statistics (NaN for 1978-2017)
- rainfall_data_coverage.csv - Coverage metadata
- rainfall_districtwise_daily_imd.csv - Raw 2026 daily observations
- raw/RF25_ind2021_rfp25.nc through raw/RF25_ind2025_rfp25.nc - Original NetCDF files (PRESERVED)

---

## Crop Production Data (ICRISAT)

### GENUINE HISTORICAL DATA - Retained
| Metric | Value |
|--------|-------|
| Records | 179,283 |
| Years | 1978-2017 (40 years) |
| Districts | 309 ICRISAT districts (matched to canonical) |
| Crops | 23 major crops (Rice, Wheat, Maize, Sorghum, Pearl Millet, Finger Millet, Barley, Chickpea, Pigeonpea, Groundnut, Soybean, Cotton, Sugarcane, etc.) |
| Source | ICRISAT District Level Database |
| Provenance | icrisat_district_database |

### IMPORTANT LIMITATIONS
1. No temporal overlap with IMD rainfall: ICRISAT data ends 2017, IMD rainfall starts 2021
2. District name schema mismatch: ICRISAT uses different district naming than IMD canonical list
3. No 2018-2025 crop data: NOT fabricated - correctly left as gap
4. Missing crops: Only 23 crops covered; horticulture, minor pulses, oilseeds partially missing

### Key Files
- processed/crop_production_district_icrisat.csv - Production data (179,283 records)
- processed/crop_yield_district_icrisat.csv - Yield data
- raw/icrisat_*.csv - Original downloaded files (PRESERVED)
- acquire_crop_data.py - Download script with API credentials

### District Mapping Status
- district_name_mapping.csv maps ICRISAT districts to canonical 641
- Mapping covers 309 ICRISAT districts that match to canonical
- Gap: ~332 districts in IMD have no ICRISAT crop history

---

## Soil Data

### CURRENT STATE: SYNTHETIC PLACEHOLDER
| File | Status | Notes |
|------|--------|-------|
| soil_characteristics.csv | SYNTHETIC | Uniform values per state, not district-level |
| raw/soil_ph.csv | Raw download | Needs processing to district level |
| raw/soil_organic_carbon.csv | Raw download | Needs processing to district level |

SoilGrids/NBSS&LUP genuine data: Raw files downloaded but NOT yet processed to district level.
The current soil_characteristics.csv in datasets/ is a synthetic placeholder generated per-state.

### Required Action
Process raw/soil_ph.csv and raw/soil_organic_carbon.csv to aggregate to 641 canonical districts using SoilGrids 250m rasters or NBSS&LUP district profiles.

---

## Master Dataset (master_agri_dataset.csv)

| Metric | Value |
|--------|-------|
| Total Records | 179,283 (matches ICRISAT production) |
| Years | 1978-2017 |
| Districts | 309 (ICRISAT coverage matched to canonical) |
| Crops | 23 |
| Rainfall Coverage | 0 records (NaN) - NO YEAR OVERLAP WITH IMD 2021-2026 |
| Yield Coverage | 179,283 (100%) |
| Production Coverage | 179,283 (100%) |
| Soil pH Coverage | 179,283 (100% - synthetic per-state) |
| Soil OC Coverage | 179,283 (100% - synthetic per-state) |

### Critical Note on Rainfall in Master Dataset
The annual_rainfall_mm column is ALL NaN because:
- ICRISAT crop data: 1978-2017
- IMD rainfall data: 2021-2026
- Zero year overlap -> cannot merge on (district, state, year)

Rainfall data is available separately in:
- temp_annual.pkl (processed, ready for modeling with future crop data)
- district_rainfall_history.csv (long-form CSV)
- district_rainfall_summary.json (summary stats)

---

## Data Gaps Summary

| Gap | Severity | Action Required |
|-----|----------|-----------------|
| No 2018-2025 crop production data | HIGH | Acquire from DES/Ministry of Agriculture APIs |
| No rainfall-crop year overlap | HIGH | Acquire 2018-2020 rainfall or 2018-2025 crop data |
| District name mismatch (IMD ICRISAT) | MEDIUM | Complete district_name_mapping.csv for all 641 districts |
| Soil data synthetic | MEDIUM | Process SoilGrids/NBSS&LUP raw downloads to district level |
| Only 23 crops covered | LOW | Extend to horticulture, minor pulses, oilseeds |
| ~332 IMD districts lack crop history | MEDIUM | Accept limitation or acquire state-level aggregates |

---

## Provenance Tracking
All datasets include data_source / rainfall_data_source columns tracking:
- netcdf_grid_derived - IMD NetCDF 2021-2025
- imd_district_observation - IMD 2026 district observations
- icrisat_district_database - ICRISAT 1978-2017
- synthetic_placeholder - NONE in current master (removed)
- state_level_synthetic - Soil pH/OC (current placeholder)

---

*Report generated: Validation & Reconciliation Pass Complete*
*Next: Phase 3 - Feature Engineering & Model Training (pending data gap resolution)*
