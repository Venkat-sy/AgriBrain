"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface FarmContextType {
  // Core farm state
  selectedCrop: string | null;
  setSelectedCrop: (crop: string | null) => void;
  
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
  
  // Navigation state
  currentStep: number;
  setCurrentStep: (step: number) => void;
  
  // Reset function
  resetFarm: () => void;
}

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export function FarmProvider({ children }: { children: ReactNode }) {
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null);
  const [simulationResults, setSimulationResults] = useState<any | null>(null);
  const [farmParams, setFarmParams] = useState<any | null>(null);
  const [calendarStages, setCalendarStages] = useState<any[] | null>(null);
  const [currentStep, setCurrentStep] = useState(1);

  const resetFarm = () => {
    setSelectedCrop(null);
    setSimulationResults(null);
    setFarmParams(null);
    setCalendarStages(null);
    setCurrentStep(1);
  };

  return (
    <FarmContext.Provider value={{
      selectedCrop,
      setSelectedCrop,
      simulationResults,
      setSimulationResults,
      farmParams,
      setFarmParams,
      calendarStages,
      setCalendarStages,
      currentStep,
      setCurrentStep,
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