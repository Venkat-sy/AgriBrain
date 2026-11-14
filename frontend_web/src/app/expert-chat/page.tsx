 "use client";

 import { useState, useEffect } from "react";
 import Link from "next/link";
 import { useFarm } from "@/context/FarmContext";
 import ChatAssistant from "@/components/ChatAssistant";
 import { WeatherWidget } from "@/components/WeatherWidget";
 import { AlertsWidget } from "@/components/AlertsWidget";
 import { DigitalTwinWidget } from "@/components/DigitalTwinWidget";
 import { Loader2, Sparkles, Trash2, AlertCircle, RefreshCw, Info } from "lucide-react";

 export default function ExpertChatPage() {
   const { 
     simulationResults, 
     selectedCrop, 
     farmParams,
     calendarStages,
     currentStep,
     setCurrentStep
   } = useFarm();
   
   const [contextSummary, setContextSummary] = useState<string>("");
   const [userMessageCount, setUserMessageCount] = useState(0);

   // Generate context summary for display
   useEffect(() => {
     if (simulationResults && selectedCrop && farmParams) {
       const summary = `
 Farm Context:
 - Crop: ${selectedCrop}
 - Location: District ID ${farmParams.district_id}, ${farmParams.soil_type}
 - Land Area: ${farmParams.land_area_ha} ha
 - Planting Season: ${farmParams.planting_season}
 - Planting Date: ${farmParams.planned_start_date}
 
 Simulation Results:
 - Expected Yield: ${simulationResults.expected_yield_tons?.toFixed(1) || 0} tons
 - Expected Revenue: ₹${simulationResults.expected_revenue_inr?.toLocaleString() || 0}
 - Total Cost: ₹${simulationResults.total_cost_inr?.toLocaleString() || 0}
 - ROI: ${simulationResults.roi_percent?.toFixed(1) || 0}%
 - Risk Level: ${simulationResults.risk_level || "Unknown"}
 
 Calendar Stages: ${calendarStages?.length || 0} months planned
 Current Stage: ${calendarStages?.[0]?.stage || "Not started"}
       `.trim();
       setContextSummary(summary);
       setCurrentStep(5);
     }
   }, [simulationResults, selectedCrop, farmParams, calendarStages, setCurrentStep]);

   // Progress indicator
   const steps = [
     { number: 1, label: "Farm Input", href: "/simulate", active: true },
     { number: 2, label: "Crop Selection", href: "/simulate", active: true },
     { number: 3, label: "Simulation", href: "/simulate", active: true },
     { number: 4, label: "Calendar", href: "/calendar", active: true },
     { number: 5, label: "Expert Chat", href: "/expert-chat", active: currentStep >= 5 },
   ];

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
               <Link href="/calendar" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-white/5 rounded-lg transition-colors">Calendar</Link>
               <Link href="/expert-chat" className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-purple-500/20 rounded-lg">Expert Chat</Link>
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
                       ? "bg-purple-600 text-white" 
                       : "bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400"
                   }`}>
                     {step.active ? (
                       <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                       </svg>
                     ) : step.number}
                   </div>
                   <span className={`ml-2 text-sm font-medium ${step.active ? "text-purple-600 dark:text-purple-400" : "text-slate-500 dark:text-slate-400"}`}>
                     {step.label}
                   </span>
                 </div>
                 {index < steps.length - 1 && (
                   <div className={`w-16 h-0.5 mx-2 ${step.active ? "bg-purple-500" : "bg-slate-200 dark:bg-slate-700"}`} />
                 )}
               </div>
             ))}
           </div>
         </div>
       </div>

       <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
         <div className="mb-8">
           <h1 className="text-3xl font-bold text-white mb-2">Expert Agronomist Chat</h1>
           <p className="text-slate-300">
             AI-powered agricultural advisor with full context of your farm simulation
           </p>
         </div>

         {/* Context Indicator */}
         <div className="mb-6 glass-card p-4 card-hover">
           <div className="flex items-center gap-3 mb-3">
             <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
               <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
             </div>
             <div>
               <h3 className="text-lg font-semibold text-white">Context-Aware Mode Active</h3>
               <p className="text-sm text-slate-300">
                 The AI has access to your farm parameters, simulation results, and cultivation calendar
               </p>
             </div>
             <span className="ml-auto px-3 py-1 text-sm font-medium bg-green-500/20 text-green-400 rounded-full">
               Fully Contextualized
             </span>
           </div>
           
           {contextSummary && (
             <details className="group">
               <summary className="flex items-center justify-between cursor-pointer text-sm text-slate-300 hover:text-white">
                 <span>View Full Context Sent to AI</span>
                 <svg className="w-5 h-5 transition-transform group-open:rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                 </svg>
               </summary>
               <pre className="mt-3 p-4 glass-card border-white/10 text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap">
                 {contextSummary}
               </pre>
             </details>
           )}
         </div>

         {/* Main Content Grid */}
         <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
           {/* Chat Interface - 2/3 width */}
           <div className="lg:col-span-2">
             <ChatAssistant is_context_aware={true} />
           </div>
           
           {/* Sidebar Widgets - 1/3 width */}
           <div className="lg:col-span-1 space-y-6">
             {/* Quick Action Buttons */}
             <div className="glass-card p-6 card-hover">
               <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                 <Loader2 className="w-5 h-5 text-purple-500" />
                 Quick Questions
               </h3>
               <div className="space-y-2">
                 <button className="w-full text-left p-3 glass-card border-white/10 hover:bg-white/10 transition-colors text-sm text-slate-300">
                   "What's the optimal irrigation schedule for my current growth stage?"
                 </button>
                 <button className="w-full text-left p-3 glass-card border-white/10 hover:bg-white/10 transition-colors text-sm text-slate-300">
                   "How can I improve my ROI based on current market conditions?"
                 </button>
                 <button className="w-full text-left p-3 glass-card border-white/10 hover:bg-white/10 transition-colors text-sm text-slate-300">
                   "What pests should I watch for during the flowering stage?"
                 </button>
                 <button className="w-full text-left p-3 glass-card border-white/10 hover:bg-white/10 transition-colors text-sm text-slate-300">
                   "When is the best time to harvest for maximum quality?"
                 </button>
               </div>
             </div>
             
             {/* Context Summary Cards */}
             <div className="glass-card p-6 card-hover">
               <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                 <Info className="w-5 h-5 text-blue-500" />
                 Active Context
               </h3>
               <div className="space-y-3">
                 {selectedCrop && (
                   <div className="flex items-center gap-3 p-3 glass-card border-green-500/20">
                     <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4" />
                     </svg>
                     <div>
                       <p className="text-xs text-green-400">Crop</p>
                       <p className="font-medium text-green-300 capitalize">{selectedCrop}</p>
                     </div>
                   </div>
                 )}
                 {farmParams && (
                   <div className="flex items-center gap-3 p-3 glass-card border-blue-500/20">
                     <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                     </svg>
                     <div>
                       <p className="text-xs text-blue-400">Location & Soil</p>
                       <p className="font-medium text-blue-300">{farmParams.soil_type}, District {farmParams.district_id}</p>
                     </div>
                   </div>
                 )}
                 {simulationResults && (
                   <div className="flex items-center gap-3 p-3 glass-card border-purple-500/20">
                     <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                     </svg>
                     <div>
                       <p className="text-xs text-purple-400">Simulation</p>
                       <p className="font-medium text-purple-300">Yield: {simulationResults.expected_yield_tons?.toFixed(1) || 0}t | ROI: {simulationResults.roi_percent?.toFixed(1) || 0}%</p>
                     </div>
                   </div>
                 )}
                 {calendarStages && calendarStages.length > 0 && (
                   <div className="flex items-center gap-3 p-3 glass-card border-amber-500/20">
                     <svg className="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 002 2z" />
                     </svg>
                     <div>
                       <p className="text-xs text-amber-700 dark:text-amber-300">Calendar</p>
                       <p className="font-medium text-amber-900 dark:text-amber-100">{calendarStages.length} stages | Current: {calendarStages[0]?.stage}</p>
                     </div>
                   </div>
                 )}
               </div>
             </div>
             
             {/* Widgets */}
             <div className="space-y-6">
               <WeatherWidget />
               <AlertsWidget />
               <DigitalTwinWidget />
             </div>
           </div>
         </div>
       </main>
     </div>
   );
 }