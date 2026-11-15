with open('build_geospatial_and_master.py', 'r') as f:
    content = f.read()

idx = content.find('Rainfall has DISTRICT')
before = content[:idx-50]
after = content[idx+600:]

new_section = """# Note: IMD rainfall data (2021-2026) does NOT overlap with ICRISAT crop data (1978-2017)
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

new_content = before + new_section + after

with open('build_geospatial_and_master.py', 'w') as f:
    f.write(new_content)

print('Fixed')