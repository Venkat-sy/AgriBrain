import pandas as pd
import numpy as np
import json
import pickle
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 5. RECONCILE CSV DISTRICTS AGAINST CANONICAL REGISTRY
# ============================================================
print("Reconciling CSV districts against canonical registry...")

# Load canonical districts
districts = pd.read_pickle('temp_districts.pkl')
canonical_keys = set(districts['canonical_key'].unique())

# Load CSV processed
csv_processed = pd.read_pickle('temp_csv_processed.pkl')
csv_keys = set(csv_processed['canonical_key'].unique())

matched = csv_keys & canonical_keys
unmatched_csv = csv_keys - canonical_keys
unmatched_canonical = canonical_keys - csv_keys

print(f"Canonical districts: {len(canonical_keys)}")
print(f"CSV districts: {len(csv_keys)}")
print(f"Matched: {len(matched)}")
print(f"CSV-only (unmatched): {len(unmatched_csv)}")
print(f"Canonical-only (missing from CSV): {len(unmatched_canonical)}")

if unmatched_csv:
    print(f"\nSample unmatched CSV keys: {sorted(list(unmatched_csv))[:20]}")

# Keep only matched records from CSV
csv_matched = csv_processed[csv_processed['canonical_key'].isin(matched)].copy()
print(f"\nCSV matched records: {len(csv_matched)}")
print(f"CSV matched districts: {csv_matched['canonical_key'].nunique()}")

# Save for next part
csv_matched.to_pickle('temp_csv_matched.pkl')
with open('temp_matched_keys.json', 'w') as f:
    json.dump(list(matched), f)
print("Saved temp_csv_matched.pkl and temp_matched_keys.json")