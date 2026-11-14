"""Live weather service for AgriBrain.

Fetches real-time IMD-sourced weather for an Indian city/district from the
IndianAPI weather gateway and normalizes it for the ML pipeline.

Falls back to historical averages when the API key is missing, the request
fails, or the city is not present in the API response.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

# Populate os.environ from .env when running locally (Render injects real
# environment variables, which always win because load_dotenv does not override).
load_dotenv()

logger = logging.getLogger(__name__)

WEATHER_API_URL = "https://weather.indianapi.in/india/weather"
API_TIMEOUT_SECONDS = (5, 15)  # (connect, read)

# Historical-average fallback (national baselines, aligned with the
# Alluvial Soil entry in backend.services.data_lookup.NATIONAL_BASELINES).
HISTORICAL_AVERAGES = {
    "temperature": 27.0,
    "humidity": 65.0,
    "rainfall": 1000.0,
}

# The API response shape is not guaranteed; accept any of these key spellings.
_FIELD_ALIASES = {
    "temperature": ("temperature", "temp", "temperature_c", "temp_c", "temperature_celsius"),
    "humidity": ("humidity", "humidity_percent", "relative_humidity", "rh"),
    "rainfall": ("rainfall", "rainfall_mm", "rain", "precipitation", "precipitation_mm"),
}

# Wrappers the payload may nest the metrics under.
_PAYLOAD_WRAPPERS = ("data", "current", "result", "weather", "response")

_VALUE_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")

# Plausible physical ranges; values outside are treated as missing.
_VALID_RANGES = {
    "temperature": (-20.0, 60.0),
    "humidity": (0.0, 100.0),
    "rainfall": (0.0, 10000.0),
}


def _to_float(value: Any) -> Optional[float]:
    """Coerce an API value (number or '28°C' / '65 %' / '10 mm') to float."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = _VALUE_PATTERN.search(str(value).replace(",", ""))
    return float(match.group()) if match else None


def _within_range(metric: str, value: float) -> bool:
    lo, hi = _VALID_RANGES[metric]
    return lo <= value <= hi


def _first_match(mapping: Dict[str, Any], keys) -> Optional[float]:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            value = _to_float(mapping[key])
            if value is not None:
                return value
    return None


def _extract_metrics(payload: Any) -> Dict[str, Optional[float]]:
    """Pull temperature/humidity/rainfall out of whatever shape the API returns."""
    candidates: list = []
    if isinstance(payload, dict):
        candidates.append(payload)
        for wrapper in _PAYLOAD_WRAPPERS:
            inner = payload.get(wrapper)
            if isinstance(inner, dict):
                candidates.append(inner)
            elif isinstance(inner, list) and inner and isinstance(inner[0], dict):
                candidates.append(inner[0])

    for candidate in candidates:
        metrics = {
            metric: _first_match(candidate, aliases)
            for metric, aliases in _FIELD_ALIASES.items()
        }
        if any(value is not None for value in metrics.values()):
            return metrics
    return {"temperature": None, "humidity": None, "rainfall": None}


def get_live_weather(
    city_name: str,
    historical: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Fetch live weather metrics for a city/district from IndianAPI.

    Args:
        city_name: City or district name to query.
        historical: Optional historical-average values used as the fallback
            (keys: temperature, humidity, rainfall). Defaults to the national
            baselines in HISTORICAL_AVERAGES.

    Returns:
        Dict with keys:
            temperature, humidity, rainfall  (floats, always present)
            source          - "live" or "historical_fallback"
            sources         - per-metric provenance ("live"/"historical_fallback")
            city, fetched_at, error
    """
    fallback = {**HISTORICAL_AVERAGES, **(historical or {})}
    result: Dict[str, Any] = {
        "temperature": fallback["temperature"],
        "humidity": fallback["humidity"],
        "rainfall": fallback["rainfall"],
        "sources": {
            "temperature": "historical_fallback",
            "humidity": "historical_fallback",
            "rainfall": "historical_fallback",
        },
        "source": "historical_fallback",
        "city": city_name,
        "fetched_at": None,
        "error": None,
    }

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        result["error"] = "WEATHER_API_KEY not configured"
        logger.warning(
            "[weather] WEATHER_API_KEY missing; using historical averages for %s", city_name
        )
        return result

    try:
        response = requests.get(
            WEATHER_API_URL,
            params={"city": city_name},
            headers={"x-api-key": api_key},
            timeout=API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        result["error"] = f"api request failed: {exc}"
        logger.warning(
            "[weather] API call failed for %s (%s); using historical averages", city_name, exc
        )
        return result
    except ValueError as exc:
        result["error"] = f"invalid JSON response: {exc}"
        logger.warning(
            "[weather] API returned non-JSON for %s (%s); using historical averages", city_name, exc
        )
        return result

    metrics = _extract_metrics(payload)
    if all(value is None for value in metrics.values()):
        # API call succeeded but the city is missing / no metrics returned.
        result["error"] = "no weather data for city in API response"
        logger.warning(
            "[weather] city missing from API response for %s; using historical averages", city_name
        )
        return result

    for metric in ("temperature", "humidity", "rainfall"):
        value = metrics.get(metric)
        if value is not None and _within_range(metric, value):
            result[metric] = round(value, 2)
            result["sources"][metric] = "live"

    if any(origin == "live" for origin in result["sources"].values()):
        result["source"] = "live"
        result["fetched_at"] = datetime.now(timezone.utc).isoformat()
    else:
        result["error"] = "API response values out of expected range"

    return result
