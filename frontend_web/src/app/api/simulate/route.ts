import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Map frontend fields to backend fields
    const response = await fetch(`${BACKEND_URL}/api/v1/simulation/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        district_id: body.district_id || 1,
        selected_crop: body.crop_name,
        land_area_ha: body.land_area_ha,
        budget_inr: body.budget_inr || 100000,
        confirmed_soil_type: body.soil_type || "Alluvial Soil",
        rainfall_override_mm: body.rainfall_mm || 750,
        planting_season: body.planting_season || "Kharif",
        planned_start_date: body.planting_date || "2024-06-15",
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    // Transform to match frontend expectations
    const simulation = {
      crop_name: data.selected_crop,
      land_area_ha: data.land_area_ha,
      water_availability_liters: Math.round(data.rainfall_mm * data.land_area_ha * 10000 * 0.5),
      water_requirement_liters: Math.round(data.rainfall_mm * data.land_area_ha * 10000 * 0.5),
      water_sufficiency: true,
      fertilizer_requirement_kg: { N: 120, P: 40, K: 150 },
      fertilizer_cost_inr: 15000,
      total_cost_inr: data.total_cost_inr,
      expected_yield_tons: data.estimated_yield_tons,
      expected_revenue_inr: data.market_value_inr,
      expected_profit_inr: data.net_profit_inr,
      roi_percent: data.roi_percentage,
      sustainability_index: data.risk_level === "low" ? 0.8 : data.risk_level === "medium" ? 0.5 : 0.3,
      risk_level: data.risk_level,
      monthly_breakdown: Array.from({ length: 6 }, (_, i) => ({
        month: i + 1,
        rainfall_mm: Math.round(data.rainfall_mm / 6),
        irrigation_needed_mm: 0,
        water_available_liters: Math.round(5000000 / 6),
        water_used_liters: Math.round(5000000 / 6),
        growth_stage: ["germination", "vegetative", "flowering", "grain_filling", "maturity", "harvest"][i],
      })),
    };
    
    return NextResponse.json({ simulation });
  } catch (error) {
    console.error("Simulation API error:", error);
    return NextResponse.json(
      { error: "Failed to run simulation" },
      { status: 500 }
    );
  }
}