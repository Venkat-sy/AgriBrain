import pandas as pd

df = pd.read_csv('ICRISAT-District Level Data.csv')
print(f'Records: {len(df)}')
print(f'Columns: {len(df.columns)}')
print(f'Years: {sorted(df["Year"].unique())}')
print(f'Year range: {df["Year"].min()}-{df["Year"].max()}')
print(f'States: {df["State Name"].nunique()}')
print(f'Districts: {df["Dist Name"].nunique()}')
print(f'Crops in columns: {[c for c in df.columns if "AREA" in c]}')
print()
print('State/District sample:')
print(df[['State Name', 'Dist Name', 'Year']].head(20).to_string())