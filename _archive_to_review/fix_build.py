with open('build_geospatial_and_master.py', 'r') as f:
    content = f.read()

# Fix the broken section
old_broken = """    #     # Rainfall columns already standardized in load_rainfall_data()
    # No need to rename again - keep DISTRICT, STATE, YEAR, ANNUAL_RAINFALL_mm for merging

    # Merge production and yieldRAINFALL_mm': 'annual_rainfall_mm'
    })


    # Merge production and yield"""

new_fixed = """    # Rainfall columns already standardized in load_rainfall_data()
    # No need to rename again - keep DISTRICT, STATE, YEAR, ANNUAL_RAINFALL_mm for merging

    # Merge production and yield"""

content = content.replace(old_broken, new_fixed)

with open('build_geospatial_and_master.py', 'w') as f:
    f.write(content)

print('Fixed')