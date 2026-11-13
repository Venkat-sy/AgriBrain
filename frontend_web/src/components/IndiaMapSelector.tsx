"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import dynamic from "next/dynamic";
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
          `${feature.properties.name}, ${feature.properties.state}`,
          {
            permanent: false,
            direction: "top",
            offset: [0, -10],
            className: "leaflet-tooltip-custom",
          }
        );
      }}
    />
  );
};

// Marker for selected district
const SelectedMarker = ({
  position,
  districtName,
  icon,
}: {
  position: [number, number] | null;
  districtName: string;
  icon: any;
}) => {
  if (!position || !icon) return null;

  return (
    <Marker position={position} icon={icon}>
      <Tooltip direction="top" offset={[0, -20]}>
        <div className="bg-white dark:bg-slate-800 px-2 py-1 rounded shadow-lg text-sm font-medium">
          {districtName}
        </div>
      </Tooltip>
    </Marker>
  );
};

export function IndiaMapSelector({
  onDistrictSelect,
  isLoading = false,
  initialCenter = [20.5937, 78.9629],
  initialZoom = 5,
}: IndiaMapSelectorProps) {
  const [geojsonData, setGeojsonData] = useState<DistrictGeoJSON | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictFeature | null>(null);
  const [lookupResult, setLookupResult] = useState<SpatialLookupResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [iconClass, setIconClass] = useState<any>(null);

  // Load Icon class on client side
  useEffect(() => {
    import("leaflet").then((mod) => {
      setIconClass(mod.Icon);
    });
  }, []);

  // Create default icon using the loaded Icon class
  const getDefaultIcon = useCallback(() => {
    if (!iconClass || typeof window === "undefined") return null;
    return new iconClass({
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    });
  }, [iconClass]);

  // Load district boundaries on mount
  useEffect(() => {
    const fetchGeoJSON = async () => {
      try {
        const res = await fetch("/api/v1/spatial/districts-geojson");
        if (res.ok) {
          const data = await res.json();
          setGeojsonData(data);
        } else {
          setError("Failed to load district boundaries");
        }
      } catch (err) {
        console.error("Failed to load GeoJSON:", err);
        setError("Failed to load district boundaries");
      }
    };
    fetchGeoJSON();
  }, []);

  // Handle district click on map
  const handleDistrictClick = useCallback(
    async (feature: DistrictFeature) => {
      const { name, state, state_code, district_code, soil_type, id } = feature.properties;
      setSelectedDistrict(feature);
      setError(null);

      // Perform spatial lookup to get detailed parameters
      if (feature.geometry?.type === "Point") {
        const [lon, lat] = feature.geometry.coordinates;
        await performLookup(lat, lon);
      } else if (feature.geometry?.type === "Polygon" || feature.geometry?.type === "MultiPolygon") {
        // Calculate centroid for polygon
        const coords = feature.geometry.coordinates[0][0] as number[][]; // First ring of first polygon
        const centroid = coords.reduce(
          (acc: [number, number], coord: number[]): [number, number] => [acc[0] + coord[0], acc[1] + coord[1]],
          [0, 0] as [number, number]
        );
        const lat = centroid[1] / coords.length;
        const lon = centroid[0] / coords.length;
        await performLookup(lat, lon);
      }
    },
    []
  );

// Perform spatial lookup
  const performLookup = async (lat: number, lon: number) => {
    setIsLookingUp(true);
    try {
      const res = await fetch(`/api/v1/spatial/lookup?lat=${lat}&lon=${lon}`);
      if (res.ok) {
        const data = await res.json();
        setLookupResult(data);
        if (onDistrictSelect) {
          onDistrictSelect(data);
        }
      } else {
        setError("Failed to lookup district details");
      }
    } catch (err) {
      console.error("Lookup error:", err);
      setError("Failed to lookup district details");
    } finally {
      setIsLookingUp(false);
    }
  };

  // Get selected district centroid for marker
  const getSelectedCentroid = (): [number, number] | null => {
    if (!selectedDistrict || !selectedDistrict.geometry) return null;
    if (selectedDistrict.geometry.type === "Point") {
      const [lon, lat] = selectedDistrict.geometry.coordinates;
      return [lat, lon];
    }
    if (selectedDistrict.geometry.type === "Polygon" || selectedDistrict.geometry.type === "MultiPolygon") {
      const coords = selectedDistrict.geometry.coordinates[0][0] as number[][];
      const centroid = coords.reduce(
        (acc: [number, number], coord: number[]): [number, number] => [acc[0] + coord[0], acc[1] + coord[1]],
        [0, 0] as [number, number]
      );
      return [centroid[1] / coords.length, centroid[0] / coords.length];
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="h-96 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex items-center justify-center border border-slate-200 dark:border-slate-700">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-green-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="h-96 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700">
        <MapContainer
          center={initialCenter}
          zoom={initialZoom}
          scrollWheelZoom={true}
          className="h-full w-full"
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
            icon={getDefaultIcon()}
          />
        </MapContainer>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-4 left-4 right-4 pointer-events-none">
        <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 shadow-lg max-w-md mx-auto pointer-events-auto">
          <p className="text-sm text-slate-600 dark:text-slate-400 text-center">
            Click on a district to select it and view soil parameters
          </p>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="absolute top-4 left-4 right-4 pointer-events-none">
          <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-3 shadow-lg max-w-md mx-auto pointer-events-auto">
            <p className="text-sm text-red-600 dark:text-red-400 text-center">{error}</p>
          </div>
        </div>
      )}

      {/* Loading indicator for lookup */}
      {isLookingUp && (
        <div className="absolute top-4 left-4 right-4 pointer-events-none">
          <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3 shadow-lg max-w-md mx-auto pointer-events-auto">
            <div className="flex items-center justify-center gap-2 text-sm text-blue-600 dark:text-blue-400">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
              Looking up district details...
            </div>
          </div>
        </div>
      )}

      {/* Selected district info panel */}
      {lookupResult && (
        <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg animate-slide-up">
          <h4 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-2">
            {lookupResult.district_name}, {lookupResult.state}
          </h4>
          <div className="grid grid-cols-2 gap-2 text-sm text-slate-600 dark:text-slate-400">
            <div>Soil: {lookupResult.soil_type}</div>
            <div>Zone: {lookupResult.agro_climatic_zone || "N/A"}</div>
            <div>N: {lookupResult.baseline_parameters.n} kg/ha</div>
            <div>P: {lookupResult.baseline_parameters.p} kg/ha</div>
            <div>K: {lookupResult.baseline_parameters.k} kg/ha</div>
            <div>pH: {lookupResult.baseline_parameters.ph}</div>
            <div>Temp: {lookupResult.baseline_parameters.temperature_c}°C</div>
            <div>Humidity: {lookupResult.baseline_parameters.humidity_percent}%</div>
            <div>Rainfall: {lookupResult.baseline_parameters.rainfall_mm} mm</div>
          </div>
        </div>
      )}
    </div>
  );
}
