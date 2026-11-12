 "use client";

 interface Recommendation {
   crop_name: string;
   confidence: number;
   match_reasons: string[];
   expected_yield_tons_per_ha: number | null;
   season: string | null;
 }

 interface CropCardProps {
   recommendation: Recommendation;
   rank: number;
   onClick?: () => void;
 }

 export function CropCard({ recommendation, rank, onClick }: CropCardProps) {
   const confidencePercent = Math.round(recommendation.confidence * 100);
   const yieldText = recommendation.expected_yield_tons_per_ha
     ? `${recommendation.expected_yield_tons_per_ha.toFixed(1)} t/ha`
     : "N/A";
   
   // Estimate market price per ton based on crop (placeholder values)
   const marketPrices: Record<string, number> = {
     rice: 25000,
     wheat: 22000,
     maize: 18000,
     chickpea: 55000,
     cotton: 65000,
     sugarcane: 3500,
     coffee: 200000,
     grapes: 80000,
     apple: 90000,
     jute: 45000,
   };
   
   const marketPricePerTon = marketPrices[recommendation.crop_name.toLowerCase()] || 25000;

   return (
     <div 
       className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 hover:shadow-lg transition-all"
       onClick={onClick}
       style={{ cursor: onClick ? 'pointer' : 'default' }}
     >
       <div className="flex items-start justify-between mb-4">
         <div className="flex items-center gap-3">
           <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
             <span className="text-sm font-bold text-green-600 dark:text-green-400">{rank}</span>
           </div>
           <div>
             <h3 className="text-lg font-semibold text-slate-900 dark:text-white capitalize">{recommendation.crop_name}</h3>
             <p className="text-sm text-slate-500 dark:text-slate-400">ML Confidence: {confidencePercent}%</p>
           </div>
         </div>
       </div>

       <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden mb-4">
         <div
           className="h-full bg-green-500 rounded-full transition-all duration-500"
           style={{ width: `${confidencePercent}%` }}
         ></div>
       </div>

       <div className="grid grid-cols-2 gap-3 mb-4">
         <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
           <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Expected Yield</p>
           <p className="font-semibold text-slate-900 dark:text-white">{yieldText}</p>
         </div>
         <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
           <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Est. Price</p>
           <p className="font-semibold text-slate-900 dark:text-white">₹{marketPricePerTon.toLocaleString()}/ton</p>
         </div>
       </div>

       {recommendation.season && (
         <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg mb-4">
           <p className="text-xs text-green-800 dark:text-green-200"><strong>Best Season:</strong> {recommendation.season}</p>
         </div>
       )}

       {recommendation.match_reasons && recommendation.match_reasons.length > 0 && (
         <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg mb-4">
           <p className="text-xs text-blue-800 dark:text-blue-200"><strong>Match Reasons:</strong> {recommendation.match_reasons.join(", ")}</p>
         </div>
       )}

       <div className="text-center text-xs text-slate-500 dark:text-slate-400">
         Ranked #{rank} by ML model
       </div>
     </div>
   );
 }