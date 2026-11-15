with open('build_geospatial_and_master.py', 'r') as f:
    lines = f.readlines()

# Find and remove the problematic block (lines 3-7 in the 0-indexed view above)
# Which corresponds to lines 247-251 in 1-indexed
# Keep lines up to line 247 (index 246), skip 248-252, keep from 253 onwards

# Line 247 (index 246): '    # Add crop agronomy features   # Rename the rainfall column to match expected lowercase name\n'
# Line 248 (index 247): "    merged = merged.rename(columns={'ANNUAL_RAINFALL_mm': 'annual_rainfall_mm'})\n"
# Line 249 (index 248): '    print(f"   After rainfall merge: {len(merged)}")\n'
# Line 250 (index 249): '    print(f"   Rainfall coverage: {merged[\'annual_rainfall_mm\'].notna().sum()} records")\n'
# Line 251 (index 250): '    print(f"   Rainfall sources: {merged[\'data_source\'].dropna().unique()}")\n'
# Line 252 (index 251): '    \n'
# Line 253 (index 252): '    # Add crop agronomy features\n'

# Keep 0-246 (up to and including rainfall_data_source line), skip 247-251, keep 252 onwards
new_lines = lines[:247] + lines[252:]

with open('build_geospatial_and_master.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed - removed duplicate lines')