import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${BACKEND_URL}/api/v1/crop/recommend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...body,
        top_k: 10
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    // Transform to match frontend expectations
    const recommendations = data.recommendations.map((crop: any, index: number) => ({
      crop_id: index + 1,
      crop_name: crop.crop_name,
      confidence_score: crop.confidence,
      expected_yield_tons_per_ha: crop.expected_yield_tons_per_ha,
      water_requirement_mm: body.rainfall_mm || 750,
      fertilizer_requirement_kg_per_ha: { N: 120, P: 40, K: 150 },
      estimated_cost_inr_per_ha: 50000,
      estimated_revenue_inr_per_ha: 80000,
      risk_score: 1 - crop.confidence,
      sustainability_score: crop.confidence,
      reason: crop.match_reasons.join("; "),
      land_area_ha: body.land_area_ha || 2.0,
    }));
    
    return NextResponse.json({ recommendations });
  } catch (error) {
    console.error("Recommendation API error:", error);
    return NextResponse.json(
      { error: "Failed to fetch recommendations" },
      { status: 500 }
    );
  }
}