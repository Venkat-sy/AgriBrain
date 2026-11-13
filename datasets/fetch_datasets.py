#!/usr/bin/env python
"""
Download open-source Indian District Rainfall and Crop Production datasets
into datasets/raw/.
"""
import os
import requests
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(exist_ok=True)

# Open-source dataset URLs for Indian agricultural data
RAINFALL_URLS = {
    "rainfall_district_annual.csv": "https://raw.githubusercontent.com/rohan-paul/MachineLearning-DeepLearning-Code-for-my-YouTube-Channel/master/Indian_Agriculture_Dataset/rainfall_in_india_1901-2015.csv",
    "crop_production_district.csv": "https://raw.githubusercontent.com/rohan-paul/MachineLearning-DeepLearning-Code-for-my-YouTube-Channel/master/Indian_Agriculture_Dataset/crop_production.csv",
    "crop_yield_district.csv": "https://raw.githubusercontent.com/rohan-paul/MachineLearning-DeepLearning-Code-for-my-YouTube-Channel/master/Indian_Agriculture_Dataset/crop_yield.csv",
}

def download_file(url, output_path):
    """Download a file from URL."""
    try:
        print(f"Downloading {url}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Saved to {output_path} ({len(response.content)} bytes)")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def create_sample_rainfall_csv():
    """Create a sample rainfall CSV for our 10 districts if downloads fail."""
    import numpy as np
    
    districts = [
        "Ludhiana", "Karnal", "Coimbatore", "Nashik", "East Godavari",
        "Guntur", "Ahmednagar", "Sangli", "Belgaum", "Mysore"
    ]
    
    states = {
        "Ludhiana": "Punjab", "Karnal": "Haryana", "Coimbatore": "Tamil Nadu",
        "Nashik": "Maharashtra", "East Godavari": "Andhra Pradesh",
        "Guntur": "Andhra Pradesh", "Ahmednagar": "Maharashtra",
        "Sangli": "Maharashtra", "Belgaum": "Karnataka", "Mysore": "Karnataka"
    }
    
    np.random.seed(42)
    rows = []
    
    for district in districts:
        state = states[district]
        if state in ["Punjab", "Haryana"]:
            base_rainfall = 600
        elif state == "Tamil Nadu":
            base_rainfall = 800
        elif state == "Maharashtra":
            base_rainfall = 900
        elif state == "Andhra Pradesh":
            base_rainfall = 1000
        elif state == "Karnataka":
            base_rainfall = 1100
        else:
            base_rainfall = 800
        
        for year in range(2000, 2020):
            rainfall = base_rainfall + np.random.normal(0, 150) + (year - 2000) * 2
            rainfall = max(200, min(2000, rainfall))
            
            rows.append({
                "DISTRICT": district,
                "STATE": state,
                "YEAR": year,
                "ANNUAL_RAINFALL_mm": round(rainfall, 1)
            })
    
    df = pd.DataFrame(rows)
    output_path = RAW_DIR / "rainfall_district_annual.csv"
    df.to_csv(output_path, index=False)
    print(f"Created sample rainfall data: {output_path} ({len(df)} rows)")
    return output_path

