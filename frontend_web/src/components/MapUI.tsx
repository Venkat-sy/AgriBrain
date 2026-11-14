"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { useMapEvents } from "react-leaflet";
import { LatLngBoundsExpression } from "leaflet";
import L from "leaflet";
// Leaflet CSS loaded dynamically to avoid SSR issues

// Fix Leaflet marker icon paths for Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Define India's rough bounding box (South-West to North-East)
const indiaBounds: LatLngBoundsExpression = [
  [6.5333, 68.1114],   // South-West corner
  [35.6745, 97.3956],  // North-East corner
];

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

interface MapUIProps {
  onDistrictSelect: (district: SpatialLookupResponse) => void;
  isLoading?: boolean;
  initialCenter?: [number, number];
  initialZoom?: number;
  onMapClick?: (lat: number, lng: number) => void;
}

// District GeoJSON loader component
const DistrictLayer = ({
  geojsonData,
  onDistrictClick,
  selectedDistrictId,
}: {
  geojsonData: DistrictGeoJSON | null;
  onDistrictClick: (feature: DistrictFeature) => void;
  selectedDistrictId: number | null;
}) => {
  const handleFeatureClick = useCallback(
    (e: any) => {
      const feature = e.target.feature;
      if (feature && feature.properties) {
        onDistrictClick(feature);
      }
    },
    [onDistrictClick]
  );

  if (!geojsonData) return null;

  return (
    <GeoJSON
      data={geojsonData}
      style={(feature) => {
        if (!feature || !feature.properties) {
          return {
            fillColor: "#22c55e",
            weight: 1.5,
            color: "#166534",
            fillOpacity: 0.2,
            dashArray: "3",
          };
        }
        return {
          fillColor: feature.properties.id === selectedDistrictId ? "#16a34a" : "#22c55e",
          weight: feature.properties.id === selectedDistrictId ? 3 : 1.5,
          color: feature.properties.id === selectedDistrictId ? "#15803d" : "#166534",
          fillOpacity: feature.properties.id === selectedDistrictId ? 0.4 : 0.2,
          dashArray: "3",
        };
      }}
      onEachFeature={(feature, layer) => {
        layer.on("click", handleFeatureClick);
        layer.bindTooltip(
          `${feature.properties?.name || "Unknown"}, ${feature.properties?.state || "Unknown"}`,
          { permanent: false, direction: "top", offset: [0, -10] }
        );
      }}
    />
  );
};

// Leaflet marker icon - created once at module level
let markerIcon: any = null;

const getMarkerIcon = async () => {
  if (!markerIcon) {
    const L = await import("leaflet");
    markerIcon = new L.Icon({
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    });
  }
  return markerIcon;
};

// Selected district marker
const SelectedMarker = ({
  position,
  districtName,
}: {
  position: [number, number] | null;
  districtName: string;
}) => {
  const [icon, setIcon] = useState<any>(null);

  useEffect(() => {
    if (position) {
      getMarkerIcon().then(setIcon);
    }
  }, [position]);

  if (!position || !icon) return null;

  return (
    <Marker position={position} icon={icon}>
      <Tooltip>{districtName}</Tooltip>
    </Marker>
  );
};

// Separate component for handling map clicks with useMapEvents hook
function MapClickHandler({ onClick }: { onClick?: (lat: number, lng: number) => void }) {
  const handleClick = useCallback((e: any) => {
    if (!onClick) return;
    const { lat, lng } = e.latlng;
    onClick(lat, lng);
  }, [onClick]);

  useMapEvents({
    click: handleClick,
  });

  return null;
}

