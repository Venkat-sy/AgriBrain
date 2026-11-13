import xarray as xr

ds = xr.open_dataset('RF25_ind2021_rfp25.nc')
print(ds)
print('\nRainfall shape:', ds['RAINFALL'].shape)
print('Time:', ds['TIME'].values[:5])
print('LAT:', ds['LAT'].values[:5])
print('LON:', ds['LON'].values[:5])
print('LAT range:', ds['LAT'].min().values, 'to', ds['LAT'].max().values)
print('LON range:', ds['LON'].min().values, 'to', ds['LON'].max().values)