import os

files = ['rainfall_districtwise_daily_imd.csv', 'RF25_indselect_rfp25.nc', 'RF25_ind2025_rfp25.nc']
for f in files:
    size = os.path.getsize(f)
    print(f'{f}: {size} bytes ({size/1024/1024:.2f} MB)')