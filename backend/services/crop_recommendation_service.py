"""Crop recommendation service layer.

This service bridges the API layer and the ML inference module.
"""

import sys
import os
# Add project root directory to path for ml imports
# This file is at: backend/services/crop_recommendation_service.py
# Project root is: ../../ (go up 2 levels from backend/services)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from typing import List, Dict, Any
from backend.ml.inference.crop_recommendation import recommend


def recommend_crops(input_features: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
    """Get crop recommendations from the ML inference module.
    
    Args:
        input_features: Dict with keys N, P, K, temperature, humidity, ph, rainfall
        top_k: Number of top recommendations to return
    
    Returns:
        List of recommendation dicts with crop_name, confidence, match_reasons
    """
    # Map API field names (N, P, K) to ML field names (n, p, k)
    mapped_features = {
        'n': input_features.get('N') or input_features.get('n'),
        'p': input_features.get('P') or input_features.get('p'),
        'k': input_features.get('K') or input_features.get('k'),
        'temperature': input_features.get('temperature'),
        'humidity': input_features.get('humidity'),
        'ph': input_features.get('ph'),
        'rainfall': input_features.get('rainfall'),
    }
    
    # Filter out None values
    mapped_features = {k: v for k, v in mapped_features.items() if v is not None}
    
    return recommend(mapped_features, top_k=top_k)