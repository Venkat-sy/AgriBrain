 "use client";

 import { useState, useEffect } from "react";
 import { useFarm } from "@/context/FarmContext";
 import { Loader2, Thermometer, Droplets, Leaf, TrendingUp } from "lucide-react";

 interface TwinMetrics {
   soilTemp: number;
   moisture: number;
   nitrogenLevel: number;
   yieldEstimate: number;
 }

 interface SimulationScenario {
   name: string;
   color: string;
   risk: string;
 }

 export function DigitalTwinWidget() {
   const { simulationResults, selectedCrop, farmParams } = useFarm();
   const [metrics, setMetrics] = useState<TwinMetrics | null>(null);
   const [scenario, setScenario] = useState("normal");
   const [progress, setProgress] = useState(0);
   const [loading, setLoading] = useState(false);

   const scenarios: SimulationScenario[] = [
     { name: "Normal", color: "#39ff14", risk: "Low" },
     { name: "Drought", color: "#ff4757", risk: "High" },
     { name: "Flood", color: "#00ffff", risk: "Medium" },
     { name: "Optimal", color: "#bf00ff", risk: "Very Low" },
   ];

   // Animate progress
   useEffect(() => {
     const interval = setInterval(() => {
       setProgress(prev => (prev >= 100 ? 0 : prev + 1));
     }, 100);
     return () => clearInterval(interval);
   }, []);

   // Generate metrics from simulation results
   useEffect(() => {
     if (simulationResults) {
       setMetrics({
         soilTemp: 25 + Math.random() * 10,
         moisture: 60 + Math.random() * 30,
         nitrogenLevel: 70 + Math.random() * 30,
         yieldEstimate: simulationResults.expected_yield_tons || 4.2,
       });
     } else {
       setMetrics({
         soilTemp: 28.4,
         moisture: 67,
         nitrogenLevel: 85,
         yieldEstimate: 4.2,
       });
     }
   }, [simulationResults]);

   const currentScenario = scenarios.find(s => s.name.toLowerCase() === scenario.toLowerCase()) || scenarios[0];

   return (
     <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
       <div className="flex items-center justify-between mb-6">
         <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
           <TrendingUp className="w-5 h-5 text-purple-500" />
           Digital Twin
         </h2>
         <select
           value={scenario}
           onChange={e => setScenario(e.target.value)}
           className="px-3 py-1 text-sm border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 focus:ring-2 focus:ring-green-500"
         >
           {scenarios.map(s => (
             <option key={s.name} value={s.name.toLowerCase()}>
               {s.name} ({s.risk} Risk)
             </option>
           ))}
         </select>
       </div>

       {/* Scenario Progress */}
       <div className="mb-6">
         <div className="flex items-center justify-between mb-2">
           <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
             Simulation Progress: {scenario} Scenario
           </span>
           <span className="text-sm font-bold" style={{ color: currentScenario.color }}>
             {progress}%
           </span>
         </div>
         <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
           <div
             className="h-full rounded-full transition-all duration-300"
             style={{
               width: `${progress}%`,
               backgroundColor: currentScenario.color,
             }}
           />
         </div>
         <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-1">
           {scenarios.map(s => (
             <span key={s.name} style={{ color: s.color }}>
               {s.name}: {s.risk}
             </span>
           ))}
         </div>
       </div>

       {/* Twin Metrics */}
       <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
         <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
           <div className="flex items-center gap-2 mb-2">
             <Thermometer className="w-5 h-5 text-amber-500" />
             <span className="text-sm text-amber-700 dark:text-amber-300">Soil Temp</span>
           </div>
           <div className="text-2xl font-bold text-slate-900 dark:text-white">
             {metrics?.soilTemp.toFixed(1) || "—"}°C
           </div>
         </div>
         <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
           <div className="flex items-center gap-2 mb-2">
             <Droplets className="w-5 h-5 text-blue-500" />
             <span className="text-sm text-blue-700 dark:text-blue-300">Moisture</span>
           </div>
           <div className="text-2xl font-bold text-slate-900 dark:text-white">
             {metrics?.moisture.toFixed(0) || "—"}%
           </div>
         </div>
         <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
           <div className="flex items-center gap-2 mb-2">
             <Leaf className="w-5 h-5 text-green-500" />
             <span className="text-sm text-green-700 dark:text-green-300">N Level</span>
           </div>
           <div className="text-2xl font-bold text-slate-900 dark:text-white">
             {metrics?.nitrogenLevel.toFixed(0) || "—"}ppm
           </div>
         </div>
         <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl">
           <div className="flex items-center gap-2 mb-2">
             <TrendingUp className="w-5 h-5 text-purple-500" />
             <span className="text-sm text-purple-700 dark:text-purple-300">Yield Est.</span>
           </div>
           <div className="text-2xl font-bold text-slate-900 dark:text-white">
             {metrics?.yieldEstimate.toFixed(1) || "—"}t/ha
           </div>
         </div>
       </div>

       {/* Simulation Results */}
       {simulationResults && (
         <div className="p-4 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-xl">
           <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
             <Loader2 className="w-4 h-4 text-green-500" />
             Simulation Output
           </h3>
           <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
             <div>
               <div className="text-xs text-slate-500 dark:text-slate-400">Total Cost</div>
               <div className="font-semibold text-slate-900 dark:text-white">
                 ₹{simulationResults.total_cost_inr?.toLocaleString() || 0}
               </div>
             </div>
             <div>
               <div className="text-xs text-slate-500 dark:text-slate-400">Expected Yield</div>
               <div className="font-semibold text-slate-900 dark:text-white">
                 {simulationResults.expected_yield_tons?.toFixed(1) || 0}t
               </div>
             </div>
             <div>
               <div className="text-xs text-slate-500 dark:text-slate-400">Market Value</div>
               <div className="font-semibold text-slate-900 dark:text-white">
                 ₹{simulationResults.expected_revenue_inr?.toLocaleString() || 0}
               </div>
             </div>
             <div>
               <div className="text-xs text-slate-500 dark:text-slate-400">Net Profit</div>
               <div className="font-semibold text-green-600 dark:text-green-400">
                 ₹{simulationResults.expected_profit_inr?.toLocaleString() || 0}
               </div>
             </div>
             <div className="md:col-span-4">
               <div className="text-xs text-slate-500 dark:text-slate-400">ROI</div>
               <div className="font-semibold text-purple-600 dark:text-purple-400 text-xl">
                 {simulationResults.roi_percent?.toFixed(1) || 0}%
               </div>
             </div>
             <div className="md:col-span-4">
               <div className="text-xs text-slate-500 dark:text-slate-400">Risk Level</div>
               <div className="font-semibold text-slate-900 dark:text-white capitalize">
                 {simulationResults.risk_level || "Unknown"}
               </div>
             </div>
           </div>
           
           {simulationResults.cost_breakdown && (
             <details className="mt-4">
               <summary className="cursor-pointer text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                 View Cost Breakdown
               </summary>
               <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-400">
                 {simulationResults.cost_breakdown.map((item: any, idx: number) => (
                   <li key={idx} className="flex justify-between">
                     <span>{item.activity}: {item.quantity} {item.unit} × ₹{item.unit_cost}</span>
                     <span className="font-medium">₹{item.total_cost}</span>
                   </li>
                 ))}
               </ul>
             </details>
           )}
         </div>
       )}

       {!simulationResults && (
         <div className="text-center py-8 text-slate-600 dark:text-slate-400">
           <p>Run a simulation to see digital twin results</p>
         </div>
       )}
     </div>
   );
 }