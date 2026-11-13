"""
SQLAlchemy ORM models for AgriSim backend.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class District(Base):
    """District model for Indian agricultural districts."""
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    state_code = Column(String(10))
    district_code = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    area_km2 = Column(Float)
    population = Column(Integer)
    soil_type = Column(String(50))
    agro_climatic_zone = Column(String(100))
    geometry = Column(Text)  # GeoJSON
    centroid = Column(Text)  # GeoJSON Point
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    soil_types = relationship("DistrictSoilType", back_populates="district")
    rainfall_monthly = relationship("RainfallMonthly", back_populates="district")
    rainfall_forecasts = relationship("RainfallForecast", back_populates="district")
    crop_costs = relationship("CropCost", back_populates="district")


class SoilType(Base):
    """Soil type reference model."""
    __tablename__ = "soil_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    typical_crops = Column(JSON, nullable=True)  # JSON array
    properties = Column(JSON, nullable=True)  # JSON object
    color_hex = Column(String(7))

    # Relationships
    district_soil_types = relationship("DistrictSoilType", back_populates="soil_type")


class DistrictSoilType(Base):
    """Association table between districts and soil types with percentages."""
    __tablename__ = "district_soil_types"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    soil_type_id = Column(Integer, ForeignKey("soil_types.id"), nullable=False)
    percentage = Column(Float, nullable=False)
    is_predominant = Column(Boolean, default=False)

    # Relationships
    district = relationship("District", back_populates="soil_types")
    soil_type = relationship("SoilType", back_populates="district_soil_types")


class CropProfile(Base):
    """Crop profile with agronomic requirements."""
    __tablename__ = "crop_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    common_name = Column(String(100))
    category = Column(String(50))
    season = Column(String(50))
    description = Column(Text)
    suitable_soil_types = Column(JSON, nullable=True)  # JSON array
    ph_min = Column(Float)
    ph_max = Column(Float)
    rainfall_min_mm = Column(Float)
    rainfall_max_mm = Column(Float)
    temp_min_c = Column(Float)
    temp_max_c = Column(Float)
    n_requirement = Column(Float)
    p_requirement = Column(Float)
    k_requirement = Column(Float)
    spacing_cm = Column(Float)
    row_spacing_cm = Column(Float)
    duration_days = Column(Integer)
    expected_yield_tons_per_ha = Column(Float)
    water_requirement_mm = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    costs = relationship("CropCost", back_populates="crop")
    prices = relationship("CropPrice", back_populates="crop")


class RainfallMonthly(Base):
    """Historical monthly rainfall data."""
    __tablename__ = "rainfall_monthly"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    rainfall_mm = Column(Float, nullable=False)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    district = relationship("District", back_populates="rainfall_monthly")


class RainfallForecast(Base):
    """Rainfall forecast data."""
    __tablename__ = "rainfall_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    forecast_date = Column(Date, nullable=False)
    predicted_mm = Column(Float, nullable=False)
    lower_bound_mm = Column(Float)
    upper_bound_mm = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    district = relationship("District", back_populates="rainfall_forecasts")


class CropCost(Base):
    """Crop cultivation cost breakdown."""
    __tablename__ = "crop_costs"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop_profiles.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)  # Optional regional override
    activity = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    unit_cost = Column(Float, nullable=False)
    quantity_per_ha = Column(Float, nullable=False)
    region = Column(String(50), default="national")
    validity_start = Column(Date)
    validity_end = Column(Date)
    source = Column(String(100))

    # Relationships
    crop = relationship("CropProfile", back_populates="costs")
    district = relationship("District", back_populates="crop_costs")


class CropPrice(Base):
    """Crop market price data."""
    __tablename__ = "crop_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop_profiles.id"), nullable=False)
    market = Column(String(100))
    price_per_ton = Column(Float, nullable=False)
    price_date = Column(Date, nullable=False)
    source = Column(String(100))

    # Relationships
    crop = relationship("CropProfile", back_populates="prices")


class SoilImageResult(Base):
    """Soil image analysis result."""
    __tablename__ = "soil_image_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    image_path = Column(String(500), nullable=False)
    predicted_soil = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    user_confirmed_soil = Column(String(100))
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class SimulationResult(Base):
    """Simulation result for farming scenario."""
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    selected_crop = Column(String(100), nullable=False)
    land_area_ha = Column(Float, nullable=False)
    budget_inr = Column(Float, nullable=False)
    confirmed_soil_type = Column(String(100), nullable=False)
    rainfall_override_mm = Column(Float)
    plant_capacity = Column(Integer)
    total_cost_inr = Column(Float)
    cost_breakdown = Column(Text)  # JSON
    estimated_yield_tons = Column(Float)
    estimated_yield_tons_per_ha = Column(Float)
    market_value_inr = Column(Float)
    net_profit_inr = Column(Float)
    roi_percentage = Column(Float)
    risk_level = Column(String(20))
    risk_factors = Column(Text)  # JSON array
    farming_roadmap = Column(Text)  # JSON array
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    district = relationship("District")


# Export all models
__all__ = [
    "Base",
    "District",
    "SoilType",
    "DistrictSoilType",
    "CropProfile",
    "RainfallMonthly",
    "RainfallForecast",
    "CropCost",
    "CropPrice",
    "SoilImageResult",
    "SimulationResult",
]