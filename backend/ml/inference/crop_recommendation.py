"""backend.ml.crop_recommendation
==========================================

Production crop-recommendation and yield prediction inference module.

This module loads the trained RandomForest models and StandardScaler from the
training pipeline and provides:
- recommend(): crop recommendations with confidence scores
- predict_yield(): yield prediction in tons per hectare
"""

from __future__ import annotations

import json
import joblib
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder

# ---------------------------------------------------------------------------
# Paths to trained model artifacts
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"c:\Users\USER\Downloads\FinalYearProject")
TRAIN_DATA_DIR = BASE_DIR / "training_data"
MODEL_DIR = BASE_DIR / "models"

# Feature columns for crop recommendation (exact order from training)
FEATURE_COLUMNS = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]

# Feature columns for yield prediction
YIELD_FEATURE_COLUMNS = ["State_Name_Encoded", "District_Encoded", "Crop_Encoded", "Season_Encoded", "Crop_Year"]


def _load_model_and_scaler() -> Tuple[RandomForestClassifier, StandardScaler, Dict[int, str]]:
    """Load the trained crop recommendation model, scaler, and label mapping from disk."""
    model_path = MODEL_DIR / "crop_recommendation_model.pkl"
    scaler_path = TRAIN_DATA_DIR / "crop_scaler.pkl"
    label_mapping_path = TRAIN_DATA_DIR / "crop_label_mapping.json"
    
    if not model_path.is_file():
        # If model doesn't exist, train it on-the-fly (fallback for testing)
        from backend.ml.crop_recommendation import merge_data, train_model
        X, y = merge_data()
        model = train_model(X, y)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
    else:
        model = joblib.load(model_path)
    
    scaler = joblib.load(scaler_path)
    
    with open(label_mapping_path, "r") as f:
        label_mapping = json.load(f)
    
    # Reverse mapping: encoded_label -> crop_name
    idx_to_crop = {int(v): k for k, v in label_mapping.items()}
    
    return model, scaler, idx_to_crop


def _load_yield_model() -> Tuple[RandomForestRegressor, LabelEncoder, Dict[str, Any]]:
    """Load the trained yield prediction model and encoders from disk."""
    model_path = MODEL_DIR / "yield_model.pkl"
    encoder_path = MODEL_DIR / "yield_district_encoder.pkl"
    info_path = MODEL_DIR / "yield_model_info.json"
    
    model = joblib.load(model_path)
    district_encoder = joblib.load(encoder_path)
    
    with open(info_path, "r") as f:
        model_info = json.load(f)
    
    return model, district_encoder, model_info


# Load model artifacts at module import (lazy loading)
_MODEL = None
_SCALER = None
_IDX_TO_CROP = None
_YIELD_MODEL = None
_YIELD_DISTRICT_ENCODER = None
_YIELD_MODEL_INFO = None
# Cached encoders for yield prediction
_YIELD_STATE_ENCODER = None
_YIELD_CROP_ENCODER = None
_YIELD_SEASON_ENCODER = None
_YIELD_DF = None


def _get_model_artifacts():
    """Lazy-load crop recommendation model artifacts."""
    global _MODEL, _SCALER, _IDX_TO_CROP
    if _MODEL is None:
        _MODEL, _SCALER, _IDX_TO_CROP = _load_model_and_scaler()
    return _MODEL, _SCALER, _IDX_TO_CROP


def _get_yield_model_artifacts():
    """Lazy-load yield prediction model artifacts."""
    global _YIELD_MODEL, _YIELD_DISTRICT_ENCODER, _YIELD_MODEL_INFO
    if _YIELD_MODEL is None:
        _YIELD_MODEL, _YIELD_DISTRICT_ENCODER, _YIELD_MODEL_INFO = _load_yield_model()
    return _YIELD_MODEL, _YIELD_DISTRICT_ENCODER, _YIELD_MODEL_INFO


def _get_yield_encoders():
    """Lazy-load and cache yield prediction encoders."""
    global _YIELD_STATE_ENCODER, _YIELD_CROP_ENCODER, _YIELD_SEASON_ENCODER, _YIELD_DF
    if _YIELD_STATE_ENCODER is None:
        import pandas as pd
        from sklearn.preprocessing import LabelEncoder
        
        _YIELD_DF = pd.read_csv(TRAIN_DATA_DIR / "crop_production_processed.csv")
        
        _YIELD_STATE_ENCODER = LabelEncoder()
        _YIELD_STATE_ENCODER.fit(_YIELD_DF['State_Name'].astype(str))
        
        _YIELD_CROP_ENCODER = LabelEncoder()
        _YIELD_CROP_ENCODER.fit(_YIELD_DF['Crop'].astype(str))
        
        _YIELD_SEASON_ENCODER = LabelEncoder()
        _YIELD_SEASON_ENCODER.fit(_YIELD_DF['Season'].astype(str))
        
        # Create case-insensitive lookup for districts
        global _DISTRICT_LOOKUP
        _DISTRICT_LOOKUP = {k.upper(): v for k, v in zip(
            _YIELD_DF['District_Name'].astype(str), 
            _YIELD_DISTRICT_ENCODER.transform(_YIELD_DF['District_Name'].astype(str))
        )}
    
    return _YIELD_STATE_ENCODER, _YIELD_CROP_ENCODER, _YIELD_SEASON_ENCODER


