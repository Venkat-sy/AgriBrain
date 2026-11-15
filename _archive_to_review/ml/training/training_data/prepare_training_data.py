import os
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = r"c:\Users\USER\Downloads\FinalYearProject"
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR = os.path.join(BASE_DIR, "training_data")

os.makedirs(OUT_DIR, exist_ok=True)

config = {}

def task1():
    print("Starting Task 1: Crop Recommendation")
    df = pd.read_csv(os.path.join(DATASETS_DIR, "01_crop_recommendation", "Crop_recommendation.csv"))
    
    assert df.isnull().sum().sum() == 0, "Missing values found!"
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]

    scaler = StandardScaler()
    numeric_cols = ['n', 'p', 'k', 'temperature', 'humidity', 'ph', 'rainfall']
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    le = LabelEncoder()
    df['label_encoded'] = le.fit_transform(df['label'])

    train, temp = train_test_split(df, test_size=0.3, stratify=df['label_encoded'], random_state=42)
    val, test = train_test_split(temp, test_size=0.5, stratify=temp['label_encoded'], random_state=42)

    train.to_csv(os.path.join(OUT_DIR, "crop_recommendation_train.csv"), index=False)
    val.to_csv(os.path.join(OUT_DIR, "crop_recommendation_val.csv"), index=False)
    test.to_csv(os.path.join(OUT_DIR, "crop_recommendation_test.csv"), index=False)

    joblib.dump(scaler, os.path.join(OUT_DIR, "crop_scaler.pkl"))
    with open(os.path.join(OUT_DIR, "crop_label_mapping.json"), 'w') as f:
        json.dump({str(k): int(v) for k, v in zip(le.classes_, le.transform(le.classes_))}, f)

    config["crop_recommendation"] = {
        "input_features": numeric_cols,
        "target_column": "label_encoded",
        "num_classes": len(le.classes_),
        "scaler_ref": "crop_scaler.pkl",
        "types": df[numeric_cols].dtypes.astype(str).to_dict()
    }
    print(f"  Train: {train.shape}, Val: {val.shape}, Test: {test.shape}")
    print(f"  Classes: {len(le.classes_)}, Features: {numeric_cols}")
    print("Task 1 complete.\n")

def task2():
    print("Starting Task 2: Fertilizer Recommendation")
    df1 = pd.read_csv(os.path.join(DATASETS_DIR, "02_fertilizer_recommendation", "Fertilizer Prediction.csv"))
    df1.rename(columns={'Temparature': 'Temperature', 'Humidity ': 'Humidity'}, inplace=True)
    
    df2 = pd.read_csv(os.path.join(DATA_DIR, "soil_health_data.csv"))
    df2.rename(columns={
        'Nitrogen_mg_kg': 'Nitrogen',
        'Phosphorus_mg_kg': 'Phosphorous',
        'Potassium_mg_kg': 'Potassium',
        'pH_Level': 'pH',
        'Temperature_C': 'Temperature',
        'Rainfall_mm': 'Rainfall',
        'Recommended_Fertilizer': 'Fertilizer Name'
    }, inplace=True)
    
    # Common schema map for fertilizer names could be applied here if they differ
    
    df1['Source'] = 'df1'
    df2['Source'] = 'df2'
    
    df = pd.concat([df1, df2], ignore_index=True)
    
    df['Soil Type'] = df['Soil Type'].fillna('Unknown')
    df['Crop Type'] = df['Crop Type'].fillna('Unknown')
    
    df = pd.get_dummies(df, columns=['Soil Type', 'Crop Type'], drop_first=False)
    
    le = LabelEncoder()
    df['Fertilizer Name'] = df['Fertilizer Name'].astype(str)
    df['Fertilizer_Encoded'] = le.fit_transform(df['Fertilizer Name'])
    
    numeric_cols = ['Temperature', 'Humidity', 'Moisture', 'Nitrogen', 'Potassium', 'Phosphorous']
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
            
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols].fillna(0))
    
    train, temp = train_test_split(df, test_size=0.3, stratify=df['Fertilizer_Encoded'], random_state=42)
    val, test = train_test_split(temp, test_size=0.5, stratify=temp['Fertilizer_Encoded'], random_state=42)
    
    train.to_csv(os.path.join(OUT_DIR, "fertilizer_recommendation_train.csv"), index=False)
    val.to_csv(os.path.join(OUT_DIR, "fertilizer_recommendation_val.csv"), index=False)
    test.to_csv(os.path.join(OUT_DIR, "fertilizer_recommendation_test.csv"), index=False)
    
    joblib.dump(scaler, os.path.join(OUT_DIR, "fertilizer_scaler.pkl"))
    with open(os.path.join(OUT_DIR, "fertilizer_label_mapping.json"), 'w') as f:
        json.dump({str(k): int(v) for k, v in zip(le.classes_, le.transform(le.classes_))}, f)
        
    ohe_cols = [c for c in df.columns if c.startswith('Soil Type_') or c.startswith('Crop Type_')]
    config["fertilizer_recommendation"] = {
        "input_features": numeric_cols + ohe_cols,
        "target_column": "Fertilizer_Encoded",
        "num_classes": len(le.classes_),
        "scaler_ref": "fertilizer_scaler.pkl",
        "types": df[numeric_cols].dtypes.astype(str).to_dict()
    }
    print(f"  Combined dataset: {df.shape} (Kaggle: {len(df1)}, SoilHealth: {len(df2)})")
    print(f"  Train: {train.shape}, Val: {val.shape}, Test: {test.shape}")
    print(f"  Classes: {len(le.classes_)}, OHE cols: {len(ohe_cols)}")
    print("Task 2 complete.\n")

