#!/usr/bin/env python3
"""
ML Yield Model Training Script
==============================
Generates a synthetic dataset for crop yield prediction and trains a real
scikit-learn/XGBoost model pipeline. Saves model artifacts to backend/models/.

Usage:
    python backend/ml/train_yield_model.py
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Try to import XGBoost for better performance
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[Yield Training] XGBoost not available, using RandomForest")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # FinalYearProject/
MODELS_DIR = BASE_DIR / "backend" / "models"
TRAIN_DATA_DIR = BASE_DIR / "backend" / "ml" / "training_data"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
TRAIN_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Indian states for synthetic data
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

# Crops with typical yield ranges (tons/hectare)
CROPS = {
    "Rice": {"yield_range": (2.0, 6.5), "season": "Kharif", "base_yield": 3.5},
    "Wheat": {"yield_range": (2.5, 5.5), "season": "Rabi", "base_yield": 3.2},
    "Maize": {"yield_range": (3.0, 8.0), "season": "Kharif", "base_yield": 4.5},
    "Bajra": {"yield_range": (1.0, 3.0), "season": "Kharif", "base_yield": 1.5},
    "Jowar": {"yield_range": (0.8, 2.5), "season": "Kharif", "base_yield": 1.2},
    "Ragi": {"yield_range": (1.2, 3.5), "season": "Kharif", "base_yield": 1.8},
    "Barley": {"yield_range": (2.0, 4.0), "season": "Rabi", "base_yield": 2.8},
    "Gram": {"yield_range": (0.8, 1.8), "season": "Rabi", "base_yield": 1.1},
    "Tur": {"yield_range": (0.7, 1.5), "season": "Kharif", "base_yield": 0.9},
    "Moong": {"yield_range": (0.5, 1.2), "season": "Kharif", "base_yield": 0.7},
    "Urad": {"yield_range": (0.5, 1.2), "season": "Kharif", "base_yield": 0.7},
    "Groundnut": {"yield_range": (1.0, 2.5), "season": "Kharif", "base_yield": 1.5},
    "Soybean": {"yield_range": (1.0, 2.5), "season": "Kharif", "base_yield": 1.3},
    "Sunflower": {"yield_range": (0.8, 2.0), "season": "Rabi", "base_yield": 1.1},
    "Cotton": {"yield_range": (0.4, 1.2), "season": "Kharif", "base_yield": 0.6},
    "Sugarcane": {"yield_range": (60.0, 100.0), "season": "Annual", "base_yield": 75.0},
    "Jute": {"yield_range": (1.5, 3.0), "season": "Kharif", "base_yield": 2.0},
    "Potato": {"yield_range": (15.0, 30.0), "season": "Rabi", "base_yield": 20.0},
    "Onion": {"yield_range": (10.0, 25.0), "season": "Rabi", "base_yield": 16.0},
}

SEASONS = ["Kharif", "Rabi", "Zaid", "Annual"]

# Years for training data
YEARS = list(range(2010, 2024))


def generate_synthetic_data(n_samples: int = 50000) -> pd.DataFrame:
    """
    Generate synthetic crop production data with realistic relationships.
    
    Features:
    - State_Name, District_Name, Crop, Season, Crop_Year
    - Area (hectares), Production (tons), Yield (tons/hectare)
    - Weather: Annual_Rainfall, Avg_Temperature, Avg_Humidity
    - Soil: N, P, K, pH
    """
    np.random.seed(42)
    
    rows = []
    
    # Pre-generate district names per state (simplified)
    districts_per_state = {
        state: [f"{state} District {i}" for i in range(1, 6)]
        for state in INDIAN_STATES
    }
    
    for _ in range(n_samples):
        state = np.random.choice(INDIAN_STATES)
        district = np.random.choice(districts_per_state[state])
        crop = np.random.choice(list(CROPS.keys()))
        crop_info = CROPS[crop]
        season = np.random.choice(SEASONS)
        year = np.random.choice(YEARS)
        
        # Area: log-normal distribution (most farms small, some large)
        area = np.random.lognormal(mean=2.0, sigma=1.0)  # ~7.4 hectares median
        area = np.clip(area, 0.1, 500.0)
        
        # Weather factors
        # Rainfall varies by state and season
        base_rainfall = {
            "Andhra Pradesh": 900, "Assam": 2500, "Bihar": 1200, "Gujarat": 800,
            "Haryana": 500, "Karnataka": 1000, "Madhya Pradesh": 1100, "Maharashtra": 1000,
            "Punjab": 600, "Rajasthan": 400, "Tamil Nadu": 950, "Telangana": 900,
            "Uttar Pradesh": 1000, "West Bengal": 1500
        }.get(state, 1000)
        
        # Seasonal adjustment
        season_rainfall_factor = {"Kharif": 1.5, "Rabi": 0.3, "Zaid": 0.2, "Annual": 1.0}
        annual_rainfall = base_rainfall * season_rainfall_factor.get(season, 1.0)
        annual_rainfall += np.random.normal(0, annual_rainfall * 0.2)
        annual_rainfall = max(100, annual_rainfall)
        
        # Temperature
        base_temp = {
            "Himachal Pradesh": 15, "Uttarakhand": 16, "Jharkhand": 25,
            "Punjab": 24, "Haryana": 25, "Rajasthan": 28, "Gujarat": 27,
            "Madhya Pradesh": 26, "Maharashtra": 27, "Karnataka": 26,
            "Tamil Nadu": 28, "Andhra Pradesh": 28, "Telangana": 27,
            "Odisha": 27, "West Bengal": 26, "Bihar": 25, "Uttar Pradesh": 25
        }.get(state, 26)
        avg_temp = base_temp + np.random.normal(0, 2)
        avg_temp = np.clip(avg_temp, 10, 40)
        
        # Humidity
        avg_humidity = np.random.normal(65, 15)
        avg_humidity = np.clip(avg_humidity, 30, 95)
        
        # Soil parameters (vary by state)
        n_kg_ha = np.random.normal(180, 50)
        p_kg_ha = np.random.normal(50, 20)
        k_kg_ha = np.random.normal(180, 50)
        ph = np.random.normal(6.8, 0.8)
        ph = np.clip(ph, 4.5, 8.5)
        
        # Compute yield with realistic relationships
        base_yield = crop_info["base_yield"]
        
        # Weather impact on yield
        # Optimal rainfall around 1000-1200mm for most crops
        rainfall_factor = 1.0 - 0.3 * abs(annual_rainfall - 1000) / 1000
        rainfall_factor = np.clip(rainfall_factor, 0.4, 1.3)
        
        # Temperature impact (crop-specific optima)
        temp_opt = {
            "Wheat": 20, "Barley": 18, "Gram": 22, "Mustard": 20,
            "Rice": 28, "Maize": 25, "Bajra": 30, "Jowar": 28,
            "Cotton": 30, "Sugarcane": 28, "Groundnut": 28
        }.get(crop, 25)
        temp_factor = 1.0 - 0.15 * abs(avg_temp - temp_opt) / 10
        temp_factor = np.clip(temp_factor, 0.5, 1.2)
        
        # Soil fertility impact
        n_factor = 1.0 + 0.1 * (n_kg_ha - 150) / 100
        n_factor = np.clip(n_factor, 0.7, 1.3)
        
        p_factor = 1.0 + 0.05 * (p_kg_ha - 40) / 30
        p_factor = np.clip(p_factor, 0.8, 1.2)
        
        k_factor = 1.0 + 0.05 * (k_kg_ha - 150) / 80
        k_factor = np.clip(k_factor, 0.8, 1.2)
        
        ph_factor = 1.0 - 0.1 * abs(ph - 6.5)
        ph_factor = np.clip(ph_factor, 0.6, 1.1)
        
        # Year trend (technology improvement ~1% per year)
        year_factor = 1.0 + 0.01 * (year - 2010)
        
        # Random noise
        noise = np.random.lognormal(0, 0.15)
        
        # Final yield
        yield_t_ha = (base_yield * rainfall_factor * temp_factor * 
                      n_factor * p_factor * k_factor * ph_factor * 
                      year_factor * noise)
        
        # Clip to reasonable range
        min_y, max_y = crop_info["yield_range"]
        yield_t_ha = np.clip(yield_t_ha, min_y * 0.5, max_y * 1.5)
        
        production = yield_t_ha * area
        
        rows.append({
            "State_Name": state,
            "District_Name": district,
            "Crop": crop,
            "Season": season,
            "Crop_Year": year,
            "Area": round(area, 2),
            "Production": round(production, 2),
            "Yield": round(yield_t_ha, 2),
            "Annual_Rainfall": round(annual_rainfall, 1),
            "Avg_Temperature": round(avg_temp, 1),
            "Avg_Humidity": round(avg_humidity, 1),
            "N_kg_ha": round(n_kg_ha, 1),
            "P_kg_ha": round(p_kg_ha, 1),
            "K_kg_ha": round(k_kg_ha, 1),
            "pH": round(ph, 1),
        })
    
    df = pd.DataFrame(rows)
    return df


def train_model(df: pd.DataFrame) -> tuple:
    """Train the yield prediction model and return model, encoders, scaler."""
    
    # Encode categorical features
    state_encoder = LabelEncoder()
    district_encoder = LabelEncoder()
    crop_encoder = LabelEncoder()
    season_encoder = LabelEncoder()
    
    df["State_Name_Encoded"] = state_encoder.fit_transform(df["State_Name"])
    df["District_Encoded"] = district_encoder.fit_transform(df["District_Name"])
    df["Crop_Encoded"] = crop_encoder.fit_transform(df["Crop"])
    df["Season_Encoded"] = season_encoder.fit_transform(df["Season"])
    
    # Feature columns for training
    feature_cols = [
        "State_Name_Encoded", "District_Encoded", "Crop_Encoded", 
        "Season_Encoded", "Crop_Year", "Area", "Annual_Rainfall",
        "Avg_Temperature", "Avg_Humidity", "N_kg_ha", "P_kg_ha", 
        "K_kg_ha", "pH"
    ]
    
    X = df[feature_cols]
    y = df["Yield"]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    if XGBOOST_AVAILABLE:
        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        model_type = "XGBoost"
    else:
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        model_type = "RandomForest"
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"[Yield Training] Model: {model_type}")
    print(f"[Yield Training] Test MAE: {mae:.3f} t/ha")
    print(f"[Yield Training] Test RMSE: {rmse:.3f} t/ha")
    print(f"[Yield Training] Test R²: {r2:.3f}")
    
    # Feature importance
    if hasattr(model, "feature_importances_"):
        importance = pd.DataFrame({
            "feature": feature_cols,
            "importance": model.feature_importances_
        }).sort_values("importance", ascending=False)
        print(f"[Yield Training] Top 5 features:\n{importance.head()}")
    
    return model, scaler, state_encoder, district_encoder, crop_encoder, season_encoder, feature_cols


def main():
    print("=" * 60)
    print("AgriBrain Yield Model Training")
    print("=" * 60)
    
    # Generate synthetic data
    print("[Yield Training] Generating synthetic dataset...")
    df = generate_synthetic_data(n_samples=50000)
    
    # Save processed dataset
    processed_path = TRAIN_DATA_DIR / "crop_production_processed.csv"
    df.to_csv(processed_path, index=False)
    print(f"[Yield Training] Saved processed data to {processed_path}")
    print(f"[Yield Training] Dataset shape: {df.shape}")
    print(f"[Yield Training] Yield range: {df['Yield'].min():.2f} - {df['Yield'].max():.2f} t/ha")
    print(f"[Yield Training] Crops: {df['Crop'].nunique()}, States: {df['State_Name'].nunique()}")
    
    # Train model
    print("\n[Yield Training] Training model...")
    model, scaler, state_enc, district_enc, crop_enc, season_enc, feature_cols = train_model(df)
    
    # Save model artifacts
    model_path = MODELS_DIR / "yield_model.pkl"
    scaler_path = MODELS_DIR / "yield_scaler.pkl"
    district_encoder_path = MODELS_DIR / "yield_district_encoder.pkl"
    state_encoder_path = MODELS_DIR / "yield_state_encoder.pkl"
    crop_encoder_path = MODELS_DIR / "yield_crop_encoder.pkl"
    season_encoder_path = MODELS_DIR / "yield_season_encoder.pkl"
    info_path = MODELS_DIR / "yield_model_info.json"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(district_enc, district_encoder_path)
    joblib.dump(state_enc, state_encoder_path)
    joblib.dump(crop_enc, crop_encoder_path)
    joblib.dump(season_enc, season_encoder_path)
    
    # Save model info
    model_info = {
        "model_type": "XGBoost" if XGBOOST_AVAILABLE else "RandomForest",
        "feature_columns": feature_cols,
        "target": "Yield (tons/hectare)",
        "crops": list(CROPS.keys()),
        "states": INDIAN_STATES,
        "seasons": SEASONS,
        "years": YEARS,
        "n_samples": len(df),
        "training_date": pd.Timestamp.now().isoformat()
    }
    with open(info_path, "w") as f:
        json.dump(model_info, f, indent=2)
    
    print(f"\n[Yield Training] Model saved to {model_path}")
    print(f"[Yield Training] Scaler saved to {scaler_path}")
    print(f"[Yield Training] Encoders saved to {MODELS_DIR}")
    print(f"[Yield Training] Model info saved to {info_path}")
    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()