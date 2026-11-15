import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://agribrain-35zr.onrender.com";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const state = searchParams.get("state");

    const url = `${BACKEND_URL}/api/v1/spatial/districts-geojson${state ? `?state=${encodeURIComponent(state)}` : ""}`;

    const response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      next: { revalidate: 300 }, // cache 5 min
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: "Failed to fetch district boundaries" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Districts GeoJSON API error:", error);
    return NextResponse.json({ error: "Failed to fetch district boundaries" }, { status: 500 });
  }
}