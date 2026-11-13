"use client";

import { createContext, useContext, useState, ReactNode, useCallback } from "react";

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

interface FarmContextType {
  // Core farm state
  selectedCrop: string | null;
  setSelectedCrop: (crop: string | null) => void;

  // Location & coordinates
  coordinates: Coordinates | null;
  setCoordinates: (coords: Coordinates | null) => void;

  // Auto-fetched soil parameters
  soilParams: SoilParameters | null;
  setSoilParams: (params: SoilParameters | null) => void;

  // Annual rainfall
  annualRainfall: number | null;
  setAnnualRainfall: (rainfall: number | null) => void;

  // Simulation state
  simulationResults: any | null;
  setSimulationResults: (results: any) => void;

  // Farm parameters
  farmParams: {
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
  } | null;
  setFarmParams: (params: any) => void;

  // Calendar state
  calendarStages: any[] | null;
  setCalendarStages: (stages: any[]) => void;
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
}

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export function FarmProvider({ children }: { children: ReactNode }) {
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null);
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [soilParams, setSoilParams] = useState<SoilParameters | null>(null);
  const [annualRainfall, setAnnualRainfall] = useState<number | null>(null);
  const [simulationResults, setSimulationResults] = useState<any | null>(null);
  const [farmParams, setFarmParams] = useState<any | null>(null);
  const [calendarStages, setCalendarStages] = useState<any[] | null>(null);
  const [currentCalendarStage, setCurrentCalendarStage] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);

  const addChatMessage = useCallback((message: ChatMessage) => {
    setChatHistory(prev => [...prev, message]);
  }, []);

  const clearChatHistory = useCallback(() => {
    setChatHistory([]);
  }, []);

  const resetFarm = () => {
    setSelectedCrop(null);
    setCoordinates(null);
    setSoilParams(null);
    setAnnualRainfall(null);
    setSimulationResults(null);
    setFarmParams(null);
    setCalendarStages(null);
    setCurrentCalendarStage(null);
    setCurrentStep(1);
    // Note: chatHistory is NOT reset - persists across sessions
  };

  return (
    <FarmContext.Provider value={{
      selectedCrop,
      setSelectedCrop,
      coordinates,
      setCoordinates,
      soilParams,
      setSoilParams,
      annualRainfall,
      setAnnualRainfall,
      simulationResults,
      setSimulationResults,
      farmParams,
      setFarmParams,
      calendarStages,
      setCalendarStages,
      currentCalendarStage,
      setCurrentCalendarStage,
      currentStep,
      setCurrentStep,
      chatHistory,
      addChatMessage,
      clearChatHistory,
      resetFarm,
    }}>
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