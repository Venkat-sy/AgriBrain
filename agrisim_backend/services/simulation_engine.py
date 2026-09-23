from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from agrisim_backend.models import (
    CropProfile, CropCost, CropPrice, District, RainfallMonthly
)
from agrisim_backend.schemas import (
    SimulationRequest,
    SimulationResponse,
    CostBreakdownItem,
    RiskLevel,
    RoadmapActivity,
    ActivityType
)


@dataclass
class SimulationResult:
    plant_capacity: int
    cost_breakdown: List[CostBreakdownItem]
    total_cost_inr: float
    estimated_yield_tons: float
    estimated_yield_tons_per_ha: float
    market_value_inr: float
    net_profit_inr: float
    roi_percentage: float
    risk_level: RiskLevel
    risk_factors: List[str]


class SimulationEngine:
    """
    Core simulation engine for crop production and profitability analysis.
    Uses agronomic models and economic calculations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_rainfall_for_district(self, district_id: int, month: Optional[int] = None) -> float:
        """Get average monthly rainfall for a district, optionally for a specific month."""
        query = self.db.query(RainfallMonthly).filter(
            RainfallMonthly.district_id == district_id
        )
        
        if month:
            query = query.filter(RainfallMonthly.month == month)
        
        records = query.all()
        if not records:
            return 100.0  # Default fallback
        
        return sum(r.rainfall_mm for r in records) / len(records)
    
    def get_latest_market_price(self, crop_id: int) -> float:
        """Get the latest market price for a crop."""
        latest_price = self.db.query(CropPrice).filter(
            CropPrice.crop_id == crop_id
        ).order_by(CropPrice.price_date.desc()).first()
        
        if latest_price:
            return latest_price.price_per_ton
        
        # Fallback prices (INR per ton) - approximate market rates
        fallback_prices = {
            "Rice": 20000,
            "Wheat": 22000,
            "Maize": 18000,
            "Cotton": 55000,
            "Sugarcane": 3000,
            "Soybean": 45000,
            "Groundnut": 55000,
            "Mustard": 50000,
            "Chickpea": 50000,
            "Pigeonpea": 60000,
            "Mungbean": 70000,
            "Urad": 65000,
        }
        
        crop = self.db.query(CropProfile).filter(CropProfile.id == crop_id).first()
        return fallback_prices.get(crop.name if crop else "Rice", 20000)
    
    def get_crop_costs(self, crop_id: int, region: str = "national") -> List[CropCost]:
        """Get input costs for a crop."""
        query = self.db.query(CropCost).filter(CropCost.crop_id == crop_id)
        costs = query.all()
        
        if not costs:
            # Return default costs for the crop
            return self.get_default_costs(crop_id)
        
        return costs

    def get_default_costs(self, crop_id: int) -> List[CropCost]:
        """Generate default cultivation costs for a crop when database has no entries."""
        crop = self.db.query(CropProfile).filter(CropProfile.id == crop_id).first()
        if not crop:
            return []

        # Default cost activities for most crops (INR per hectare)
        default_costs = [
            ("Land Preparation", "ha", 3000, 1),
            ("Seeds/Seedlings", "kg", 200, 20),
            ("Sowing/Transplanting", "ha", 2000, 1),
            ("Basal Fertilizer (NPK)", "ha", 4000, 1),
            ("Top Dressing - Nitrogen", "ha", 2500, 2),
            ("Pesticides/Insecticides", "ha", 3000, 2),
            ("Weeding (Manual/Mechanical)", "ha", 2500, 2),
            ("Irrigation", "ha", 1500, 4),
            ("Harvesting", "ha", 4000, 1),
            ("Post-harvest Handling", "ha", 2000, 1),
        ]

        # Adjust for specific crops
        if crop.name == "cotton":
            default_costs = [
                ("Land Preparation", "ha", 3500, 1),
                ("Seeds (Bt Cotton)", "kg", 800, 2),
                ("Sowing", "ha", 2000, 1),
                ("Basal Fertilizer (NPK)", "ha", 5000, 1),
                ("Top Dressing - Nitrogen", "ha", 3000, 3),
                ("Pesticides/Insecticides", "ha", 8000, 4),
                ("Weeding", "ha", 3000, 3),
                ("Irrigation", "ha", 2000, 5),
                ("Harvesting (Multiple pickings)", "ha", 10000, 1),
                ("Post-harvest Handling", "ha", 3000, 1),
            ]
        elif crop.name == "rice":
            default_costs = [
                ("Land Preparation (Puddling)", "ha", 4000, 1),
                ("Seeds", "kg", 25, 40),
                ("Transplanting", "ha", 3500, 1),
                ("Basal Fertilizer (NPK)", "ha", 4500, 1),
                ("Top Dressing - Nitrogen", "ha", 2500, 2),
                ("Pesticides/Insecticides", "ha", 2500, 2),
                ("Weeding", "ha", 2000, 2),
                ("Irrigation", "ha", 3000, 8),
                ("Harvesting", "ha", 4000, 1),
                ("Threshing & Winnowing", "ha", 2500, 1),
            ]

        # Create CropCost objects (not saved to DB, just for calculation)
        from agrisim_backend.models import CropCost as CropCostModel
        result = []
        for activity, unit, unit_cost, qty in default_costs:
            cost_obj = CropCostModel(
                crop_id=crop_id,
                activity=activity,
                unit=unit,
                unit_cost=unit_cost,
                quantity_per_ha=qty,
                region="default"
            )
            result.append(cost_obj)

        return result

    def calculate_plant_capacity(self, land_area_ha: float, spacing_cm: float, row_spacing_cm: float) -> int:
        """Calculate number of plants that can be accommodated."""
        if not spacing_cm or not row_spacing_cm:
            return int(land_area_ha * 25000)  # Default assumption
        
        # Convert cm to meters
        spacing_m = spacing_cm / 100
        row_spacing_m = row_spacing_cm / 100
        
        # Plants per hectare
        plants_per_ha = int(10000 / (spacing_m * row_spacing_m))
        
        return int(plants_per_ha * land_area_ha)

    def calculate_yield(
        self,
        crop: CropProfile,
        land_area_ha: float,
        rainfall_mm: float,
        soil_type: str,
        confirmed_soil_type: str
    ) -> float:
        """Calculate estimated yield based on crop requirements and conditions."""
        base_yield = crop.expected_yield_tons_per_ha or 4.0
        
        # Rainfall factor
        if crop.rainfall_min_mm and crop.rainfall_max_mm:
            if rainfall_mm < crop.rainfall_min_mm:
                rainfall_factor = 0.5 + 0.3 * (rainfall_mm / crop.rainfall_min_mm)
            elif rainfall_mm > crop.rainfall_max_mm:
                rainfall_factor = 0.9 - 0.2 * min(1, (rainfall_mm - crop.rainfall_max_mm) / crop.rainfall_max_mm)
            else:
                rainfall_factor = 0.8 + 0.2 * (rainfall_mm - crop.rainfall_min_mm) / (crop.rainfall_max_mm - crop.rainfall_min_mm)
        else:
            rainfall_factor = 0.9
        
        # Soil suitability factor
        soil_factor = 1.0
        if crop.suitable_soil_types and confirmed_soil_type in crop.suitable_soil_types:
            soil_factor = 1.1
        elif crop.suitable_soil_types and soil_type in crop.suitable_soil_types:
            soil_factor = 1.05
        else:
            soil_factor = 0.8
        
        # Temperature factor (simplified)
        temp_factor = 1.0
        
        yield_tons_per_ha = base_yield * rainfall_factor * soil_factor * temp_factor
        return max(0.1, min(yield_tons_per_ha, base_yield * 1.5))  # Cap at 1.5x base yield
    
    def calculate_costs(
        self,
        crop_costs: List[CropCost],
        land_area_ha: float
    ) -> tuple:
        """Calculate total cultivation costs and breakdown."""
        cost_breakdown = []
        total_cost = 0.0
        
        for cost in crop_costs:
            item_cost = cost.unit_cost * cost.quantity_per_ha * land_area_ha
            cost_breakdown.append(CostBreakdownItem(
                activity=cost.activity,
                unit=cost.unit,
                unit_cost=cost.unit_cost,
                quantity=cost.quantity_per_ha * land_area_ha,
                total_cost=item_cost
            ))
            total_cost += item_cost
        
        return cost_breakdown, total_cost
    
    def assess_risk(
        self,
        crop: CropProfile,
        land_area_ha: float,
        budget_inr: float,
        total_cost: float,
        rainfall_mm: float,
        soil_type: str
    ) -> tuple:
        """Assess risk level and factors for the simulation."""
        risk_factors = []
        
        # Budget risk
        cost_ratio = total_cost / budget_inr if budget_inr > 0 else 2.0
        if cost_ratio > 1.0:
            risk_factors.append(f"Budget shortfall: costs exceed budget by {(cost_ratio - 1) * 100:.0f}%")
        elif cost_ratio > 0.9:
            risk_factors.append("High budget utilization (>90%)")
        
        # Rainfall risk
        if crop.rainfall_min_mm and rainfall_mm < crop.rainfall_min_mm * 0.7:
            risk_factors.append(f"Low rainfall risk: {rainfall_mm:.0f}mm vs required {crop.rainfall_min_mm:.0f}mm")
        
        # Soil suitability risk
        if crop.suitable_soil_types and soil_type not in crop.suitable_soil_types:
            risk_factors.append(f"Soil type '{soil_type}' not ideal for {crop.name}")
        
        # Scale risk
        if land_area_ha > 50:
            risk_factors.append("Large scale operation increases management complexity")
        
        # Determine risk level
        if len(risk_factors) == 0:
            risk_level = RiskLevel.LOW
        elif len(risk_factors) <= 2:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH
        
        return risk_level, risk_factors
    
    def run_simulation(
        self,
        request: SimulationRequest,
        district: District,
        crop: CropProfile
    ) -> SimulationResponse:
        """Run complete simulation and return results."""
        
        # Get rainfall
        rainfall_mm = request.rainfall_override_mm or self.get_rainfall_for_district(
            request.district_id, request.planting_month
        )
        
        # Get soil type (use confirmed or predominant)
        soil_type = request.confirmed_soil_type
        
        # Calculate yield
        yield_tons_per_ha = self.calculate_yield(
            crop, request.land_area_ha, rainfall_mm, soil_type, request.confirmed_soil_type
        )
        estimated_yield_tons = yield_tons_per_ha * request.land_area_ha
        
        # Get costs
        crop_costs = self.get_crop_costs(crop.id)
        cost_breakdown, total_cost = self.calculate_costs(crop_costs, request.land_area_ha)
        
        # Get market price
        price_per_ton = self.get_latest_market_price(crop.id)
        market_value = estimated_yield_tons * price_per_ton
        
        # Calculate profit metrics
        net_profit = market_value - total_cost
        roi_percentage = (net_profit / total_cost * 100) if total_cost > 0 else 0
        
        # Plant capacity
        plant_capacity = self.calculate_plant_capacity(
            request.land_area_ha, crop.spacing_cm or 30, crop.row_spacing_cm or 30
        )
        
        # Risk assessment
        risk_level, risk_factors = self.assess_risk(
            crop, request.land_area_ha, request.budget_inr, total_cost, rainfall_mm, soil_type
        )
        
        return SimulationResponse(
            district_id=request.district_id,
            district_name=district.name,
            selected_crop=request.selected_crop,
            land_area_ha=request.land_area_ha,
            budget_inr=request.budget_inr,
            confirmed_soil_type=request.confirmed_soil_type,
            rainfall_mm=rainfall_mm,
            plant_capacity=plant_capacity,
            cost_breakdown=cost_breakdown,
            total_cost_inr=total_cost,
            estimated_yield_tons=estimated_yield_tons,
            estimated_yield_tons_per_ha=yield_tons_per_ha,
            market_value_inr=market_value,
            net_profit_inr=net_profit,
            roi_percentage=roi_percentage,
            risk_level=risk_level,
            risk_factors=risk_factors,
            model_version="1.0.0",
            generated_at=datetime.utcnow()
        )
    
    def generate_roadmap(
        self,
        request: SimulationRequest,
        crop: CropProfile
    ) -> List[RoadmapActivity]:
        """Generate farming activity roadmap."""
        activities = []
        activity_id = 1
        
        # Default planting date
        planting_month = request.planting_month or 6
        planting_date = date(datetime.now().year, planting_month, 15)
        if planting_date < date.today():
            planting_date = date(datetime.now().year + 1, planting_month, 15)
        
        duration_days = crop.duration_days or 120
        
        # Activity templates based on crop
        activity_templates = [
            {
                "type": ActivityType.LAND_PREPARATION,
                "title": "Land Preparation & Tillage",
                "description": "Ploughing, harrowing, and leveling the field",
                "days_before_planting": -14,
                "duration_days": 7,
                "cost_per_ha": 3000,
                "is_critical": True
            },
            {
                "type": ActivityType.SOWING,
                "title": f"Sowing/Transplanting {crop.name}",
                "description": f"Seed rate: {crop.spacing_cm}cm x {crop.row_spacing_cm}cm spacing",
                "days_before_planting": 0,
                "duration_days": 3,
                "cost_per_ha": 2000,
                "is_critical": True
            },
            {
                "type": ActivityType.FERTILIZER_APPLICATION,
                "title": "Basal Fertilizer Application",
                "description": "Apply basal dose of NPK fertilizers",
                "days_before_planting": 3,
                "duration_days": 2,
                "cost_per_ha": 4000,
                "is_critical": True
            },
            {
                "type": ActivityType.IRRIGATION,
                "title": "First Irrigation",
                "description": "Initial irrigation after sowing",
                "days_before_planting": 5,
                "duration_days": 2,
                "cost_per_ha": 1500,
                "is_critical": True
            },
            {
                "type": ActivityType.FERTILIZER_APPLICATION,
                "title": "Top Dressing - Nitrogen (1st split)",
                "description": f"Apply {crop.n_requirement * 0.3:.0f} kg/ha Nitrogen",
                "days_before_planting": 21,
                "duration_days": 2,
                "cost_per_ha": 2000,
                "is_critical": True
            },
            {
                "type": ActivityType.WEEDING,
                "title": "First Weeding",
                "description": "Manual or mechanical weeding",
                "days_before_planting": 25,
                "duration_days": 5,
                "cost_per_ha": 2500,
                "is_critical": False
            }
        ]
        
        for template in activity_templates:
            start_date = planting_date + timedelta(days=template["days_before_planting"])
            end_date = start_date + timedelta(days=template["duration_days"])
            
            activities.append(RoadmapActivity(
                id=activity_id,
                activity_type=template["type"],
                title=template["title"],
                description=template["description"],
                start_date=start_date,
                end_date=end_date,
                estimated_cost=round(template["cost_per_ha"] * request.land_area_ha, 2),
                is_critical=template["is_critical"],
                depends_on=[activity_id - 1] if activity_id > 1 and template["is_critical"] else None
            ))
            activity_id += 1
        
        return activities