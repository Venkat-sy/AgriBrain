"use client";

import { useState } from "react";

interface Recommendation {
  crop_name: string;
  confidence: number;
  match_reasons: string[];
  expected_yield_tons_per_ha: number | null;
  season: string | null;
}

interface SimulationPanelProps {
  recommendations: Recommendation[];
  onSimulationComplete?: (results: any) => void;
  selectedCrop?: string | null;
  farmParams?: any;
}

export function SimulationPanel({ recommendations }: SimulationPanelProps) {
  const [selectedCrop, setSelectedCrop] = useState<Recommendation | null>(null);
  const [simulationResults, setSimulationResults] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Run Simulation</h2>
        <p className="text-slate-600 dark:text-slate-400 text-center py-8">No recommendations available. Get crop recommendations first.</p>
      </div>
    );
  }

  const handleSimulate = async (crop: Recommendation) => {
    setSelectedCrop(crop);
    setIsSimulating(true);
    try {
      // Get district_id, soil_type, rainfall_mm from the form context
      const response = await fetch("/api/v1/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district_id: 1,
          crop_name: crop.crop_name,
          land_area_ha: 2.0,
          budget_inr: 100000,
          soil_type: "Alluvial Soil",
          rainfall_mm: 750,
          planting_season: "Kharif",
          planting_date: "2024-06-15",
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setSimulationResults(data.simulation);
      }
    } catch (error) {
      console.error("Simulation failed:", error);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleBack = () => {
    setSelectedCrop(null);
    setSimulationResults(null);
  };

  if (selectedCrop) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center justify-between">
          <span>Simulation Results: {selectedCrop.crop_name}</span>
          <button onClick={handleBack} className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">Back</button>
        </h2>
        {isSimulating ? (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-slate-600 dark:text-slate-400">Running simulation...</p>
          </div>
        ) : simulationResults ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <p className="text-sm text-green-700 dark:text-green-300">Expected Yield</p>
                <p className="text-2xl font-bold text-green-900 dark:text-green-100">{simulationResults.expected_yield_tons?.toFixed(1) || 0} tons</p>
              </div>
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-sm text-blue-700 dark:text-blue-300">Expected Revenue</p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">₹{simulationResults.expected_revenue_inr?.toLocaleString() || 0}</p>
              </div>
              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <p className="text-sm text-amber-700 dark:text-amber-300">Total Cost</p>
                <p className="text-2xl font-bold text-amber-900 dark:text-amber-100">₹{simulationResults.total_cost_inr?.toLocaleString() || 0}</p>
              </div>
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                <p className="text-sm text-purple-700 dark:text-purple-300">ROI</p>
                <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">{simulationResults.roi_percent?.toFixed(1) || 0}%</p>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-center text-slate-600 dark:text-slate-400 py-8">Simulation completed but no results returned.</p>
        )}
        <button onClick={handleBack} className="mt-6 w-full py-2 px-4 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">Back to Crop Selection</button>
      </div>
    );
  }
return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Run Simulation</h2>
      <p className="text-slate-600 dark:text-slate-400 mb-6">Select a crop to simulate its growth, water needs, costs, and profitability.</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {recommendations.map((rec, index) => (
          <div
            key={`${rec.crop_name}-${index}`}
            className="p-4 border border-slate-200 dark:border-slate-700 rounded-xl hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => handleSimulate(rec)}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <span className="text-sm font-bold text-green-600 dark:text-green-400">{index + 1}</span>
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white capitalize">{rec.crop_name}</h3>
            </div>
            <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden mb-3">
              <div
                className="h-full bg-green-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.round(rec.confidence * 100)}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400">
              <span>Confidence: {Math.round(rec.confidence * 100)}%</span>
              <span>Yield: {rec.expected_yield_tons_per_ha ? rec.expected_yield_tons_per_ha.toFixed(1) + " t/ha" : "N/A"}</span>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); handleSimulate(rec); }}
              disabled={isSimulating}
              className="mt-3 w-full py-2 px-4 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSimulating ? "Simulating..." : "Run Simulation"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}