def task3():
    print("Starting Task 3: Yield Prediction")
    df_yield = pd.read_csv(os.path.join(DATASETS_DIR, "05_crop_yield_prediction", "crop_yield.csv"))
    df_yield['Season'] = df_yield['Season'].str.strip()
    
    q99 = df_yield['Yield'].quantile(0.99)
    df_yield['Yield'] = np.where(df_yield['Yield'] > q99, q99, df_yield['Yield'])
    
    if 'Yield_per_Area' not in df_yield.columns:
        df_yield['Yield_per_Area'] = df_yield['Production'] / df_yield['Area']
    df_yield['Fertilizer_per_Area'] = df_yield['Fertilizer'] / df_yield['Area']
    
    df_adv = pd.read_csv(os.path.join(DATA_DIR, "advanced_agri_dataset.csv"))
    df_adv['pH'] = df_adv['pH'].fillna(df_adv['pH'].median())
    df_adv['Soil_Moisture_pct'] = df_adv['Soil_Moisture_pct'].fillna(df_adv['Soil_Moisture_pct'].median())
    
    encoders = {}
    for col in ['Crop', 'Season', 'State']:
        if col in df_yield.columns:
            le = LabelEncoder()
            df_yield[col + '_Encoded'] = le.fit_transform(df_yield[col].astype(str))
            encoders[col] = le
            
    if 'Crop_Type' in df_adv.columns:
        le_crop = LabelEncoder()
        df_adv['Crop_Type_Encoded'] = le_crop.fit_transform(df_adv['Crop_Type'].astype(str))
        encoders['Crop_Type'] = le_crop
        
    scaler_yield = StandardScaler()
    num_cols_yield = ['Area', 'Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide', 'Fertilizer_per_Area']
    df_yield[num_cols_yield] = scaler_yield.fit_transform(df_yield[num_cols_yield])
    
    train_y, temp_y = train_test_split(df_yield, test_size=0.3, random_state=42)
    val_y, test_y = train_test_split(temp_y, test_size=0.5, random_state=42)
    
    train_y.to_csv(os.path.join(OUT_DIR, "yield_prediction_train.csv"), index=False)
    val_y.to_csv(os.path.join(OUT_DIR, "yield_prediction_val.csv"), index=False)
    test_y.to_csv(os.path.join(OUT_DIR, "yield_prediction_test.csv"), index=False)
    
    train_a, temp_a = train_test_split(df_adv, test_size=0.3, random_state=42)
    val_a, test_a = train_test_split(temp_a, test_size=0.5, random_state=42)
    
    train_a.to_csv(os.path.join(OUT_DIR, "advanced_yield_train.csv"), index=False)
    val_a.to_csv(os.path.join(OUT_DIR, "advanced_yield_val.csv"), index=False)
    test_a.to_csv(os.path.join(OUT_DIR, "advanced_yield_test.csv"), index=False)
    
    joblib.dump(scaler_yield, os.path.join(OUT_DIR, "yield_scaler.pkl"))
    joblib.dump(encoders, os.path.join(OUT_DIR, "yield_label_encoders.pkl"))
    
    config["yield_prediction"] = {
        "input_features": num_cols_yield + [c for c in df_yield.columns if c.endswith('_Encoded')],
        "target_column": "Yield",
        "scaler_ref": "yield_scaler.pkl",
        "types": df_yield[num_cols_yield].dtypes.astype(str).to_dict()
    }
    config["advanced_yield"] = {
        "input_features": ['Nitrogen', 'Phosphorus', 'Potassium', 'pH', 'Rainfall_mm', 'Temperature_C', 'Humidity_pct', 'Soil_Moisture_pct', 'Crop_Type_Encoded'],
        "target_columns": ['Yield_tons_per_ha', 'Irrigation_Demand_mm', 'Crop_Failure_Risk'],
        "types": {"task": "multi_output_regression_and_classification"}
    }
    print(f"  Yield dataset: {df_yield.shape}, outlier cap at 99th pctile: {q99:.2f}")
    print(f"  Yield Train: {train_y.shape}, Val: {val_y.shape}, Test: {test_y.shape}")
    print(f"  Advanced Train: {train_a.shape}, Val: {val_a.shape}, Test: {test_a.shape}")
    print("Task 3 complete.\n")

