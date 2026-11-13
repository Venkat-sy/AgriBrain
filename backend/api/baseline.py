from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import pandas as pd
from pathlib import Path

from backend.core.config import get_db
from backend.models import District
from backend.schemas import (
    BaselineParametersRequest,
    BaselineParametersResponse,
    BaselineParametersStoreRequest,
    LookupMethod
)

router = APIRouter(prefix="/api/v1/baseline", tags=["baseline"])


# Load master dataset for fallback calculations
def get_master_dataset():
    """Load the master dataset for parameter fallbacks."""
    project_root = Path(__file__).resolve().parents[2]
    master_path = project_root / "datasets" / "All_India_AgriSim_Master_Dataset.csv"
    if master_path.exists():
        return pd.read_csv(master_path)
    return None


def get_rainfall_csv():
    """Load the district-wise rainfall normal CSV."""
    project_root = Path(__file__).resolve().parents[2]
    rainfall_path = project_root / "datasets" / "04_rainfall_india" / "district wise rainfall normal.csv"
    if rainfall_path.exists():
        return pd.read_csv(rainfall_path)
    return None


def find_exact_district(db: Session, district: str, state: str) -> Optional[District]:
    """Find exact district match in database."""
    return db.query(District).filter(
        District.name.ilike(district),
        District.state.ilike(state)
    ).first()


def calculate_state_average(master_df: pd.DataFrame, state: str) -> dict:
    """Calculate average parameters for a state."""
    state_data = master_df[master_df['State'].str.strip().str.lower() == state.strip().lower()]
    if state_data.empty:
        return None
    
    return {
        'n': float(state_data['Soil_Nitrogen_kg_ha_Estimate'].mean()),
        'p': 25.0,  # Default - master dataset doesn't have P
        'k': 180.0,  # Default - master dataset doesn't have K
        'ph': float(state_data['Soil_pH_Estimate'].mean()),
        'temperature_c': 26.5,  # Default
        'humidity_percent': 62.0,  # Default
        'rainfall_mm': 1000.0,  # Will be overridden by rainfall CSV
    }


def calculate_soil_average(master_df: pd.DataFrame, soil_type: str) -> dict:
    """Calculate average parameters for a soil type across all states."""
    # The master dataset doesn't have explicit soil type column, 
    # so we use typical values based on soil type
    soil_defaults = {
        "Black Soil (Regur)": {'n': 300, 'p': 30, 'k': 200, 'ph': 7.5, 'temperature_c': 27.0, 'humidity_percent': 60, 'rainfall_mm': 900},
        "Red Soil (Laterite)": {'n': 200, 'p': 20, 'k': 150, 'ph': 5.5, 'temperature_c': 27.5, 'humidity_percent': 65, 'rainfall_mm': 1100},
        "Alluvial Soil": {'n': 280, 'p': 28, 'k': 180, 'ph': 7.0, 'temperature_c': 26.5, 'humidity_percent': 68, 'rainfall_mm': 1200},
        "Sandy Soil": {'n': 150, 'p': 15, 'k': 100, 'ph': 6.5, 'temperature_c': 28.0, 'humidity_percent': 55, 'rainfall_mm': 700},
        "Clay Soil": {'n': 320, 'p': 35, 'k': 220, 'ph': 7.2, 'temperature_c': 26.0, 'humidity_percent': 70, 'rainfall_mm': 1300},
    }
    
    return soil_defaults.get(soil_type, {
        'n': 250, 'p': 25, 'k': 180, 'ph': 7.0,
        'temperature_c': 26.5, 'humidity_percent': 62, 'rainfall_mm': 1000
    })


def get_rainfall_for_district(rainfall_df: pd.DataFrame, district: str, state: str) -> Optional[float]:
    """Get annual rainfall for a specific district from CSV."""
    if rainfall_df is None:
        return None
    
    # Case-insensitive match
    match = rainfall_df[
        (rainfall_df['DISTRICT'].str.strip().str.lower() == district.strip().lower()) &
        (rainfall_df['STATE_UT_NAME'].str.strip().str.lower() == state.strip().lower())
    ]
    
    if not match.empty:
        annual = match['ANNUAL'].values[0]
        if pd.notna(annual):
            return float(annual)
    return None


