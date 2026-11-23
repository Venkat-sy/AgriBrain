"use client";

import React, { createContext, useContext, useState, ReactNode, useCallback, useEffect, useRef } from "react";

interface Coordinates {
  lat: number;
  lon: number;
}

interface SoilParameters {
  ph: number;
  texture: string;
  organic_carbon: number;
  n: number;
  p: number;
  k: number;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface SimulationResults {
  expected_yield_tons?: number;
  expected_revenue_inr?: number;
  total_cost_inr?: number;
  roi_percent?: number;
  risk_level?: string;
  water_sufficiency?: boolean;
  monthly_breakdown?: Array<{
    month: number;
    growth_stage: string;
    irrigation_needed_mm?: number;
    rainfall_mm?: number;
  }>;
  cost_breakdown?: Array<{
    activity: string;
    quantity: number;
    unit: string;
    unit_cost: number;
    total_cost: number;
  }>;
  [key: string]: unknown;
}

interface FarmParameters {
  district_id: number;
  soil_type: string;
  land_area_ha: number;
  budget_inr: number;
  rainfall_mm: number;
  temperature_c: number;
  humidity_percent: number;
  ph: number;
  n: number;
  p: number;
  k: number;
  planting_season: string;
  planned_start_date: string;
}

interface CalendarStage {
  month: number;
  stage: string;
  description: string;
  water_needed_mm: number;
  rainfall_mm: number;
  tasks: string[];
  start_date: string;
  end_date: string;
}

// Extended state for the design spec
interface FarmOverrides {
  rainfallOverride?: number;
  tempOverride?: number;
}

interface IrrigationType {
  type: "Rainfed" | "Canal" | "Drip" | "Sprinkler";
}

interface FarmContextType {
  // Core farm state
  selectedCrop: string | null;
  setSelectedCrop: (crop: string | null) => void;

  // Location & coordinates
  coordinates: Coordinates | null;
  setCoordinates: (coords: Coordinates | null) => void;
  district: string | null;
  setDistrict: (district: string | null) => void;
  state: string | null;
  setState: (state: string | null) => void;
  icarZone: string | null;
  setIcarZone: (zone: string | null) => void;

  // Auto-fetched soil parameters
  soilParams: SoilParameters | null;
  setSoilParams: (params: SoilParameters | null) => void;

  // Annual rainfall
  annualRainfall: number | null;
  setAnnualRainfall: (rainfall: number | null) => void;

  // Simulation state
  simulationResults: SimulationResults | null;
  setSimulationResults: (results: SimulationResults | null) => void;

  // Farm parameters
  farmParams: FarmParameters | null;
  setFarmParams: (params: FarmParameters | null) => void;

  // Overrides
  overrides: FarmOverrides;
  setOverrides: (overrides: FarmOverrides) => void;

  // Irrigation type
  irrigationType: IrrigationType["type"] | null;
  setIrrigationType: (type: IrrigationType["type"] | null) => void;

  // Soil override
  soilOverride: string | null;
  setSoilOverride: (soil: string | null) => void;

  // Calendar state
  calendarStages: CalendarStage[] | null;
  setCalendarStages: (stages: CalendarStage[] | null) => void;
  currentCalendarStage: string | null;
  setCurrentCalendarStage: (stage: string | null) => void;

  // Navigation state
  currentStep: number;
  setCurrentStep: (step: number) => void;

  // Chat conversation history (persisted across pages)
  chatHistory: ChatMessage[];
  addChatMessage: (message: ChatMessage) => void;
  clearChatHistory: () => void;

  // Reset function
  resetFarm: () => void;

