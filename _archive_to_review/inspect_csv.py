import pandas as pd

df = pd.read_csv('rainfall_districtwise_daily_imd.csv', nrows=5)
print("Columns:", list(df.columns))
print("\nFirst 5 rows:")
print(df.to_string())
print("\nShape:", df.shape)
print("\nDtypes:")
print(df.dtypes)