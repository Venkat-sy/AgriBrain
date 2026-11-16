"use client";
import React, { useState } from "react";
import dynamic from "next/dynamic";

const MapUI = dynamic(() => import("@/components/MapUI"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[320px] sm:h-[400px] lg:h-[460px] rounded-2xl bg-slate-900 animate-pulse flex items-center justify-center text-slate-400 border border-slate-800">
      Loading Interactive India Map...
    </div>
  ),
});

export default function SimulatePage() {
  const [pin, setPin] = useState<{ lat: number; lng: number } | null>(null);
  const [areaAcres, setAreaAcres] = useState<number>(3.0);
  const [setupType, setSetupType] = useState<"short-term" | "long-term">("short-term");
  const [useOverrides, setUseOverrides] = useState<boolean>(false);
  const [overrides, setOverrides] = useState({ rainfall: 140, temp: 28, ph: 6.5, N: 160 });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  const handlePinDrop = async (lat: number, lng: number) => {
    setPin({ lat, lng });
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/spatial/reverse-geocode?lat=${lat}&lon=${lng}`);
      if (res.ok) {
        const preview = await res.json();
        setData((prev: any) => ({
          ...prev,
          district: preview.district,
          state: preview.state,
          agro_zone: preview.agro_zone,
          weather: preview.weather,
          soil: preview.soil,
        }));
        setOverrides({
          rainfall: Math.round(preview.weather?.rainfall || 140),
          temp: Math.round(preview.weather?.temp || 28),
          ph: preview.soil?.pH || 6.5,
          N: preview.soil?.N || 160,
        });
      }
    } catch {
      // Non-blocking spatial preview
    }
  };

  const runSimulation = async () => {
    if (!pin) {
      setError("Click anywhere on the map to drop a farm location pin first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/simulation/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: pin.lat,
          lng: pin.lng,
          area_acres: areaAcres,
          setup_type: setupType,
          crop_duration_preference: setupType,
          overrides: useOverrides ? overrides : null,
        }),
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server responded with ${res.status}`);
      }
      const result = await res.json();
      setData(result);
      localStorage.setItem("agribrain_last_simulation", JSON.stringify(result));
    } catch (err: any) {
      setError(err.message || "Failed to connect to backend simulation engine.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-3 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              AgriBrain AI Digital Twin Platform
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
              40+ Indian Crop Ensemble • Yield & Irrigation Forecasting • SHAP Explainability • What-If Climate Simulator
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {pin && (
              <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                📍 {pin.lat.toFixed(4)}°N, {pin.lng.toFixed(4)}°E
              </span>
            )}
            <span className="px-3 py-1.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
              🌾 40 Crops Indexed
            </span>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/40 text-red-400 text-sm font-medium">
            ⚠️ {error}
          </div>
        )}

        {/* Main Responsive Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Map, Farm Inputs & What-If Sliders (6 cols) */}
          <div className="lg:col-span-6 space-y-4">
            <MapUI onPinDrop={handlePinDrop} pin={pin} />

            {/* Farm Setup & Input Card */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <span className="text-[11px] uppercase tracking-wider text-emerald-400 font-semibold">
                    Selected Agro-Climatic Region
                  </span>
                  <h3 className="text-base sm:text-lg font-bold text-white">
                    {data?.district ? `${data.district}, ${data.state}` : pin ? "Coordinates Locked" : "Tap anywhere on the map"}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {data?.agro_zone || "Drop a pin on the map to auto-detect zone & soil"}
                  </p>
                </div>
                <span className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 text-amber-300 border border-slate-700 self-start sm:self-center">
                  {data?.soil?.type || "Soil: Awaiting Pin"}
                </span>
              </div>

              {/* Farm Land Area & Crop Horizon Controls */}
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                <div className="sm:col-span-4">
                  <label className="text-xs uppercase tracking-wider text-slate-400 font-semibold block mb-1.5">
                    Farm Area (Acres)
                  </label>
                  <input
                    type="number"
                    min="0.2"
                    max="1000"
                    step="0.5"
                    value={areaAcres}
                    onChange={(e) => setAreaAcres(Math.max(0.1, parseFloat(e.target.value) || 1))}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white font-semibold text-sm focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <div className="sm:col-span-8">
                  <label className="text-xs uppercase tracking-wider text-slate-400 font-semibold block mb-1.5">
                    Crop Duration / Cultivation Type
                  </label>
                  <div className="grid grid-cols-2 gap-2.5">
                    <button
                      type="button"
                      onClick={() => setSetupType("short-term")}
                      className={`py-2.5 px-3 rounded-xl font-medium text-xs sm:text-sm transition-all border ${
                        setupType === "short-term"
                          ? "bg-emerald-600 text-white border-emerald-400 shadow-lg shadow-emerald-600/20"
                          : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
                      }`}
                    >
                      🌾 Short-Term (22)
                    </button>
                    <button
                      type="button"
                      onClick={() => setSetupType("long-term")}
                      className={`py-2.5 px-3 rounded-xl font-medium text-xs sm:text-sm transition-all border ${
                        setupType === "long-term"
                          ? "bg-emerald-600 text-white border-emerald-400 shadow-lg shadow-emerald-600/20"
                          : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
                      }`}
                    >
                      🌴 Long-Term (18)
                    </button>
                  </div>
                </div>
              </div>

              {/* Interactive Digital Twin What-If Scenario Simulator */}
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                    🎛️ Digital Twin "What-If" Scenario Sliders
                  </span>
                  <button
                    type="button"
                    onClick={() => setUseOverrides(!useOverrides)}
                    className={`text-xs px-2.5 py-1 rounded-md font-medium border ${
                      useOverrides
                        ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                        : "bg-slate-800 text-slate-400 border-slate-700"
                    }`}
                  >
                    {useOverrides ? "Custom Overrides ON" : "Using Live Auto-Telemetry"}
                  </button>
                </div>

                {useOverrides && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 text-xs">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-slate-400">Simulated Rainfall:</span>
                        <span className="font-semibold text-white">{overrides.rainfall} mm</span>
                      </div>
                      <input
                        type="range"
                        min="30"
                        max="350"
                        value={overrides.rainfall}
                        onChange={(e) => setOverrides({ ...overrides, rainfall: Number(e.target.value) })}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-slate-400">Simulated Temp:</span>
                        <span className="font-semibold text-white">{overrides.temp} °C</span>
                      </div>
                      <input
                        type="range"
                        min="12"
                        max="42"
                        value={overrides.temp}
                        onChange={(e) => setOverrides({ ...overrides, temp: Number(e.target.value) })}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-slate-400">Soil pH Override:</span>
                        <span className="font-semibold text-white">{overrides.ph}</span>
                      </div>
                      <input
                        type="range"
                        min="4.5"
                        max="8.5"
                        step="0.1"
                        value={overrides.ph}
                        onChange={(e) => setOverrides({ ...overrides, ph: Number(e.target.value) })}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-slate-400">Soil Nitrogen (N):</span>
                        <span className="font-semibold text-white">{overrides.N} kg/ha</span>
                      </div>
                      <input
                        type="range"
                        min="60"
                        max="280"
                        value={overrides.N}
                        onChange={(e) => setOverrides({ ...overrides, N: Number(e.target.value) })}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={runSimulation}
                disabled={loading}
                className="w-full py-3.5 px-6 rounded-xl font-bold text-sm sm:text-base text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 shadow-lg shadow-emerald-600/25 transition-all"
              >
                {loading ? "⚡ Simulating Digital Twin Pipeline..." : "⚡ Run Full Digital Twin Simulation"}
              </button>
            </div>
          </div>

          {/* Right Column: Always-Visible Telemetry, Digital Twin & SHAP (6 cols) */}
          <div className="lg:col-span-6 space-y-4">
            {/* Weather & Soil Baseline Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className={`bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl ${loading ? "animate-pulse" : ""}`}>
                <span className="text-xs font-semibold uppercase tracking-wider text-sky-400">
                  ☀️ Weather Telemetry
                </span>
                <div className="mt-3 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Temperature:</span>
                    <span className="font-semibold text-white">{data?.weather?.temp ?? "--"} °C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Humidity:</span>
                    <span className="font-semibold text-white">{data?.weather?.humidity ?? "--"} %</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Seasonal Rain:</span>
                    <span className="font-semibold text-sky-300">{data?.weather?.rainfall ?? "--"} mm</span>
                  </div>
                </div>
              </div>

              <div className={`bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl ${loading ? "animate-pulse" : ""}`}>
                <span className="text-xs font-semibold uppercase tracking-wider text-amber-400">
                  🌱 Soil NPK & pH Profile
                </span>
                <div className="mt-3 space-y-1.5 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">N / P / K:</span>
                    <span className="font-semibold text-white">
                      {data?.soil ? `${data.soil.N} / ${data.soil.P} / ${data.soil.K} kg/ha` : "-- / -- / --"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Soil pH:</span>
                    <span className="font-semibold text-emerald-400">{data?.soil?.pH ?? "--"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Land Area:</span>
                    <span className="font-semibold text-amber-300">{areaAcres} Acres</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Primary Crop Recommendation & Multi-Feature SHAP Explainability */}
            <div className={`bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 ${loading ? "animate-pulse" : ""}`}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400 block">
                    🤖 Top ML Crop Recommendation ({setupType === "long-term" ? "Long-Term / Orchard" : "Short-Term / Seasonal"})
                  </span>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-white mt-0.5">
                    {data?.recommended_crop || "Awaiting Simulation Run"}
                  </h2>
                </div>
                <div className="text-right">
                  <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-300 font-bold border border-emerald-500/30">
                    Suitability: {data?.score_pct ? `${data.score_pct}%` : "--%"}
                  </span>
                  {data?.season && (
                    <span className="block text-[11px] text-slate-400 mt-1">
                      Season: {data.season} (~{data.duration_days} days)
                    </span>
                  )}
                </div>
              </div>

              {/* SHAP Feature Attribution Bars */}
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2.5">
                <span className="text-xs font-semibold text-emerald-400 block">
                  📊 SHAP Feature Attribution Breakdown
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {data?.shap_data?.reasoning || "Drop a pin and run simulation to inspect feature-level SHAP weights."}
                </p>
                {data?.shap_data?.breakdown && (
                  <div className="grid grid-cols-2 gap-2 pt-1">
                    {data.shap_data.breakdown.map((item: any, idx: number) => (
                      <div key={idx} className="p-2 rounded-lg bg-slate-900 border border-slate-800 flex justify-between items-center text-xs">
                        <span className="text-slate-300">{item.feature}</span>
                        <span className={`font-bold ${item.impact >= 0 ? "text-emerald-400" : "text-amber-400"}`}>
                          {item.impact >= 0 ? `+${item.impact}` : item.impact}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Top 5 Ranked Alternatives */}
              {data?.alternatives && data.alternatives.length > 0 && (
                <div>
                  <span className="text-xs text-slate-400 font-medium block mb-2">
                    Other High-Suitability {setupType === "long-term" ? "Orchard/Plantation" : "Seasonal"} Alternatives:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {data.alternatives.map((alt: any, idx: number) => (
                      <span
                        key={idx}
                        className="text-xs px-3 py-1.5 rounded-xl bg-slate-800 text-slate-200 border border-slate-700 font-medium"
                      >
                        {alt.crop} <strong className="text-emerald-400">({alt.score_pct}%)</strong>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Digital Twin Forecasting Card: Yield, Revenue, Irrigation & Risk Matrix */}
            <div className={`bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4 ${loading ? "animate-pulse" : ""}`}>
              <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400 block">
                🌐 Digital Twin Telemetry (For {data?.area_acres || areaAcres} Acres)
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[11px] text-slate-400 uppercase">Predicted Yield</span>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {data?.digital_twin ? `${data.digital_twin.total_yield_tonnes} Tonnes` : "-- Tonnes"}
                  </div>
                  <span className="text-[11px] text-emerald-400">
                    {data?.digital_twin ? `${data.digital_twin.yield_per_acre_tonnes} T / Acre` : "Awaiting run"}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[11px] text-slate-400 uppercase">Est. Gross Value</span>
                  <div className="text-lg font-bold text-emerald-400 mt-0.5">
                    {data?.digital_twin ? `₹${data.digital_twin.estimated_revenue_inr.toLocaleString("en-IN")}` : "₹ --"}
                  </div>
                  <span className="text-[11px] text-slate-400">MSP / Market Baseline</span>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[11px] text-slate-400 uppercase">Irrigation Demand</span>
                  <div className="text-lg font-bold text-sky-400 mt-0.5">
                    {data?.digital_twin ? `${data.digital_twin.daily_water_liters.toLocaleString("en-IN")} L/day` : "-- L/day"}
                  </div>
                  <span className="text-[11px] text-slate-400">
                    {data?.digital_twin ? `Total: ${data.digital_twin.total_water_m3} m³` : "Net crop water"}
                  </span>
                </div>
              </div>

              {/* Risk Classification Matrix */}
              <div className="grid grid-cols-3 gap-2.5 pt-1 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-800/70 border border-slate-700/70">
                  <span className="text-slate-400 block">Drought Risk</span>
                  <strong className="text-white">{data?.digital_twin?.risks?.drought || "--"}</strong>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-800/70 border border-slate-700/70">
                  <span className="text-slate-400 block">Pest & Blight Risk</span>
                  <strong className="text-white">{data?.digital_twin?.risks?.pest_disease || "--"}</strong>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-800/70 border border-slate-700/70">
                  <span className="text-slate-400 block">Soil pH Status</span>
                  <strong className="text-white">{data?.digital_twin?.risks?.soil_reaction || "--"}</strong>
                </div>
              </div>
            </div>

            {/* Stage-by-Stage Cultivation Timeline */}
            <div className={`bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3 ${loading ? "animate-pulse" : ""}`}>
              <span className="text-xs font-semibold uppercase tracking-wider text-purple-400 block">
                📅 AI Cultivation Stage Schedule
              </span>
              {data?.timeline && data.timeline.length > 0 ? (
                <div className="space-y-2.5 max-h-[280px] overflow-y-auto pr-1">
                  {data.timeline.map((stage: any, i: number) => (
                    <div key={i} className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 space-y-1">
                      <div className="flex justify-between items-center text-xs sm:text-sm font-semibold text-white">
                        <span>{i + 1}. {stage.stage_name}</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                          {stage.days || stage.estimated_days} Days
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">{stage.agronomy_advice}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 py-3 text-center">
                  Run the simulation to generate a localized 5-stage cultivation calendar.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}