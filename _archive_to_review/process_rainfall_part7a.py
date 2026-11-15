import pandas as pd
import numpy as np
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 7. GENERATE OUTPUT FILES
# ============================================================
print("Generating output files...")

# Load data
combined = pd.read_pickle('temp_combined.pkl')
districts = pd.read_pickle('temp_districts.pkl')

# Map canonical key to original names
name_col = 'district_name'
state_col = 'state_name'
key_to_names = {}
for _, row in districts.iterrows():
    key_to_names[row['canonical_key']] = {
        'district': row[name_col],
        'state': row[state_col]
    }

# Add year column
combined['year'] = combined['date'].dt.year

# Map back to original district/state names
combined['district_name'] = combined['canonical_key'].map(lambda k: key_to_names.get(k, {}).get('district', k.split('_')[0] if '_' in k else k))
combined['state_name'] = combined['canonical_key'].map(lambda k: key_to_names.get(k, {}).get('state', k.split('_')[1] if '_' in k else ''))

# 7a. district_rainfall_history.csv
print("\nGenerating district_rainfall_history.csv...")
annual = combined.groupby(['district_name', 'state_name', 'year', 'source'])['rainfall_mm'].sum().reset_index()
annual.columns = ['district_name', 'state_name', 'year', 'source', 'annual_rainfall_mm']
annual.to_csv('district_rainfall_history.csv', index=False)
print(f"Saved district_rainfall_history.csv: {len(annual)} records")

# 7b. district_rainfall_summary.json
print("\nGenerating district_rainfall_summary.json...")
summary = {}
for key in combined['canonical_key'].unique():
    district_data = combined[combined['canonical_key'] == key]
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

# Save summary for next part
with open('temp_summary.json', 'w') as f:
    json.dump(summary, f)
print("Saved temp_summary.json")

# Save annual for next part
annual.to_pickle('temp_annual.pkl')
print("Saved temp_annual.pkl")