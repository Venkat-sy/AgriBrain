#!/usr/bin/env python
"""
Download India districts shapefile from DataMeet/maps (open-source)
and convert to GeoJSON with standardized property keys (district_name, state_name).
"""
import json
import requests
import zipfile
import io
from pathlib import Path
import geopandas as gpd

# DataMeet/maps Census 2011 Districts shapefile URL
SHAPEFILE_URL = "https://github.com/datameet/maps/raw/master/Districts/Census_2011/2011_Dist.zip"
OUTPUT_PATH = Path(__file__).parent / "india_districts.geojson"

def download_and_convert():
    print(f"Downloading India districts shapefile from {SHAPEFILE_URL}...")
    response = requests.get(SHAPEFILE_URL, timeout=60)
    response.raise_for_status()
    
    # Extract shapefile from zip
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Extract to a temporary directory
        temp_dir = Path(__file__).parent / "temp_shapefile"
        temp_dir.mkdir(exist_ok=True)
        z.extractall(temp_dir)
        
        # Find the .shp file
        shp_files = list(temp_dir.glob("*.shp"))
        if not shp_files:
            raise FileNotFoundError("No .shp file found in the zip")
        
        shp_path = shp_files[0]
        print(f"Found shapefile: {shp_path}")
        
        # Read with geopandas
        gdf = gpd.read_file(shp_path)
        print(f"Loaded {len(gdf)} districts")
        print(f"Columns: {list(gdf.columns)}")
        print(f"Sample rows:\n{gdf.head()}")
        
        # Standardize property keys to district_name and state_name
        # Check column names for district and state
        district_col = None
        state_col = None
        
        for col in gdf.columns:
            col_lower = col.lower()
            if 'dist' in col_lower and 'name' in col_lower:
                district_col = col
            elif 'state' in col_lower and 'name' in col_lower:
                state_col = col
            elif col_lower in ['district', 'dist_name', 'dtname']:
                district_col = col
            elif col_lower in ['state', 'statename', 'st_nm']:
                state_col = col
        
        print(f"District column: {district_col}, State column: {state_col}")
        
        # Create standardized columns
        gdf['district_name'] = gdf[district_col] if district_col else ''
        gdf['state_name'] = gdf[state_col] if state_col else ''
        
        # Clean up names
        gdf['district_name'] = gdf['district_name'].astype(str).str.strip()
        gdf['state_name'] = gdf['state_name'].astype(str).str.strip()
        
        # Keep only essential columns + geometry
        output_gdf = gdf[['district_name', 'state_name', 'geometry']].copy()
        
        # Save as GeoJSON
        output_gdf.to_file(OUTPUT_PATH, driver='GeoJSON')
        print(f"Saved standardized GeoJSON to {OUTPUT_PATH}")
        
        # Extract canonical district names
        district_names = output_gdf['district_name'].tolist()
        print(f"Found {len(district_names)} districts with names")
        print(f"Sample district names: {district_names[:10]}")
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir)
        
        return district_names

if __name__ == "__main__":
    download_and_convert()