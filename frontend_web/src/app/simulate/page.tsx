"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { InputPanel } from "@/components/InputPanel";
import { SimulationPanel } from "@/components/SimulationPanel";
import { CropCard } from "@/components/CropCard";
import { useFarm } from "@/context/FarmContext";
import { WeatherWidget } from "@/components/WeatherWidget";
import { AlertsWidget } from "@/components/AlertsWidget";
import { DigitalTwinWidget } from "@/components/DigitalTwinWidget";

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

interface Recommendation {
  crop_name: string;
  confidence: number;
  match_reasons: string[];
  expected_yield_tons_per_ha: number | null;
  season: string | null;
}

interface ApiResponse {
  district_id: number;
  soil_type: string;
  rainfall_mm: number;
  recommendations: Recommendation[];
  model_version: string;
  generated_at: string;
}

export default function SimulatePage() {
  const {
    setFarmParams,
    simulationResults,
    setSimulationResults,
    selectedCrop,
    setSelectedCrop,
    currentStep,
    setCurrentStep,
    setCoordinates,
    setSoilParams,
    setAnnualRainfall,
  } = useFarm();

  const [activeTab, setActiveTab] = useState<"input" | "simulate">("input");
  const [isLoading, setIsLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [apiError, setApiError] = useState<string | null>(null);
  const [mapDistrict, setMapDistrict] = useState<SpatialLookupResponse | null>(null);

  // Strict dynamic import with ssr: false - completely blocks SSR for Leaflet
  const MapUI = dynamic(
    () => import("@/components/MapUI").then((mod) => mod.MapUI),
    {
      ssr: false,
      loading: () => (
        <div className="h-[400px] w-full bg-slate-800 animate-pulse rounded-xl flex items-center justify-center text-slate-400">
          Initializing Map Engine...
        </div>
      ),
    }
  );

  // Handle map click / district selection -> auto-fetch soil + rainfall into global state
  const handleMapDistrictSelect = (district: SpatialLookupResponse) => {
    setMapDistrict(district);
    // Persist auto-fetched location + soil data to global state
    if (district.centroid) {
      setCoordinates({ lat: district.centroid.lat, lon: district.centroid.lon });
    }
    if (district.baseline_parameters) {
      const bp = district.baseline_parameters;
      setSoilParams({
        ph: bp.ph,
        texture: district.soil_type,
        organic_carbon: 0.6,
        n: bp.n,
        p: bp.p,
        k: bp.k,
      });
      setAnnualRainfall(bp.rainfall_mm);
    }
  };

  // Form submit -> get crop recommendations
  const handleRecommendationSubmit = async (formData: any) => {
    setIsLoading(true);
    setApiError(null);
    setActiveTab("simulate");
    setCurrentStep(2);

    try {
      const response = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district_id: formData.district_id || mapDistrict?.district_id,
          soil_type: formData.soil_type,
          rainfall_mm: formData.rainfall_mm,
          temperature_c: formData.temperature_c,
          humidity_percent: formData.humidity_percent,
          ph: formData.ph,
          n: formData.n,
          p: formData.p,
          k: formData.k,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || `API error: ${response.status}`);
      }

      const data = await response.json();
      if (data.recommendations?.length > 0) {
        setRecommendations(data.recommendations);
      }
    } catch (err: any) {
      setApiError(err.message || "Failed to get recommendations. Check backend connectivity.");
    } finally {
      setIsLoading(false);
    }
  };

  // Crop selection -> store in global state
  const handleCropSelect = (rec: Recommendation) => {
    setSelectedCrop(rec.crop_name);
    setCurrentStep(3);
  };

  // Simulation complete -> store results + navigate
  const handleSimulationComplete = (results: any) => {
    setSimulationResults(results);
    setCurrentStep(4);
  };

  return (
    <div className="min-h-screen bg-digital-twin transition-colors">
      <header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Link href="/" className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-white tracking-tight">AgriBrain</h1>
              </Link>
            </div>

            <nav className="flex items-center gap-1">
              <Link
                href="/simulate"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-green-400 bg-green-500/20 rounded-lg"
              >
                <span className="w-4 h-4 rounded-full bg-green-500"></span>
                Simulation
              </Link>
              <Link
                href="/calendar"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-slate-800/50 rounded-lg transition-colors"
              >
                Calendar
              </Link>
              <Link
                href="/expert-chat"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-slate-800/50 rounded-lg transition-colors"
              >
                Expert Chat
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-1 p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">
          {/* Progress Tracker */}
          <div className="mb-6 flex items-center gap-2 overflow-x-auto pb-2">
            {[
              { label: "Farm Input", step: 1 },
              { label: "Crop Selection", step: 2 },
              { label: "Simulation", step: 3 },
              { label: "Calendar", step: 4 },
              { label: "Expert Chat", step: 5 },
            ].map((item, idx) => (
              <div key={item.label} className="flex items-center gap-1 whitespace-nowrap">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
                    currentStep >= item.step
                      ? "bg-green-500 text-white"
                      : "bg-white/10 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                  }`}
                >
                  {item.step}
                </div>
                <span
                  className={`hidden sm:block text-sm font-medium ${
                    currentStep >= item.step
                      ? "text-green-400"
                      : "text-slate-500 dark:text-slate-400"
                  }`}
                >
                  {item.label}
                </span>
                {idx < 4 && (
                  <div
                    className={`hidden lg:block w-12 h-0.5 rounded ${
                      currentStep > item.step
                        ? "bg-green-500"
                        : "bg-white/10 dark:bg-slate-700"
                    }`}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="grid lg:grid-cols-12 gap-6">
            {/* Map Panel - 7/12 width */}
            <div className="lg:col-span-7 space-y-6">
              <div className="glass-card overflow-hidden">
                <div className="p-4 border-b border-white/10 dark:border-slate-700/50">
                  <h2 className="text-xl font-bold text-white">Interactive District Map</h2>
                  <p className="text-sm text-slate-400 mt-1">Click a district to auto-fill soil parameters and get crop recommendations</p>
                </div>
                <div className="p-4">
                  <MapUI
                    onDistrictSelect={handleMapDistrictSelect}
                    isLoading={isLoading}
                    initialCenter={[20.5937, 78.9629]}
                    initialZoom={5}
                  />

                  {mapDistrict && (
                    <div className="mt-4 p-4 glass-card border-green-500/30 animate-slide-in">
                      <h4 className="text-lg font-semibold text-green-400 mb-2">
                        {mapDistrict.district_name}, {mapDistrict.state}
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm text-slate-400">
                        <div>Soil: {mapDistrict.soil_type}</div>
                        <div>Zone: {mapDistrict.agro_climatic_zone || "N/A"}</div>
                        <div>N: {mapDistrict.baseline_parameters?.n} kg/ha</div>
                        <div>P: {mapDistrict.baseline_parameters?.p} kg/ha</div>
                        <div>K: {mapDistrict.baseline_parameters?.k} kg/ha</div>
                        <div>pH: {mapDistrict.baseline_parameters?.ph}</div>
                        <div>Temp: {mapDistrict.baseline_parameters?.temperature_c}°C</div>
                        <div>Humidity: {mapDistrict.baseline_parameters?.humidity_percent}%</div>
                        <div>Rainfall: {mapDistrict.baseline_parameters?.rainfall_mm} mm</div>
                      </div>
                    </div>
                  )}

                  {apiError && (
                    <div className="mt-4 p-4 glass-card border-red-500/30 animate-slide-in">
                      <p className="text-sm text-red-400">{apiError}</p>
                    </div>
                  )}
                </div>
              </div>

              {activeTab === "simulate" && recommendations.length > 0 && (
                <div className="glass-card p-6 animate-slide-in">
                  <h2 className="text-xl font-bold text-white mb-6">Select Crop to Simulate</h2>
                  <p className="text-slate-400 mb-6">Click on a crop card to select it, then run the digital twin simulation.</p>
                  <div className="grid grid-cols-1 gap-4">
                    {recommendations.map((rec, index) => (
                      <CropCard
                        key={`${rec.crop_name}-${index}`}
                        recommendation={rec}
                        rank={index + 1}
                        onClick={() => handleCropSelect(rec)}
                      />
                    ))}
                  </div>
                  <button
                    onClick={() => setActiveTab("input")}
                    className="mt-6 w-full py-2 px-4 bg-white/10 text-slate-300 font-medium rounded-lg hover:bg-white/20 transition-colors"
                  >
                    Back to Input
                  </button>
                </div>
              )}
            </div>

            {/* Sidebar - 5/12 width */}
            <div className="lg:col-span-5 space-y-6">
              {activeTab === "input" && (
                <InputPanel
                  onSubmit={handleRecommendationSubmit}
                  isLoading={isLoading}
                  hasRecommendations={recommendations.length > 0}
                />
              )}

              {activeTab === "simulate" && (
                <SimulationPanel
                  recommendations={recommendations}
                  onSimulationComplete={handleSimulationComplete}
                  selectedCrop={selectedCrop}
                />
              )}

              {/* Sidebar Widgets */}
              <WeatherWidget />
              <AlertsWidget />
              <DigitalTwinWidget />

              {/* Continue to Calendar */}
              {simulationResults && (
                <div className="glass-card border-green-500/30 p-6 animate-slide-in">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-green-400">Simulation Complete!</h3>
                      <p className="text-green-300">Your digital twin simulation for <strong>{selectedCrop}</strong> is ready with yield, revenue, and ROI predictions.</p>
                    </div>
                    <Link
                      href="/calendar"
                      className="btn-primary"
                    >
                      View Cultivation Calendar →
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}