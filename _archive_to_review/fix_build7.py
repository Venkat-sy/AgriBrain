with open('build_geospatial_and_master.py', 'r') as f:
    content = f.read()

old = """    # Add placeholder annual_rainfall_mm column (will be NaN due to no year overlap)
    import numpy as np
    merged['annual_rainfall_mm'] = np.nan
    merged['rainfall_data_source'] = 'netcdf_grid_derived (2021-2025), imd_district_observation (2026)'

    # Add crop agronomy features   # Rename the rainfall column to match expected lowercase name
    merged = merged.rename(columns={'ANNUAL_RAINFALL_mm': 'annual_rainfall_mm'})
    print(f"   After rainfall merge: {len(merged)}")
    print(f"   Rainfall coverage: {merged['annual_rainfall_mm'].notna().sum()} records")
    print(f"   Rainfall sources: {merged['data_source'].dropna().unique()}")

    # Add crop agronomy features"""

new = """    # Add placeholder annual_rainfall_mm column (will be NaN due to no year overlap)
    import numpy as np
    merged['annual_rainfall_mm'] = np.nan
    merged['rainfall_data_source'] = 'netcdf_grid_derived (2021-2025), imd_district_observation (2026)'

    # Add crop agronomy features"""

content = content.replace(old, new)

with open('build_geospatial_and_master.py', 'w') as f:
    f.write(content)

print('Fixed')