@router.post("/parameters", response_model=BaselineParametersResponse)
async def get_baseline_parameters(
    request: BaselineParametersRequest,
    db: Session = Depends(get_db)
):
    """
    Get baseline agricultural parameters with 3-tier fallback strategy:
    Tier 1: Exact district match
    Tier 2: State average
    Tier 3: Soil type average
    """
    master_df = get_master_dataset()
    rainfall_df = get_rainfall_csv()
    
    # Tier 1: Try exact district match
    exact_district = find_exact_district(db, request.district, request.state)
    
    # Also check if district exists in master dataset
    master_df = get_master_dataset()
    if exact_district and master_df is not None:
        # Get parameters from master dataset for this district
        district_data = master_df[
            (master_df['District'].str.strip().str.lower() == request.district.strip().lower()) &
            (master_df['State'].str.strip().str.lower() == request.state.strip().lower())
        ]
        
        if not district_data.empty:
            # Get rainfall from CSV
            rainfall = get_rainfall_for_district(rainfall_df, request.district, request.state)
            if rainfall is None:
                rainfall = 1000.0  # Default
            
            params = {
                'n': float(district_data['Soil_Nitrogen_kg_ha_Estimate'].mean()),
                'p': 25.0,  # Default - master dataset doesn't have P
                'k': 180.0,  # Default - master dataset doesn't have K
                'ph': float(district_data['Soil_pH_Estimate'].mean()),
                'temperature_c': 26.5,
                'humidity_percent': 62.0,
                'rainfall_mm': rainfall,
                'district': request.district,
                'state': request.state,
                'soil_type': request.soil_type,
                'lookup_method': LookupMethod.EXACT
            }
            return BaselineParametersResponse(**params)
    
    # Tier 2: State average fallback
    if master_df is not None:
        state_avg = calculate_state_average(master_df, request.state)
        if state_avg:
            # Try to get state average rainfall
            rainfall = get_state_average_rainfall(rainfall_df, request.state)
            if rainfall is None:
                rainfall = state_avg['rainfall_mm']
            
            params = {
                **state_avg,
                'rainfall_mm': rainfall,
                'district': request.district,
                'state': request.state,
                'soil_type': request.soil_type,
                'lookup_method': LookupMethod.STATE_AVERAGE
            }
            return BaselineParametersResponse(**params)
    
    # Tier 3: Soil type average fallback
    soil_avg = calculate_soil_average(master_df, request.soil_type)
    if soil_avg:
        # Try to get state average rainfall even for soil fallback
        rainfall = get_state_average_rainfall(rainfall_df, request.state)
        if rainfall is None:
            rainfall = soil_avg['rainfall_mm']
        
        params = {
            **soil_avg,
            'rainfall_mm': rainfall,
            'district': request.district,
            'state': request.state,
            'soil_type': request.soil_type,
            'lookup_method': LookupMethod.SOIL_AVERAGE
        }
        return BaselineParametersResponse(**params)
    
    # Ultimate fallback - should never reach here
    raise HTTPException(
        status_code=404,
        detail="Unable to determine baseline parameters for the given location and soil type"
    )


@router.post("/store", response_model=BaselineParametersResponse)
async def store_baseline_parameters(
    request: BaselineParametersStoreRequest,
    db: Session = Depends(get_db)
):
    """
    Store baseline parameters for a district/soil combination.
    This would typically update a dedicated table, but for now returns the input.
    """
    # In a full implementation, this would store to a database table
    # For now, just echo back with exact lookup method
    return BaselineParametersResponse(
        n=request.n,
        p=request.p,
        k=request.k,
        ph=request.ph,
        temperature_c=request.temperature_c,
        humidity_percent=request.humidity_percent,
        rainfall_mm=request.rainfall_mm,
        district=request.district,
        state=request.state,
        soil_type=request.soil_type,
        lookup_method=LookupMethod.EXACT
    )


@router.get("/states")
async def get_available_states(
    db: Session = Depends(get_db)
):
    """Get list of available states from the database."""
    states = db.query(District.state).distinct().all()
    return {"states": sorted([s[0] for s in states if s[0]])}


@router.get("/districts")
async def get_districts_by_state(
    state: str = Query(..., description="State name"),
    db: Session = Depends(get_db)
):
    """Get list of districts for a given state."""
    districts = db.query(District.name).filter(District.state.ilike(f"%{state}%")).all()
    return {"districts": sorted([d[0] for d in districts if d[0]])}
def get_state_average_rainfall(rainfall_df: pd.DataFrame, state: str) -> Optional[float]:
    """Get average rainfall for a state from CSV."""
    if rainfall_df is None:
        return None
    
    state_data = rainfall_df[
        rainfall_df['STATE_UT_NAME'].str.strip().str.lower() == state.strip().lower()
    ]
    
    if not state_data.empty:
        avg_rainfall = state_data['ANNUAL'].mean()
        if pd.notna(avg_rainfall):
            return float(avg_rainfall)
    return None