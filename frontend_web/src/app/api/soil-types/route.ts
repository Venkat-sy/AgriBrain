import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/map/districts`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(error, { status: response.status });
    }

    const districts = await response.json();
    // Extract unique soil types from districts (if available) or return common soil types
    // For now, return common Indian soil types as fallback
    const soilTypes = [
      "Alluvial Soil",
      "Black Soil",
      "Red Soil",
      "Laterite Soil",
      "Mountain Soil",
      "Desert Soil",
      "Saline Soil",
      "Peaty Soil",
    ];

    return NextResponse.json({ soil_types: soilTypes });
  } catch (error) {
    console.error("Soil types API error:", error);
    // Return fallback soil types on error
    const soilTypes = [
      "Alluvial Soil",
      "Black Soil",
      "Red Soil",
      "Laterite Soil",
      "Mountain Soil",
      "Desert Soil",
      "Saline Soil",
      "Peaty Soil",
    ];
    return NextResponse.json({ soil_types: soilTypes });
  }
}