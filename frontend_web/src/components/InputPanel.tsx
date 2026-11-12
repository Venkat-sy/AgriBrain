"use client";

import { useState, useMemo, useEffect } from "react";

interface InputPanelProps {
  onSubmit: (formData: {
    district_id: number;
    soil_type: string;
    rainfall_mm: number;
    temperature_c?: number;
    humidity_percent?: number;
    ph?: number;
    n?: number;
    p?: number;
    k?: number;
   land_area_ha: number;
   budget_inr: number;
   planting_season: string;
   planned_start_date: string;
  }) => void;
  isLoading: boolean;
  hasRecommendations: boolean;
  districts: Array<{id: number, name: string, rainfall_mm: number}>;
  soilTypes: string[];
}

const PLANTING_SEASONS = ["Kharif", "Rabi", "Zaid", "Annual"];

export function InputPanel({ onSubmit, isLoading, hasRecommendations, districts, soilTypes }: InputPanelProps) {
  const [formData, setFormData] = useState({
    district_id: districts[0]?.id || 1,
    soil_type: soilTypes[0] || "Alluvial Soil",
    land_area_ha: 2.0,
    budget_inr: 100000,
    rainfall_mm: districts[0]?.rainfall_mm || 750,
    temperature_c: 28,
    humidity_percent: 65,
    ph: 6.5,
    n: 120,
    p: 40,
    k: 150,
    planting_season: "Kharif",
    planned_start_date: "",
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  // Update form when districts/soilTypes load
  useEffect(() => {
    if (districts.length > 0) {
      setFormData(prev => ({ 
        ...prev, 
        district_id: prev.district_id || districts[0].id,
        rainfall_mm: prev.rainfall_mm || districts[0].rainfall_mm
      }));
    }
    if (soilTypes.length > 0) {
      setFormData(prev => ({ ...prev, soil_type: prev.soil_type || soilTypes[0] }));
    }
  }, [districts, soilTypes]);

  const handleDistrictChange = (districtId: number) => {
    const district = districts.find(d => d.id === districtId);
    if (district) {
      setFormData(prev => ({ ...prev, district_id: districtId, rainfall_mm: district.rainfall_mm }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      district_id: formData.district_id,
      soil_type: formData.soil_type,
      rainfall_mm: formData.rainfall_mm,
      temperature_c: formData.temperature_c,
      humidity_percent: formData.humidity_percent,
      ph: formData.ph,
      n: formData.n,
      p: formData.p,
      k: formData.k,
     land_area_ha: formData.land_area_ha,
     budget_inr: formData.budget_inr,
     planting_season: formData.planting_season,
     planned_start_date: formData.planned_start_date,
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const parsedValue = type === "number" ? parseFloat(value) : value;
    setFormData(prev => ({ ...prev, [name]: parsedValue }));
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, planned_start_date: e.target.value }));
  };

  const content = useMemo(() => (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Basic Parameters */}
      <div className="space-y-5">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
          </svg>
          Basic Parameters
        </h3>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            District <span className="text-red-500">*</span>
          </label>
          <select name="district_id" value={formData.district_id} onChange={e => handleDistrictChange(parseInt(e.target.value))} className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading}>
            {districts.map(district => (<option key={district.id} value={district.id}>{district.name}</option>))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Soil Type <span className="text-red-500">*</span>
          </label>
          <select name="soil_type" value={formData.soil_type} onChange={handleChange} className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading}>
            {soilTypes.map(soil => (<option key={soil} value={soil}>{soil}</option>))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Land Area (hectares) <span className="text-red-500">*</span></label>
            <input type="number" name="land_area_ha" value={formData.land_area_ha} onChange={handleChange} min="0.1" max="1000" step="0.1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Budget (₹) <span className="text-red-500">*</span></label>
            <input type="number" name="budget_inr" value={formData.budget_inr} onChange={handleChange} min="1000" max="10000000" step="1000" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Rainfall (mm) <span className="text-red-500">*</span></label>
          <input type="number" name="rainfall_mm" value={formData.rainfall_mm} onChange={handleChange} min="0" max="5000" step="1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Planting Season</label>
            <select name="planting_season" value={formData.planting_season} onChange={handleChange} className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading}>
              {PLANTING_SEASONS.map(season => (<option key={season} value={season}>{season}</option>))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Planned Start Date</label>
            <input type="date" name="planned_start_date" value={formData.planned_start_date} onChange={handleDateChange} className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
          </div>
        </div>
      </div>

      {/* Advanced Parameters Toggle */}
      <button type="button" onClick={() => setShowAdvanced(!showAdvanced)} className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors" disabled={isLoading}>
        <span>{showAdvanced ? "Hide" : "Show"} Advanced Parameters</span>
        <svg className={`w-5 h-5 transition-transform ${showAdvanced ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </button>

      {/* Advanced Parameters */}
      {showAdvanced && (
        <div className="space-y-5 animate-fade-in border-t border-slate-200 dark:border-slate-700 pt-5">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Advanced Soil & Climate Parameters
          </h3>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Temperature (°C)</label>
              <input type="number" name="temperature_c" value={formData.temperature_c} onChange={handleChange} min="-10" max="50" step="0.5" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Humidity (%)</label>
              <input type="number" name="humidity_percent" value={formData.humidity_percent} onChange={handleChange} min="0" max="100" step="1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Soil pH</label>
              <input type="number" name="ph" value={formData.ph} onChange={handleChange} min="3" max="10" step="0.1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Nitrogen (kg/ha)</label>
              <input type="number" name="n" value={formData.n} onChange={handleChange} min="0" max="500" step="1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Phosphorus (kg/ha)</label>
              <input type="number" name="p" value={formData.p} onChange={handleChange} min="0" max="200" step="1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Potassium (kg/ha)</label>
              <input type="number" name="k" value={formData.k} onChange={handleChange} min="0" max="500" step="1" className="w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors" disabled={isLoading} />
            </div>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button type="submit" disabled={isLoading} className="w-full py-3 px-6 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 focus:ring-4 focus:ring-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all">
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Analyzing...
          </span>
        ) : (
          "Get Crop Recommendations"
        )}
      </button>

      {hasRecommendations && (
        <p className="text-center text-sm text-green-600 dark:text-green-400">Recommendations received! Switch to the "Run Simulation" tab to proceed.</p>
      )}
    </form>
  ), [formData, showAdvanced, isLoading, hasRecommendations]);

  return (
    <div className="sticky top-24 space-y-6 animate-slide-up">
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Farm Parameters</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Enter your farm details to get crop recommendations</p>
          </div>
        </div>
        {content}
      </div>
    </div>
  );
}