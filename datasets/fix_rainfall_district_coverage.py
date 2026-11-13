import pandas as pd
import numpy as np

# TASK 6: Investigate why IMD gridded rainfall coverage changed from 641 to 631 districts
# The grid map has 641 districts, but temp_annual.pkl has 631 unique district_name values
# This is because 10 districts share names across states (e.g., Aurangabad in Bihar and Maharashtra)

df = pd.read_pickle('temp_annual.pkl')

# The issue: district_name alone is not unique - need district_name + state_name
print("District name duplicates across states:")
district_counts = df.groupby('district_name')['state_name'].nunique()
multi_state = district_counts[district_counts > 1]
print(multi_state)

# The real unique count is district-state pairs
print(f"\nUnique district-state pairs: {df.drop_duplicates(subset=['district_name', 'state_name']).shape[0]}")
print(f"Unique district_name values: {df['district_name'].nunique()}")

# So the coverage IS 641 districts (by district-state pair)
# The 631 is just unique district_name strings, not unique districts
# This is NOT a data loss - it's a naming collision

# Let's verify by checking the grid map
import pickle
with open('temp_district_grid_map.pkl', 'rb') as f:
    dgm = pickle.load(f)
print(f"\nGrid map districts (canonical keys): {len(dgm)}")

# The canonical keys include state, so they are unique
# The problem is in step3_combine_and_generate.py where it maps back to original names
# Let's check what names are in the grid map vs what comes out

# Load the districts used for mapping
districts = pd.read_pickle('temp_districts.pkl')
print(f"Districts pickle shape: {districts.shape}")
print(f"Columns: {districts.columns.tolist()}")
print(districts[['canonical_key', 'district_name', 'state_name']].head(10))

# The grid map has 641 canonical keys, each with state
# But when mapped back, if two canonical keys map to same district_name but different states,
# the district_name count drops

# Check for canonical keys that have same district_name but different state_name
name_state = districts[['district_name', 'state_name']].drop_duplicates()
print(f"\nUnique district-state in GeoJSON: {len(name_state)}")

# Find duplicates in district_name
dup_names = name_state[name_state.duplicated(subset=['district_name'], keep=False)]
print(f"\nDuplicate district names across states:")
print(dup_names.sort_values('district_name'))