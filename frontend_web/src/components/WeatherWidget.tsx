 "use client";

 import { useState, useEffect } from "react";
 import { useFarm } from "@/context/FarmContext";

 interface WeatherData {
   current: {
     temperature: number;
     feelsLike: number;
     humidity: number;
     windSpeed: number;
     windDirection: string;
     condition: string;
   };
   forecast: Array<{
     day: string;
     temp: number;
     condition: string;
     rain: number;
     humidity: number;
   }>;
 }

 export function WeatherWidget() {
   const { farmParams } = useFarm();
   const [weather, setWeather] = useState<WeatherData | null>(null);
   const [loading, setLoading] = useState(false);
   const [error, setError] = useState<string | null>(null);

   useEffect(() => {
     if (farmParams?.district_id) {
       fetchWeather();
     }
   }, [farmParams?.district_id]);

   const fetchWeather = async () => {
     setLoading(true);
     setError(null);
     try {
       // In production, this would call a weather API with location from farmParams
       // For now, use mock data similar to the React app
       const mockWeather: WeatherData = {
         current: {
           temperature: 28,
           feelsLike: 30,
           humidity: 67,
           windSpeed: 12,
           windDirection: "NE",
           condition: "Partly Cloudy",
         },
         forecast: [
           { day: "Today", temp: 28, condition: "Partly Cloudy", rain: 10, humidity: 67 },
           { day: "Tomorrow", temp: 30, condition: "Sunny", rain: 5, humidity: 60 },
           { day: "Wed", temp: 27, condition: "Rainy", rain: 80, humidity: 85 },
           { day: "Thu", temp: 26, condition: "Cloudy", rain: 40, humidity: 75 },
           { day: "Fri", temp: 28, condition: "Sunny", rain: 10, humidity: 55 },
           { day: "Sat", temp: 29, condition: "Partly Cloudy", rain: 20, humidity: 65 },
           { day: "Sun", temp: 27, condition: "Cloudy", rain: 30, humidity: 70 },
         ],
       };
       setWeather(mockWeather);
     } catch (err) {
       setError("Failed to fetch weather data");
     } finally {
       setLoading(false);
     }
   };

   const getWeatherIcon = (condition: string) => {
     const icons: Record<string, string> = {
       Sunny: "☀️",
       "Partly Cloudy": "⛅",
       Cloudy: "☁️",
       Rainy: "🌧️",
     };
     return icons[condition] || "🌤️";
   };

   if (!weather) {
     return (
       <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
         {loading ? (
           <div className="text-center py-8">
             <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full mx-auto mb-4"></div>
             <p className="text-slate-600 dark:text-slate-400">Loading weather...</p>
           </div>
         ) : (
           <div className="text-center py-8">
             <div className="text-4xl mb-2">🌤️</div>
             <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">Weather data unavailable</h3>
             <p className="text-slate-600 dark:text-slate-400">Complete farm setup to see local weather</p>
           </div>
         )}
       </div>
     );
   }

   return (
     <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
       <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
         <span className="text-2xl">🌤️</span>
         Weather Forecast
       </h2>

       {/* Current Conditions */}
       <div className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
         <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-4">Current Conditions</h3>
         <div className="flex items-center gap-6 mb-4">
           <div className="text-6xl">{getWeatherIcon(weather.current.condition)}</div>
           <div>
             <div className="text-4xl font-bold text-slate-900 dark:text-white">
               {weather.current.temperature}°C
             </div>
             <div className="text-lg text-slate-600 dark:text-slate-400 mt-1">
               {weather.current.condition}
             </div>
             <div className="text-sm text-slate-500 dark:text-slate-500 mt-1">
               Feels like {weather.current.feelsLike}°C
             </div>
           </div>
         </div>

         <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
           <div className="text-center p-3 bg-white dark:bg-slate-700 rounded-lg">
             <div className="text-2xl mb-1">💧</div>
             <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
               {weather.current.humidity}%
             </div>
             <div className="text-xs text-slate-500 dark:text-slate-400">Humidity</div>
           </div>
           <div className="text-center p-3 bg-white dark:bg-slate-700 rounded-lg">
             <div className="text-2xl mb-1">💨</div>
             <div className="text-xl font-bold text-green-600 dark:text-green-400">
               {weather.current.windSpeed}
             </div>
             <div className="text-xs text-slate-500 dark:text-slate-400">Wind (km/h)</div>
           </div>
           <div className="text-center p-3 bg-white dark:bg-slate-700 rounded-lg">
             <div className="text-2xl mb-1">🧭</div>
             <div className="text-xl font-bold text-purple-600 dark:text-purple-400">
               {weather.current.windDirection}
             </div>
             <div className="text-xs text-slate-500 dark:text-slate-400">Direction</div>
           </div>
           <div className="text-center p-3 bg-white dark:bg-slate-700 rounded-lg">
             <div className="text-2xl mb-1">🌧️</div>
             <div className="text-xl font-bold text-blue-600 dark:text-blue-400">0mm</div>
             <div className="text-xs text-slate-500 dark:text-slate-400">Rainfall</div>
           </div>
         </div>
       </div>

       {/* 7-Day Forecast */}
       <div>
         <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">7-Day Forecast</h3>
         <div className="grid grid-cols-7 gap-2 overflow-x-auto pb-2">
           {weather.forecast.map((day, index) => (
             <div
               key={index}
               className="flex-shrink-0 min-w-[80px] text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
             >
               <div className="text-sm font-semibold text-slate-900 dark:text-white mb-1">
                 {day.day}
               </div>
               <div className="text-3xl mb-1">{getWeatherIcon(day.condition)}</div>
               <div className="text-lg font-bold text-slate-900 dark:text-white">
                 {day.temp}°C
               </div>
               <div className="text-xs text-blue-600 dark:text-blue-400">
                 💧 {day.rain}%
               </div>
             </div>
           ))}
         </div>
       </div>
     </div>
   );
 }