"use client";

import { useState, useEffect } from "react";
import { Loader2, ChevronDown, ChevronUp, MapPin, Sprout } from "lucide-react";

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
    const parsed = type === "number" ? parseFloat(value) : value;
    setFormData((prev) => ({ ...prev, [name]: parsed }));
  };

  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = parseInt(e.target.value);
    const district = filteredDistricts.find((d) => d.id === id);
    setFormData((prev) => ({
      ...prev,
      district_id: id,
      rainfall_mm: district?.rainfall_mm || prev.rainfall_mm,
    }));
  };

  const handleSoilChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const soil = e.target.value;
    setFormData((prev) => ({
      ...prev,
      soil_type: soil,
      rainfall_mm: DEFAULT_RAINFALL[soil] || prev.rainfall_mm,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.district_id) return;
    onSubmit(formData);
  };

  const selectClass =
    "w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm";

  const inputClass =
    "w-full px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors disabled:opacity-50 text-sm";

  const labelClass = "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5";

  return (
    <div className="sticky top-24 space-y-4">
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <Sprout className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Farm Parameters</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Enter your farm details for ML-powered recommendations
            </p>
          </div>
        </div>

        {locationError && (
          <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-xs text-amber-700 dark:text-amber-300">
            {locationError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* ── LOCATION ── */}
          <div>
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-3 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-green-600" />
              Location
            </h3>

            {/* State selector */}
            <div className="mb-3">
              <label className={labelClass}>
                State <span className="text-red-500">*</span>
              </label>
              {locationLoading ? (
                <div className="flex items-center gap-2 px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <Loader2 className="w-4 h-4 animate-spin text-green-600" />
                  <span className="text-sm text-slate-500">Loading states...</span>
                </div>
              ) : (
                <select
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  className={selectClass}
                  disabled={isLoading || states.length === 0}
                >
                  {states.length === 0 && (
                    <option value="">No states available</option>
                  )}
                  {states.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* District selector — cascades from state */}
            <div>
              <label className={labelClass}>
                District <span className="text-red-500">*</span>
              </label>
              {locationLoading ? (
                <div className="flex items-center gap-2 px-4 py-2.5 border border-slate-300 dark:border-slate-600 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <Loader2 className="w-4 h-4 animate-spin text-green-600" />
                  <span className="text-sm text-slate-500">Loading districts...</span>
                </div>
              ) : (
                <select
                  value={formData.district_id || ""}
                  onChange={handleDistrictChange}
                  className={selectClass}
                  disabled={isLoading || filteredDistricts.length === 0}
                >
                  {filteredDistricts.length === 0 && (
                    <option value="">No districts for selected state</option>
                  )}
                  {filteredDistricts.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name}
                    </option>
                  ))}
                </select>
              )}
              {!locationLoading && filteredDistricts.length > 0 && (
                <p className="mt-1 text-xs text-slate-400">
                  {filteredDistricts.length} district
                  {filteredDistricts.length !== 1 ? "s" : ""} in {selectedState}
                </p>
              )}
            </div>
          </div>

          {/* ── SOIL ── */}
          <div>
            <label className={labelClass}>
              Soil Type <span className="text-red-500">*</span>
            </label>
            <select
              name="soil_type"
              value={formData.soil_type}
              onChange={handleSoilChange}
              className={selectClass}
              disabled={isLoading}
            >
              {SOIL_TYPES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* ── FARM BASICS ── */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>
                Land Area (ha) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                name="land_area_ha"
                value={formData.land_area_ha}
                onChange={handleChange}
                min="0.1"
                max="1000"
                step="0.1"
                className={inputClass}
                disabled={isLoading}
              />
            </div>
            <div>
              <label className={labelClass}>
                Budget (₹) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                name="budget_inr"
                value={formData.budget_inr}
                onChange={handleChange}
                min="1000"
                max="10000000"
                step="1000"
                className={inputClass}
                disabled={isLoading}
              />
            </div>
          </div>

          {/* ── RAINFALL & SEASON ── */}
          <div>
            <label className={labelClass}>Rainfall (mm)</label>
            <input
              type="number"
              name="rainfall_mm"
              value={formData.rainfall_mm}
              onChange={handleChange}
              min="0"
              max="5000"
              step="1"
              className={inputClass}
              disabled={isLoading}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelClass}>Planting Season</label>
              <select
                name="planting_season"
                value={formData.planting_season}
                onChange={handleChange}
                className={selectClass}
                disabled={isLoading}
              >
                {PLANTING_SEASONS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>Start Date</label>
              <input
                type="date"
                name="planned_start_date"
                value={formData.planned_start_date}
                onChange={handleChange}
                className={inputClass}
                disabled={isLoading}
              />
            </div>
          </div>

          {/* ── ADVANCED TOGGLE ── */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-700 rounded-lg transition-colors"
            disabled={isLoading}
          >
            <span>Advanced Soil & Climate Parameters</span>
            {showAdvanced ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          {showAdvanced && (
            <div className="space-y-4 border-t border-slate-200 dark:border-slate-700 pt-4">
              <div className="grid grid-cols-2 gap-3">
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
              <div className="grid grid-cols-2 gap-3">
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
              <div className="grid grid-cols-2 gap-3">
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
            className="w-full py-3 px-6 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 focus:ring-4 focus:ring-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing farm data...
              </>
            ) : (
              "Get Crop Recommendations"
            )}
          </button>

          {hasRecommendations && (
            <p className="text-center text-sm text-green-600 dark:text-green-400 font-medium">
              ✓ Recommendations ready — scroll right to view results
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
