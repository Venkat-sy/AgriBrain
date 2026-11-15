import pandas as pd
master = pd.read_pickle('master_agri_dataset_v2.pkl')
print(master.columns.tolist())
print()
print([c for c in master.columns if 'source' in c.lower()])