"""backend.ml.crop_recommendation
==========================================

Production crop-recommendation inference module.

This module loads the trained RandomForest model and StandardScaler from the
training pipeline and provides a recommend() function that accepts real-world
input features (N, P, K, temperature, humidity, ph, rainfall) and returns
actual crop recommendations with confidence scores.
"""

from __future__ import annotations

import json
import joblib
from pathlib import Path
from typing import Tuple, List, Dict, Any

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Paths to trained model artifacts
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"c:\Users\USER\Downloads\FinalYearProject")
TRAIN_DATA_DIR = BASE_DIR / "training_data"
MODEL_DIR = BASE_DIR / "models"

# Feature columns in the exact order used during training (from training data)
FEATURE_COLUMNS = ["n", "p", "k", "temperature", "humidity", "ph", "rainfall"]


def _load_model_and_scaler() -> Tuple[RandomForestClassifier, StandardScaler, Dict[int, str]]:
    """Load the trained model, scaler, and label mapping from disk."""
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


# Load model artifacts at module import
_MODEL = None
_SCALER = None
_IDX_TO_CROP = None


def _get_model_artifacts():
    """Lazy-load model artifacts."""
    global _MODEL, _SCALER, _IDX_TO_CROP
    if _MODEL is None:
        _MODEL, _SCALER, _IDX_TO_CROP = _load_model_and_scaler()
    return _MODEL, _SCALER, _IDX_TO_CROP


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
    
    # Extract features in the correct order and convert to array
    X_raw = np.array([[input_features.get(col, 0) for col in FEATURE_COLUMNS]])
    
    # Apply the same scaling used during training
    X_scaled = scaler.transform(X_raw)
    
    # Get prediction probabilities
    probs = model.predict_proba(X_scaled)[0]
    
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
