import pandas as pd
import numpy as np
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 6. COMBINE NETCDF AND CSV (NO DOUBLE COUNTING)
# ============================================================
print("Combining NetCDF and CSV data...")

nc_df = pd.read_pickle('temp_nc_df.pkl')
csv_matched = pd.read_pickle('temp_csv_matched.pkl')

print(f"NetCDF records: {len(nc_df)}")
print(f"CSV matched records: {len(csv_matched)}")

# NetCDF covers 2025, CSV covers 2026 (Aug-Nov)
# They don't overlap in time, so no double-counting issue
combined = pd.concat([nc_df, csv_matched], ignore_index=True)
print(f"Combined records: {len(combined)}")
print(f"Districts: {combined['canonical_key'].nunique()}")
print(f"Date range: {combined['date'].min()} to {combined['date'].max()}")
print(f"Sources:\n{combined['source'].value_counts()}")

# Save combined
combined.to_pickle('temp_combined.pkl')
print("Saved temp_combined.pkl")