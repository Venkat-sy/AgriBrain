"""
Live Market Pricing Service
Fetches real-time market prices from DataGov API for ROI calculations.
"""
import os
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, date
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

logger = logging.getLogger(__name__)

# DataGov API endpoint for market prices
DATAGOV_MARKET_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# Fallback baseline prices (INR per quintal) - converted to per ton by multiplying by 10
# These are approximate modal prices for major crops in India
BASELINE_PRICES_PER_QUINTAL: Dict[str, float] = {
    "Rice": 2000,
    "Wheat": 2200,
    "Maize": 1800,
    "Cotton": 5500,
    "Sugarcane": 300,
    "Soybean": 4500,
    "Groundnut": 5500,
    "Mustard": 5000,
    "Chickpea": 5000,
    "Pigeonpea": 6000,
    "Mungbean": 7000,
    "Urad": 6500,
    "Bajra": 2200,
    "Jowar": 2800,
    "Barley": 2000,
    "Sunflower": 5800,
    "Sesame": 7500,
    "Niger": 6000,
    "Safflower": 5500,
    "Linseed": 5500,
    "Castor": 5000,
    "Coconut": 2500,
    "Oil Palm": 1000,
    "Tobacco": 15000,
    "Jute": 4200,
    "Mesta": 3500,
    "Tea": 25000,
    "Coffee": 20000,
    "Rubber": 15000,
    "Potato": 1500,
    "Onion": 1800,
    "Tomato": 2000,
    "Banana": 2000,
    "Mango": 4000,
    "Citrus": 3000,
    "Grapes": 5000,
    "Apple": 6000,
    "Pomegranate": 5000,
    "Papaya": 2500,
    "Guava": 3000,
    "Sapota": 2000,
    "Cabbage": 1500,
    "Cauliflower": 1800,
    "Brinjal": 1500,
    "Okra": 2000,
    "Peas": 3000,
    "Beans": 3500,
}

# State name mapping for API (API uses specific state names)
STATE_MAPPING = {
    "Andhra Pradesh": "Andhra Pradesh",
    "Arunachal Pradesh": "Arunachal Pradesh",
    "Assam": "Assam",
    "Bihar": "Bihar",
    "Chhattisgarh": "Chhattisgarh",
    "Goa": "Goa",
    "Gujarat": "Gujarat",
    "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal Pradesh",
    "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka",
    "Kerala": "Kerala",
    "Madhya Pradesh": "Madhya Pradesh",
    "Maharashtra": "Maharashtra",
    "Manipur": "Manipur",
    "Meghalaya": "Meghalaya",
    "Mizoram": "Mizoram",
    "Nagaland": "Nagaland",
    "Odisha": "Odisha",
    "Punjab": "Punjab",
    "Rajasthan": "Rajasthan",
    "Sikkim": "Sikkim",
    "Tamil Nadu": "Tamil Nadu",
    "Telangana": "Telangana",
    "Tripura": "Tripura",
    "Uttar Pradesh": "Uttar Pradesh",
    "Uttarakhand": "Uttarakhand",
    "West Bengal": "West Bengal",
    "Andaman and Nicobar Islands": "Andaman and Nicobar Islands",
    "Chandigarh": "Chandigarh",
    "Dadra and Nagar Haveli": "Dadra and Nagar Haveli",
    "Daman and Diu": "Daman and Diu",
    "Delhi": "NCT of Delhi",
    "Lakshadweep": "Lakshadweep",
    "Puducherry": "Puducherry",
    "Jammu and Kashmir": "Jammu and Kashmir",
    "Ladakh": "Ladakh",
}

def get_datagov_api_key() -> Optional[str]:
    """Get DataGov API key from environment variables."""
    return os.getenv("DATAGOV_API_KEY")


def fetch_live_market_price(crop_name: str, state_name: str) -> float:
    """
    Fetch live market price for a crop in a specific state from DataGov API.
    
    Args:
        crop_name: Name of the crop (e.g., "Rice", "Wheat")
        state_name: Name of the state (e.g., "Maharashtra", "Punjab")
    
    Returns:
        Price per ton (INR) - converted from modal_price per quintal
    """
    api_key = get_datagov_api_key()
    
    if not api_key:
        logger.warning("DATAGOV_API_KEY not found in environment, using fallback price")
        return _get_fallback_price_per_ton(crop_name)
    
    # Normalize state name
    normalized_state = STATE_MAPPING.get(state_name, state_name)
    
    # Build API request
    params = {
        "api-key": api_key,
        "format": "json",
        "filters[commodity]": crop_name,
        "filters[state]": normalized_state,
        "limit": 100
    }
    
    try:
        response = requests.get(DATAGOV_MARKET_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        records = data.get("records", [])
        
        if not records:
            logger.info(f"No market data found for {crop_name} in {state_name}, using fallback")
            return _get_fallback_price_per_ton(crop_name)
        
        # Get the most recent record (API returns latest first typically)
        # Filter for records with modal_price
        valid_records = [r for r in records if r.get("modal_price") is not None]
        
        if not valid_records:
            logger.info(f"No valid modal_price for {crop_name} in {state_name}, using fallback")
            return _get_fallback_price_per_ton(crop_name)
        
        # Use the latest record's modal_price
        latest_record = valid_records[0]
        modal_price_per_quintal = float(latest_record.get("modal_price", 0))
        
        if modal_price_per_quintal <= 0:
            logger.warning(f"Invalid modal_price ({modal_price_per_quintal}) for {crop_name}, using fallback")
            return _get_fallback_price_per_ton(crop_name)
        
        # Convert from per quintal (100kg) to per ton (1000kg) = multiply by 10
        price_per_ton = modal_price_per_quintal * 10
        
        logger.info(f"Fetched live price for {crop_name} in {state_name}: ₹{price_per_ton:,.0f}/ton")
        return price_per_ton
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching market price for {crop_name} in {state_name}")
        return _get_fallback_price_per_ton(crop_name)
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {crop_name} in {state_name}: {e}")
        return _get_fallback_price_per_ton(crop_name)
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Error parsing API response for {crop_name} in {state_name}: {e}")
        return _get_fallback_price_per_ton(crop_name)


def _get_fallback_price_per_ton(crop_name: str) -> float:
    """
    Get fallback price per ton from baseline dictionary.
    
    Args:
        crop_name: Name of the crop
    
    Returns:
        Price per ton (INR)
    """
    # Try exact match first
    if crop_name in BASELINE_PRICES_PER_QUINTAL:
        return BASELINE_PRICES_PER_QUINTAL[crop_name] * 10
    
    # Try case-insensitive match
    for crop, price in BASELINE_PRICES_PER_QUINTAL.items():
        if crop.lower() == crop_name.lower():
            return price * 10
    
    # Try partial match
    for crop, price in BASELINE_PRICES_PER_QUINTAL.items():
        if crop.lower() in crop_name.lower() or crop_name.lower() in crop.lower():
            return price * 10
    
    # Default fallback
    logger.warning(f"No baseline price found for {crop_name}, using default Rice price")
    return BASELINE_PRICES_PER_QUINTAL["Rice"] * 10


def get_market_price_with_fallback(crop_name: str, state_name: str) -> float:
    """
    Get market price with automatic fallback.
    This is the main function to be used by the simulation engine.
    
    Args:
        crop_name: Name of the crop
        state_name: Name of the state
    
    Returns:
        Price per ton (INR)
    """
    return fetch_live_market_price(crop_name, state_name)