with open('build_geospatial_and_master.py', 'r') as f:
    lines = f.readlines()

# Remove lines 6-10 (0-indexed: 5-9) which are the duplicate problematic lines
# Line 6: '    # Add crop agronomy features   # Rename the rainfall column to match expected lowercase name\n'
# Line 7: "    merged = merged.rename(columns={'ANNUAL_RAINFALL_mm': 'annual_rainfall_mm'})\n"
# Line 8: '    print(f"   After rainfall merge: {len(merged)}")\n'
# Line 9: '    print(f"   Rainfall coverage: {merged[\\'annual_rainfall_mm\\'].notna().sum()} records")\n'
# Line 10: '    print(f"   Rainfall sources: {merged[\\'data_source\\'].dropna().unique()}")\n'

# Keep line 5 (blank line), remove lines 6-10, keep line 11 (blank line), keep line 12 onwards
new_lines = lines[:6] + lines[11:]

with open('build_geospatial_and_master.py', 'w') as f:
    f.writelines(new_lines)

print('Fixed - removed lines 6-10')