def merge_data() -> Tuple[pd.DataFrame, pd.Series]:
    """Load the pre-processed training data for crop recommendation.

    Returns
    -------
    X, y
        ``X`` - a ``DataFrame`` of feature columns (already scaled).
        ``y`` - a ``Series`` of integer class labels.
    """
    df = pd.read_csv(TRAIN_DATA_DIR / "crop_recommendation_train.csv")
    if "label_encoded" not in df.columns:
        raise KeyError("'label_encoded' column missing from training data")
    y = df["label_encoded"]
    X = df.drop(columns=["label_encoded", "label"], errors="ignore")
    return X, y


def train_model(X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> RandomForestClassifier:
    """Train a RandomForest classifier (used for initial model training)."""
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    return clf


def recommend(
    input_features: Dict[str, Any],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Generate crop recommendations for a single input record.

    Parameters
    ----------
    input_features:
        Mapping of feature name to value. Expected keys: n, p, k, temperature, 
        humidity, ph, rainfall (raw values, NOT scaled).
    top_k:
        Number of top recommendations to return.

    Returns
    -------
    List[Dict]
        Each dict contains ``crop_name`` (actual crop name), ``confidence``
        (probability), and ``match_reasons`` (empty list for now).
    """
    model, scaler, idx_to_crop = _get_model_artifacts()
    
    # Create DataFrame with exact training column names to avoid sklearn feature warnings
    X_raw = pd.DataFrame(
        [[input_features.get(col, 0) for col in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS
    )
    
    # Apply the same scaling used during training
    X_scaled = scaler.transform(X_raw)

    # Convert back to DataFrame with feature names to avoid sklearn feature name warnings
    X_scaled_df = pd.DataFrame(X_scaled, columns=FEATURE_COLUMNS)

    # Get prediction probabilities
    probs = model.predict_proba(X_scaled_df)[0]

    # Get class indices sorted by probability descending
    sorted_indices = np.argsort(probs)[::-1]
    top_indices = sorted_indices[:top_k]
    
    recommendations = []
    for idx in top_indices:
        crop_name = idx_to_crop.get(idx, f"Unknown_{idx}")
        recommendations.append({
            "crop_name": crop_name,
            "confidence": float(probs[idx]),
            "match_reasons": [],
        })
    
    # Pad if model has fewer classes than top_k
    while len(recommendations) < top_k:
        dummy_idx = len(recommendations)
        recommendations.append({
            "crop_name": f"Crop_{dummy_idx}",
            "confidence": 0.0,
            "match_reasons": [],
        })
    
    return recommendations


# Backwards compatibility: expose model training functions for the training script
def load_model_for_training() -> Tuple[RandomForestClassifier, StandardScaler]:
    """Load model and scaler for training script."""
    model, scaler, _ = _get_model_artifacts()
    return model, scaler


def predict_yield(
    state_name: str,
    district_name: str,
    crop_name: str,
    season: str,
    crop_year: int,
    state_encoder: Optional[LabelEncoder] = None,
    crop_encoder: Optional[LabelEncoder] = None,
    season_encoder: Optional[LabelEncoder] = None,
) -> float:
    """Predict crop yield in tons per hectare.
    
    Parameters
    ----------
    state_name : str
        State name (e.g., "Maharashtra")
    district_name : str
        District name (e.g., "Pune")
    crop_name : str
        Crop name (e.g., "Rice")
    season : str
        Season (e.g., "Kharif", "Rabi", "Whole Year")
    crop_year : int
        Year for prediction (e.g., 2024)
    state_encoder, crop_encoder, season_encoder : LabelEncoder, optional
        Pre-fitted encoders for categorical features. If not provided, 
        defaults will be used (may be less accurate).
    
    Returns
    -------
    float
        Predicted yield in tons per hectare
    """
    yield_model, district_encoder, model_info = _get_yield_model_artifacts()
    
    # Default encoders (these would ideally come from training artifacts)
    # For now, we need to load the state/crop/season encoders from the training data
    # Let's load them from the crop production data
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    
    df = pd.read_csv(TRAIN_DATA_DIR / "crop_production_processed.csv")
    
    # Create encoders if not provided
    if state_encoder is None:
        state_encoder = LabelEncoder()
        state_encoder.fit(df['State_Name'].astype(str))
    
    if crop_encoder is None:
        crop_encoder = LabelEncoder()
        crop_encoder.fit(df['Crop'].astype(str))
    
    if season_encoder is None:
        season_encoder = LabelEncoder()
        season_encoder.fit(df['Season'].astype(str))
    
    # Encode features
    try:
        state_encoded = state_encoder.transform([state_name])[0]
    except ValueError:
        state_encoded = 0  # Unknown state
    
    try:
        district_encoded = district_encoder.transform([district_name])[0]
    except ValueError:
        district_encoded = 0  # Unknown district
    
    try:
        crop_encoded = crop_encoder.transform([crop_name])[0]
    except ValueError:
        crop_encoded = 0  # Unknown crop
    
    try:
        season_encoded = season_encoder.transform([season])[0]
    except ValueError:
        season_encoded = 0  # Unknown season
    
    # Create feature DataFrame
    X = pd.DataFrame([{
        'State_Name_Encoded': state_encoded,
        'District_Encoded': district_encoded,
        'Crop_Encoded': crop_encoded,
        'Season_Encoded': season_encoded,
        'Crop_Year': crop_year
    }])
    
    # Predict
    yield_pred = yield_model.predict(X)[0]
    
    # Ensure non-negative
    return max(0.0, float(yield_pred))
