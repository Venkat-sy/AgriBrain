 "use client";

 import { useState, useEffect } from "react";
 import Link from "next/link";
 import { useRouter } from "next/navigation";
 import { InputPanel } from "@/components/InputPanel";
 import { SimulationPanel } from "@/components/SimulationPanel";
 import { CropCard } from "@/components/CropCard";
 import { useFarm } from "@/context/FarmContext";
 import { WeatherWidget } from "@/components/WeatherWidget";
 import { AlertsWidget } from "@/components/AlertsWidget";
 import { DigitalTwinWidget } from "@/components/DigitalTwinWidget";

 interface District {
   id: number;
   name: string;
   rainfall_mm: number;
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
     farmParams, 
     setFarmParams, 
     simulationResults, 
     setSimulationResults,
     selectedCrop,
     setSelectedCrop,
     currentStep,
     setCurrentStep
   } = useFarm();
   
   const router = useRouter();
   const [districts, setDistricts] = useState<District[]>([]);
   const [soilTypes, setSoilTypes] = useState<string[]>([]);
   const [activeTab, setActiveTab] = useState<"input" | "simulate">("input");
   const [isLoading, setIsLoading] = useState(false);
   const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
   const [apiError, setApiError] = useState<string | null>(null);

   // Load districts and soil types on mount
   useEffect(() => {
     const fetchMetadata = async () => {
       try {
         const [districtsRes, soilTypesRes] = await Promise.all([
           fetch("/api/districts"),
           fetch("/api/soil-types"),
         ]);
         if (districtsRes.ok) {
           const data = await districtsRes.json();
           setDistricts(data.districts || []);
         }
         if (soilTypesRes.ok) {
           const data = await soilTypesRes.json();
           setSoilTypes(data.soil_types || []);
         }
       } catch (error) {
         console.error("Failed to load metadata:", error);
       }
     };
     fetchMetadata();
   }, []);

   // Restore farm params from context if available
   useEffect(() => {
     if (farmParams && districts.length > 0 && soilTypes.length > 0) {
       // Params already in context, we could pre-fill but let InputPanel handle it
     }
   }, [farmParams, districts, soilTypes]);

   const handleRecommendationSubmit = async (formData: {
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
   }) => {
     setIsLoading(true);
     setApiError(null);
     try {
       // Store farm params in context
       setFarmParams(formData);
       
       const response = await fetch("/api/v1/crop/recommend", {
         method: "POST",
         headers: { "Content-Type": "application/json" },
         body: JSON.stringify({ 
           district_id: formData.district_id,
           soil_type: formData.soil_type,
           rainfall_mm: formData.rainfall_mm,
           temperature_c: formData.temperature_c,
           humidity_percent: formData.humidity_percent,
           ph: formData.ph,
           n: formData.n,
           p: formData.p,
           k: formData.k,
           top_k: 5 
         }),
       });

       if (!response.ok) {
         const errorData = await response.json();
         throw new Error(errorData.detail || "Failed to get recommendations");
       }

       const data: ApiResponse = await response.json();
       setRecommendations(data.recommendations);
       setActiveTab("simulate");
       setCurrentStep(2);
     } catch (error) {
       setApiError(error instanceof Error ? error.message : "Unknown error");
     } finally {
       setIsLoading(false);
     }
   };

   const handleSimulationComplete = (results: any) => {
     setSimulationResults(results);
     setCurrentStep(3);
   };

   const handleCropSelect = (crop: Recommendation) => {
     setSelectedCrop(crop.crop_name);
   };

   // Progress indicator
   const steps = [
     { number: 1, label: "Farm Input", href: "/simulate", active: currentStep >= 1 },
     { number: 2, label: "Crop Selection", href: "/simulate", active: currentStep >= 2 },
     { number: 3, label: "Simulation Results", href: "/simulate", active: currentStep >= 3 },
     { number: 4, label: "Calendar", href: "/calendar", active: currentStep >= 4 },
   ];

   return (
     <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
       <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
           <div className="flex items-center justify-between h-16">
             <div className="flex items-center gap-3">
               <Link href="/" className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                   <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4" />
                   </svg>
                 </div>
                 <h1 className="text-2xl font-bold text-slate-900 dark:text-white">AgriBrain</h1>
               </Link>
             </div>
             <nav className="flex gap-4">
               <Link href="/" className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Home</Link>
               <Link href="/simulate" className="px-4 py-2 text-sm font-medium text-green-600 dark:text-green-400">Simulation</Link>
               <Link href="/calendar" className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Calendar</Link>
               <Link href="/expert-chat" className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Expert Chat</Link>
             </nav>
           </div>
         </div>
       </header>

       {/* Progress Indicator */}
       <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
           <div className="flex items-center justify-between">
             {steps.map((step, index) => (
               <div key={step.number} className="flex items-center">
                 <div className="flex items-center">
                   <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                     step.active 
                       ? "bg-green-600 text-white" 
                       : "bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
                   }`}>
                     {step.active ? (
                       <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                       </svg>
                     ) : step.number}
                   </div>
                   <span className={`ml-2 text-sm font-medium ${step.active ? "text-green-600 dark:text-green-400" : "text-slate-500 dark:text-slate-400"}`}>
                     {step.label}
                   </span>
                 </div>
                 {index < steps.length - 1 && (
                   <div className={`w-16 h-0.5 mx-2 ${step.active ? "bg-green-500" : "bg-slate-200 dark:bg-slate-700"}`} />
                 )}
               </div>
             ))}
           </div>
         </div>
       </div>

       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
         <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
           <div className="lg:col-span-1">
             {activeTab === "input" && (
               <>
                 <InputPanel 
                   onSubmit={handleRecommendationSubmit} 
                   isLoading={isLoading} 
                   hasRecommendations={recommendations.length > 0}
                   districts={districts}
                   soilTypes={soilTypes}
                 />
                 {apiError && (
                   <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                     <p className="text-sm text-red-600 dark:text-red-400">{apiError}</p>
                   </div>
                 )}
               </>
             )}
             
             {activeTab === "simulate" && recommendations.length > 0 && (
               <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 animate-slide-up">
                 <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Select Crop to Simulate</h2>
                 <p className="text-slate-600 dark:text-slate-400 mb-6">Click on a crop card to run the digital twin simulation.</p>
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
                   className="mt-6 w-full py-2 px-4 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                 >
                   Back to Input
                 </button>
               </div>
             )}
             
             {/* Sidebar Widgets - always visible */}
             <div className="mt-6 space-y-6">
               <WeatherWidget />
               <AlertsWidget />
               <DigitalTwinWidget />
             </div>
           </div>
           
           <div className="lg:col-span-2 space-y-6">
             {activeTab === "simulate" && (
               <SimulationPanel 
                 recommendations={recommendations}
                 onSimulationComplete={handleSimulationComplete}
                 selectedCrop={selectedCrop}
                 farmParams={farmParams}
               />
             )}
             
             {activeTab === "input" && (
               <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
                 <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Simulation Results</h2>
                 <p className="text-slate-600 dark:text-slate-400 text-center py-12">
                   Configure your farm parameters and get crop recommendations to run simulations.
                 </p>
               </div>
             )}

             {/* Continue to Calendar button */}
             {simulationResults && (
               <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6 animate-slide-up">
                 <div className="flex items-center justify-between">
                   <div>
                     <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">Simulation Complete!</h3>
                     <p className="text-green-700 dark:text-green-300">Your digital twin simulation for <strong>{selectedCrop}</strong> is ready with yield, revenue, and ROI predictions.</p>
                   </div>
                   <Link 
                     href="/calendar"
                     className="px-6 py-3 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 focus:ring-4 focus:ring-green-500/30 transition-all"
                   >
                     View Cultivation Calendar →
                   </Link>
                 </div>
               </div>
             )}
           </div>
         </div>
       </main>
     </div>
   );
 }