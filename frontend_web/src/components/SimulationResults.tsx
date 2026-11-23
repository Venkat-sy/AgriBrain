"use client";

export interface SimulationResult {
  crop_name: string;
  land_area_ha: number;
  water_availability_liters: number;
  water_requirement_liters: number;
  water_sufficiency: boolean;
  fertilizer_requirement_kg: { N: number; P: number; K: number };
  fertilizer_cost_inr: number;
  total_cost_inr: number;
  expected_yield_tons: number;
  expected_revenue_inr: number;
  expected_profit_inr: number;
  roi_percent: number;
  sustainability_index: number;
  risk_level: string;
  monthly_breakdown: Array<{
    month: number;
    rainfall_mm: number;
    irrigation_needed_mm: number;
    water_available_liters: number;
    water_used_liters: number;
    growth_stage: string;
  }>;
}

export interface CropRecommendation {
  crop_id: number;
  crop_name: string;
  confidence_score: number;
  expected_yield_tons_per_ha: number;
  water_requirement_mm: number;
  fertilizer_requirement_kg_per_ha: { N: number; P: number; K: number };
  estimated_cost_inr_per_ha: number;
  estimated_revenue_inr_per_ha: number;
  risk_score: number;
  sustainability_score: number;
  reason: string;
  land_area_ha?: number;
}