def task4():
    print("Starting Task 4: Rainfall")
    df = pd.read_csv(os.path.join(DATASETS_DIR, "04_rainfall_india", "rainfall in india 1901-2015.csv"))
    
    # ffill then bfill within each subdivision group
    fill_cols = [c for c in df.columns if c not in ['SUBDIVISION', 'YEAR']]
    df[fill_cols] = df.groupby('SUBDIVISION')[fill_cols].transform(lambda x: x.ffill().bfill())
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    df['ANNUAL'] = df['ANNUAL'].fillna(df[months].sum(axis=1))
    
    df['Monsoon_Ratio'] = df['Jun-Sep'] / df['ANNUAL']
    
    df['Rainfall_Variability'] = df.groupby('SUBDIVISION')['ANNUAL'].transform(lambda x: x.rolling(window=5, min_periods=1).std())
    df['Rainfall_Variability'] = df['Rainfall_Variability'].fillna(0)
    
    df['SUBDIVISION'] = df['SUBDIVISION'].str.upper().str.strip()
    
    df.to_csv(os.path.join(OUT_DIR, "rainfall_processed.csv"), index=False)
    
    config["rainfall"] = {
        "description": "Processed rainfall data with monsoon ratio and variability features",
        "engineered_features": ["Monsoon_Ratio", "Rainfall_Variability"],
        "types": df.dtypes.astype(str).to_dict()
    }
    print(f"  Processed shape: {df.shape}, NaN remaining: {df.isnull().sum().sum()}")
    print("Task 4 complete.\n")

def task5():
    print("Starting Task 5: Crop Production")
    df = pd.read_csv(os.path.join(DATASETS_DIR, "03_crop_production_india", "crop_production.csv"))
    df['Season'] = df['Season'].str.strip()
    
    df.dropna(subset=['Production'], inplace=True)
    
    df['Area'] = df['Area'].replace(0, np.nan)
    df.dropna(subset=['Area'], inplace=True)
    df['Yield_per_ha'] = df['Production'] / df['Area']
    
    df.drop_duplicates(subset=['State_Name', 'District_Name', 'Crop_Year', 'Season', 'Crop'], inplace=True)
    
    for col in ['State_Name', 'Crop', 'Season']:
        le = LabelEncoder()
        df[col + '_Encoded'] = le.fit_transform(df[col].astype(str))
        
    df.to_csv(os.path.join(OUT_DIR, "crop_production_processed.csv"), index=False)
    
    config["crop_production"] = {
        "description": "District-level crop production data with yield per hectare",
        "engineered_features": ["Yield_per_ha"],
        "encoded_columns": ["State_Name_Encoded", "Crop_Encoded", "Season_Encoded"],
        "types": df.dtypes.astype(str).to_dict()
    }
    print(f"  Processed shape: {df.shape} (dropped {3730} null Production + deduped)")
    print("Task 5 complete.\n")

