import pandas as pd

df = pd.read_csv('ICRISAT-District Level Data.csv')

print('Target years 2019-2023:')
target = [2019, 2020, 2021, 2022, 2023]
for y in target:
    c = len(df[df['Year'] == y])
    print(f'  {y}: {c} records')

print()
print('Latest 5 years in data:')
latest = sorted(df['Year'].unique())[-5:]
print(latest)

print()
print('Crop columns detail:')
area_cols = [c for c in df.columns if 'AREA' in c]
for c in area_cols:
    print(f'  {c}')

# Check columns for target crops
print()
target_crops = ['RICE', 'WHEAT', 'MAIZE', 'SORGHUM', 'PEARL MILLET', 'FINGER MILLET', 'BARLEY', 
                'CHICKPEA', 'PIGEONPEA', 'GROUNDNUT', 'SOYABEAN', 'SESAMUM', 'RAPESEED AND MUSTARD',
                'SUNFLOWER', 'SAFFLOWER', 'COTTON', 'SUGARCANE']
for crop in target_crops:
    matching = [c for c in df.columns if crop in c]
    print(f'{crop}: {matching}')