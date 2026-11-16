"use client";

import { useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";

// ─── Types (strict spec §1 + §3) ──────────────────────────────────────────

interface TimelineStage {
  stage_name: string;
  estimated_days: number;
  agronomy_advice: string;
}

interface SimulationResult {
  district: string;
  soil_n: number;
  soil_p: number;
  soil_k: number;
  soil_ph: number;
  live_temp: number;
  live_humidity: number;
  live_rainfall: number;
  recommended_crop: string;
  confidence_score: number;
  cultivation_timeline: TimelineStage[];
}

// ─── Map UI (SSR-disabled Leaflet) ────────────────────────────────────────

const MapUI = dynamic(
  () => import("@/components/MapUI").then((mod) => mod.MapUI),
  {
    ssr: false,
    loading: () => (
      <div className="h-[50vh] md:h-[600px] w-full bg-slate-800 animate-pulse rounded-xl flex items-center justify-center text-slate-400">
        Initializing Map Engine...
      </div>
    ),
  }
);

// ─── Skeleton loader ───────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div className="animate-pulse space-y-4 p-6 rounded-2xl bg-white/5 border border-white/10">
      <div className="h-6 bg-white/10 rounded w-1/2" />
      <div className="h-4 bg-white/10 rounded w-3/4" />
      <div className="h-4 bg-white/10 rounded w-2/3" />
      <div className="grid grid-cols-2 gap-3 mt-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="h-10 bg-white/10 rounded" />
        ))}
      </div>
    </div>
  );
}

// ─── Empty state widget ────────────────────────────────────────────────────

function EmptyStateWidget() {
  return (
    <div className="flex flex-col items-center justify-center h-full py-16 text-center space-y-4">
      <div className="w-16 h-16 rounded-2xl bg-green-500/20 flex items-center justify-center">
        <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white">No simulation yet</h3>
        <p className="text-sm text-slate-400 mt-1">Pin a location on the map, choose your farm type, and click <strong className="text-green-400">Run Simulation</strong>.</p>
      </div>
    </div>
  );
}

// ─── Results widget ────────────────────────────────────────────────────────

