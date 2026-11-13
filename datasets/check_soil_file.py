import pandas as pd
df = pd.read_csv('processed/soil_features_district.csv')
print(df.shape)
print(df.columns.tolist())
print(df.head())