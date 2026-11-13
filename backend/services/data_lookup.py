
"""
3-Tier Data Lookup Service for AgriBrain.

Provides soil and climate data with fallback hierarchy:
- Tier 1: Exact district match from india_soilgrids_subset.csv
- Tier 2: State-level average for missing districts
- Tier 3: National soil-type baseline averages

Returns explicit keys: N, P, K, ph, temperature, humidity, rainfall, fallback_tier
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Path to the SoilGrids subset CSV
DATA_DIR = Path(__file__).resolve().parents[3] / "datasets"
SOILGRIDS_CSV = DATA_DIR / "india_soilgrids_subset.csv"

# District to coordinates mapping (simplified - in production use geocoding)
# This would normally come from a district boundary file
DISTRICT_COORDS = {
    # Tamil Nadu
    "Erode": (11.3410, 77.7172),
    "Coimbatore": (11.0168, 76.9558),
    "Salem": (11.6643, 78.1460),
    "Madurai": (9.9252, 78.1198),
    "Tiruchirappalli": (10.7905, 78.7047),
    # Haryana
    "Karnal": (29.6857, 76.9905),
    # Punjab
    "Ludhiana": (30.9010, 75.8573),
    "Amritsar": (31.6340, 74.8723),
    # Maharashtra
    "Nashik": (19.9975, 73.7898),
    "Ahmednagar": (19.0948, 74.7480),
    # Add more as needed
}

# State to districts mapping for Tier 2 fallback
STATE_DISTRICTS = {
    "Tamil Nadu": ["Erode", "Coimbatore", "Salem", "Madurai", "Tiruchirappalli"],
    "Haryana": ["Karnal"],
    "Punjab": ["Ludhiana", "Amritsar"],
    "Maharashtra": ["Nashik", "Ahmednagar"],
}

# National baseline values (fallback Tier 3)
NATIONAL_BASELINES = {
    "Alluvial Soil": {"N": 250, "P": 25, "K": 200, "ph": 7.0, "temperature": 27, "humidity": 65, "rainfall": 1000},
    "Black Soil (Regur)": {"N": 200, "P": 20, "K": 300, "ph": 8.0, "temperature": 28, "humidity": 60, "rainfall": 800},
    "Red Soil": {"N": 150, "P": 15, "K": 150, "ph": 6.0, "temperature": 28, "humidity": 65, "rainfall": 900},
    "Laterite Soil": {"N": 100, "P": 10, "K": 100, "ph": 5.0, "temperature": 27, "humidity": 75, "rainfall": 2000},
    "Desert Soil": {"N": 50, "P": 5, "K": 100, "ph": 8.5, "temperature": 30, "humidity": 30, "rainfall": 300},
    "Mountain Soil": {"N": 200, "P": 20, "K": 180, "ph": 6.5, "temperature": 20, "humidity": 70, "rainfall": 1500},
    "Peaty & Marshy Soil": {"N": 300, "P": 30, "K": 250, "ph": 5.5, "temperature": 25, "humidity": 80, "rainfall": 1800},
}

# Load the SoilGrids data once at module import
_SOILGRIDS_DF = None

def _load_soilgrids() -> pd.DataFrame:
    """Load and cache the SoilGrids CSV."""
    global _SOILGRIDS_DF
    if _SOILGRIDS_DF is None:
        if SOILGRIDS_CSV.exists():
            _SOILGRIDS_DF = pd.read_csv(SOILGRIDS_CSV)
            logger.info(f"Loaded SoilGrids data: {len(_SOILGRIDS_DF)} records")
        else:
            logger.warning(f"SoilGrids CSV not found at {SOILGRIDS_CSV}")
            _SOILGRIDS_DF = pd.DataFrame()
    return _SOILGRIDS_DF

def _find_nearest_grid(lat: float, lon: float, df: pd.DataFrame) -> Optional[pd.Series]:
    """Find the nearest grid point in SoilGrids data to given coordinates."""
    if df.empty:
        return None
    # Calculate Euclidean distance (approximate for lat/lon)
    df = df.copy()
    df['distance'] = np.sqrt((df['latitude'] - lat)**2 + (df['longitude'] - lon)**2)
    nearest = df.loc[df['distance'].idxmin()]
    return nearest

def _convert_soilgrids_to_npk(row: pd.Series) -> Dict[str, float]:
    """Convert SoilGrids raw columns to N, P, K, pH, etc."""
    # SoilGrids columns: soc_0_5cm_dg_kg (soil organic carbon), phh2o_0_5cm (pH), clay_0_5cm_g_kg (clay %)
    # Approximate conversions based on standard pedotransfer functions
    soc = row.get('soc_0_5cm_dg_kg', 100)  # g/kg
    ph = row.get('phh2o_0_5cm', 7.0)
    clay = row.get('clay_0_5cm_g_kg', 200)  # g/kg
    
    # Rough estimates from SOC and clay content
    # N ≈ SOC * 0.1 (assuming C:N ratio ~10)
    n = soc * 0.1 * 10  # Convert to kg/ha (approximate)
    # P and K are harder to estimate from SoilGrids alone; use clay-based estimates
    p = max(10, clay * 0.1)  # Approximate
    k = max(50, clay * 0.8)  # Approximate
    
    return {
        "N": round(n, 1),
        "P": round(p, 1),
        "K": round(k, 1),
        "ph": round(ph, 1),
    }

def get_soil_data(district: str, state: str, soil_type: str = "Alluvial Soil") -> Dict[str, Any]:
    """
    Get soil and climate data for a district with 3-tier fallback.
    
    Returns:
        Dict with keys: N, P, K, ph, temperature, humidity, rainfall, fallback_tier
    """
    df = _load_soilgrids()
    
    # Tier 1: Exact district match via coordinates
    if district in DISTRICT_COORDS:
        lat, lon = DISTRICT_COORDS[district]
        nearest = _find_nearest_grid(lat, lon, df)
        if nearest is not None:
            result = _convert_soilgrids_to_npk(nearest)
            # Add climate estimates (would come from separate climate data in production)
            result.update({
                "temperature": 27.0,
                "humidity": 65.0,
                "rainfall": 800.0,
                "fallback_tier": 1
            })
            logger.info(f"Tier 1 match for {district}, {state}")
            return result
    
    # Tier 2: State-level average
    state_districts = STATE_DISTRICTS.get(state, [])
    if state_districts:
        coords = [DISTRICT_COORDS.get(d) for d in state_districts if d in DISTRICT_COORDS]
        if coords:
            vals = []
            for lat, lon in coords:
                nearest = _find_nearest_grid(lat, lon, df)
                if nearest is not None:
                    vals.append(_convert_soilgrids_to_npk(nearest))
            if vals:
                avg = {}
                for key in ["N", "P", "K", "ph"]:
                    avg[key] = round(np.mean([v[key] for v in vals]), 1)
                avg.update({
                    "temperature": 27.0,
                    "humidity": 65.0,
                    "rainfall": 800.0,
                    "fallback_tier": 2
                })
                logger.info(f"Tier 2 (state avg) for {district}, {state}")
                return avg
    
    # Tier 3: National soil-type baseline
    baseline = NATIONAL_BASELINES.get(soil_type, NATIONAL_BASELINES["Alluvial Soil"])
    result = baseline.copy()
    result["fallback_tier"] = 3
    logger.info(f"Tier 3 (national baseline) for soil_type={soil_type}")
    return result