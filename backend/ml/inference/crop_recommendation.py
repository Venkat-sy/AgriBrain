"""backend.ml.inference.crop_recommendation
==========================================

Production crop-recommendation inference module (XGBoost v2).

Loads the trained XGBoost model bundle from
``backend/ml/saved_models/xgboost_crop_model.joblib`` and provides:
- recommend(): crop recommendations with confidence scores
- predict_yield(): yield prediction in tons per hectare  (unchanged)

The bundle contains:
    model           -- fitted XGBClassifier
    label_encoder   -- fitted LabelEncoder  (int <-> crop name)
    feature_columns -- ordered list of 7 feature names

Falls back to the legacy RandomForest pipeline when the XGBoost bundle is
not found.
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

# SHAP for model explainability
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    shap = None
    SHAP_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ML_DIR = Path(__file__).resolve().parent.parent            # backend/ml/
XGBOOST_BUNDLE_PATH = ML_DIR / "saved_models" / "xgboost_crop_model.joblib"

# Legacy paths (kept for fallback + yield model)
BASE_DIR = Path(r"c:\Users\USER\Downloads\FinalYearProject")
TRAIN_DATA_DIR = BASE_DIR / "training_data"
MODEL_DIR = BASE_DIR / "models"

# Feature columns for the XGBoost model (exact order from training)
XGBOOST_FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Legacy feature columns (lowercase) for RandomForest fallback
LEGACY_FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Yield prediction feature columns
YIELD_FEATURE_COLUMNS = ["State_Name_Encoded", "District_Encoded", "Crop_Encoded", "Season_Encoded", "Crop_Year"]


# ---------------------------------------------------------------------------
# XGBoost model loader (primary)
# ---------------------------------------------------------------------------
_XGB_PIPELINE: Optional[Any] = None


def _load_xgboost_bundle() -> Dict[str, Any]:
    """Load the XGBoost pipeline from disk."""
    pipeline = joblib.load(XGBOOST_BUNDLE_PATH)
    print(f"[ML] Loaded XGBoost crop model pipeline")
    
    # Load label mapping from the saved info file
    import json
    info_path = XGBOOST_BUNDLE_PATH.parent / "xgboost_crop_model_info.json"
    label_mapping = {}
    if info_path.is_file():
        with open(info_path, 'r') as f:
            info = json.load(f)
            label_mapping = info.get("label_mapping", {})
    
    # Create a simple label encoder-like object for inverse_transform
    class SimpleLabelEncoder:
        def __init__(self, mapping):
            self.mapping = {int(v): k for k, v in mapping.items()}
        
        def inverse_transform(self, indices):
            return [self.mapping.get(int(i), f"Unknown_{i}") for i in indices]
    
    # Return a bundle-like dict for backward compatibility
    return {
        "model": pipeline,
        "label_encoder": SimpleLabelEncoder(label_mapping),
        "feature_columns": ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"],
    }


# ---------------------------------------------------------------------------
# SHAP Explainer (authentic model explainability)
# ---------------------------------------------------------------------------
_SHAP_EXPLAINER = None


def _get_shap_explainer() -> Any:
    """Get or create SHAP TreeExplainer for the XGBoost model."""
    global _SHAP_EXPLAINER
    if _SHAP_EXPLAINER is not None:
        return _SHAP_EXPLAINER
    
    if not SHAP_AVAILABLE:
        print("[SHAP] shap library not available, returning None")
        return None
    
    try:
        bundle = _load_xgboost_bundle()
        model = bundle["model"]
        # XGBoost models work with TreeExplainer
        _SHAP_EXPLAINER = shap.TreeExplainer(model)
        print("[SHAP] TreeExplainer initialized for XGBoost model")
        return _SHAP_EXPLAINER
    except Exception as e:
        print(f"[SHAP] Failed to initialize explainer: {e}")
        return None


def compute_shap_values(input_features: Dict[str, float]) -> Dict[str, Any]:
    """
    Compute authentic SHAP feature importance values for the given input.
    
    Args:
        input_features: Dict with keys N, P, K, temperature, humidity, ph, rainfall
        
    Returns:
        Dict with SHAP values, base values, and feature rankings
    """
    if not SHAP_AVAILABLE:
        print("[SHAP] shap library not installed, returning empty explanation")
        return {
            "shap_values": {},
            "base_values": {},
            "feature_importance": [],
            "status": "shap_unavailable"
        }
    
    try:
        # Get the model bundle
        bundle = _load_xgboost_bundle()
        model = bundle["model"]
        feature_columns = bundle["feature_columns"]
        
        # Prepare input array in correct order
        X = np.array([[input_features.get(col, 0) for col in feature_columns]])
        X_df = pd.DataFrame(X, columns=feature_columns)
        
        # Load scaler and transform
        scaler = joblib.load(XGBOOST_BUNDLE_PATH.parent / "xgboost_crop_scaler.joblib")
        X_scaled = scaler.transform(X_df)
        X_scaled_df = pd.DataFrame(X_scaled, columns=feature_columns)
        
        # Get SHAP explainer
        explainer = _get_shap_explainer()
        if explainer is None:
            return {
                "shap_values": {},
                "base_values": {},
                "feature_importance": [],
                "status": "explainer_failed"
            }
        
        # Compute SHAP values
        shap_values = explainer.shap_values(X_scaled_df)
        
        # For multi-class, shap_values is list of arrays (one per class)
        # We'll use the mean absolute SHAP across all classes for overall importance
        if isinstance(shap_values, list):
            # Mean absolute SHAP across classes
            mean_shap = np.mean([np.abs(sv) for sv in shap_values], axis=0)
            shap_vals = mean_shap[0]  # Single sample
            base_values = np.mean([explainer.expected_value] if np.isscalar(explainer.expected_value) 
                                  else explainer.expected_value)
        else:
            shap_vals = np.abs(shap_values[0])
            base_values = explainer.expected_value if np.isscalar(explainer.expected_value) else explainer.expected_value[0]
        
        # Create feature importance ranking
        feature_importance = []
        for i, col in enumerate(feature_columns):
            feature_importance.append({
                "feature": col,
                "value": float(shap_vals[i]),
                "input_value": float(input_features.get(col, 0)),
                "impact": "positive" if shap_vals[i] > 0 else "negative"
            })
        
        # Sort by absolute SHAP value
        feature_importance.sort(key=lambda x: abs(x["value"]), reverse=True)
        
        return {
            "shap_values": {col: float(shap_vals[i]) for i, col in enumerate(feature_columns)},
            "base_values": float(base_values) if np.isscalar(base_values) else float(base_values[0]),
            "feature_importance": feature_importance,
            "status": "success"
        }
        
    except Exception as e:
        print(f"[SHAP] Computation failed: {e}")
        return {
            "shap_values": {},
            "base_values": 0.0,
            "feature_importance": [],
            "status": f"error: {str(e)}"
        }


def _get_xgboost_bundle() -> Optional[Dict[str, Any]]:
    """Lazy-load the XGBoost pipeline. Returns None if not on disk yet."""
    global _XGB_PIPELINE
    if _XGB_PIPELINE is None and XGBOOST_BUNDLE_PATH.is_file():
        _XGB_PIPELINE = _load_xgboost_bundle()
    return _XGB_PIPELINE


# ---------------------------------------------------------------------------
# SHAP Explainer (for XGBoost model explainability)
# ---------------------------------------------------------------------------
_XGB_EXPLAINER: Optional[Any] = None


def _get_xgboost_explainer(bundle: Dict[str, Any]) -> Optional[Any]:
    """Get or create SHAP TreeExplainer for the XGBoost model."""
    global _XGB_EXPLAINER
    if not SHAP_AVAILABLE:
        return None
    
    if _XGB_EXPLAINER is None:
        try:
            xgb_model = bundle["model"].named_steps["xgb"]
            _XGB_EXPLAINER = shap.TreeExplainer(xgb_model)
            print("[ML] SHAP TreeExplainer initialized for XGBoost model")
        except Exception as e:
            print(f"[ML] Failed to initialize SHAP explainer: {e}")
            return None
    return _XGB_EXPLAINER


def compute_shap_values(
    bundle: Dict[str, Any],
    input_features: Dict[str, Any],
    feature_cols: List[str],
) -> Optional[List[Dict[str, Any]]]:
    """
    Compute authentic SHAP feature importance values for a single prediction.
    
    Returns list of dicts with feature name, value, and SHAP impact value.
    Returns None if SHAP is not available or fails.
    """
    if not SHAP_AVAILABLE:
        return None
    
    explainer = _get_xgboost_explainer(bundle)
    if explainer is None:
        return None
    
    try:
        # Build input DataFrame
        row = []
        for col in feature_cols:
            val = (
                input_features.get(col)
                or input_features.get(col.lower())
                or input_features.get(col.upper())
                or 0
            )
            row.append(float(val))
        
        X = pd.DataFrame([row], columns=feature_cols)
        
        # Compute SHAP values
        shap_values = explainer.shap_values(X)
        
        # For multi-class, shap_values is a list of arrays (one per class)
        # We'll use the mean absolute SHAP value across all classes for each feature
        if isinstance(shap_values, list):
            # Average absolute SHAP values across classes
            mean_shap = np.mean([np.abs(sv) for sv in shap_values], axis=0)
            shap_vals = mean_shap[0]  # Single row
        else:
            shap_vals = np.abs(shap_values[0])
        
        # Create feature importance list
        feature_importance = []
        for i, col in enumerate(feature_cols):
            feature_importance.append({
                "feature": col,
                "value": float(X.iloc[0, i]),
                "shap_value": float(shap_vals[i]),
            })
        
        # Sort by absolute SHAP value descending
        feature_importance.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        return feature_importance
        
    except Exception as e:
        print(f"[ML] SHAP computation failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Legacy RandomForest loader (fallback)
# ---------------------------------------------------------------------------
_MODEL = None
_SCALER = None
_IDX_TO_CROP = None


def _load_model_and_scaler() -> Tuple[RandomForestClassifier, StandardScaler, Dict[int, str]]:
    """Load the trained crop recommendation model, scaler, and label mapping from disk."""
    model_path = MODEL_DIR / "crop_recommendation_model.pkl"
    scaler_path = TRAIN_DATA_DIR / "crop_scaler.pkl"
    label_mapping_path = TRAIN_DATA_DIR / "crop_label_mapping.json"

    if not model_path.is_file():
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


def _get_legacy_artifacts() -> Tuple[RandomForestClassifier, StandardScaler, Dict[int, str]]:
    """Lazy-load legacy RandomForest model artifacts."""
    global _MODEL, _SCALER, _IDX_TO_CROP
    if _MODEL is None:
        _MODEL, _SCALER, _IDX_TO_CROP = _load_model_and_scaler()
    return _MODEL, _SCALER, _IDX_TO_CROP


# ---------------------------------------------------------------------------
# Yield model (unchanged)
# ---------------------------------------------------------------------------


_YIELD_MODEL = None
_YIELD_DISTRICT_ENCODER = None
_YIELD_MODEL_INFO = None
_YIELD_STATE_ENCODER = None
_YIELD_CROP_ENCODER = None
_YIELD_SEASON_ENCODER = None
_YIELD_DF = None


def _load_yield_model() -> Tuple[RandomForestRegressor, LabelEncoder, Dict[str, Any]]:
    model_path = MODEL_DIR / "yield_model.pkl"
    encoder_path = MODEL_DIR / "yield_district_encoder.pkl"
    info_path = MODEL_DIR / "yield_model_info.json"
    model = joblib.load(model_path)
    district_encoder = joblib.load(encoder_path)
    with open(info_path, "r") as f:
        model_info = json.load(f)
    return model, district_encoder, model_info


def _get_yield_model_artifacts() -> Tuple[RandomForestRegressor, LabelEncoder, Dict[str, Any]]:
    global _YIELD_MODEL, _YIELD_DISTRICT_ENCODER, _YIELD_MODEL_INFO
    if _YIELD_MODEL is None:
        _YIELD_MODEL, _YIELD_DISTRICT_ENCODER, _YIELD_MODEL_INFO = _load_yield_model()
    return _YIELD_MODEL, _YIELD_DISTRICT_ENCODER, _YIELD_MODEL_INFO


def _get_yield_encoders():
    global _YIELD_STATE_ENCODER, _YIELD_CROP_ENCODER, _YIELD_SEASON_ENCODER, _YIELD_DF
    if _YIELD_STATE_ENCODER is None:
        _YIELD_DF = pd.read_csv(TRAIN_DATA_DIR / "crop_production_processed.csv")
        _YIELD_STATE_ENCODER = LabelEncoder()
        _YIELD_STATE_ENCODER.fit(_YIELD_DF['State_Name'].astype(str))
        _YIELD_CROP_ENCODER = LabelEncoder()
        _YIELD_CROP_ENCODER.fit(_YIELD_DF['Crop'].astype(str))
        _YIELD_SEASON_ENCODER = LabelEncoder()
        _YIELD_SEASON_ENCODER.fit(_YIELD_DF['Season'].astype(str))
    return _YIELD_STATE_ENCODER, _YIELD_CROP_ENCODER, _YIELD_SEASON_ENCODER


# ---------------------------------------------------------------------------
# Public API -- recommend()
# ---------------------------------------------------------------------------
def recommend(
    input_features: Dict[str, Any],
    top_k: int = 5,
    include_shap: bool = False,
) -> List[Dict[str, Any]]:
    """Generate crop recommendations for a single input record.

    Parameters
    ----------
    input_features:
        Mapping of feature name -> value.
        Accepts both upper (N, P, K) and lower (n, p, k) keys.
    top_k:
        Number of top recommendations to return.
    include_shap:
        If True, compute and include SHAP feature importance values.

    Returns
    -------
    List[Dict]
        Each dict: ``crop_name``, ``confidence``, ``match_reasons``, and optionally ``shap_values``.
    """
    bundle = _get_xgboost_bundle()

    if bundle is not None:
        return _recommend_xgboost(bundle, input_features, top_k, include_shap)
    else:
        return _recommend_legacy(input_features, top_k, include_shap)


def _recommend_xgboost(
    bundle: Dict[str, Any],
    input_features: Dict[str, Any],
    top_k: int,
    include_shap: bool = False,
) -> List[Dict[str, Any]]:
    """Inference using the XGBoost model bundle."""
    pipeline = bundle["model"]
    le = bundle["label_encoder"]
    feature_cols = bundle["feature_columns"]

    # Build a single-row DataFrame -- accept both upper and lower key variants
    row = []
    for col in feature_cols:
        val = (
            input_features.get(col)
            or input_features.get(col.lower())
            or input_features.get(col.upper())
            or 0
        )
        row.append(float(val))

    X = pd.DataFrame([row], columns=feature_cols)

    # Get prediction probabilities from the XGB classifier in the pipeline
    xgb_model = pipeline.named_steps["xgb"]
    probs = xgb_model.predict_proba(X)[0]
    sorted_indices = np.argsort(probs)[::-1][:top_k]

    recommendations = []
    for idx in sorted_indices:
        crop_name = le.inverse_transform([idx])[0]
        recommendations.append({
            "crop_name": crop_name,
            "confidence": float(probs[idx]),
            "match_reasons": [],
        })

    # Compute SHAP values if requested
    if include_shap:
        shap_values = compute_shap_values(bundle, input_features, feature_cols)
        if shap_values:
            recommendations[0]["shap_values"] = shap_values

    # Pad if fewer classes than top_k
    while len(recommendations) < top_k:
        recommendations.append({
            "crop_name": f"Crop_{len(recommendations)}",
            "confidence": 0.0,
            "match_reasons": [],
        })

    return recommendations


def _recommend_legacy(
    input_features: Dict[str, Any],
    top_k: int,
    include_shap: bool = False,
) -> List[Dict[str, Any]]:
    """Fallback: inference using the legacy RandomForest + scaler pipeline."""
    model, scaler, idx_to_crop = _get_legacy_artifacts()

    X_raw = pd.DataFrame(
        [[input_features.get(col, 0) for col in LEGACY_FEATURE_COLUMNS]],
        columns=LEGACY_FEATURE_COLUMNS,
    )
    X_scaled = scaler.transform(X_raw)
    X_scaled_df = pd.DataFrame(X_scaled, columns=LEGACY_FEATURE_COLUMNS)

    probs = model.predict_proba(X_scaled_df)[0]
    sorted_indices = np.argsort(probs)[::-1][:top_k]

    recommendations = []
    for idx in sorted_indices:
        crop_name = idx_to_crop.get(idx, f"Unknown_{idx}")
        recommendations.append({
            "crop_name": crop_name,
            "confidence": float(probs[idx]),
            "match_reasons": [],
        })

    while len(recommendations) < top_k:
        recommendations.append({
            "crop_name": f"Crop_{len(recommendations)}",
            "confidence": 0.0,
            "match_reasons": [],
        })

    return recommendations


# ---------------------------------------------------------------------------
# Backward-compat helpers (used by shim + tests)
# ---------------------------------------------------------------------------
def merge_data() -> Tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(TRAIN_DATA_DIR / "crop_recommendation_train.csv")
    if "label_encoded" not in df.columns:
        raise KeyError("'label_encoded' column missing from training data")
    y = df["label_encoded"]
    X = df.drop(columns=["label_encoded", "label"], errors="ignore")
    return X, y


def train_model(X, y) -> RandomForestClassifier:
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    return clf


def load_model_for_training() -> Tuple[RandomForestClassifier, StandardScaler]:
    model, scaler, _ = _get_legacy_artifacts()
    return model, scaler


# ---------------------------------------------------------------------------
# Yield prediction (unchanged from original)
# ---------------------------------------------------------------------------
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
    """Predict crop yield in tons per hectare."""
    yield_model, district_encoder, model_info = _get_yield_model_artifacts()

    df = pd.read_csv(TRAIN_DATA_DIR / "crop_production_processed.csv")

    if state_encoder is None:
        state_encoder = LabelEncoder()
        state_encoder.fit(df['State_Name'].astype(str))

    if crop_encoder is None:
        crop_encoder = LabelEncoder()
        crop_encoder.fit(df['Crop'].astype(str))

    if season_encoder is None:
        season_encoder = LabelEncoder()
        season_encoder.fit(df['Season'].astype(str))

    try:
        state_encoded = state_encoder.transform([state_name])[0]
    except ValueError:
        state_encoded = 0

    try:
        district_encoded = district_encoder.transform([district_name])[0]
    except ValueError:
        district_encoded = 0

    try:
        crop_encoded = crop_encoder.transform([crop_name])[0]
    except ValueError:
        crop_encoded = 0

    try:
        season_encoded = season_encoder.transform([season])[0]
    except ValueError:
        season_encoded = 0

    X = pd.DataFrame([{
        'State_Name_Encoded': state_encoded,
        'District_Encoded': district_encoded,
        'Crop_Encoded': crop_encoded,
        'Season_Encoded': season_encoded,
        'Crop_Year': crop_year
    }])

    yield_pred = yield_model.predict(X)[0]

    return max(0.0, float(yield_pred))