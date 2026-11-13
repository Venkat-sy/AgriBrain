import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 7c. rainfall_data_coverage.csv and metadata updates
# ============================================================
print("Generating rainfall_data_coverage.csv...")

with open('temp_summary.json', 'r') as f:
    summary = json.load(f)

coverage_rows = []
for key, info in summary.items():
    coverage_rows.append({
        'district_name': info['district_name'],
        'state_name': info['state_name'],
        'canonical_key': key,
        'years_available': ','.join(map(str, info['years_available'])),
        'num_years': len(info['years_available']),
        'mean_annual_rainfall_mm': info['mean_annual_mm'],
        'data_sources': ','.join(info['data_sources']),
        'total_daily_records': info['total_records'],
        'date_start': info['date_range']['start'],
        'date_end': info['date_range']['end'],
        'has_netcdf_2025': 'netcdf_grid_derived' in info['data_sources'],
        'has_imd_observation_2026': 'imd_district_observation' in info['data_sources']
    })

coverage_df = pd.DataFrame(coverage_rows)
coverage_df.to_csv('rainfall_data_coverage.csv', index=False)
print(f"Saved rainfall_data_coverage.csv: {len(coverage_df)} districts")

# ============================================================
# 8. UPDATE METADATA FILES
# ============================================================
print("\nUpdating dataset_source_manifest.json...")

# Load existing manifest
with open('dataset_source_manifest.json', 'r') as f:
    manifest = json.load(f)

# Update rainfall_data section
manifest['rainfall_data'] = {
    "source": "MIXED - IMD district-wise daily observations (2026) + IMD gridded NetCDF (2025) aggregated to districts",
    "csv_source_file": "rainfall_districtwise_daily_imd.csv (IMD district-wise daily, 2026-08-19 to 2026-11-06)",
    "netcdf_source_file": "RF25_ind2025_rfp25.nc (IMD gridded 0.25deg, 2025 full year)",
    "netcdf_incomplete_file": "RF25_indselect_rfp25.nc (0 KB, incomplete, NOT processed)",
    "csv_date_range": "2026-08-19 to 2026-11-06",
    "netcdf_date_range": "2025-01-01 to 2025-12-31",
    "csv_original_districts": 728,
    "csv_matched_districts": 437,
    "netcdf_derived_districts": 641,
    "combined_districts": 641,
    "csv_original_records": 57465,
    "csv_matched_records": 34523,
    "netcdf_derived_records": 233965,
    "combined_records": 268488,
    "spatial_resolution_netcdf": "0.25 x 0.25 degrees",
    "rainfall_units": "mm",
    "aggregation_method": "Spatial average of grid cells intersecting district polygon",
    "coordinate_system": "EPSG:4326 (WGS84)",
    "data_availability": "PARTIAL - 2025 (gridded, all 641 districts), 2026 partial (observations, 437 districts, Aug-Nov only)",
    "notes": "CSV contains 2026 monsoon season only (Aug-Nov). NetCDF contains full 2025. No overlap in years. Historical 2021-2024 still missing. 291 CSV districts could not be matched to canonical registry due to naming differences."
}

# Update master_dataset info
manifest['master_dataset'] = {
    "total_rows": manifest['master_dataset']['total_rows'],
    "unique_districts": manifest['master_dataset']['unique_districts'],
    "unique_crops": manifest['master_dataset']['unique_crops'],
    "year_range": manifest['master_dataset']['year_range'],
    "records_with_actual_soil": manifest['master_dataset']['records_with_actual_soil'],
    "records_with_estimated_soil": manifest['master_dataset']['records_with_estimated_soil'],
    "records_missing_soil": manifest['master_dataset']['records_missing_soil'],
    "data_sources": {
        "rainfall": "mixed_imd_observation_2026_netcdf_grid_2025",
        "production": manifest['master_dataset']['data_sources']['production'],
        "yield": manifest['master_dataset']['data_sources']['yield']
    },
    "rainfall_coverage": {
        "2025": "gridded_all_641_districts",
        "2026": "observations_437_districts_partial_monsoon_only"
    }
}

with open('dataset_source_manifest.json', 'w') as f:
    json.dump(manifest, f, indent=2)
print("Updated dataset_source_manifest.json")

# Save coverage_df for next part
coverage_df.to_pickle('temp_coverage_df.pkl')
print("Saved temp_coverage_df.pkl")