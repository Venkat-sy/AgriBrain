
with open('IndiaMapSelector.tsx', 'w') as f:
    f.write('''"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { useMapEvents } from "react-leaflet";
import { Icon } from "leaflet";
import "leaflet/dist/leaflet.css";

const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);
const GeoJSON = dynamic(
  () => import("react-leaflet").then((mod) => mod.GeoJSON),
  { ssr: false }
);
const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false }
);
const Tooltip = dynamic(
  () => import("react-leaflet").then((mod) => mod.Tooltip),
  { ssr: false }
);

interface DistrictFeature {
  type: "Feature";
  properties: {
    name: string;
    state: string;
    state_code: string;
    district_code: string;
    id?: number;
    soil_type?: string;
    latitude?: number;
    longitude?: number;
  };
  geometry: GeoJSON.Geometry | null;
}

interface DistrictGeoJSON {
  type: "FeatureCollection";
  features: DistrictFeature[];
}

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

interface IndiaMapSelectorProps {
  onDistrictSelect: (district: SpatialLookupResponse) => void;
  isLoading?: boolean;
  initialCenter?: [number, number];
  initialZoom?: number;
}

// Icon for markers
const defaultIcon = new Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});''')
print('Part 1 written')