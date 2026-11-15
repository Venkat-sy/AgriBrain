import pandas as pd
import numpy as np
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# STEP 3: Combine all years and generate output files
# ============================================================

# Load existing combined data (2025 + 2026)
existing_combined = pd.read_pickle('temp_combined.pkl')
print(f"Existing combined records (2025+2026): {len(existing_combined)}")

# Load all new year data
with open('temp_all_year_dfs.pkl', 'rb') as f:
    all_year_dfs = pickle.load(f)

# Combine all new years
new_combined = pd.concat(all_year_dfs, ignore_index=True)
print(f"New records (2021-2024): {len(new_combined)}")

# Full combined
full_combined = pd.concat([new_combined, existing_combined], ignore_index=True)
print(f"Full combined records: {len(full_combined)}")
print(f"Districts: {full_combined['canonical_key'].nunique()}")
print(f"Date range: {full_combined['date'].min()} to {full_combined['date'].max()}")
print(f"Years: {sorted(full_combined['year'].unique())}")
print(f"Sources:\n{full_combined['source'].value_counts()}")

# Save full combined
full_combined.to_pickle('temp_combined_full.pkl')
print("Saved temp_combined_full.pkl")

# Load districts for name mapping
districts = pd.read_pickle('temp_districts.pkl')
name_col = 'district_name'
state_col = 'state_name'

# Map canonical key to original names
key_to_names = {}
for _, row in districts.iterrows():
    key_to_names[row['canonical_key']] = {
        'district': row[name_col],
        'state': row[state_col]
    }

# Add year column
full_combined['year'] = full_combined['date'].dt.year

# Map back to original district/state names
full_combined['district_name'] = full_combined['canonical_key'].map(
    lambda k: key_to_names.get(k, {}).get('district', k.split('_')[0] if '_' in k else k))
full_combined['state_name'] = full_combined['canonical_key'].map(
    lambda k: key_to_names.get(k, {}).get('state', k.split('_')[1] if '_' in k else ''))

# 1. district_rainfall_history.csv
print("\nGenerating district_rainfall_history.csv...")
annual = full_combined.groupby(['district_name', 'state_name', 'year', 'source'])['rainfall_mm'].sum().reset_index()
annual.columns = ['district_name', 'state_name', 'year', 'source', 'annual_rainfall_mm']
annual.to_csv('district_rainfall_history.csv', index=False)
print(f"Saved district_rainfall_history.csv: {len(annual)} records")

# 2. district_rainfall_summary.json
print("\nGenerating district_rainfall_summary.json...")
summary = {}
for key in full_combined['canonical_key'].unique():
    district_data = full_combined[full_combined['canonical_key'] == key]
    years = district_data['year'].unique()
    annual_totals = district_data.groupby('year')['rainfall_mm'].sum()
    
    info = key_to_names.get(key, {'district': key.split('_')[0], 'state': key.split('_')[1] if '_' in key else ''})
    
    summary[key] = {
        'district_name': info['district'],
        'state_name': info['state'],
        'years_available': sorted([int(y) for y in years]),
        'annual_rainfall_mm': {int(y): float(annual_totals[y]) for y in annual_totals.index},
        'mean_annual_mm': float(annual_totals.mean()),
        'std_annual_mm': float(annual_totals.std()) if len(annual_totals) > 1 else 0.0,
        'min_annual_mm': float(annual_totals.min()),
        'max_annual_mm': float(annual_totals.max()),
        'data_sources': district_data['source'].unique().tolist(),
        'total_records': int(len(district_data)),
        'date_range': {
            'start': str(district_data['date'].min()),
            'end': str(district_data['date'].max())
        }
    }

with open('district_rainfall_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"Saved district_rainfall_summary.json: {len(summary)} districts")

# 3. rainfall_data_coverage.csv
print("\nGenerating rainfall_data_coverage.csv...")
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
        'has_netcdf_2021': 'netcdf_grid_derived' in info['data_sources'] and 2021 in info['years_available'],
        'has_netcdf_2022': 'netcdf_grid_derived' in info['data_sources'] and 2022 in info['years_available'],
        'has_netcdf_2023': 'netcdf_grid_derived' in info['data_sources'] and 2023 in info['years_available'],
        'has_netcdf_2024': 'netcdf_grid_derived' in info['data_sources'] and 2024 in info['years_available'],
        'has_netcdf_2025': 'netcdf_grid_derived' in info['data_sources'] and 2025 in info['years_available'],
        'has_imd_observation_2026': 'imd_district_observation' in info['data_sources']
    })

coverage_df = pd.DataFrame(coverage_rows)
coverage_df.to_csv('rainfall_data_coverage.csv', index=False)
print(f"Saved rainfall_data_coverage.csv: {len(coverage_df)} districts")

# Save annual and coverage for next step
annual.to_pickle('temp_annual.pkl')
coverage_df.to_pickle('temp_coverage_df.pkl')
print("Saved temp_annual.pkl and temp_coverage_df.pkl")