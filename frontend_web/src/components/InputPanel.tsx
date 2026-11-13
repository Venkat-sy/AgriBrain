"use client";

import { useState, useEffect } from "react";
import { Loader2, ChevronDown, ChevronUp, MapPin, Sprout, Eye, EyeOff, ArrowRight, CheckCircle2 } from "lucide-react";

interface District {
  id: number;
  name: string;
  state: string;
  rainfall_mm?: number;
}

interface InputPanelProps {
  onSubmit: (formData: FormPayload) => void;
  isLoading: boolean;
  hasRecommendations: boolean;
}

interface FormPayload {
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
}

const SOIL_TYPES = [
  "Alluvial Soil",
  "Black Soil",
  "Red Soil",
  "Laterite Soil",
  "Sandy Soil",
  "Clayey Soil",
  "Loamy Soil",
];

const PLANTING_SEASONS = ["Kharif", "Rabi", "Zaid", "Annual"];

const DEFAULT_RAINFALL: Record<string, number> = {
  "Alluvial Soil": 900,
  "Black Soil": 750,
  "Red Soil": 700,
  "Laterite Soil": 1200,
  "Sandy Soil": 400,
  "Clayey Soil": 800,
  "Loamy Soil": 850,
};

export function InputPanel({ onSubmit, isLoading, hasRecommendations }: InputPanelProps) {
  // Location data
  const [allDistricts, setAllDistricts] = useState<District[]>([]);
  const [states, setStates] = useState<string[]>([]);
  const [selectedState, setSelectedState] = useState<string>("");
  const [filteredDistricts, setFilteredDistricts] = useState<District[]>([]);
  const [locationLoading, setLocationLoading] = useState(true);
  const [locationError, setLocationError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<FormPayload>({
    district_id: 0,
    soil_type: "Alluvial Soil",
    land_area_ha: 2.0,
    budget_inr: 100000,
    rainfall_mm: 900,
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

  // Fetch all districts + states on mount
  useEffect(() => {
    setLocationLoading(true);
    fetch("/api/districts")
      .then((res) => res.json())
      .then((data) => {
        const districts: District[] = data.districts || [];
        const stateList: string[] = data.states || [];
        setAllDistricts(districts);
        setStates(stateList);
        if (stateList.length > 0) {
          setSelectedState(stateList[0]);
        }
      })
      .catch(() => setLocationError("Failed to load districts. Using defaults."))
      .finally(() => setLocationLoading(false));
  }, []);

  // Filter districts when state changes
  useEffect(() => {
    if (!selectedState) {
      setFilteredDistricts(allDistricts);
      return;
    }
    const filtered = allDistricts.filter((d) => d.state === selectedState);
    setFilteredDistricts(filtered);
    if (filtered.length > 0) {
      setFormData((prev) => ({
        ...prev,
        district_id: filtered[0].id,
        rainfall_mm: filtered[0].rainfall_mm || prev.rainfall_mm,
      }));
    }
  }, [selectedState, allDistricts]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    if (type === "number") {
      setFormData((prev) => ({ ...prev, [name]: parseFloat(value) || 0 }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSoilTypeChange = (soilType: string) => {
    setFormData((prev) => ({
      ...prev,
      soil_type: soilType,
      rainfall_mm: DEFAULT_RAINFALL[soilType] || prev.rainfall_mm,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.district_id) {
      onSubmit(formData);
    }
  };

  const glassCard = "bg-white/5 dark:bg-slate-900/5 backdrop-blur-md border border-white/10 dark:border-slate-800/50 rounded-2xl shadow-xl shadow-slate-900/5";
  const inputClass = "w-full px-4 py-3 bg-white/5 dark:bg-slate-800/30 border border-white/10 dark:border-slate-700/50 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed";
  const labelClass = "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2";
  const selectClass = "w-full px-4 py-3 bg-white/5 dark:bg-slate-800/30 border border-white/10 dark:border-slate-700/50 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-transparent transition-all appearance-none";

  return (
    <div className="animate-fade-in">
      {/* Glassmorphism Card */}
      <div className={glassCard}>
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
              <MapPin className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Farm Parameters</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">Configure your farm details for accurate recommendations</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* ── LOCATION SECTION ── */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Location
              </h4>

              {/* State Select */}
              <div>
                <label className={labelClass}>State</label>
                <div className="relative">
                  <select
                    name="state"
                    value={selectedState}
                    onChange={(e) => setSelectedState(e.target.value)}
                    disabled={isLoading || locationLoading}
                    className={selectClass + " pr-10"}
                  >
                    {locationLoading ? (
                      <option value="">Loading states...</option>
                    ) : (
                      <>
                        <option value="">Select a state</option>
                        {states.map((state) => (
                          <option key={state} value={state}>
                            {state}
                          </option>
                        ))}
                      </>
                    )}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                </div>
              </div>

              {/* District Select */}
              <div>
                <label className={labelClass}>District</label>
                <div className="relative">
                  <select
                    name="district_id"
                    value={formData.district_id}
                    onChange={(e) => setFormData((prev) => ({ ...prev, district_id: parseInt(e.target.value) }))}
                    disabled={isLoading || locationLoading}
                    className={selectClass + " pr-10"}
                  >
                    <option value="0">Select a district</option>
                    {filteredDistricts.map((district) => (
                      <option key={district.id} value={district.id}>
                        {district.name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                </div>
                {locationError && (
                  <p className="mt-1 text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
                    <span className="w-3 h-3" />{locationError}
                  </p>
                )}
              </div>
            </div>

            <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent dark:via-slate-700/50 my-4" />

            {/* ── BASIC FARM PARAMETERS ── */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Basic Parameters
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={labelClass}>Soil Type</label>
                  <div className="relative">
                    <select
                      name="soil_type"
                      value={formData.soil_type}
                      onChange={(e) => handleSoilTypeChange(e.target.value)}
                      disabled={isLoading}
                      className={selectClass + " pr-10"}
                    >
                      {SOIL_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                <div>
                  <label className={labelClass}>Land Area (hectares)</label>
                  <input
                    type="number"
                    name="land_area_ha"
                    value={formData.land_area_ha}
                    onChange={handleChange}
                    min="0.1"
                    max="10000"
                    step="0.1"
                    className={inputClass}
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label className={labelClass}>Budget (₹)</label>
                  <input
                    type="number"
                    name="budget_inr"
                    value={formData.budget_inr}
                    onChange={handleChange}
                    min="1000"
                    max="100000000"
                    step="1000"
                    className={inputClass}
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label className={labelClass}>Planting Season</label>
                  <div className="relative">
                    <select
                      name="planting_season"
                      value={formData.planting_season}
                      onChange={(e) => setFormData((prev) => ({ ...prev, planting_season: e.target.value }))}
                      disabled={isLoading}
                      className={selectClass + " pr-10"}
                    >
                      {PLANTING_SEASONS.map((season) => (
                        <option key={season} value={season}>
                          {season}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                  </div>
                </div>

                <div>
                  <label className={labelClass}>Planting Date</label>
                  <input
                    type="date"
                    name="planned_start_date"
                    value={formData.planned_start_date}
                    onChange={(e) => setFormData((prev) => ({ ...prev, planned_start_date: e.target.value }))}
                    className={inputClass}
                    disabled={isLoading}
                  />
                </div>

                <div>
                  <label className={labelClass}>Rainfall (mm/year)</label>
                  <input
                    type="number"
                    name="rainfall_mm"
                    value={formData.rainfall_mm}
                    onChange={handleChange}
                    min="0"
                    max="5000"
                    step="10"
                    className={inputClass}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            {/* ── ADVANCED PARAMETERS TOGGLE ── */}
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full flex items-center justify-between px-2 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <span className="flex items-center gap-2">
                <Sprout className="w-4 h-4" />
                Advanced Soil Parameters
              </span>
              {showAdvanced ? (
                <ChevronUp className="w-5 h-5 transition-transform" />
              ) : (
                <ChevronDown className="w-5 h-5 transition-transform" />
              )}
            </button>

            {showAdvanced && (
              <div className="space-y-4 animate-slide-up border-t border-white/10 dark:border-slate-700/50 pt-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className={labelClass}>Temperature (°C)</label>
                    <input
                      type="number"
                      name="temperature_c"
                      value={formData.temperature_c}
                      onChange={handleChange}
                      min="-10"
                      max="50"
                      step="0.5"
                      className={inputClass}
                      disabled={isLoading}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Humidity (%)</label>
                    <input
                      type="number"
                      name="humidity_percent"
                      value={formData.humidity_percent}
                      onChange={handleChange}
                      min="0"
                      max="100"
                      step="1"
                      className={inputClass}
                      disabled={isLoading}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={labelClass}>Soil pH</label>
                    <input
                      type="number"
                      name="ph"
                      value={formData.ph}
                      onChange={handleChange}
                      min="3"
                      max="10"
                      step="0.1"
                      className={inputClass}
                      disabled={isLoading}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Nitrogen (kg/ha)</label>
                    <input
                      type="number"
                      name="n"
                      value={formData.n}
                      onChange={handleChange}
                      min="0"
                      max="500"
                      step="1"
                      className={inputClass}
                      disabled={isLoading}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={labelClass}>Phosphorus (kg/ha)</label>
                    <input
                      type="number"
                      name="p"
                      value={formData.p}
                      onChange={handleChange}
                      min="0"
                      max="200"
                      step="1"
                      className={inputClass}
                      disabled={isLoading}
                    />
                  </div>
                  <div>
                    <label className={labelClass}>Potassium (kg/ha)</label>
                    <input
                      type="number"
                      name="k"
                      value={formData.k}
                      onChange={handleChange}
                      min="0"
                      max="500"
                      step="1"
                      className={inputClass}
                      disabled={isLoading}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* ── SUBMIT ── */}
            <button
              type="submit"
              disabled={isLoading || !formData.district_id}
              className="w-full py-4 px-6 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-xl hover:from-green-600 hover:to-emerald-600 focus:ring-4 focus:ring-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-3 shadow-lg shadow-green-500/25"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analyzing farm data...</span>
                </>
              ) : (
                <>
                  <Sprout className="w-5 h-5" />
                  <span>Get Crop Recommendations</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>

            {hasRecommendations && (
              <p className="text-center text-sm text-green-500 dark:text-green-400 font-medium flex items-center justify-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Recommendations ready — view results
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}