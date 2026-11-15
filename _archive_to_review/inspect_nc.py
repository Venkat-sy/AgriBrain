import xarray as xr

ds = xr.open_dataset('RF25_ind2025_rfp25.nc')
print("Dataset:")
print(ds)
print("\nDimensions:", dict(ds.dims))
print("\nVariables:", list(ds.data_vars))
print("\nCoordinates:", list(ds.coords))
print("\nCRS:", ds.attrs.get('crs', 'Not found'))
for var in ds.data_vars:
    print(f"\n{var}:")
    print(f"  Shape: {ds[var].shape}")
    print(f"  Dims: {ds[var].dims}")
    print(f"  Units: {ds[var].attrs.get('units', 'Not found')}")
    print(f"  Long name: {ds[var].attrs.get('long_name', 'Not found')}")

# Check time dimension
if 'time' in ds.coords:
    print("\nTime range:", ds['time'].min().values, "to", ds['time'].max().values)
    print("Number of time steps:", len(ds['time']))