def task7():
    """Integrate crop economics data.

    Expected CSV format (placed under ``datasets/economics``):
    ``crop_name, planting_density, seed_cost, fertilizer_cost, labor_cost, market_price``
    The function merges this information with the crop recommendation
    features so that downstream models can incorporate cost‑aware targets.
    """
    print("Starting Task 7: Crop Economics")
    eco_path = os.path.join(DATASETS_DIR, "economics", "crop_economics.csv")
    if not os.path.isfile(eco_path):
        # Try alternative path
        eco_path_alt = os.path.join(DATASETS_DIR, "04_crop_economics", "crop_economics.csv")
        if os.path.isfile(eco_path_alt):
            eco_path = eco_path_alt
        else:
            raise FileNotFoundError(f"Crop economics file not found: {eco_path} or {eco_path_alt}")
    eco_df = pd.read_csv(eco_path)
    # Standardise column names
    eco_df.columns = [c.lower().replace(' ', '_') for c in eco_df.columns]
    # Persist for later use – models can load it directly from training_data
    eco_df.to_csv(os.path.join(OUT_DIR, "crop_economics_processed.csv"), index=False)
    # Update config with economics schema
    config["crop_economics"] = {
        "input_features": [c for c in eco_df.columns if c != "crop_name"],
        "target_column": "crop_name",
        "types": eco_df.dtypes.astype(str).to_dict()
    }
    print(f"  Processed economics shape: {eco_df.shape}")
    print("Task 7 complete.\n")


def task8():
    """Task 8 – Run the Phase 4 crop‑recommendation model training.

    The training script writes a ``crop_recommendations.csv`` file and a tiny
    ``crop_recommendation_metadata.json`` containing the output path. We load that
    metadata and expose it via the global ``config`` dictionary so downstream
    steps (or the API) can discover the artefact.
    """
    print("Starting Task 8: Crop Recommendation Model Training")
    import subprocess, sys
    script_path = os.path.join(BASE_DIR, "train_crop_recommendation.py")
    subprocess.run([sys.executable, script_path], check=True)
    # Load metadata if the script produced it.
    meta_path = os.path.join(OUT_DIR, "crop_recommendation_metadata.json")
    if os.path.isfile(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
        config["crop_recommendation_output"] = meta.get("crop_recommendation_output")
    print("Task 8 complete.\n")

def task6():
    print("Starting Task 6: Config")
    with open(os.path.join(OUT_DIR, "feature_config.json"), 'w') as f:
        json.dump(config, f, indent=4)
    print("Task 6 complete.")

if __name__ == "__main__":
    print("=" * 70)
    print("TRAINING DATA PREPARATION PIPELINE")
    print("AI-Driven Nutrient Recommendation System")
    print("=" * 70 + "\n")
    
    tasks = [
        ("Task 1: Crop Recommendation", task1),
        ("Task 2: Fertilizer Recommendation", task2),
        ("Task 3: Yield Prediction", task3),
        ("Task 4: Rainfall Processing", task4),
        ("Task 5: Crop Production Processing", task5),
        ("Task 7: Crop Economics", task7),
        ("Task 8: Crop Recommendation Model Training", task8),
        ("Task 6: Feature Config", task6),
    ]
    
    results = []
    for name, fn in tasks:
        try:
            fn()
            results.append((name, True))
        except Exception as e:
            print(f"  ❌ {name} FAILED: {e}")
            import traceback; traceback.print_exc()
            results.append((name, False))
    
    # Final summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    for name, ok in results:
        print(f"  {'✅' if ok else '❌'} {name}")
    
    print(f"\nOutput directory: {OUT_DIR}")
    print("\nGenerated files:")
    for f in sorted(os.listdir(OUT_DIR)):
        if f == 'prepare_training_data.py':
            continue
        fpath = os.path.join(OUT_DIR, f)
        size = os.path.getsize(fpath)
        if size > 1024 * 1024:
            print(f"  📄 {f} ({size / (1024*1024):.2f} MB)")
        elif size > 1024:
            print(f"  📄 {f} ({size / 1024:.1f} KB)")
        else:
            print(f"  📄 {f} ({size} B)")
    
    print(f"\n✅ Pipeline complete! {sum(1 for _,ok in results if ok)}/{len(results)} tasks succeeded.")
