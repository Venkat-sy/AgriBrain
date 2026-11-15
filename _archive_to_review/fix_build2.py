with open('build_geospatial_and_master.py', 'r') as f:
    content = f.read()

old = """# Merge with rainfall
    print("\\n6. Merging with rainfall data...")
    # Rainfall has DISTRICT, STATE, YEAR (after rename)
    # Need to match on district, state, year
    print(f"   DEBUG: Rainfall columns before merge: {rainfall.columns.tolist()}")
    print(f"   DEBUG: Rainfall shape: {rainfall.shape}")
    rainfall_subset = rainfall[['DISTRICT', 'STATE', 'YEAR', 'ANNUAL_RAINFALL_mm', 'data_source']]
    print(f"   DEBUG: Rainfall subset shape: {rainfall_subset.shape}")
    merged = pd.merge(
        merged,
        rainfall_subset,
        left_on=['district_name', 'state_name', 'year'],
        right_on=['DISTRICT', 'STATE', 'YEAR'],
        how='left'
    )
    # Rename the rainfall column to match expected lowercase name
    merged = merged.rename(columns={'ANNUAL_RAINFALL_mm': 'annual_rainfall_mm'})
    print(f"   After rainfall merge: {len(merged)}")
    print(f"   Rainfall coverage: {merged['annual_rainfall_mm'].notna().sum()} records")
    print(f"   Rainfall sources: {merged['data_source'].dropna().unique()}")

    # Add crop agronomy features"""

new = """# Note: IMD rainfall data (2021-2026) does NOT overlap with ICRISAT crop data (1978-2017)
    # So we cannot merge by year. Instead, we keep rainfall data as a separate reference
    # and set annual_rainfall_mm to NaN (will be populated when we have overlapping years)
    print("\\n6. Rainfall data note:")
    print("   IMD rainfall data covers 2021-2026 (NetCDF 2021-2025 + obs 2026)")
    print("   ICRISAT crop data covers 1978-2017")
    print("   No year overlap - rainfall will be NaN in master dataset")
    print("   Rainfall data available separately in district_rainfall_history.csv")
    
    # Add placeholder annual_rainfall_mm column (will be NaN due to no year overlap)
    import numpy as np
    merged['annual_rainfall_mm'] = np.nan
    merged['rainfall_data_source'] = 'netcdf_grid_derived (2021-2025), imd_district_observation (2026)'

    # Add crop agronomy features"""

content = content.replace(old, new)

with open('build_geospatial_and_master.py', 'w') as f:
    f.write(content)

print('Replaced')