export function MapUI({
  onDistrictSelect,
  isLoading = false,
  initialCenter = [20.5937, 78.9629],
  initialZoom = 5,
  onMapClick,
}: MapUIProps) {
  const [geojsonData, setGeojsonData] = useState<DistrictGeoJSON | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictFeature | null>(null);
  const [lookupResult, setLookupResult] = useState<SpatialLookupResponse | null>(null);
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clickMarker, setClickMarker] = useState<[number, number] | null>(null);

  // Load district GeoJSON on mount
  useEffect(() => {
    const loadGeoJSON = async () => {
      try {
        const response = await fetch(
          "https://raw.githubusercontent.com/datasets/geo-india/master/data/india_district.geojson"
        );
        if (!response.ok) throw new Error("Failed to load GeoJSON");
        const data = await response.json();
        setGeojsonData(data);
      } catch (err) {
        console.error("GeoJSON load error:", err);
        setError("Failed to load district boundaries. Using fallback...");
      }
    };
    loadGeoJSON();
  }, []);

  // Handle district click -> API lookup
  const handleDistrictClick = async (feature: DistrictFeature) => {
    if (!feature.properties?.id) return;

    setSelectedDistrict(feature);
    setIsLookingUp(true);
    setError(null);

    try {
      const [lat, lon] = feature.properties?.latitude && feature.properties?.longitude
        ? [feature.properties.latitude, feature.properties.longitude]
        : [20.5937, 78.9629];

      const response = await fetch(`/api/districts?lat=${lat}&lon=${lon}`);
      if (!response.ok) throw new Error("Failed to lookup district");
      const data = await response.json();
      setLookupResult(data);
      onDistrictSelect(data);
    } catch (err) {
      setError("Failed to fetch district details. Please try again.");
    } finally {
      setIsLookingUp(false);
    }
  };

  // Handle map click anywhere -> drop pin and trigger spatial lookup
  const handleMapClick = useCallback((lat: number, lng: number) => {
    setClickMarker([lat, lng]);
    if (onMapClick) {
      onMapClick(lat, lng);
    }
  }, [onMapClick]);

  const getSelectedCentroid = (): [number, number] | null => {
    if (lookupResult?.centroid) return [lookupResult.centroid.lat, lookupResult.centroid.lon];
    const selectedGeom = selectedDistrict?.geometry as GeoJSON.Polygon | GeoJSON.MultiPolygon | null;
    if (selectedGeom?.coordinates?.[0]?.[0]) {
      const coords = selectedGeom.coordinates[0][0];
      return [Number(coords[1]), Number(coords[0])];
    }
    if (selectedDistrict?.properties?.latitude && selectedDistrict?.properties?.longitude) {
      return [selectedDistrict.properties.latitude, selectedDistrict.properties.longitude];
    }
    if (clickMarker) return clickMarker;
    return null;
  };

  // Load leaflet CSS
  useEffect(() => {
    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css";
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }
  }, []);

  return (
    <div className="relative w-full h-[400px] rounded-2xl overflow-hidden bg-slate-900/50 border border-white/10">
      <MapContainer
        center={[20.5937, 78.9629]}
        zoom={5}
        minZoom={4}
        maxBounds={indiaBounds}
        maxBoundsViscosity={1.0}
        scrollWheelZoom={true}
        className="h-[400px] w-full rounded-xl z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <DistrictLayer
          geojsonData={geojsonData}
          onDistrictClick={handleDistrictClick}
          selectedDistrictId={selectedDistrict?.properties?.id || null}
        />
        <SelectedMarker
          position={getSelectedCentroid()}
          districtName={selectedDistrict?.properties?.name || ""}
        />
        <MapClickHandler onClick={onMapClick} />
      </MapContainer>

      {/* Instructions */}
      <div className="absolute bottom-4 left-4 right-4 pointer-events-none">
        <div className="bg-white/10 dark:bg-slate-900/80 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-md mx-auto pointer-events-auto border border-white/10">
          <p className="text-sm text-slate-300 text-center mb-1">
            Click on a district or anywhere on the map to select location
          </p>
          <p className="text-xs text-slate-500 text-center">
            A pin will be dropped and soil parameters auto-filled
          </p>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="absolute top-4 left-4 right-4 pointer-events-none">
          <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-3 shadow-lg max-w-md mx-auto pointer-events-auto">
            <p className="text-sm text-red-300 text-center">{error}</p>
          </div>
        </div>
      )}

      {/* Loading indicator for lookup */}
      {isLookingUp && (
        <div className="absolute top-4 left-4 right-4 pointer-events-none">
          <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-3 shadow-lg max-w-md mx-auto pointer-events-auto">
            <div className="flex items-center justify-center gap-2 text-sm text-blue-300">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
              Looking up district details...
            </div>
          </div>
        </div>
      )}

      {/* Selected district info panel */}
      {lookupResult && (
        <div className="absolute bottom-4 left-4 right-4 md:bottom-auto md:top-4 md:left-auto md:right-4 md:w-80 pointer-events-none">
          <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4 shadow-lg pointer-events-auto animate-fade-in">
            <h4 className="text-lg font-semibold text-green-400 mb-2">
              {lookupResult.district_name}, {lookupResult.state}
            </h4>
            <div className="grid grid-cols-2 gap-2 text-sm text-slate-300">
              <div>Soil: {lookupResult.soil_type}</div>
              <div>Zone: {lookupResult.agro_climatic_zone || "N/A"}</div>
              <div>N: {lookupResult.baseline_parameters?.n} kg/ha</div>
              <div>P: {lookupResult.baseline_parameters?.p} kg/ha</div>
              <div>K: {lookupResult.baseline_parameters?.k} kg/ha</div>
              <div>pH: {lookupResult.baseline_parameters?.ph}</div>
              <div>Temp: {lookupResult.baseline_parameters?.temperature_c}°C</div>
              <div>Humidity: {lookupResult.baseline_parameters?.humidity_percent}%</div>
              <div>Rainfall: {lookupResult.baseline_parameters?.rainfall_mm} mm</div>
            </div>
          </div>
        </div>
      )}
      
      {/* Click marker - shows pin where user clicked on map */}
      {clickMarker && (
        <SelectedMarker
          position={clickMarker}
          districtName="Selected Location"
        />
      )}
    </div>
  );
}

export default MapUI;