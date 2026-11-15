"""
Dataset Downloader for AI-Driven Nutrient Recommendation System
================================================================
This script downloads all required datasets from Kaggle using kagglehub.
Each dataset is saved into its own subfolder within the datasets/ directory.

Datasets downloaded:
1. Crop Recommendation Dataset (atharvaingle)
2. Fertilizer Recommendation Dataset
3. Crop Production Statistics India
4. Rainfall in India (1901-2015)
5. Crop Yield Prediction Dataset
"""

import kagglehub
import shutil
import os

DATASETS_DIR = os.path.dirname(os.path.abspath(__file__))

# Define all datasets to download
DATASETS = [
    {
        "slug": "atharvaingle/crop-recommendation-dataset",
        "target_folder": "01_crop_recommendation",
        "description": "Crop Recommendation Dataset - NPK, pH, temperature, humidity, rainfall with crop labels"
    },
    {
        "slug": "gdabhishek/fertilizer-prediction",
        "target_folder": "02_fertilizer_recommendation",
        "description": "Fertilizer Prediction Dataset - soil type, crop type, NPK values with fertilizer labels"
    },
    {
        "slug": "abhinand05/crop-production-in-india",
        "target_folder": "03_crop_production_india",
        "description": "Crop Production in India - state/district-wise area, production, yield data"
    },
    {
        "slug": "rajanand/rainfall-in-india",
        "target_folder": "04_rainfall_india",
        "description": "Rainfall in India (1901-2015) - subdivision-wise monthly and annual rainfall"
    },
    {
        "slug": "akshatgupta7/crop-yield-in-indian-states-dataset",
        "target_folder": "05_crop_yield_prediction",
        "description": "Crop Yield in Indian States - crop, season, area, production, yield data"
    },
]


def download_dataset(slug, target_folder, description):
    """Download a single dataset from Kaggle and copy to target folder."""
    target_path = os.path.join(DATASETS_DIR, target_folder)
    
    print(f"\n{'='*70}")
    print(f"Downloading: {description}")
    print(f"  Kaggle slug: {slug}")
    print(f"  Target: {target_path}")
    print(f"{'='*70}")
    
    try:
        # Download using kagglehub
        cached_path = kagglehub.dataset_download(slug)
        print(f"  Downloaded to cache: {cached_path}")
        
        # Copy from cache to our target directory
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        if os.path.isdir(cached_path):
            shutil.copytree(cached_path, target_path)
        else:
            os.makedirs(target_path, exist_ok=True)
            shutil.copy2(cached_path, target_path)
        
        # List downloaded files
        files = []
        for root, dirs, fnames in os.walk(target_path):
            for fname in fnames:
                fpath = os.path.join(root, fname)
                size_mb = os.path.getsize(fpath) / (1024 * 1024)
                rel_path = os.path.relpath(fpath, target_path)
                files.append((rel_path, size_mb))
        
        print(f"  ✅ SUCCESS - Files copied to {target_path}:")
        for fname, size in files:
            print(f"     📄 {fname} ({size:.2f} MB)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR downloading {slug}: {e}")
        return False


def main():
    print("=" * 70)
    print("DATASET DOWNLOADER - AI-Driven Nutrient Recommendation System")
    print("Final Year Project - Precision Agriculture / AI")
    print("=" * 70)
    
    results = []
    
    for ds in DATASETS:
        success = download_dataset(ds["slug"], ds["target_folder"], ds["description"])
        results.append((ds["target_folder"], ds["description"], success))
    
    # Print summary
    print("\n\n" + "=" * 70)
    print("DOWNLOAD SUMMARY")
    print("=" * 70)
    
    for folder, desc, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {status} | {folder} | {desc}")
    
    successful = sum(1 for _, _, s in results if s)
    print(f"\nTotal: {successful}/{len(results)} datasets downloaded successfully.")
    print(f"Location: {DATASETS_DIR}")


if __name__ == "__main__":
    main()
