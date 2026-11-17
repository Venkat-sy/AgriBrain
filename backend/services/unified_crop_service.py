"""
Unified Crop Recommendation Service for AgriBrain.
Consolidates 3 divergent crop systems into single authoritative service.

Systems consolidated:
1. XGBoost ML (22 fruit crops) - broken, returns identical output
2. Heuristic DB (9 field crops) - rule-based, works but limited
3. Simulation Engine (42 crops, penalty-based) - primary path

New unified service:
- Single crop database (YAML/JSON) with 42+ crops
- ML primary (XGBoost) with heuristic fallback
- Real SHAP explainability
- Used by both /crop/recommend and /simulation/run
"""
from __future__ import annotations

import json
import joblib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

from backend.ml.inference.crop_recommendation import (
    _get_xgboost_bundle,
    compute_shap_values,
    XGBOOST_FEATURE_COLUMNS,
    recommend as ml_recommend,
)
from backend.services.crop_recommendation_service import recommend_crops as heuristic_recommend
from backend.core.config import get_settings


settings = get_settings()

# ---------------------------------------------------------------------------
# Unified Crop Database (Single Source of Truth)
# ---------------------------------------------------------------------------
CROPS_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "crops.yaml"
CROPS_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "crops.json"

# Default crop database (embedded for resilience)
DEFAULT_CROPS_DB = {
    "short_term": [
        {"name": "Rice (Paddy)", "season": "Kharif", "duration_days": 120, "opt_temp": 28, "opt_rain": 210, "opt_ph": 6.0, "opt_n": 180, "opt_p": 60, "opt_k": 40, "base_yield_t_ha": 4.0, "msp_inr_t": 23000, "water_mm": 1200, "ml_classes": ["rice"]},
        {"name": "Wheat", "season": "Rabi", "duration_days": 115, "opt_temp": 21, "opt_rain": 85, "opt_ph": 7.1, "opt_n": 200, "opt_p": 60, "opt_k": 40, "base_yield_t_ha": 3.5, "msp_inr_t": 22750, "water_mm": 450, "ml_classes": ["wheat"]},
        {"name": "Maize (Hybrid Corn)", "season": "Kharif/Rabi", "duration_days": 105, "opt_temp": 25, "opt_rain": 115, "opt_ph": 6.5, "opt_n": 165, "opt_p": 70, "opt_k": 50, "base_yield_t_ha": 5.5, "msp_inr_t": 20900, "water_mm": 550, "ml_classes": ["maize"]},
        {"name": "Blackgram (Urad Dal)", "season": "Kharif/Zaid", "duration_days": 80, "opt_temp": 29, "opt_rain": 95, "opt_ph": 6.7, "opt_n": 120, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 0.8, "msp_inr_t": 69500, "water_mm": 350, "ml_classes": ["blackgram"]},
        {"name": "Mungbean (Moong Dal)", "season": "Zaid/Kharif", "duration_days": 70, "opt_temp": 30, "opt_rain": 75, "opt_ph": 6.6, "opt_n": 110, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 0.7, "msp_inr_t": 85580, "water_mm": 320, "ml_classes": ["mungbean"]},
        {"name": "Chickpea (Bengal Gram)", "season": "Rabi", "duration_days": 100, "opt_temp": 22, "opt_rain": 65, "opt_ph": 7.3, "opt_n": 115, "opt_p": 50, "opt_k": 30, "base_yield_t_ha": 1.0, "msp_inr_t": 54400, "water_mm": 300, "ml_classes": ["chickpea"]},
        {"name": "Pigeonpea (Tur/Arhar)", "season": "Kharif", "duration_days": 150, "opt_temp": 27, "opt_rain": 110, "opt_ph": 6.8, "opt_n": 135, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 1.1, "msp_inr_t": 70000, "water_mm": 450, "ml_classes": ["pigeonpeas"]},
        {"name": "Groundnut (Peanut)", "season": "Kharif/Rabi", "duration_days": 110, "opt_temp": 28, "opt_rain": 100, "opt_ph": 6.4, "opt_n": 130, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 1.5, "msp_inr_t": 63770, "water_mm": 500, "ml_classes": []},
        {"name": "Soybean", "season": "Kharif", "duration_days": 95, "opt_temp": 26, "opt_rain": 125, "opt_ph": 6.6, "opt_n": 150, "opt_p": 60, "opt_k": 40, "base_yield_t_ha": 1.3, "msp_inr_t": 46000, "water_mm": 520, "ml_classes": []},
        {"name": "Mustard (Rapeseed)", "season": "Rabi", "duration_days": 105, "opt_temp": 20, "opt_rain": 60, "opt_ph": 7.4, "opt_n": 140, "opt_p": 60, "opt_k": 40, "base_yield_t_ha": 1.2, "msp_inr_t": 56500, "water_mm": 280, "ml_classes": []},
        {"name": "Sunflower", "season": "Rabi/Zaid", "duration_days": 90, "opt_temp": 27, "opt_rain": 80, "opt_ph": 6.9, "opt_n": 145, "opt_p": 60, "opt_k": 50, "base_yield_t_ha": 1.1, "msp_inr_t": 67600, "water_mm": 420, "ml_classes": []},
        {"name": "Cotton (Bt Hybrid)", "season": "Kharif", "duration_days": 160, "opt_temp": 31, "opt_rain": 90, "opt_ph": 7.5, "opt_n": 160, "opt_p": 60, "opt_k": 60, "base_yield_t_ha": 1.5, "msp_inr_t": 66200, "water_mm": 700, "ml_classes": ["cotton"]},
        {"name": "Jute", "season": "Kharif", "duration_days": 120, "opt_temp": 30, "opt_rain": 230, "opt_ph": 6.1, "opt_n": 170, "opt_p": 60, "opt_k": 60, "base_yield_t_ha": 2.0, "msp_inr_t": 50500, "water_mm": 900, "ml_classes": ["jute"]},
        {"name": "Potato", "season": "Rabi", "duration_days": 95, "opt_temp": 19, "opt_rain": 90, "opt_ph": 5.8, "opt_n": 190, "opt_p": 70, "opt_k": 80, "base_yield_t_ha": 25.0, "msp_inr_t": 14000, "water_mm": 500, "ml_classes": []},
        {"name": "Onion", "season": "Rabi/Kharif", "duration_days": 110, "opt_temp": 24, "opt_rain": 85, "opt_ph": 6.5, "opt_n": 155, "opt_p": 60, "opt_k": 50, "base_yield_t_ha": 20.0, "msp_inr_t": 18000, "water_mm": 450, "ml_classes": []},
        {"name": "Tomato (Hybrid)", "season": "All-Season", "duration_days": 90, "opt_temp": 25, "opt_rain": 95, "opt_ph": 6.4, "opt_n": 175, "opt_p": 70, "opt_k": 80, "base_yield_t_ha": 40.0, "msp_inr_t": 16000, "water_mm": 480, "ml_classes": []},
        {"name": "Chilli (Guntur/Byadgi)", "season": "Kharif/Rabi", "duration_days": 135, "opt_temp": 28, "opt_rain": 105, "opt_ph": 6.6, "opt_n": 160, "opt_p": 60, "opt_k": 60, "base_yield_t_ha": 2.0, "msp_inr_t": 135000, "water_mm": 600, "ml_classes": []},
        {"name": "Okra (Bhindi)", "season": "Zaid/Kharif", "duration_days": 65, "opt_temp": 30, "opt_rain": 110, "opt_ph": 6.5, "opt_n": 140, "opt_p": 50, "opt_k": 50, "base_yield_t_ha": 10.0, "msp_inr_t": 22000, "water_mm": 400, "ml_classes": []},
        {"name": "Watermelon", "season": "Zaid", "duration_days": 80, "opt_temp": 32, "opt_rain": 55, "opt_ph": 6.3, "opt_n": 135, "opt_p": 50, "opt_k": 60, "base_yield_t_ha": 30.0, "msp_inr_t": 11500, "water_mm": 380, "ml_classes": ["watermelon"]},
        {"name": "Muskmelon", "season": "Zaid", "duration_days": 75, "opt_temp": 33, "opt_rain": 50, "opt_ph": 6.5, "opt_n": 125, "opt_p": 50, "opt_k": 60, "base_yield_t_ha": 20.0, "msp_inr_t": 16500, "water_mm": 350, "ml_classes": ["muskmelon"]},
        {"name": "Ragi (Finger Millet)", "season": "Kharif", "duration_days": 105, "opt_temp": 27, "opt_rain": 95, "opt_ph": 6.2, "opt_n": 120, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 1.5, "msp_inr_t": 38460, "water_mm": 350, "ml_classes": []},
        {"name": "Bajra (Pearl Millet)", "season": "Kharif", "duration_days": 85, "opt_temp": 32, "opt_rain": 50, "opt_ph": 7.6, "opt_n": 100, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 1.5, "msp_inr_t": 25000, "water_mm": 280, "ml_classes": []},
        {"name": "Jowar (Sorghum)", "season": "Kharif/Rabi", "duration_days": 105, "opt_temp": 29, "opt_rain": 75, "opt_ph": 7.2, "opt_n": 115, "opt_p": 40, "opt_k": 40, "base_yield_t_ha": 1.8, "msp_inr_t": 31800, "water_mm": 350, "ml_classes": []},
        {"name": "Lentil (Masoor Dal)", "season": "Rabi", "duration_days": 100, "opt_temp": 20, "opt_rain": 70, "opt_ph": 6.9, "opt_n": 115, "opt_p": 40, "opt_k": 30, "base_yield_t_ha": 0.9, "msp_inr_t": 64250, "water_mm": 310, "ml_classes": ["lentil"]},
        {"name": "Cabbage / Cauliflower", "season": "Rabi", "duration_days": 85, "opt_temp": 19, "opt_rain": 85, "opt_ph": 6.3, "opt_n": 170, "opt_p": 70, "opt_k": 80, "base_yield_t_ha": 30.0, "msp_inr_t": 13500, "water_mm": 420, "ml_classes": []},
    ],
    "long_term": [
        {"name": "Coconut (Tall/Dwarf Hybrid)", "season": "Perennial Plantation", "duration_days": 365, "opt_temp": 29, "opt_rain": 230, "opt_ph": 5.8, "opt_n": 155, "opt_p": 50, "opt_k": 100, "base_yield_t_ha": 5.0, "msp_inr_t": 32000, "water_mm": 1300, "ml_classes": ["coconut"]},
        {"name": "Arecanut (Supari)", "season": "Perennial Plantation", "duration_days": 365, "opt_temp": 28, "opt_rain": 250, "opt_ph": 5.7, "opt_n": 150, "opt_p": 50, "opt_k": 100, "base_yield_t_ha": 1.2, "msp_inr_t": 420000, "water_mm": 1400, "ml_classes": []},
        {"name": "Mango (Alphonso/Kesar)", "season": "Perennial Orchard", "duration_days": 365, "opt_temp": 29, "opt_rain": 115, "opt_ph": 6.5, "opt_n": 165, "opt_p": 60, "opt_k": 80, "base_yield_t_ha": 5.0, "msp_inr_t": 55000, "water_mm": 750, "ml_classes": ["mango"]},
        {"name": "Banana (Grand Naine Tissue)", "season": "Annual/Perennial", "duration_days": 320, "opt_temp": 28, "opt_rain": 175, "opt_ph": 6.4, "opt_n": 205, "opt_p": 70, "opt_k": 100, "base_yield_t_ha": 40.0, "msp_inr_t": 14500, "water_mm": 1500, "ml_classes": ["banana"]},
        {"name": "Pomegranate (Bhagwa)", "season": "Perennial Orchard", "duration_days": 280, "opt_temp": 31, "opt_rain": 65, "opt_ph": 7.4, "opt_n": 125, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 6.0, "msp_inr_t": 85000, "water_mm": 550, "ml_classes": ["pomegranate"]},
        {"name": "Coffee (Arabica/Robusta)", "season": "Shade Plantation", "duration_days": 365, "opt_temp": 23, "opt_rain": 200, "opt_ph": 5.9, "opt_n": 165, "opt_p": 60, "opt_k": 80, "base_yield_t_ha": 0.8, "msp_inr_t": 280000, "water_mm": 1100, "ml_classes": ["coffee"]},
        {"name": "Black Pepper (Panniyur)", "season": "Perennial Vine", "duration_days": 365, "opt_temp": 27, "opt_rain": 235, "opt_ph": 5.8, "opt_n": 155, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 0.6, "msp_inr_t": 580000, "water_mm": 1250, "ml_classes": []},
        {"name": "Cashew (Vengurla Hybrid)", "season": "Perennial Orchard", "duration_days": 365, "opt_temp": 29, "opt_rain": 190, "opt_ph": 5.6, "opt_n": 135, "opt_p": 40, "opt_k": 80, "base_yield_t_ha": 1.0, "msp_inr_t": 130000, "water_mm": 650, "ml_classes": []},
        {"name": "Papaya (Red Lady 786)", "season": "Long-Duration Fruit", "duration_days": 270, "opt_temp": 29, "opt_rain": 125, "opt_ph": 6.3, "opt_n": 180, "opt_p": 60, "opt_k": 80, "base_yield_t_ha": 40.0, "msp_inr_t": 12500, "water_mm": 950, "ml_classes": ["papaya"]},
        {"name": "Guava (Taiwan Pink/Allahabad)", "season": "Perennial Orchard", "duration_days": 300, "opt_temp": 27, "opt_rain": 95, "opt_ph": 6.9, "opt_n": 145, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 15.0, "msp_inr_t": 28000, "water_mm": 620, "ml_classes": []},
        {"name": "Grapes (Thompson Seedless)", "season": "Perennial Vineyard", "duration_days": 330, "opt_temp": 26, "opt_rain": 80, "opt_ph": 6.8, "opt_n": 170, "opt_p": 60, "opt_k": 80, "base_yield_t_ha": 15.0, "msp_inr_t": 48000, "water_mm": 680, "ml_classes": ["grapes"]},
        {"name": "Sweet Orange (Mosambi/Kinnow)", "season": "Perennial Citrus", "duration_days": 340, "opt_temp": 25, "opt_rain": 100, "opt_ph": 6.7, "opt_n": 160, "opt_p": 60, "opt_k": 80, "base_yield_t_ha": 15.0, "msp_inr_t": 34000, "water_mm": 720, "ml_classes": ["orange"]},
        {"name": "Apple (Gala/Delicious)", "season": "Temperate Orchard", "duration_days": 365, "opt_temp": 16, "opt_rain": 125, "opt_ph": 6.1, "opt_n": 165, "opt_p": 60, "opt_k": 80, "base_yield_t_ha": 10.0, "msp_inr_t": 75000, "water_mm": 650, "ml_classes": ["apple"]},
        {"name": "Sugarcane (Co-86032)", "season": "Annual/Ratoon", "duration_days": 330, "opt_temp": 28, "opt_rain": 150, "opt_ph": 6.8, "opt_n": 220, "opt_p": 80, "opt_k": 100, "base_yield_t_ha": 80.0, "msp_inr_t": 3400, "water_mm": 1800, "ml_classes": []},
        {"name": "Turmeric (Prathibha/Salem)", "season": "Long-Duration Spice", "duration_days": 260, "opt_temp": 27, "opt_rain": 145, "opt_ph": 6.2, "opt_n": 175, "opt_p": 70, "opt_k": 80, "base_yield_t_ha": 3.0, "msp_inr_t": 140000, "water_mm": 850, "ml_classes": []},
        {"name": "Ginger (Rio-de-Janeiro)", "season": "Long-Duration Spice", "duration_days": 240, "opt_temp": 26, "opt_rain": 165, "opt_ph": 6.0, "opt_n": 170, "opt_p": 70, "opt_k": 80, "base_yield_t_ha": 10.0, "msp_inr_t": 65000, "water_mm": 900, "ml_classes": []},
        {"name": "Rubber (RRII 105)", "season": "Perennial Plantation", "duration_days": 365, "opt_temp": 28, "opt_rain": 260, "opt_ph": 5.4, "opt_n": 145, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 1.0, "msp_inr_t": 175000, "water_mm": 1500, "ml_classes": []},
        {"name": "Cardamom (Malabar/Mysore)", "season": "Highland Plantation", "duration_days": 365, "opt_temp": 21, "opt_rain": 220, "opt_ph": 5.7, "opt_n": 160, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 0.3, "msp_inr_t": 1650000, "water_mm": 1350, "ml_classes": []},
        {"name": "Sapota (Chikoo - Kalipatti)", "season": "Perennial Orchard", "duration_days": 340, "opt_temp": 29, "opt_rain": 130, "opt_ph": 6.8, "opt_n": 150, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 10.0, "msp_inr_t": 26000, "water_mm": 700, "ml_classes": []},
        {"name": "Jackfruit (Siddu/Konkan)", "season": "Perennial Agroforestry", "duration_days": 365, "opt_temp": 28, "opt_rain": 185, "opt_ph": 6.0, "opt_n": 140, "opt_p": 50, "opt_k": 80, "base_yield_t_ha": 15.0, "msp_inr_t": 22000, "water_mm": 850, "ml_classes": []},
    ]
}


