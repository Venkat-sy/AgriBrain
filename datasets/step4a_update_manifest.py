import pandas as pd
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# STEP 4a: Update dataset_source_manifest.json
# ============================================================

# Load data for metadata
with open('temp_all_year_dfs.pkl', 'rb') as f:
    all_year_dfs = pickle.load(f)

full_combined = pd.read_pickle('temp_combined_full.pkl')

print("Updating dataset_source_manifest.json...")

with open('dataset_source_manifest.json', 'r') as f:
    manifest = json.load(f)

# Update rainfall_data section
manifest['rainfall_data'] = {
    "source": "MIXED - IMD district-wise daily observations (2026) + IMD gridded NetCDF (2021-2025) aggregated to districts",
    "csv_source_file": "rainfall_districtwise_daily_imd.csv (IMD district-wise daily, 2026-08-19 to 2026-11-06)",
    "netcdf_source_files": {
        "2021": "RF25_ind2021_rfp25.nc (IMD gridded 0.25deg, 2021 full year)",
        "2022": "RF25_ind2022_rfp25.nc (IMD gridded 0.25deg, 2022 full year)",
        "2023": "RF25_ind2023_rfp25.nc (IMD gridded 0.25deg, 2023 full year)",
        "2024": "RF25_ind2024_rfp25.nc (IMD gridded 0.25deg, 2024 full year - leap year 366 days)",
        "2025": "RF25_ind2025_rfp25.nc (IMD gridded 0.25deg, 2025 full year)"
    },
    "netcdf_incomplete_file": "RF25_indselect_rfp25.nc (0 KB, incomplete, NOT processed)",
    "csv_date_range": "2026-08-19 to 2026-11-06",
    "netcdf_date_ranges": {
        "2021": "2021-01-01 to 2021-12-31",
        "2022": "2022-01-01 to 2022-12-31",
        "2023": "2023-01-01 to 2023-12-31",
        "2024": "2024-01-01 to 2024-12-31",
        "2025": "2025-01-01 to 2025-12-31"
    },
    "csv_original_districts": 728,
    "csv_matched_districts": 437,
    "netcdf_derived_districts": 641,
    "combined_districts": 641,
    "csv_original_records": 57465,
    "csv_matched_records": 34523,
    "netcdf_derived_records_per_year": {
        "2021": int(len(all_year_dfs[0])),
        "2022": int(len(all_year_dfs[1])),
        "2023": int(len(all_year_dfs[2])),
        "2024": int(len(all_year_dfs[3])),
        "2025": 233965
    },
    "combined_records": int(len(full_combined)),
    "spatial_resolution_netcdf": "0.25 x 0.25 degrees",
    "rainfall_units": "mm",
    "aggregation_method": "Spatial average of grid cells intersecting district polygon",
    "coordinate_system": "EPSG:4326 (WGS84)",
    "data_availability": "COMPLETE 2021-2025 (gridded, all 641 districts), 2026 partial (observations, 437 districts, Aug-Nov only)",
    "notes": "CSV contains 2026 monsoon season only (Aug-Nov). NetCDF contains full years 2021-2025. No overlap in years. 291 CSV districts could not be matched to canonical registry due to naming differences. All 5 years of gridded data now available."
}

# Update master_dataset info
manifest['master_dataset']['data_sources']['rainfall'] = "mixed_imd_observation_2026_netcdf_grid_2021_2025"
manifest['master_dataset']['rainfall_coverage'] = {
    "2021": "gridded_all_641_districts",
    "2022": "gridded_all_641_districts",
    "2023": "gridded_all_641_districts",
    "2024": "gridded_all_641_districts",
    "2025": "gridded_all_641_districts",
    "2026": "observations_437_districts_partial_monsoon_only"
}

with open('dataset_source_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print("Updated dataset_source_manifest.json")