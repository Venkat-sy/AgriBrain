# Phase 3 Readiness Assessment - UPDATED

**Generated:** 2025-11-06 (after Phase 2 dataset rebuild with combined years)

---

## Executive Summary

**NOT READY for ML Training** - Critical gaps remain.

### Usable Training Records: **0**

**Reason:** Zero temporal overlap between genuine crop data (ICRISAT: 1978–2017) and genuine rainfall data (IMD NetCDF: 2021–2025, Observations: 2026). No district-crop-year has both genuine crop production AND genuine rainfall.

Soil data: **0 genuine records** - all NaN, explicitly marked as NOT_AVAILABLE.

---

## Data Inventory

| Dataset | Source | Years | Districts | Crops | Records | Provenance |
|---------|--------|-------|-----------|-------|---------|------------|
| Crop Production + Yield | ICRISAT District Database | 1978–2017 | 309 (of 641 canonical) | 23 | 179,283 | **GENUINE** |
| Rainfall (Gridded) | IMD NetCDF RF25 | 2021–2025 | 631 (of 641 canonical) | N/A | ~3,155 | **GENUINE** |
| Rainfall (District Obs) | IMD District Reports | 2026 (partial) | 437 | N/A | 437 | **GENUINE** |
| Soil | SoilGrids / NBSS&LUP | — | 0 / 641 | N/A | 0 | **MISSING** |

---

## Coverage Matrix Summary

### By Year
- **1978–2017**: Crop data only (179,283 genuine records), NO rainfall, NO soil
- **2018–2020**: NO data of any kind
- **2021–2025**: Rainfall only (~73,715 genuine records), NO crop, NO soil
- **2026**: Rainfall only (10,051 genuine records), NO crop, NO soil

### By Data Type Overlap
- **Crop + Rainfall**: **0 records** (zero year overlap)
- **Crop + Soil**: **0 records** (no soil data)
- **Rainfall + Soil**: **0 records** (no soil data)
- **All Three**: **0 records**

### District Coverage
- **309 districts** have ICRISAT crop history (1978–2017)
- **332 districts** have NO crop data at all
- **631 districts** have IMD gridded rainfall (2021–2025)
- **437 districts** have IMD observed rainfall (2026)
- **0 districts** have genuine soil data

---

## Blockers for Phase 3 (ML Training)

### 1. CRITICAL: Zero Crop-Rainfall Temporal Overlap
- ICRISAT data ends 2017, IMD gridded rainfall starts 2021
- **Gap: 2018–2020** (3 years, no data from either source)
- **No shared years** between the two genuine datasets

### 2. CRITICAL: No Genuine Soil Data
- SoilGrids rasters not downloaded/processed
- NBSS&LUP/ICAR district soil profiles not acquired
- All 641 districts marked NOT_AVAILABLE with explicit provenance

### 3. HIGH: Crop Data Only Covers 48% of Districts
- 309/641 canonical districts have any ICRISAT data
- 332 districts have zero crop history

### 4. MEDIUM: Recent Crop Data (2018–2025) Not Available
- data.gov.in API (dataset 9ef84268-d588-465a-a308-a864a43d0070) returns **market prices**, not production
- No programmatic access to DAC&FW district-wise production for 2018–2025
- Manual download from https://aps.dac.gov.in/ required but not automated

---

## Required Actions Before Phase 3

### Must Fix (Blockers)
1. **Acquire 2018–2025 district-wise crop production/area/yield**
   - Source: DAC&FW (aps.dac.gov.in) or state agricultural departments
   - Must cover at least 2021–2025 to overlap with IMD rainfall
   - Without this: **zero training records**

2. **Acquire genuine district-level soil data**
   - Download SoilGrids 250m rasters for India (pH, SOC, N, P, K, texture)
   - Aggregate to 641 canonical districts using grid map
   - Or acquire NBSS&LUP district soil profiles
   - Mark model-derived estimates clearly (e.g., `soil_data_provenance: "SoilGrids_250m_aggregated"`)

### Should Fix
3. **Fill 2018–2020 rainfall gap** (if IMD has data)
   - Check if IMD RF25 NetCDF exists for 2018–2020
   - If not, use IMD district observations or CHIRPS as fallback (marked as model-derived)

4. **Expand crop district coverage**
   - Map remaining 332 districts to nearest ICRISAT district or use state-level averages
   - Clearly mark imputed vs genuine

---

## Usable Training Records Projection

| Scenario | Crop Years | Rainfall Years | Overlap Years | Est. Records |
|----------|------------|----------------|---------------|--------------|
| Current | 1978–2017 | 2021–2026 | **None** | **0** |
| + 2018–2025 crop data | 1978–2025 | 2021–2026 | 2021–2025 | ~300 districts × 23 crops × 5 years ≈ **34,500** |
| + Soil data | — | — | — | Adds features to above |

---

## Recommendation

**Do not start ML training.** The dataset has **zero usable training records** due to:
1. No temporal overlap between crop and rainfall
2. No soil data whatsoever

**Priority:** Acquire 2021–2025 district crop production data and SoilGrids rasters.

---

*This assessment reflects the state after Phase 2 rebuild (master_agri_dataset_v2.csv with combined years 1978–2026).*
