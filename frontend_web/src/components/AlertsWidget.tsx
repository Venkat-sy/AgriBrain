 "use client";

 import { useState, useEffect } from "react";
 import { useFarm } from "@/context/FarmContext";
 import { CheckCircle, AlertCircle, Info, X } from "lucide-react";

 interface Alert {
   id: number;
   type: "critical" | "warning" | "info";
   title: string;
   message: string;
   timestamp: Date;
   read: boolean;
   actionRequired: boolean;
   farmId?: number;
   fieldId?: number;
 }

 export function AlertsWidget() {
   const { farmParams, simulationResults, selectedCrop, calendarStages } = useFarm();
   const [alerts, setAlerts] = useState<Alert[]>([]);
   const [loading, setLoading] = useState(true);

   useEffect(() => {
     generateContextualAlerts();
     setLoading(false);
   }, [farmParams, simulationResults, selectedCrop, calendarStages]);

   const getStatusColor = (type: string) => {
     switch (type) {
       case "critical": return "text-red-600 dark:text-red-400 border-red-500";
       case "warning": return "text-amber-600 dark:text-amber-400 border-amber-500";
       case "info": return "text-blue-600 dark:text-blue-400 border-blue-500";
       default: return "text-slate-600 dark:text-slate-400 border-slate-500";
     }
   };

   const getRelativeTime = (date: Date) => {
     const now = new Date();
     const diff = now.getTime() - date.getTime();
     const minutes = Math.floor(diff / 60000);
     const hours = Math.floor(diff / 3600000);
     const days = Math.floor(diff / 86400000);
     
     if (minutes < 1) return "Just now";
     if (minutes < 60) return `${minutes}m ago`;
     if (hours < 24) return `${hours}h ago`;
     return `${days}d ago`;
   };

   const generateContextualAlerts = () => {
     const newAlerts: Alert[] = [];
     const now = new Date();
     
     // Alert based on simulation results
     if (simulationResults) {
       if (simulationResults.water_sufficiency === false) {
         newAlerts.push({
           id: Date.now(),
           type: "critical",
           title: "Water Stress Detected",
           message: `Your simulation shows insufficient water for ${selectedCrop}. Consider irrigation planning.`,
           timestamp: new Date(now.getTime() - 1000 * 60 * 30),
           read: false,
           actionRequired: true,
         });
       }
       
       if (simulationResults.risk_level === "high") {
         newAlerts.push({
           id: Date.now() + 1,
           type: "warning",
           title: "High Risk Simulation",
           message: `The simulation for ${selectedCrop} shows high risk level. Review parameters before planting.`,
           timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 2),
           read: false,
           actionRequired: true,
         });
       }
       
       if (simulationResults.roi_percent && simulationResults.roi_percent < 10) {
         newAlerts.push({
           id: Date.now() + 2,
           type: "warning",
           title: "Low ROI Warning",
           message: `Expected ROI of ${simulationResults.roi_percent?.toFixed(1)}% is below 10%. Consider alternative crops.`,
           timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 5),
           read: false,
           actionRequired: false,
         });
       }
     }
     
     // Alert based on calendar stage
     if (calendarStages && calendarStages.length > 0) {
       const currentStage = calendarStages[0];
       if (currentStage.stage.toLowerCase() === "flowering") {
         newAlerts.push({
           id: Date.now() + 3,
           type: "critical",
           title: "Critical Irrigation Period",
           message: `${selectedCrop} is in flowering stage - critical water period. Monitor soil moisture daily.`,
           timestamp: new Date(now.getTime() - 1000 * 60 * 15),
           read: false,
           actionRequired: true,
         });
       }
       
       if (currentStage.stage.toLowerCase() === "harvest") {
         newAlerts.push({
           id: Date.now() + 4,
           type: "info",
           title: "Harvest Approaching",
           message: `${selectedCrop} nearing harvest. Plan harvesting schedule and storage.`,
           timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24),
           read: false,
           actionRequired: false,
         });
       }
     }
     
     // General farm alerts
     if (farmParams) {
       if (farmParams.ph < 5.5 || farmParams.ph > 8.0) {
         newAlerts.push({
           id: Date.now() + 5,
           type: "warning",
           title: "Soil pH Alert",
           message: `Soil pH of ${farmParams.ph} may affect nutrient availability for ${selectedCrop || "your crop"}.`,
           timestamp: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 2),
           read: true,
           actionRequired: false,
         });
       }
     }
     
     // Default alerts if none generated
     if (newAlerts.length === 0) {
       newAlerts.push({
         id: Date.now() + 6,
         type: "info",
         title: "System Ready",
         message: "Complete your farm simulation to receive contextual alerts and recommendations.",
         timestamp: new Date(now.getTime() - 1000 * 60 * 60),
         read: false,
         actionRequired: false,
       });
     }
     
     setAlerts(newAlerts);
   };

   const markAsRead = (id: number) => {
     setAlerts(prev => prev.map(a => a.id === id ? { ...a, read: true } : a));
   };

   const dismissAlert = (id: number) => {
     setAlerts(prev => prev.filter(a => a.id !== id));
   };

   const unreadAlerts = alerts.filter(a => !a.read);
   const readAlerts = alerts.filter(a => a.read);

   if (loading) {
     return (
       <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
         <div className="text-center py-8">
           <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full mx-auto mb-4"></div>
           <p className="text-slate-600 dark:text-slate-400">Loading alerts...</p>
         </div>
       </div>
     );
   }

   return (
     <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
       <div className="flex items-center justify-between mb-4">
         <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
           <AlertCircle className="w-5 h-5 text-red-500" />
           Alerts & Notifications
         </h2>
         <span className={`px-2 py-1 text-xs font-medium rounded-full ${unreadAlerts.length > 0 ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300" : "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"}`}>
           {unreadAlerts.length} unread
         </span>
       </div>

       {unreadAlerts.length > 0 && (
         <div className="space-y-3 mb-4">
           <h3 className="text-sm font-semibold text-red-600 dark:text-red-400">Unread Alerts</h3>
           {unreadAlerts.map(alert => (
             <div
               key={alert.id}
               className={`p-4 rounded-xl border-l-4 ${getStatusColor(alert.type)} ${
                 alert.read ? "bg-slate-50 dark:bg-slate-800/50 opacity-70" : "bg-white dark:bg-slate-800 shadow-sm"
               }`}
             >
               <div className="flex items-start justify-between gap-4">
                 <div className="flex-1">
                   <div className="flex items-center gap-2 mb-1">
                     <span className={`px-2 py-0.5 text-xs font-medium rounded ${getStatusColor(alert.type).replace("border-", "bg-").replace("text-", "text-")}/10`}>
                       {alert.type.toUpperCase()}
                     </span>
                     <span className="text-xs text-slate-500 dark:text-slate-400">
                       {getRelativeTime(alert.timestamp)}
                     </span>
                   </div>
                   <h4 className="font-semibold text-slate-900 dark:text-white mb-1">{alert.title}</h4>
                   <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">{alert.message}</p>
                   <div className="flex gap-2">
                     <button
                       onClick={() => markAsRead(alert.id)}
                       className="px-3 py-1 text-xs font-medium text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 rounded"
                     >
                       <CheckCircle className="w-3 h-3 inline mr-1" /> Mark Read
                     </button>
                     {!alert.actionRequired && (
                       <button
                         onClick={() => dismissAlert(alert.id)}
                         className="px-3 py-1 text-xs font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded"
                       >
                         <X className="w-3 h-3 inline mr-1" /> Dismiss
                       </button>
                     )}
                   </div>
                 </div>
               </div>
             </div>
           ))}
         </div>
       )}

       {readAlerts.length > 0 && (
         <div className="space-y-2">
           <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400">Read Alerts</h3>
           {readAlerts.map(alert => (
             <div
               key={alert.id}
               className={`p-3 rounded-lg border-l-4 ${getStatusColor(alert.type)} bg-slate-50 dark:bg-slate-800/50 opacity-70`}
             >
               <div className="flex items-center justify-between">
                 <h4 className="font-medium text-slate-900 dark:text-white">{alert.title}</h4>
                 <span className="text-xs text-slate-500 dark:text-slate-400">{getRelativeTime(alert.timestamp)}</span>
               </div>
               <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{alert.message}</p>
             </div>
           ))}
         </div>
       )}

       {alerts.length === 0 && (
         <div className="text-center py-8">
           <AlertCircle className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
           <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">No Alerts</h3>
           <p className="text-slate-600 dark:text-slate-400">Complete your farm simulation to receive contextual alerts.</p>
         </div>
       )}
     </div>
   );
 }