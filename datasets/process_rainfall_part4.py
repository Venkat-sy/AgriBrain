import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 4. LOAD AND PROCESS CSV (2026 DISTRICT-WISE DAILY)
# ============================================================
print("Loading CSV (2026 district-wise daily)...")
csv_df = pd.read_csv('rainfall_districtwise_daily_imd.csv')
print(f"CSV shape: {csv_df.shape}")
print(f"Date range: {csv_df['Date'].min()} to {csv_df['Date'].max()}")

# Clean column names
csv_df.columns = csv_df.columns.str.strip().str.replace('\n', '').str.replace('\r', '')

# Create canonical key for CSV
csv_df['State_clean'] = csv_df['State'].str.strip().str.upper()
csv_df['District_clean'] = csv_df['District'].str.strip().str.upper()
csv_df['canonical_key'] = csv_df['District_clean'] + '_' + csv_df['State_clean']

# Parse date
csv_df['date'] = pd.to_datetime(csv_df['Date'])

# Select relevant columns
csv_processed = csv_df[['canonical_key', 'date', 'Daily Actual']].copy()
csv_processed.columns = ['canonical_key', 'date', 'rainfall_mm']
csv_processed['source'] = 'imd_district_observation'
csv_processed['rainfall_mm'] = pd.to_numeric(csv_processed['rainfall_mm'], errors='coerce')

# Remove rows with missing rainfall
csv_processed = csv_processed.dropna(subset=['rainfall_mm'])
print(f"CSV processed records: {len(csv_processed)}")
print(f"Districts covered: {csv_processed['canonical_key'].nunique()}")
print(f"Date range: {csv_processed['date'].min()} to {csv_processed['date'].max()}")

# Save for next part
csv_processed.to_pickle('temp_csv_processed.pkl')
print("Saved temp_csv_processed.pkl")