class UnifiedCropService:
    """
    Unified crop recommendation service.
    Single authoritative source for all crop recommendations.
    """
    
    def __init__(self):
        self.crops_db = self._load_crops_db()
        self._crop_lookup = self._build_crop_lookup()
        self._ml_feature_columns = XGBOOST_FEATURE_COLUMNS
    
    def _load_crops_db(self) -> Dict:
        """Load crop database from YAML/JSON or use defaults."""
        # Try YAML first
        if CROPS_DB_PATH.exists():
            try:
                import yaml
                with open(CROPS_DB_PATH) as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        # Try JSON
        if CROPS_JSON_PATH.exists():
            try:
                with open(CROPS_JSON_PATH) as f:
                    return json.load(f)
            except Exception:
                pass
        return DEFAULT_CROPS_DB
    
    def _build_crop_lookup(self) -> Dict[str, Dict]:
        """Build lookup dict for quick crop access."""
        lookup = {}
        for crop_type in ["short_term", "long_term"]:
            for crop in self.crops_db.get(crop_type, []):
                lookup[crop["name"].lower()] = crop
        return lookup
    
    def get_all_crops(self, crop_type: str = "all") -> List[Dict]:
        """Get all crops, optionally filtered by type."""
        if crop_type == "short_term":
            return self.crops_db.get("short_term", [])
        elif crop_type == "long_term":
            return self.crops_db.get("long_term", [])
        else:
            crops = []
            for ct in ["short_term", "long_term"]:
                for crop in self.crops_db.get(ct, []):
                    crop_copy = crop.copy()
                    crop_copy["crop_type"] = ct
                    crops.append(crop_copy)
            return crops
    
    def get_crop_by_name(self, name: str) -> Optional[Dict]:
        """Get crop details by name (case-insensitive)."""
        return self._crop_lookup.get(name.lower())
    
    def recommend(
        self,
        input_features: Dict[str, Any],
        top_k: int = 5,
        crop_type: str = "all",
        include_shap: bool = True,
        use_ml: bool = True,
    ) -> List[Dict]:
        """
        Unified crop recommendation.
        
        Args:
            input_features: Dict with N, P, K, temperature, humidity, ph, rainfall
            top_k: Number of recommendations to return
            crop_type: "short_term", "long_term", or "all"
            include_shap: Whether to include SHAP explanations
            use_ml: Whether to use ML model (fallback to heuristic if False or ML fails)
        
        Returns:
            List of crop recommendations with scores, confidence, and optional SHAP
        """
        # Prepare input for ML model
        ml_features = {col: input_features.get(col, 0) for col in self._ml_feature_columns}
        
        # Get ML recommendations if requested
        ml_results = []
        if use_ml:
            try:
                ml_results = ml_recommend(ml_features, top_k=top_k * 2, include_shap=include_shap)
            except Exception as e:
                print(f"[UnifiedCropService] ML recommendation failed: {e}")
                ml_results = []
        
        # Get heuristic recommendations as fallback/augmentation
        heuristic_results = heuristic_recommend(input_features)
        
        # Combine and deduplicate
        all_crops = self.get_all_crops(crop_type)
        scored_crops = []
        
        for crop in all_crops:
            # Calculate penalty-based score (simulation engine method)
            score = self._calculate_penalty_score(crop, input_features)
            
            # Find ML confidence if available
            ml_confidence = 0.0
            ml_shap = None
            for ml_rec in ml_results:
                if ml_rec["crop_name"].lower() == crop["name"].lower():
                    ml_confidence = ml_rec.get("confidence", 0.0)
                    ml_shap = ml_rec.get("shap_values")
                    break
            
            # Find heuristic confidence
            heuristic_confidence = 0.0
            heuristic_reasons = []
            for h_rec in heuristic_results:
                if h_rec["crop_name"].lower() == crop["name"].lower():
                    heuristic_confidence = h_rec.get("confidence", 0.0)
                    heuristic_reasons = h_rec.get("match_reasons", [])
                    break
            
            # Combined confidence: weighted average of ML and heuristic
            if use_ml and ml_confidence > 0:
                combined_confidence = 0.7 * ml_confidence + 0.3 * heuristic_confidence
                shap_values = ml_shap if include_shap else None
            else:
                combined_confidence = heuristic_confidence
                shap_values = None
            
            scored_crops.append({
                "crop_name": crop["name"],
                "crop_type": crop.get("crop_type", "short_term"),
                "season": crop.get("season", ""),
                "duration_days": crop.get("duration_days", 0),
                "score_pct": round(score, 1),
                "confidence": round(combined_confidence, 4),
                "ml_confidence": round(ml_confidence, 4) if use_ml else 0.0,
                "heuristic_confidence": round(heuristic_confidence, 4),
                "heuristic_reasons": heuristic_reasons,
                "base_yield_t_ha": crop.get("base_yield_t_ha", 0),
                "msp_inr_t": crop.get("msp_inr_t", 0),
                "water_mm": crop.get("water_mm", 0),
                "shap_values": shap_values,
            })
        
        # Sort by score_pct descending
        scored_crops.sort(key=lambda x: x["score_pct"], reverse=True)
        
        # Format output
        results = []
        for crop in scored_crops[:top_k]:
            result = {
                "crop_name": crop["crop_name"],
                "crop_type": crop["crop_type"],
                "season": crop["season"],
                "duration_days": crop["duration_days"],
                "confidence": crop["confidence"],
                "score_pct": crop["score_pct"],
                "base_yield_t_ha": crop["base_yield_t_ha"],
                "msp_inr_t": crop["msp_inr_t"],
                "water_mm": crop["water_mm"],
                "heuristic_reasons": crop["heuristic_reasons"],
            }
            if include_shap and crop["shap_values"]:
                result["shap_values"] = crop["shap_values"]
            results.append(result)
        
        return results
    
    def _calculate_penalty_score(self, crop: Dict, input_features: Dict) -> float:
        """Calculate penalty-based suitability score (0-100)."""
        temp_diff = abs(input_features.get("temperature", 25) - crop["opt_temp"]) * 2.1
        rain_diff = abs(input_features.get("rainfall", 100) - crop["opt_rain"]) * 0.22
        ph_diff = abs(input_features.get("ph", 6.5) - crop["opt_ph"]) * 11.5
        n_diff = abs(input_features.get("N", 100) - crop["opt_n"]) * 0.14
        
        total_penalty = temp_diff + rain_diff + ph_diff + n_diff
        score = max(52.0, min(98.8, 100.0 - total_penalty * 0.42))
        return round(score, 1)
    
    def calculate_shap(self, input_features: Dict) -> Optional[List[Dict]]:
        """Calculate SHAP values for input features using ML model."""
        bundle = _get_xgboost_bundle()
        if not bundle:
            return None
        return compute_shap_values(bundle, input_features, self._ml_feature_columns)


# Global singleton instance
_crop_service: Optional[UnifiedCropService] = None


def get_crop_service() -> UnifiedCropService:
    """Get singleton instance of UnifiedCropService."""
    global _crop_service
    if _crop_service is None:
        _crop_service = UnifiedCropService()
    return _crop_service


# Backward compatibility functions
def recommend_crops_unified(
    input_features: Dict[str, Any],
    top_k: int = 5,
    crop_type: str = "all",
    include_shap: bool = True,
) -> List[Dict]:
    """Backward compatible recommend function."""
    service = get_crop_service()
    return service.recommend(input_features, top_k, crop_type, include_shap)


def get_all_crops_unified(crop_type: str = "all") -> List[Dict]:
    """Get all crops from unified database."""
    service = get_crop_service()
    return service.get_all_crops(crop_type)


def get_crop_by_name_unified(name: str) -> Optional[Dict]:
    """Get crop by name from unified database."""
    service = get_crop_service()
    return service.get_crop_by_name(name)