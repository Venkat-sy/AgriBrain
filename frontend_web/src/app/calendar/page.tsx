 "use client";

 import { useState, useEffect } from "react";
 import Link from "next/link";
 import { useFarm } from "@/context/FarmContext";
 import { WeatherWidget } from "@/components/WeatherWidget";
 import { AlertsWidget } from "@/components/AlertsWidget";
 import { DigitalTwinWidget } from "@/components/DigitalTwinWidget";

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

 export default function CalendarPage() {
   const { 
     simulationResults, 
     selectedCrop, 
     farmParams,
     calendarStages,
     setCalendarStages,
     currentStep,
     setCurrentStep
   } = useFarm();
   
   const [stages, setStages] = useState<CalendarStage[]>([]);
   const [isLoading, setIsLoading] = useState(false);

   // Generate calendar stages from simulation results
   useEffect(() => {
     if (simulationResults && simulationResults.monthly_breakdown) {
       const generatedStages: CalendarStage[] = simulationResults.monthly_breakdown.map((month: any, index: number) => {
         const growthStages = ["Germination", "Vegetative", "Flowering", "Grain Filling", "Maturity", "Harvest"];
         const stageName = growthStages[index] || `Month ${month.month}`;
         
         // Calculate dates based on planting date
         const plantingDate = farmParams?.planned_start_date || "2024-06-15";
         const start = new Date(plantingDate);
         start.setMonth(start.getMonth() + index);
         const end = new Date(start);
         end.setMonth(end.getMonth() + 1);
         end.setDate(end.getDate() - 1);
         
         const formatDate = (date: Date) => date.toLocaleDateString("en-IN", { month: "short", day: "numeric", year: "numeric" });
         
         // Stage-specific tasks
         const stageTasks: Record<string, string[]> = {
           "Germination": [
             "Monitor soil moisture daily",
             "Ensure proper seed depth",
             "Protect from birds and pests",
             "Apply starter fertilizer if needed"
           ],
           "Vegetative": [
             "Apply nitrogen fertilizer",
             "Weed control",
             "Monitor for early pests",
             "Ensure adequate irrigation"
           ],
           "Flowering": [
             "Critical irrigation period",
             "Pollination monitoring",
             "Pest and disease scouting",
             "Avoid water stress"
           ],
           "Grain Filling": [
             "Maintain soil moisture",
             "Monitor grain development",
             "Late season pest control",
             "Prepare harvest equipment"
           ],
           "Maturity": [
             "Monitor grain moisture",
             "Plan harvest timing",
             "Ensure dry weather window",
             "Prepare storage facilities"
           ],
           "Harvest": [
             "Harvest at optimal moisture",
             "Minimize grain losses",
             "Proper drying and storage",
             "Field preparation for next season"
           ]
         };
         
         return {
           month: month.month,
           stage: stageName,
           description: `${stageName} phase - ${month.growth_stage}`,
           water_needed_mm: month.irrigation_needed_mm || 0,
           rainfall_mm: month.rainfall_mm || 0,
           tasks: stageTasks[stageName] || [
             "Monitor crop growth",
             "Check water requirements",
             "Scout for pests and diseases"
           ],
           start_date: formatDate(start),
           end_date: formatDate(end)
         };
       });
       
       setStages(generatedStages);
       setCalendarStages(generatedStages);
       setCurrentStep(4);
     } else if (calendarStages && calendarStages.length > 0) {
       setStages(calendarStages);
       setCurrentStep(4);
     }
   }, [simulationResults, calendarStages, farmParams, setCalendarStages, setCurrentStep]);

   // Progress indicator
   const steps = [
     { number: 1, label: "Farm Input", href: "/simulate", active: true },
     { number: 2, label: "Crop Selection", href: "/simulate", active: true },
     { number: 3, label: "Simulation Results", href: "/simulate", active: true },
     { number: 4, label: "Calendar", href: "/calendar", active: currentStep >= 4 },
   ];

   if (!simulationResults && (!calendarStages || calendarStages.length === 0)) {
     return (
       <div className="min-h-screen bg-digital-twin transition-colors">
         <header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">
           <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
             <div className="flex items-center justify-between h-16">
               <div className="flex items-center gap-3">
                 <Link href="/" className="flex items-center gap-3">
                   <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                     <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4" />
                     </svg>
                   </div>
                   <h1 className="text-2xl font-bold text-white">AgriBrain</h1>
                 </Link>
               </div>
               <nav className="flex gap-4">
                 <Link href="/" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Home</Link>
                 <Link href="/simulate" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Simulation</Link>
                 <Link href="/calendar" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-500/20 rounded-lg">Calendar</Link>
                 <Link href="/expert-chat" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Expert Chat</Link>
               </nav>
             </div>
           </div>
         </header>
         <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 flex-1">
           <div className="text-center">
             <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-blue-500/20 flex items-center justify-center">
               <svg className="w-10 h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 002 2z" />
               </svg>
             </div>
             <h1 className="text-4xl font-bold text-white mb-4">No Simulation Data</h1>
             <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
               Please complete a simulation first to view your cultivation calendar. The calendar is generated based on your digital twin simulation results.
             </p>
             <Link 
               href="/simulate"
               className="inline-flex items-center gap-2 px-8 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-all"
             >
               <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
               </svg>
               Run Simulation First
             </Link>
           </div>
         </main>
       </div>
     );
   }

   const getStageColor = (stage: string) => {
     switch (stage.toLowerCase()) {
       case "germination": return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800";
       case "vegetative": return "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800";
       case "flowering": return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 border-yellow-200 dark:border-yellow-800";
       case "grain filling": return "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800";
       case "maturity": return "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 border-orange-200 dark:border-orange-800";
       case "harvest": return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800";
       default: return "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800";
     }
   };

   return (
     <div className="min-h-screen bg-digital-twin transition-colors">
       <header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">
         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
           <div className="flex items-center justify-between h-16">
             <div className="flex items-center gap-3">
               <Link href="/" className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                   <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4" />
                   </svg>
                 </div>
                 <h1 className="text-2xl font-bold text-white">AgriBrain</h1>
               </Link>
             </div>
             <nav className="flex gap-4">
               <Link href="/" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Home</Link>
               <Link href="/simulate" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Simulation</Link>
               <Link href="/calendar" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-500/20 rounded-lg">Calendar</Link>
               <Link href="/expert-chat" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Expert Chat</Link>
             </nav>
           </div>
         </div>
       </header>

       {/* Progress Indicator */}
       <div className="glass-card border-b border-white/10">
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
         <div className="mb-8">
           <h1 className="text-3xl font-bold text-white mb-2">Cultivation Timeline</h1>
           <p className="text-slate-300">
             {selectedCrop ? `Growth stages for <strong className="text-white">${selectedCrop}</strong>` : "Your crop growth timeline based on simulation results"}
           </p>
         </div>

         {/* Summary Cards */}
         <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
           <div className="glass-card p-6 card-hover">
             <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Total Duration</p>
             <p className="text-3xl font-bold text-white">{stages.length} Months</p>
           </div>
           <div className="glass-card p-6 card-hover">
             <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Current Stage</p>
             <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stages[0]?.stage || "N/A"}</p>
           </div>
           <div className="glass-card p-6 card-hover">
             <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Total Water Need</p>
             <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
               {stages.reduce((sum, s) => sum + s.water_needed_mm, 0).toFixed(0)} mm
             </p>
           </div>
           <div className="glass-card p-6 card-hover">
             <p className="text-sm text-slate-500 dark:text-slate-400 mb-1">Expected Rainfall</p>
             <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
               {stages.reduce((sum, s) => sum + s.rainfall_mm, 0).toFixed(0)} mm
             </p>
           </div>
         </div>

         {/* Main Content Grid - Calendar + Widgets */}
         <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
           {/* Calendar Timeline - 2/3 width */}
           <div className="lg:col-span-2 space-y-6">
             {stages.map((stage, index) => (
               <div 
                 key={stage.month} 
                 className="glass-card overflow-hidden relative card-hover"
               >
                 {/* Timeline connector */}
                 <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-white/10 dark:bg-white/5" />
                 
                 <div className="flex flex-col md:flex-row md:items-start gap-6 p-6">
                   {/* Timeline marker */}
                   <div className="flex-shrink-0 relative z-10">
                     <div className={`w-12 h-12 rounded-full flex items-center justify-center ${getStageColor(stage.stage)} border-4 border-white/20 dark:border-slate-800/50 shadow-xl`}>
                       <span className="text-lg font-bold">{index + 1}</span>
                     </div>
                   </div>
                   
                   {/* Stage content */}
                   <div className="flex-1">
                     <div className="flex items-center gap-4 mb-3">
                       <h2 className="text-xl font-bold text-white">{stage.stage}</h2>
                       <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStageColor(stage.stage)}`}>
                         Month {stage.month}
                       </span>
                     </div>
                     
                     <p className="text-slate-300 mb-4">{stage.description}</p>
                     
                     <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                       <div className="p-3 glass-card border-blue-500/20">
                         <p className="text-xs text-blue-400 mb-1">Rainfall</p>
                         <p className="font-semibold text-blue-300">{stage.rainfall_mm.toFixed(1)} mm</p>
                       </div>
                       <div className="p-3 glass-card border-green-500/20">
                         <p className="text-xs text-green-400 mb-1">Irrigation Needed</p>
                         <p className="font-semibold text-green-300">{stage.water_needed_mm.toFixed(1)} mm</p>
                       </div>
                       <div className="p-3 glass-card border-purple-500/20">
                         <p className="text-xs text-purple-400 mb-1">Period</p>
                         <p className="font-semibold text-purple-300 text-sm">{stage.start_date} - {stage.end_date}</p>
                       </div>
                     </div>
                     
                     <div>
                       <h4 className="text-sm font-semibold text-white mb-2">Key Tasks:</h4>
                       <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                         {stage.tasks.map((task, taskIndex) => (
                           <li key={taskIndex} className="flex items-center gap-2 text-sm text-slate-300">
                             <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                             </svg>
                             {task}
                           </li>
                         ))}
                       </ul>
                     </div>
                   </div>
                 </div>
               </div>
             ))}
           </div>
           
           {/* Sidebar Widgets - 1/3 width */}
           <div className="lg:col-span-1 space-y-6">
             <WeatherWidget />
             <AlertsWidget />
             <DigitalTwinWidget />
           </div>
         </div>

         {/* Continue to Expert Chat */}
         <div className="mt-10 glass-card border-purple-500/30 p-6 animate-slide-up">
           <div className="flex items-center justify-between">
             <div>
               <h3 className="text-lg font-semibold text-purple-300">Ready for Expert Advice?</h3>
               <p className="text-purple-400">Chat with our AI agronomist who has full context of your farm, simulation, and cultivation calendar.</p>
             </div>
             <Link 
               href="/expert-chat"
               className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-xl hover:bg-purple-700 focus:ring-4 focus:ring-purple-500/30 transition-all"
             >
               Chat with Expert →
             </Link>
           </div>
         </div>
       </main>
     </div>
   );
 }