function ResultsWidget({ data }: { data: SimulationResult }) {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Crop recommendation card */}
      <div className="glass-card p-6 border border-green-500/30">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">Recommended Crop</p>
            <h2 className="text-3xl font-bold text-green-400 capitalize">{data.recommended_crop}</h2>
            <p className="text-sm text-slate-300 mt-1">📍 {data.district}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">Confidence</p>
            <p className="text-2xl font-bold text-white">{(data.confidence_score * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Live conditions */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-widest">Live Conditions</h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-blue-500/10 rounded-xl p-3 text-center">
            <p className="text-xs text-slate-400">Temperature</p>
            <p className="text-xl font-bold text-blue-300">{data.live_temp}°C</p>
          </div>
          <div className="bg-cyan-500/10 rounded-xl p-3 text-center">
            <p className="text-xs text-slate-400">Humidity</p>
            <p className="text-xl font-bold text-cyan-300">{data.live_humidity}%</p>
          </div>
          <div className="bg-indigo-500/10 rounded-xl p-3 text-center">
            <p className="text-xs text-slate-400">Rainfall</p>
            <p className="text-xl font-bold text-indigo-300">{data.live_rainfall}mm</p>
          </div>
        </div>
      </div>

      {/* Soil parameters */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-widest">Soil Baseline</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex justify-between bg-white/5 rounded-lg px-3 py-2">
            <span className="text-slate-400">N</span>
            <span className="text-white font-medium">{data.soil_n} kg/ha</span>
          </div>
          <div className="flex justify-between bg-white/5 rounded-lg px-3 py-2">
            <span className="text-slate-400">P</span>
            <span className="text-white font-medium">{data.soil_p} kg/ha</span>
          </div>
          <div className="flex justify-between bg-white/5 rounded-lg px-3 py-2">
            <span className="text-slate-400">K</span>
            <span className="text-white font-medium">{data.soil_k} kg/ha</span>
          </div>
          <div className="flex justify-between bg-white/5 rounded-lg px-3 py-2">
            <span className="text-slate-400">pH</span>
            <span className="text-white font-medium">{data.soil_ph}</span>
          </div>
        </div>
      </div>

      {/* Cultivation timeline */}
      {data.cultivation_timeline.length > 0 && (
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-widest">Cultivation Timeline</h3>
          <div className="space-y-2">
            {data.cultivation_timeline.map((stage, idx) => (
              <div key={idx} className="rounded-xl overflow-hidden border border-white/10">
                <button
                  onClick={() => setExpanded(expanded === idx ? null : idx)}
                  className="w-full flex items-center justify-between p-3 text-left hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-full bg-green-500/20 flex items-center justify-center text-xs font-bold text-green-400">
                      {idx + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{stage.stage_name}</p>
                      <p className="text-xs text-slate-400">{stage.estimated_days} days</p>
                    </div>
                  </div>
                  <svg
                    className={`w-4 h-4 text-slate-400 transition-transform ${expanded === idx ? "rotate-180" : ""}`}
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {expanded === idx && (
                  <div className="px-4 pb-3 text-xs text-slate-300 bg-white/5 leading-relaxed">
                    {stage.agronomy_advice}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigate to Calendar */}
      <Link
        href="/calendar"
        className="block w-full text-center py-3 px-4 bg-green-500 hover:bg-green-400 text-white font-semibold rounded-xl transition-colors"
      >
        View Cultivation Calendar →
      </Link>
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export default function SimulatePage() {
  // Strict state per spec §3
  const [pin, setPin] = useState<{ lat: number; lng: number } | null>(null);
  const [setupType, setSetupType] = useState<"short-term" | "long-term">("short-term");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Map pin drop (immediate — no API await per spec §2)
  const handlePinDrop = (lat: number, lng: number) => {
    setPin({ lat, lng });
    setError(null);
    // Clear old results when new pin dropped
    setResults(null);
  };

  // Run simulation via /api/v1/simulation/run
  const runSimulation = async () => {
    if (!pin) {
      setError("Please pin a location on the map first.");
      return;
    }
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://agribrain-backend.onrender.com";
      const res = await fetch(`${apiUrl}/api/v1/simulation/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lat: pin.lat,
          lng: pin.lng,
          setup_type: setupType,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `API error: ${res.status} ${res.statusText}`);
      }

      const data: SimulationResult = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Simulation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-digital-twin transition-colors">
      {/* Header */}
      <header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">AgriBrain</h1>
            </Link>
            <nav className="flex items-center gap-1">
              <Link href="/simulate" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-green-400 bg-green-500/20 rounded-lg">
                <span className="w-4 h-4 rounded-full bg-green-500" />
                Simulation
              </Link>
              <Link href="/calendar" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                Calendar
              </Link>
              <Link href="/expert-chat" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                Expert Chat
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main — strict responsive breakpoints per spec §6 */}
      <main className="min-h-screen w-full flex flex-col md:flex-row p-2 md:p-4 gap-4 max-w-7xl mx-auto">

        {/* Left: Map + controls */}
        <div className="w-full md:w-2/3 flex flex-col gap-4">
          <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-white/10">
              <h2 className="text-xl font-bold text-white">Interactive Farm Map</h2>
              <p className="text-sm text-slate-400 mt-1">
                Click anywhere on the map to drop a pin, then run the AI simulation.
              </p>
            </div>

            {/* Map container — strict spec §6 */}
            <div className="w-full h-[50vh] md:h-[600px] rounded-lg overflow-hidden relative z-0 p-2">
              <MapUI
                onDistrictSelect={() => {}}
                isLoading={loading}
                initialCenter={[20.5937, 78.9629]}
                initialZoom={5}
                onMapClick={handlePinDrop}
                onPinDrop={handlePinDrop}
              />
            </div>
          </div>

          {/* Pin info + controls */}
          <div className="glass-card p-5 space-y-4">
            {/* Pin status */}
            {pin ? (
              <div className="flex items-center gap-2 text-sm text-green-400">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                Pin set: {pin.lat.toFixed(4)}°N, {pin.lng.toFixed(4)}°E
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <span className="w-2 h-2 rounded-full bg-slate-500" />
                No pin yet — click on the map
              </div>
            )}

            {/* Setup type toggle per spec §3 */}
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-widest mb-2">Farm Type</p>
              <div className="flex rounded-xl overflow-hidden border border-white/10">
                <button
                  onClick={() => setSetupType("short-term")}
                  className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
                    setupType === "short-term"
                      ? "bg-green-500 text-white"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  Short-term / Seasonal
                </button>
                <button
                  onClick={() => setSetupType("long-term")}
                  className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
                    setupType === "long-term"
                      ? "bg-green-500 text-white"
                      : "bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
                  }`}
                >
                  Long-term / Orchard
                </button>
              </div>
            </div>

            {/* Run button */}
            <button
              onClick={runSimulation}
              disabled={loading || !pin}
              className="w-full py-3 px-4 bg-green-500 hover:bg-green-400 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  Running AI Simulation...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Run Simulation
                </>
              )}
            </button>

            {/* Error toast */}
            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-sm text-red-400 flex items-start gap-2">
                <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Right: Results panel — strict spec §6 sidebar */}
        <div className="w-full md:w-1/3 flex-shrink-0">
          <div className="glass-card p-5 min-h-[400px]">
            <h3 className="text-lg font-bold text-white mb-4">Simulation Results</h3>

            {/* Strict conditional rendering — ZERO fallback text when loading or data exists */}
            {loading ? (
              <SkeletonCard />
            ) : results ? (
              <ResultsWidget data={results} />
            ) : (
              <EmptyStateWidget />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
