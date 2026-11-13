import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const state = searchParams.get("state");

    const url = `${BACKEND_URL}/api/v1/map/districts${state ? `?state=${encodeURIComponent(state)}` : ""}`;

    const response = await fetch(url, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      next: { revalidate: 300 }, // cache 5 min
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: "Failed to fetch districts" },
        { status: response.status }
      );
    }

    const data = await response.json();
    // data is an array of { id, name, state, ... }
    const districts = Array.isArray(data) ? data : [];

    // Extract unique states
    const states = [...new Set(districts.map((d: any) => d.state).filter(Boolean))].sort();

    return NextResponse.json({ districts, states });
  } catch (error) {
    console.error("Districts API error:", error);
    return NextResponse.json({ error: "Failed to fetch districts" }, { status: 500 });
  }
}
