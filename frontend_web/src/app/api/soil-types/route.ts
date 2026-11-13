import { NextResponse } from "next/server";

// Fixed soil type list — no backend dependency needed
const SOIL_TYPES = [
  "Alluvial Soil",
  "Black Soil",
  "Red Soil",
  "Laterite Soil",
  "Sandy Soil",
  "Clayey Soil",
  "Loamy Soil",
];

export async function GET() {
  return NextResponse.json({ soil_types: SOIL_TYPES });
}
