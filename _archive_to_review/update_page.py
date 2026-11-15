with open("page.tsx", "r") as f:
    content = f.read()

old = "import { DigitalTwinWidget } from \"@/components/DigitalTwinWidget\";\n\ninterface District {"
new = """import { DigitalTwinWidget } from \"@/components/DigitalTwinWidget\";
import { IndiaMapSelector } from \"@/components/IndiaMapSelector\";

interface SpatialLookupResponse {
  district_id: number;
  district_name: string;
  state: string;
  state_code: string;
  latitude?: number;
  longitude?: number;
  soil_type: string;
  agro_climatic_zone?: string;
  area_km2?: number;
  centroid: { lat: number; lon: number };
  lookup_method: string;
  distance_km?: number;
  baseline_parameters: {
    n: number;
    p: number;
    k: number;
    ph: number;
    temperature_c: number;
    humidity_percent: number;
    rainfall_mm: number;
    lookup_method: string;
  };
  note: string;
}

interface District {"""

if old in content:
    content = content.replace(old, new)
    with open("page.tsx", "w") as f:
        f.write(content)
    print("Replaced successfully")
else:
    print("Pattern not found")