  // Hydration state
  isHydrated: boolean;
}

const STORAGE_KEY = "agribrain-farm-context";

const defaultState = {
  selectedCrop: null,
  coordinates: null,
  district: null,
  state: null,
  icarZone: null,
  soilParams: null,
  annualRainfall: null,
  simulationResults: null,
  farmParams: null,
  overrides: {},
  irrigationType: null,
  soilOverride: null,
  calendarStages: null,
  currentCalendarStage: null,
  currentStep: 1,
  chatHistory: [],
};

function loadFromStorage(): Partial<FarmContextType> {
  if (typeof window === "undefined") return {};
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Convert date strings back to Date objects for chatHistory
      if (parsed.chatHistory) {
        parsed.chatHistory = parsed.chatHistory.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
      }
      return parsed;
    }
  } catch (e) {
    console.warn("Failed to load farm context from localStorage:", e);
  }
  return {};
}

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export function FarmProvider({ children }: { children: ReactNode }) {
  const [isHydrated, setIsHydrated] = useState(false);
  const [state, setState] = useState<Partial<FarmContextType>>({});
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const loaded = loadFromStorage();
    setState(loaded);
    setIsHydrated(true);
  }, []);

  // Debounced save to localStorage
  const saveToStorage = useCallback((newState: Partial<FarmContextType>) => {
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      if (typeof window !== "undefined") {
        try {
          const toStore = { ...state, ...newState };
          localStorage.setItem(STORAGE_KEY, JSON.stringify(toStore));
        } catch (e) {
          console.warn("Failed to save farm context to localStorage:", e);
        }
      }
    }, 300);
  }, [state]);

  const updateState = useCallback(<K extends keyof FarmContextType>(key: K, value: FarmContextType[K]) => {
    setState(prev => {
      const newState = { ...prev, [key]: value };
      saveToStorage(newState);
      return newState;
    });
  }, [saveToStorage]);

  const setSelectedCrop = useCallback((crop: string | null) => updateState("selectedCrop", crop), [updateState]);
  const setCoordinates = useCallback((coords: Coordinates | null) => updateState("coordinates", coords), [updateState]);
  const setDistrict = useCallback((district: string | null) => updateState("district", district), [updateState]);
  const setState_ = useCallback((state: string | null) => updateState("state", state), [updateState]);
  const setIcarZone = useCallback((zone: string | null) => updateState("icarZone", zone), [updateState]);
  const setSoilParams = useCallback((params: SoilParameters | null) => updateState("soilParams", params), [updateState]);
  const setAnnualRainfall = useCallback((rainfall: number | null) => updateState("annualRainfall", rainfall), [updateState]);
  const setSimulationResults = useCallback((results: SimulationResults | null) => updateState("simulationResults", results), [updateState]);
  const setFarmParams = useCallback((params: FarmParameters | null) => updateState("farmParams", params), [updateState]);
  const setOverrides = useCallback((overrides: FarmOverrides) => updateState("overrides", overrides), [updateState]);
  const setIrrigationType = useCallback((type: IrrigationType["type"] | null) => updateState("irrigationType", type), [updateState]);
  const setSoilOverride = useCallback((soil: string | null) => updateState("soilOverride", soil), [updateState]);
  const setCalendarStages = useCallback((stages: CalendarStage[] | null) => updateState("calendarStages", stages), [updateState]);
  const setCurrentCalendarStage = useCallback((stage: string | null) => updateState("currentCalendarStage", stage), [updateState]);
  const setCurrentStep = useCallback((step: number) => updateState("currentStep", step), [updateState]);

  const addChatMessage = useCallback((message: ChatMessage) => {
    setState(prev => {
      const newHistory = [...(prev.chatHistory || []), message];
      saveToStorage({ ...prev, chatHistory: newHistory });
      return { ...prev, chatHistory: newHistory };
    });
  }, [saveToStorage]);

  const clearChatHistory = useCallback(() => {
    updateState("chatHistory", []);
  }, [updateState]);

  const resetFarm = useCallback(() => {
    const resetState = { ...defaultState, isHydrated: true };
    setState(resetState);
    if (typeof window !== "undefined") {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  // Provide default values for unhydrated state
  const contextValue: FarmContextType = {
    selectedCrop: state.selectedCrop ?? null,
    setSelectedCrop,
    coordinates: state.coordinates ?? null,
    setCoordinates,
    district: state.district ?? null,
    setDistrict,
    state: state.state ?? null,
    setState: setState_,
    icarZone: state.icarZone ?? null,
    setIcarZone,
    soilParams: state.soilParams ?? null,
    setSoilParams,
    annualRainfall: state.annualRainfall ?? null,
    setAnnualRainfall,
    simulationResults: state.simulationResults ?? null,
    setSimulationResults,
    farmParams: state.farmParams ?? null,
    setFarmParams,
    overrides: state.overrides ?? {},
    setOverrides,
    irrigationType: state.irrigationType ?? null,
    setIrrigationType,
    soilOverride: state.soilOverride ?? null,
    setSoilOverride,
    calendarStages: state.calendarStages ?? null,
    setCalendarStages,
    currentCalendarStage: state.currentCalendarStage ?? null,
    setCurrentCalendarStage,
    currentStep: state.currentStep ?? 1,
    setCurrentStep,
    chatHistory: state.chatHistory ?? [],
    addChatMessage,
    clearChatHistory,
    resetFarm,
    isHydrated,
  };

  if (!isHydrated) {
    return (
      <FarmContext.Provider value={contextValue}>
        {children}
      </FarmContext.Provider>
    );
  }

  return (
    <FarmContext.Provider value={contextValue}>
      {children}
    </FarmContext.Provider>
  );
}

export function useFarm() {
  const context = useContext(FarmContext);
  if (!context) {
    throw new Error("useFarm must be used within a FarmProvider");
  }
  return context;
}