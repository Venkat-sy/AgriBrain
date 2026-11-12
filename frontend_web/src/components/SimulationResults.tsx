"use client";

interface SimulationResult {
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

interface CropRecommendation {
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

interface SimulationResultsProps {
  crop: CropRecommendation;
  results: SimulationResult | null;
  isLoading: boolean;
  onBack: () => void;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IN").format(value);
}

function getRiskColor(level: string): string {
  switch (level.toLowerCase()) {
    case "low":
      return "text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30";
    case "medium":
      return "text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30";
    case "high":
      return "text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900/30";
    default:
      return "text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800/50";
  }
}