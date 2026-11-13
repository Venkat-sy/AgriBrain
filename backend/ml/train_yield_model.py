#!/usr/bin/env python3
"""
Train Yield Prediction Model
============================
Trains a RandomForestRegressor on the master agricultural dataset to predict
crop yield (tons per hectare) based on location, crop, season, and year features.
Exports the trained model as yield_model.pkl.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json

# Paths
BASE_DIR = Path(r"c:\Users\USER\Downloads\FinalYearProject")
TRAIN_DATA_DIR = BASE_DIR / "training_data"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def load_and_prepare_data():
    """Load crop production data and prepare features for yield prediction."""
    print("Loading crop production data...")
    df = pd.read_csv(TRAIN_DATA_DIR / "crop_production_processed.csv")
    print(f"Loaded {len(df)} records")
    
    # Features: State, District, Crop, Season, Year (encoded)
    # Target: Yield_per_ha
    feature_cols = ['State_Name_Encoded', 'District_Name', 'Crop_Encoded', 'Season_Encoded', 'Crop_Year']
    
    # We need to encode District_Name as well
    # Let's create a District encoder
    district_encoder = LabelEncoder()
    df['District_Encoded'] = district_encoder.fit_transform(df['District_Name'].astype(str))
    
    # Update feature columns
    feature_cols = ['State_Name_Encoded', 'District_Encoded', 'Crop_Encoded', 'Season_Encoded', 'Crop_Year']
    
    X = df[feature_cols].copy()
    y = df['Yield_per_ha'].copy()
    
    # Handle any missing values
    X = X.fillna(0)
    y = y.fillna(y.median())
    
    print(f"Features: {feature_cols}")
    print(f"Target range: {y.min():.2f} - {y.max():.2f} tons/ha")
    print(f"Target mean: {y.mean():.2f} tons/ha")
    
    return X, y, district_encoder, feature_cols

def train_yield_model():
    """Train the RandomForest regressor for yield prediction."""
    X, y, district_encoder, feature_cols = load_and_prepare_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train RandomForest Regressor
    print("Training RandomForestRegressor...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"  RMSE: {rmse:.4f} tons/ha")
    print(f"  MAE:  {mae:.4f} tons/ha")
    print(f"  R²:   {r2:.4f}")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(f"\nFeature Importance:")
    for _, row in importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Save model and encoders
    model_path = MODEL_DIR / "yield_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    
    # Save district encoder
    encoder_path = MODEL_DIR / "yield_district_encoder.pkl"
    joblib.dump(district_encoder, encoder_path)
    print(f"District encoder saved to: {encoder_path}")
    
    # Save feature columns
    feature_info = {
        "feature_columns": feature_cols,
        "target": "Yield_per_ha",
        "model_type": "RandomForestRegressor",
        "metrics": {
            "rmse": float(rmse),
            "mae": float(mae),
            "r2": float(r2)
        }
    }
    info_path = MODEL_DIR / "yield_model_info.json"
    with open(info_path, 'w') as f:
        json.dump(feature_info, f, indent=2)
    print(f"Model info saved to: {info_path}")
    
    return model, district_encoder, feature_cols

if __name__ == "__main__":
    train_yield_model()