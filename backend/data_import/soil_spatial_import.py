"""Utility script to import district GeoJSON geometry and associate soil types.

The AgriSim project requires spatial awareness of districts so that rainfall
forecasts and soil characteristics can be queried by location. This script:

1. Loads a GeoJSON file containing Indian district boundaries.
2. Inserts each district into the `district` table (if not already present).
3. Reads a CSV mapping district identifiers to soil‑type percentages.
4. Persists the mapping in the `district_soil_type` association table.

It is intended to be run once during the data‑ingestion phase (Phase 3).
"""

import os
import json
import csv
from pathlib import Path

from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm import Session

# Import ORM models lazily inside the function to avoid premature table registration
from backend.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[3]  # project root
DATA_DIR = BASE_DIR / "data"

# ---------------------------------------------------------------------------
# Configuration – replace paths if your data lives elsewhere
# ---------------------------------------------------------------------------
GEOJSON_PATH = DATA_DIR / "districts.geojson"  # Expected GeoJSON with Feature collection
SOIL_MAPPING_CSV = DATA_DIR / "district_soil_mapping.csv"


def load_geojson(path: Path):
    """Return a list of GeoJSON features from *path*.

    The function raises a clear error if the file does not exist so that the
    caller can fail fast during CI.
    """
    if not path.is_file():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("features", [])


def import_districts(session: Session, features):
    """Insert districts with geometry into the DB.

    Expected properties per feature: `name`, `state`, `state_code`, `district_code`.
    Geometry is stored as raw GeoJSON; PostGIS will handle conversion via SQLAlchemy
    JSON column mapping defined in the model.
    """
    # Lazy import of the District model
    from backend.models import District
    import json
    
    # First, get all existing district_codes
    existing_codes = set()
    existing_codes_query = session.execute(select(District.district_code)).scalars().all()
    existing_codes = set(existing_codes_query)
    
    for feat in features:
        props = feat.get("properties", {})
        district_code = props.get("district_code")
        
        # Skip if already exists
        if district_code in existing_codes:
            continue
            
        geometry = feat.get("geometry")
        district = District(
            name=props.get("name"),
            state=props.get("state"),
            state_code=props.get("state_code"),
            district_code=district_code,
            geometry=json.dumps(feat.get("geometry")) if feat.get("geometry") else None,
        )
        session.add(district)
        existing_codes.add(district_code)
    session.commit()


def import_soil_mappings(session: Session, csv_path: Path):
    """Read ``district_soil_mapping.csv`` and populate ``district_soil_type``.

    CSV columns: `district_code`, `soil_type_name`, `percentage`, `is_predominant`.
    The function resolves foreign keys via helper queries.
    """
    # Lazy import of related models
    from backend.models import SoilType, DistrictSoilType, District
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Resolve district & soil_type IDs
            district = session.execute(
                select(District.id).where(District.district_code == row["district_code"])
            ).scalar_one_or_none()
            soil = session.execute(
                select(SoilType.id).where(SoilType.name == row["soil_type_name"])
            ).scalar_one_or_none()
            if district is None or soil is None:
                continue  # Skip incomplete rows – can be logged in real usage
            # Check if mapping already exists
            existing = session.execute(
                select(DistrictSoilType).where(
                    DistrictSoilType.district_id == district,
                    DistrictSoilType.soil_type_id == soil
                )
            ).scalar_one_or_none()
            if existing is None:
                mapping = DistrictSoilType(
                    district_id=district,
                    soil_type_id=soil,
                    percentage=float(row["percentage"]),
                    is_predominant=bool(int(row.get("is_predominant", 0))),
                )
                session.add(mapping)
    session.commit()


def main():
    database_url = settings.DATABASE_URL
    is_sqlite = database_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(database_url, connect_args=connect_args)
    with Session(engine) as session:
        features = load_geojson(GEOJSON_PATH)
        import_districts(session, features)
        import_soil_mappings(session, SOIL_MAPPING_CSV)
        print("✅ Soil spatial data imported successfully.")


if __name__ == "__main__":
    main()

