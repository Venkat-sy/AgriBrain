import pandas as pd

df = pd.read_csv('rainfall_districtwise_daily_imd.csv')
print("Shape:", df.shape)
print("\nDate range:", df['Date'].min(), "to", df['Date'].max())
print("\nUnique states:", df['State'].nunique())
print("\nUnique districts:", df['District'].nunique())
print("\nStates:", sorted(df['State'].unique()))
print("\nDistricts:", sorted(df['District'].unique()))
print("\nMissing values:")
print(df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())
print("\nSample of Daily Actual stats:")
print(df['Daily Actual'].describe())