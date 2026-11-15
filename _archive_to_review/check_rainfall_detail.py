import pandas as pd

df = pd.read_pickle('temp_annual.pkl')
print(f'Total records: {len(df)}')
print(f'Unique district_name: {df["district_name"].nunique()}')
print(f'Unique state_name: {df["state_name"].nunique()}')
print(f'Unique district-state pairs: {df.drop_duplicates(subset=["district_name", "state_name"]).shape[0]}')
print(f'Years: {sorted(df["year"].unique())}')

for year in sorted(df["year"].unique()):
    year_df = df[df["year"] == year]
    print(f'  {year}: {len(year_df)} records, {year_df["district_name"].nunique()} districts')

# Check for duplicate district names across states
district_counts = df.groupby('district_name')['state_name'].nunique()
multi_state = district_counts[district_counts > 1]
print(f'\nDistricts appearing in multiple states: {len(multi_state)}')
for d, cnt in multi_state.items():
    states = df[df['district_name'] == d]['state_name'].unique()
    print(f'  {d}: {list(states)}')

# Check 2026 data
df_2026 = df[df["year"] == 2026]
print(f'\n2026 records: {len(df_2026)}')
print(f'2026 districts: {df_2026["district_name"].nunique()}')
print(f'2026 states: {df_2026["state_name"].nunique()}')