def create_sample_crop_production_csv():
    """Create a sample crop production CSV for our 10 districts."""
    import numpy as np
    
    districts = [
        "Ludhiana", "Karnal", "Coimbatore", "Nashik", "East Godavari",
        "Guntur", "Ahmednagar", "Sangli", "Belgaum", "Mysore"
    ]
    
    crops = ["Rice", "Wheat", "Maize", "Cotton", "Soybean", "Groundnut", "Sugarcane", "Chickpea"]
    
    states = {
        "Ludhiana": "Punjab", "Karnal": "Haryana", "Coimbatore": "Tamil Nadu",
        "Nashik": "Maharashtra", "East Godavari": "Andhra Pradesh",
        "Guntur": "Andhra Pradesh", "Ahmednagar": "Maharashtra",
        "Sangli": "Maharashtra", "Belgaum": "Karnataka", "Mysore": "Karnataka"
    }
    
    crop_suitability = {
        "Punjab": {"Rice": 1.0, "Wheat": 1.0, "Maize": 0.7, "Cotton": 0.8, "Soybean": 0.3, "Groundnut": 0.2, "Sugarcane": 0.5, "Chickpea": 0.6},
        "Haryana": {"Rice": 0.9, "Wheat": 1.0, "Maize": 0.7, "Cotton": 0.8, "Soybean": 0.3, "Groundnut": 0.2, "Sugarcane": 0.5, "Chickpea": 0.6},
        "Tamil Nadu": {"Rice": 1.0, "Wheat": 0.1, "Maize": 0.8, "Cotton": 0.7, "Soybean": 0.5, "Groundnut": 0.9, "Sugarcane": 0.8, "Chickpea": 0.4},
        "Maharashtra": {"Rice": 0.6, "Wheat": 0.4, "Maize": 0.9, "Cotton": 1.0, "Soybean": 1.0, "Groundnut": 0.8, "Sugarcane": 0.9, "Chickpea": 0.8},
        "Andhra Pradesh": {"Rice": 1.0, "Wheat": 0.1, "Maize": 0.8, "Cotton": 0.8, "Soybean": 0.6, "Groundnut": 0.9, "Sugarcane": 0.8, "Chickpea": 0.5},
        "Karnataka": {"Rice": 0.8, "Wheat": 0.3, "Maize": 0.9, "Cotton": 0.8, "Soybean": 0.9, "Groundnut": 0.8, "Sugarcane": 0.9, "Chickpea": 0.7},
    }
    
    np.random.seed(42)
    rows = []
    
    for district in districts:
        state = states[district]
        suitability = crop_suitability.get(state, {c: 0.5 for c in crops})
        
        for crop in crops:
            for year in range(2000, 2020):
                base_yields = {
                    "Rice": 4.0, "Wheat": 3.5, "Maize": 5.0, "Cotton": 0.5,
                    "Soybean": 1.2, "Groundnut": 1.5, "Sugarcane": 70.0, "Chickpea": 1.0
                }
                
                base = base_yields.get(crop, 2.0)
                suit = suitability.get(crop, 0.5)
                
                yield_val = base * suit * (0.8 + np.random.random() * 0.4)
                area = np.random.uniform(10000, 200000)
                production = yield_val * area / 1000
                
                rows.append({
                    "DISTRICT": district,
                    "STATE": state,
                    "CROP": crop,
                    "YEAR": year,
                    "AREA_HA": round(area),
                    "PRODUCTION_TONNES": round(production, 1),
                    "YIELD_TONNES_PER_HA": round(yield_val, 3)
                })
    
    df = pd.DataFrame(rows)
    output_path = RAW_DIR / "crop_production_district.csv"
    df.to_csv(output_path, index=False)
    print(f"Created sample crop production data: {output_path} ({len(df)} rows)")
    return output_path

def create_sample_crop_yield_csv():
    """Create a sample crop yield CSV (similar to production but focused on yield)."""
    import numpy as np
    
    districts = [
        "Ludhiana", "Karnal", "Coimbatore", "Nashik", "East Godavari",
        "Guntur", "Ahmednagar", "Sangli", "Belgaum", "Mysore"
    ]
    
    crops = ["Rice", "Wheat", "Maize", "Cotton", "Soybean", "Groundnut", "Sugarcane", "Chickpea"]
    
    states = {
        "Ludhiana": "Punjab", "Karnal": "Haryana", "Coimbatore": "Tamil Nadu",
        "Nashik": "Maharashtra", "East Godavari": "Andhra Pradesh",
        "Guntur": "Andhra Pradesh", "Ahmednagar": "Maharashtra",
        "Sangli": "Maharashtra", "Belgaum": "Karnataka", "Mysore": "Karnataka"
    }
    
    np.random.seed(42)
    rows = []
    
    for district in districts:
        state = states[district]
        
        for crop in crops:
            for year in range(2000, 2020):
                base_yields = {
                    "Rice": 4.0, "Wheat": 3.5, "Maize": 5.0, "Cotton": 0.5,
                    "Soybean": 1.2, "Groundnut": 1.5, "Sugarcane": 70.0, "Chickpea": 1.0
                }
                
                base = base_yields.get(crop, 2.0)
                yield_val = base * (0.7 + np.random.random() * 0.6)
                
                rows.append({
                    "DISTRICT": district,
                    "STATE": state,
                    "CROP": crop,
                    "YEAR": year,
                    "YIELD_TONNES_PER_HA": round(yield_val, 3)
                })
    
    df = pd.DataFrame(rows)
    output_path = RAW_DIR / "crop_yield_district.csv"
    df.to_csv(output_path, index=False)
    print(f"Created sample crop yield data: {output_path} ({len(df)} rows)")
    return output_path

def main():
    print("Attempting to download open-source datasets...")
    
    success_count = 0
    for filename, url in RAINFALL_URLS.items():
        if download_file(url, RAW_DIR / filename):
            success_count += 1
    
    # If downloads fail, create synthetic data
    if success_count == 0:
        print("Downloads failed, creating synthetic datasets...")
        create_sample_rainfall_csv()
        create_sample_crop_production_csv()
        create_sample_crop_yield_csv()
    
    print("\nVerifying raw data files:")
    for file in RAW_DIR.glob("*.csv"):
        df = pd.read_csv(file)
        print(f"  {file.name}: {len(df)} rows, columns: {list(df.columns)}")

if __name__ == "__main__":
    main()