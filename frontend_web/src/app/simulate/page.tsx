"use client";
import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Button,
  Badge,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Label,
  Alert,
  AlertTitle,
  AlertDescription,
  Table,
  TableHeader,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
} from "@/components/ui";
import {
  Leaf,
  ArrowLeft,
  AlertCircle,
  CloudRain,
  Cpu,
  Calendar,
  Droplets,
  Settings,
  Tractor,
  Package,
  IndianRupee,
  Brain,
} from "lucide-react";
import { useFarm } from "@/context/FarmContext";
import { ApiService } from "@/services/api";

const MapUI = dynamic(() => import("@/components/MapUI"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[220px] rounded-2xl bg-slate-900/50 animate-pulse flex items-center justify-center text-slate-400 border border-slate-700">
      Loading Interactive India Map...
    </div>
  ),
});

// 8 Standard Indian Soil Profiles for User Confirmation & Override
const SOIL_PROFILES: Record<string, { N: number; P: number; K: number; pH: number; desc: string }> = {
  "Indo-Gangetic Alluvial": { N: 215, P: 58, K: 155, pH: 7.1, desc: "Fertile riverine silt; ideal for cereals, pulses & sugarcane" },
  "Deccan Black Cotton (Regur)": { N: 160, P: 48, K: 185, pH: 7.4, desc: "High clay moisture retention; ideal for cotton, soybean, citrus" },
  "Coastal Lateritic / Alluvial": { N: 150, P: 38, K: 165, pH: 5.7, desc: "Acidic, well-drained coastal soil; ideal for paddy, coconut, arecanut" },
  "Southern Red Loam": { N: 145, P: 42, K: 135, pH: 6.4, desc: "Porous friable loam; ideal for millets, groundnut, mango, pulses" },
  "Arid Sandy / Calcareous": { N: 95, P: 28, K: 115, pH: 7.9, desc: "Low organic matter, fast draining; suitable for bajra, mustard, pomegranate" },
  "Mountain Forest / Podzolic": { N: 185, P: 52, K: 150, pH: 6.0, desc: "Humus-rich temperate soil; ideal for apple, spices, potato" },
  "Deltaic Clay Loam": { N: 195, P: 54, K: 170, pH: 6.6, desc: "Moisture-retentive delta soil; high yield for rice, jute, banana" },
  "Saline / Alkaline Usar": { N: 110, P: 32, K: 125, pH: 8.2, desc: "High salt profile; requires gypsum & salt-tolerant varieties" },
  };

  interface MetricCardProps {
    label: string;
    value: string;
    icon: React.ReactNode;
  }

  function MetricCard({ label, value, icon }: MetricCardProps) {
    return (
      <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400">{icon}</div>
          <div>
            <p className="text-xs text-slate-400 font-medium">{label}</p>
            <p className="text-lg font-bold text-slate-100">{value}</p>
          </div>
        </div>
      </div>
    );
  }

  export default function SimulatePage() {
    const router = useRouter();
    const { 
      coordinates, setCoordinates, 
      district, setDistrict, 
      icarZone, setIcarZone, 
      soilOverride, setSoilOverride,
      selectedCrop, setSelectedCrop
    } = useFarm();
  
    // Local state for form inputs
    const [pin, setPin] = useState<{ lat: number; lng: number } | null>(coordinates ? { lat: coordinates.lat, lng: coordinates.lon } : { lat: 20.5937, lng: 78.9629 });
    const [districtName, setDistrictName] = useState<string>(district || "Select a district on the map");
    const [agroZone, setAgroZone] = useState<string>(icarZone || "Select a location on the map");
    const [selectedSoilTypeState, setSelectedSoilTypeState] = useState<string>(soilOverride || "Indo-Gangetic Alluvial");
    const [areaAcres, setAreaAcres] = useState<number>(3.0);
    const [setupType, setSetupType] = useState<'seasonal' | 'perennial'>('seasonal');
    const [useOverrides, setUseOverrides] = useState<boolean>(false);
    const [overrides, setOverrides] = useState({ rainfall: 115, temp: 27, humidity: 64, ph: 6.4, N: 145, P: 42, K: 135 });
    const [loading, setLoading] = useState<boolean>(false);
    const [statusBanner, setStatusBanner] = useState<string | null>(null);
    const [warmingUp, setWarmingUp] = useState<boolean>(false);

    // Sync local state with FarmContext on mount and when context changes
    useEffect(() => {
      if (coordinates && !pin) {
        setPin({ lat: coordinates.lat, lng: coordinates.lon });
      }
    }, [coordinates, pin]);

    useEffect(() => {
      if (district && districtName === "Select a district on the map") {
        setDistrictName(district);
      }
    }, [district, districtName]);

    useEffect(() => {
      if (icarZone && agroZone === "Select a location on the map") {
        setAgroZone(icarZone);
      }
    }, [icarZone, agroZone]);

    useEffect(() => {
      if (soilOverride && selectedSoilTypeState === "Indo-Gangetic Alluvial") {
        setSelectedSoilTypeState(soilOverride);
      }
    }, [soilOverride, selectedSoilTypeState]);

    // Warm up backend on mount to handle Render cold starts
    useEffect(() => {
      let cancelled = false;
      const warmUp = async () => {
        setWarmingUp(true);
        setStatusBanner("Waking up AI simulation engine (may take ~40s)...");
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/\/$/, "") || "https://agribrain-backend.onrender.com"}/health`, {
            method: "GET",
            cache: "no-store",
          });
          if (!cancelled) {
            if (res.ok) {
              setStatusBanner(null);
            } else {
              setStatusBanner("Backend still warming up... please wait a moment");
            }
          }
        } catch {
          if (!cancelled) {
            setStatusBanner("Backend still warming up... please wait a moment");
          }
        } finally {
          if (!cancelled) {
            setWarmingUp(false);
          }
        }
      };
      warmUp();
      return () => { cancelled = true; };
    }, []);

    interface RankedCrop {
      name: string;
      variety: string;
      season: string;
      days: number;
      score_pct: number;
      digital_twin?: {
        yield_per_acre_tonnes?: number;
        total_yield_tonnes?: number;
        estimated_revenue_inr?: number;
        daily_water_liters?: number;
        total_water_m3?: number;
        risks?: Record<string, unknown>;
      };
      shap_breakdown?: { feature: string; impact: number }[];
      timeline?: { stage_name: string; days: number; agronomy_advice: string }[];
    }

    interface RainfallMonth {
      month: string;
      predicted_mm: number;
      anomaly_pct: number;
    }

    interface SimulationData {
      district: string | null;
      agro_zone: string | null;
      area_acres: number;
      setup_type: 'seasonal' | 'perennial';
      weather: unknown | null;
      soil: unknown | null;
      rainfall_forecast: RainfallMonth[];
      ranked_crops: RankedCrop[];
      recommended_crop: string | null;
      timeline: { stage_name: string; days: number; agronomy_advice: string }[];
    }

  const [data, setData] = useState<SimulationData | null>(null);
  const [selectedCropIndex, setSelectedCropIndex] = useState<number>(0);

  const handlePinDrop = async (lat: number, lng: number) => {
      const cleanLat = Number(lat.toFixed(4));
      const cleanLng = Number(lng.toFixed(4));
      const newPin = { lat: cleanLat, lng: cleanLng };
      setPin(newPin);
      setCoordinates({ lat: cleanLat, lon: cleanLng });
      setStatusBanner(null);

      // Get spatial data from backend
      try {
        const spatialResult = await ApiService.lookupDistrict(cleanLat, cleanLng);
        const soilType = spatialResult?.soil_type || "Indo-Gangetic Alluvial";
        const zone = spatialResult?.agro_zone || "Upper Gangetic Plains Zone";
        const dist = spatialResult?.district || `${cleanLat}°N, ${cleanLng}°E`;
      
        setSelectedSoilTypeState(soilType);
        setSoilOverride(soilType);
        setAgroZone(zone);
        setIcarZone(zone);
        setDistrictName(dist);
        setDistrict(dist);
      
        setOverrides({
          rainfall: spatialResult?.weather?.rainfall || 100,
          temp: spatialResult?.weather?.temp || 27,
          humidity: spatialResult?.weather?.humidity || 65,
          ph: spatialResult?.soil?.pH || 6.5,
          N: spatialResult?.soil?.N || 150,
          P: spatialResult?.soil?.P || 40,
          K: spatialResult?.soil?.K || 150,
        });
      } catch {
        // Fallback to coordinate-based zone determination for Uttar Pradesh region
        if (cleanLat >= 26.0 && cleanLat <= 30.0 && cleanLng >= 77.0 && cleanLng <= 81.0) {
          setAgroZone("Upper Gangetic Plains Zone");
          setIcarZone("Upper Gangetic Plains Zone");
          setSelectedSoilTypeState("Indo-Gangetic Alluvial");
          setSoilOverride("Indo-Gangetic Alluvial");
        } else {
          setAgroZone("Central Plateau and Hills Zone");
          setIcarZone("Central Plateau and Hills Zone");
          setSelectedSoilTypeState("Black Cotton / Medium Black Soil");
          setSoilOverride("Black Cotton / Medium Black Soil");
        }
        setDistrictName(`${cleanLat}°N, ${cleanLng}°E`);
        setDistrict(`${cleanLat}°N, ${cleanLng}°E`);
      }
    };

    // Run simulation via backend API
      const runSimulation = async () => {
        if (!pin) return;
        setLoading(true);
        setStatusBanner(null);

        try {
          // First get district info from spatial lookup
          const spatialResult = await ApiService.lookupDistrict(pin.lat, pin.lng);
          const districtId = spatialResult?.district_id || 1;

          // Determine planting season based on setup type and month
          const currentMonth = new Date().getMonth() + 1;
          let plantingSeason = "Kharif";
          if (setupType === "perennial") {
            plantingSeason = "Perennial";
          } else if (currentMonth >= 6 && currentMonth <= 10) {
            plantingSeason = "Kharif";
          } else if (currentMonth >= 11 || currentMonth <= 2) {
            plantingSeason = "Rabi";
          } else {
            plantingSeason = "Zaid";
          }

          const cropToRun = selectedCrop || data?.ranked_crops?.[0]?.name || data?.recommended_crop || "Rice (Paddy)";
      
          const result = await ApiService.runSimulation({
            district_id: districtId,
            selected_crop: cropToRun,
            land_area_ha: areaAcres / 2.471, // Convert acres to hectares
            budget_inr: 100000, // Default budget
            confirmed_soil_type: selectedSoilTypeState,
            rainfall_override_mm: useOverrides ? overrides.rainfall : 0,
            planting_season: plantingSeason,
            planned_start_date: new Date().toISOString().split('T')[0],
          });

          // Validate response before changing the rendered results.
          if (!result || typeof result !== 'object') {
            throw new Error('Simulation returned an invalid response');
          }
          const rankedCrops = Array.isArray(result.ranked_crops)
            ? result.ranked_crops
            : Array.isArray(result.alternatives)
              ? result.alternatives
              : [];
          const payload = {
            district: result.district ?? null,
            agro_zone: result.agro_zone ?? null,
            area_acres: areaAcres,
            setup_type: setupType,
            weather: result.weather ?? null,
            soil: result.soil ?? null,
            rainfall_forecast: (Array.isArray(result.rainfall_forecast) ? result.rainfall_forecast : []) as RainfallMonth[],
            ranked_crops: rankedCrops as RankedCrop[],
            recommended_crop: result.recommended_crop ?? null,
            timeline: (Array.isArray(result.timeline) ? result.timeline : []) as { stage_name: string; days: number; agronomy_advice: string }[],
          };

          setSelectedCropIndex(0);
          setSelectedCrop(result.recommended_crop ?? cropToRun);
          setData(payload);
          try {
            localStorage.setItem('agribrain_last_simulation', JSON.stringify(payload));
          } catch (storageError) {
            console.warn('Unable to cache simulation results:', storageError);
          }
          setLoading(false);
        } catch (error) {
          console.error('Simulation error:', error);
          const errorMessage = error instanceof Error ? error.message : 'Failed to run simulation. Please try again.';
          setStatusBanner(errorMessage);
          setLoading(false);
        }
      };

  const activeCrop = data?.ranked_crops?.[selectedCropIndex] || null;

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Status Banner */}
      {(statusBanner || warmingUp) && (
        <div className="max-w-7xl mx-auto px-4 py-2 animate-slide-down">
          <Alert 
            variant={warmingUp ? "default" : "destructive"} 
            className="mb-0 rounded-none border-x-0 border-t-0 border-b-0 bg-amber-950/80 border-amber-500/50 text-amber-200"
          >
            {warmingUp ? (
              <>
                <span className="animate-spin mr-2">⟳</span>
                <AlertTitle className="text-sm">Warming Up</AlertTitle>
                <AlertDescription className="text-xs">{statusBanner}</AlertDescription>
              </>
            ) : (
              <>
                <AlertCircle className="w-4 h-4" />
                <AlertTitle className="text-sm">Simulation notice</AlertTitle>
                <AlertDescription className="text-xs">{statusBanner}</AlertDescription>
              </>
            )}
          </Alert>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Loading Overlay */}
        {loading && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-slate-300">Running digital twin inference...</p>
              <p className="text-xs text-slate-500 mt-1">Scoring 45 crops with SHAP explainability</p>
            </div>
          </div>
        )}

        {/* Responsive Layout: Parameters FIRST on mobile, side-by-side on desktop */}
        <div className="lg:grid lg:grid-cols-[1fr_420px] gap-6">
          {/* Left Panel - Parameters (moved up for visibility) */}
          <div className="space-y-6 lg:order-2">
            {/* Input Controls - NOW VISIBLE ABOVE FOLD */}
            <div className="space-y-4">
              {/* Setup Type & Area */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
                  <Settings className="w-5 h-5 text-emerald-400" />
                  Simulation Parameters
                </h3>
                <p className="text-sm text-slate-400 mb-4">Configure farm setup, area, and environmental overrides</p>
                
                {/* Setup Type & Area */}
                <div className="grid md:grid-cols-2 gap-4 mb-6">
                  <div>
                    <Label className="block text-sm font-medium text-slate-300 mb-1.5">Farm Setup Type</Label>
                    <Select value={setupType} onValueChange={(v: string) => setSetupType(v as "seasonal" | "perennial")}>
                      <SelectTrigger className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100">
                        <SelectValue placeholder="Select setup" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        <SelectItem value="seasonal">Seasonal Crops (25 varieties)</SelectItem>
                        <SelectItem value="perennial">Perennial Crops (20 varieties)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="block text-sm font-medium text-slate-300 mb-1.5">Farm Area (Acres)</Label>
                    <Input 
                      type="number" 
                      min="0.1" 
                      max="1000" 
                      step="0.1" 
                      value={areaAcres} 
                      onChange={(e) => setAreaAcres(Number(e.target.value))} 
                      className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Soil Type */}
                <div className="mb-6">
                  <Label className="block text-sm font-medium text-slate-300 mb-1.5">Confirmed Soil Profile</Label>
                  <Select value={selectedSoilTypeState} onValueChange={setSelectedSoilTypeState}>
                    <SelectTrigger className="mt-1 w-full md:w-1/2 bg-slate-900/50 border-slate-700 text-slate-100">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700">
                      {Object.entries(SOIL_PROFILES).map(([key, v]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex flex-col">
                            <span className="font-medium text-slate-100">{key}</span>
                            <span className="text-xs text-slate-400">pH: {v.pH} | N:{v.N} P:{v.P} K:{v.K} kg/ha</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Overrides Toggle */}
                <div className="flex items-center justify-between border-t border-slate-700/50 pt-4 mb-4">
                  <div>
                    <Label className="font-medium flex items-center gap-2 text-slate-100">
                      <input
                        type="checkbox"
                        checked={useOverrides}
                        onChange={(e) => setUseOverrides(e.target.checked)}
                        className="w-4 h-4 text-emerald-500 border-slate-600 rounded focus:ring-emerald-500 bg-slate-900"
                      />
                      Enable Environmental Overrides
                    </Label>
                    <p className="text-xs text-slate-400 mt-1">Manually adjust weather & soil nutrients for scenario testing</p>
                  </div>
                </div>

                {/* Override Inputs */}
                {useOverrides && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-slate-700/50 pt-4 animate-fade-in">
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Temp (°C)</Label>
                      <Input 
                        type="number" 
                        step="0.5" 
                        min="5" 
                        max="45" 
                        value={overrides.temp} 
                        onChange={(e) => setOverrides({...overrides, temp: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Humidity (%)</Label>
                      <Input 
                        type="number" 
                        min="10" 
                        max="100" 
                        value={overrides.humidity} 
                        onChange={(e) => setOverrides({...overrides, humidity: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Rainfall (mm)</Label>
                      <Input 
                        type="number" 
                        min="0" 
                        max="3000" 
                        value={overrides.rainfall} 
                        onChange={(e) => setOverrides({...overrides, rainfall: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Soil pH</Label>
                      <Input 
                        type="number" 
                        step="0.1" 
                        min="4" 
                        max="9" 
                        value={overrides.ph} 
                        onChange={(e) => setOverrides({...overrides, ph: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Nitrogen (kg/ha)</Label>
                      <Input 
                        type="number" 
                        min="0" 
                        max="500" 
                        value={overrides.N} 
                        onChange={(e) => setOverrides({...overrides, N: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Phosphorus (kg/ha)</Label>
                      <Input 
                        type="number" 
                        min="0" 
                        max="200" 
                        value={overrides.P} 
                        onChange={(e) => setOverrides({...overrides, P: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                    <div>
                      <Label className="block text-sm text-slate-300 mb-1.5">Potassium (kg/ha)</Label>
                      <Input 
                        type="number" 
                        min="0" 
                        max="400" 
                        value={overrides.K} 
                        onChange={(e) => setOverrides({...overrides, K: Number(e.target.value)})} 
                        className="mt-1 bg-slate-900/50 border-slate-700 text-slate-100 placeholder-slate-500 focus:ring-emerald-500/50"
                      />
                    </div>
                  </div>
                )}

                {/* Run Button - Prominent */}
                <Button
                  onClick={runSimulation}
                  disabled={loading || !pin || warmingUp}
                  className="w-full py-4 text-lg gap-2 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-700 hover:to-emerald-600 text-white font-semibold rounded-xl shadow-lg shadow-emerald-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                  size="lg"
                >
                  <Cpu className="w-5 h-5" />
                  {loading ? "Running Simulation..." : warmingUp ? "Warming Up Backend..." : "Run Digital Twin Simulation"}
                </Button>
              </div>
            </div>

            {/* Map Section - Compact */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden">
              <div className="flex flex-row items-center justify-between p-4 border-b border-slate-700/50">
                <h3 className="text-lg font-semibold text-slate-100">Farm Location & Agro-Zone</h3>
                <Badge variant={pin ? "default" : "secondary"} className="text-xs bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                  {pin ? "Pinned" : "Click Map to Pin"}
                </Badge>
              </div>
              <div className="p-0">
                <MapUI
                  center={[pin?.lat || 20.5937, pin?.lng || 78.9629]}
                  zoom={pin ? 8 : 5}
                  pin={pin}
                  onPinDrop={handlePinDrop}
                  className="h-[220px] w-full"
                />
              </div>
            </div>

            {/* Detected Region Info */}
            {pin && (
              <div className="bg-slate-800/50 border border-emerald-500/30 rounded-2xl p-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div>
                    <p className="text-xs text-slate-400">District</p>
                    <p className="font-semibold text-slate-100">{districtName}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Agro-Zone</p>
                    <p className="font-semibold text-slate-100">{agroZone}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Soil Profile</p>
                    <p className="font-semibold text-emerald-400">{selectedSoilTypeState}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Coordinates</p>
                    <p className="font-mono text-xs text-slate-300">{pin.lat.toFixed(4)}, {pin.lng.toFixed(4)}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Map & Results */}
          <div className="space-y-6 lg:order-1">
            {/* Results Panel - Full width on mobile, right side on desktop */}
            <div className="space-y-6 lg:col-span-2 lg:order-3">
              {data?.ranked_crops && data.ranked_crops.length > 0 && activeCrop ? (
                <>
                  {/* Top Crop Card */}
                  <div className="bg-slate-800/50 border border-emerald-500/30 rounded-2xl relative overflow-hidden shadow-lg shadow-emerald-500/10">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl opacity-50" />
                    <div className="p-6 border-b border-slate-700/50 relative">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="default" className="text-xs bg-emerald-500/20 text-emerald-400 border-emerald-500/30">Top Match</Badge>
                            <Badge variant="secondary" className="text-xs bg-slate-700/50 text-slate-300 border-slate-600/50">
                              {data?.setup_type === "perennial" ? "Perennial" : "Seasonal"}
                            </Badge>
                          </div>
                          <h2 className="text-2xl font-bold text-slate-100">{activeCrop?.name}</h2>
                          <p className="text-sm text-slate-400">{activeCrop?.variety} • {activeCrop?.season} • {activeCrop?.days} days</p>
                        </div>
                        <div className="text-right">
                          <p className="text-4xl font-bold text-emerald-400">{activeCrop?.score_pct}%</p>
                          <p className="text-xs text-slate-400">Suitability Score</p>
                        </div>
                      </div>
                    </div>
                    <div className="p-6 space-y-4">
                      {/* Key Metrics Row */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400"><Tractor className="w-4 h-4" /></div>
                            <div>
                              <p className="text-xs text-slate-400 font-medium">Yield / Acre</p>
                              <p className="text-lg font-bold text-slate-100">{activeCrop?.digital_twin?.yield_per_acre_tonnes || 0} t</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400"><Package className="w-4 h-4" /></div>
                            <div>
                              <p className="text-xs text-slate-400 font-medium">Total Yield</p>
                              <p className="text-lg font-bold text-slate-100">{activeCrop?.digital_twin?.total_yield_tonnes || 0} t</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400"><IndianRupee className="w-4 h-4" /></div>
                            <div>
                              <p className="text-xs text-slate-400 font-medium">Est. Revenue</p>
                              <p className="text-lg font-bold text-slate-100">₹{activeCrop?.digital_twin?.estimated_revenue_inr?.toLocaleString("en-IN") || 0}</p>
                            </div>
                          </div>
                        </div>
                        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-900/30 rounded-lg text-emerald-400"><Droplets className="w-4 h-4" /></div>
                            <div>
                              <p className="text-xs text-slate-400 font-medium">Water / Day</p>
                              <p className="text-lg font-bold text-slate-100">{activeCrop?.digital_twin?.daily_water_liters?.toLocaleString("en-IN") || 0} L</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* SHAP Explainability */}
                      <div className="border-t border-slate-700/50 pt-4">
                        <h4 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                          <Brain className="w-4 h-4 text-emerald-400" />
                          SHAP Feature Impact Breakdown
                        </h4>
                        <div className="space-y-2">
                          {activeCrop?.shap_breakdown?.map((s: { feature: string; impact: number }, i: number) => (
                            <div key={i} className="flex items-center gap-3">
                              <div className="w-36 text-xs text-slate-400 font-medium">{s.feature}</div>
                              <div className="flex-1 h-3 bg-slate-700/50 rounded-full overflow-hidden">
                                <div
                                  className={`h-full rounded-full transition-all duration-500 ${s.impact >= 0 ? "bg-emerald-500" : "bg-rose-500"}`}
                                  style={{ width: `${Math.abs(s.impact) * 100}%` }}
                                />
                              </div>
                              <div className="w-24 text-xs text-slate-400 text-right">
                                {s.impact >= 0 ? "+" : ""}{s.impact.toFixed(2)}
                              </div>
                            </div>
                          ))}
                        </div>
                        <p className="text-xs text-slate-500 mt-2">Green = favorable alignment | Red = deviation from crop optimum</p>
                      </div>

                      {/* Risk Indicators */}
                      <div className="border-t border-slate-700/50 pt-4">
                        <h4 className="text-sm font-semibold text-slate-300 mb-3">Risk Assessment</h4>
                        <div className="grid grid-cols-3 gap-3">
                          {Object.entries(activeCrop?.digital_twin?.risks || {}).map(([key, val]: [string, unknown]) => (
                            <div key={key} className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50 text-center">
                              <p className="text-xs text-slate-400 capitalize">{key.replace("_", " ")}</p>
                              <p className="text-sm font-medium text-slate-100 mt-1">{String(val)}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Ranked Crops Table */}
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden">
                    <div className="p-4 border-b border-slate-700/50 flex items-center gap-2">
                      <Table className="w-5 h-5 text-emerald-400" />
                      <h3 className="text-lg font-semibold text-slate-100">Ranked Crop Suitability (Top 6)</h3>
                    </div>
                    <p className="px-4 py-2 text-sm text-slate-400 border-b border-slate-700/50">
                      All {setupType === "perennial" ? 20 : 25} crops scored • Click row for details
                    </p>
                    <div className="overflow-x-auto p-4">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-900/50">
                            <TableHead className="w-8 text-slate-400">#</TableHead>
                            <TableHead className="text-slate-300">Crop</TableHead>
                            <TableHead className="hidden md:table-cell text-slate-400">Variety</TableHead>
                            <TableHead className="text-right text-slate-400">Score</TableHead>
                            <TableHead className="text-right hidden sm:table-cell text-slate-400">Yield/Acre</TableHead>
                            <TableHead className="text-right hidden md:table-cell text-slate-400">Revenue</TableHead>
                            <TableHead className="text-right text-slate-400">Water/Day</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {(data?.ranked_crops || []).map((crop: { name: string; variety: string; score_pct: number; digital_twin?: { yield_per_acre_tonnes?: number; estimated_revenue_inr?: number; daily_water_liters?: number } }, idx: number) => (
                            <TableRow
                              key={`${crop.name}-${idx}`}
                              className={`cursor-pointer transition-colors ${selectedCropIndex === idx ? "bg-emerald-500/10" : "hover:bg-slate-700/50"}`}
                              onClick={() => setSelectedCropIndex(idx)}
                            >
                              <TableCell className="font-mono text-sm text-slate-400">{idx + 1}</TableCell>
                              <TableCell className="font-medium text-slate-100">{crop.name}</TableCell>
                              <TableCell className="hidden md:table-cell text-sm text-slate-400">{crop.variety}</TableCell>
                              <TableCell className="text-right font-semibold">
                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${crop.score_pct >= 85 ? "bg-emerald-500/20 text-emerald-400" : crop.score_pct >= 75 ? "bg-blue-500/20 text-blue-400" : crop.score_pct >= 65 ? "bg-amber-500/20 text-amber-400" : "bg-rose-500/20 text-rose-400"}`}>
                                  {crop.score_pct}%
                                </span>
                              </TableCell>
                              <TableCell className="text-right hidden sm:table-cell text-sm text-slate-400">
                                {crop.digital_twin?.yield_per_acre_tonnes ?? 0} t
                              </TableCell>
                              <TableCell className="text-right hidden md:table-cell text-sm text-slate-400 font-medium">
                                ₹{(crop.digital_twin?.estimated_revenue_inr ?? 0).toLocaleString("en-IN")}
                              </TableCell>
                              <TableCell className="text-right text-sm text-slate-400">
                                {(crop.digital_twin?.daily_water_liters ?? 0).toLocaleString("en-IN")} L
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>

                  {/* Timeline / Agronomy Calendar */}
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl">
                    <div className="p-4 border-b border-slate-700/50 flex items-center gap-2">
                      <Calendar className="w-5 h-5 text-emerald-400" />
                      <h3 className="text-lg font-semibold text-slate-100">Agronomy Timeline — {activeCrop?.name || "Crop"}</h3>
                    </div>
                    <p className="px-4 py-2 text-sm text-slate-400 border-b border-slate-700/50">Stage-wise schedule with weather-aligned advisories</p>
                    <div className="p-4 space-y-3">
                      {(activeCrop?.timeline || []).map((stage: { stage_name: string; days: number; agronomy_advice: string }, idx: number) => (
                        <div key={idx} className="flex gap-4 p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <div className="flex-shrink-0 w-16 h-16 rounded-xl bg-slate-900/50 border border-slate-700/50 flex items-center justify-center">
                            <span className="text-2xl font-bold text-emerald-400">{idx + 1}</span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <h5 className="font-semibold text-slate-100">{stage.stage_name}</h5>
                            <p className="text-xs text-slate-400 mt-0.5">{stage.days} days</p>
                            <p className="text-sm text-slate-300 mt-2 whitespace-pre-wrap">{stage.agronomy_advice}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="p-4 border-t border-slate-700/50 bg-slate-900/50 rounded-b-2xl">
                      <p className="text-sm text-emerald-400">
                        <strong>Total Cycle:</strong> {(activeCrop?.timeline || []).reduce((a: number, b: { days: number }) => a + (Number(b.days) || 0), 0)} days (~{Math.round((activeCrop?.timeline || []).reduce((a: number, b: { days: number }) => a + (Number(b.days) || 0), 0) / 30)} months)
                        {" | "}
                        <strong>Total Water:</strong> {(activeCrop?.digital_twin?.total_water_m3 || 0).toLocaleString("en-IN")} m³
                        {" | "}
                        <strong>Projected Gross:</strong> ₹{(activeCrop?.digital_twin?.estimated_revenue_inr || 0).toLocaleString("en-IN")}
                      </p>
                    </div>
                  </div>

                  {/* Rainfall Forecast */}
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl">
                    <div className="p-4 border-b border-slate-700/50 flex items-center gap-2">
                      <CloudRain className="w-5 h-5 text-emerald-400" />
                      <h3 className="text-lg font-semibold text-slate-100">6-Month Rainfall Forecast (Heuristic)</h3>
                    </div>
                    <p className="px-4 py-2 text-sm text-slate-400 border-b border-slate-700/50">Seasonal distribution based on agro-zone climatology</p>
                    <div className="p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                      {(data?.rainfall_forecast || []).map((m: { month: string; predicted_mm: number; anomaly_pct: number }, idx: number) => (
                        <div key={idx} className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50 text-center">
                          <p className="text-xs text-slate-400">{m.month}</p>
                          <p className="text-2xl font-bold text-emerald-400 mt-1">{m.predicted_mm} mm</p>
                          <p className={`text-xs mt-1 ${m.anomaly_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                            {m.anomaly_pct >= 0 ? "+" : ""}{m.anomaly_pct}% vs normal
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                </>
              ) : (
                <>
                  {/* Empty State */}
                  <div className="bg-slate-800/50 border border-slate-700 rounded-2xl h-full min-h-[500px] flex flex-col items-center justify-center">
                    <div className="text-center">
                      <Cpu className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                      <h3 className="text-xl font-semibold text-slate-300 mb-2">Ready to Simulate</h3>
                      <p className="text-slate-400 mb-6 max-w-sm">
                        Pin your farm location on the map, configure parameters, and run the digital twin engine
                        to get AI-scored crop recommendations with SHAP explainability.
                      </p>
                      <div className="grid grid-cols-3 gap-4 text-sm text-center">
                        <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <p className="text-2xl font-bold text-emerald-400">45</p>
                          <p className="text-slate-400">Crops in Database</p>
                        </div>
                        <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <p className="text-2xl font-bold text-emerald-400">8</p>
                          <p className="text-slate-400">Indian Soil Profiles</p>
                        </div>
                        <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                          <p className="text-2xl font-bold text-emerald-400">15</p>
                          <p className="text-slate-400">Agro-Climatic Zones</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
