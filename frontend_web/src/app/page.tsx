"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { InputPanel } from "@/components/InputPanel";
import { CropCard } from "@/components/CropCard";
import { SimulationPanel } from "@/components/SimulationPanel";
import ChatAssistant from "@/components/ChatAssistant";

export default function WelcomePage() {
  const [activeTab, setActiveTab] = useState<"recommend" | "simulate" | "chat">("recommend");
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [districts, setDistricts] = useState<any[]>([]);
  const [soilTypes, setSoilTypes] = useState<string[]>([]);

  // Fetch districts and soil types on mount
  useEffect(() => {
    fetch("/api/districts")
      .then(res => res.json())
      .then(data => setDistricts(data.districts || []))
      .catch(() => setDistricts([]));
    
    fetch("/api/soil-types")
      .then(res => res.json())
      .then(data => setSoilTypes(data.soilTypes || []))
      .catch(() => setSoilTypes([]));
  }, []);

  const handleRecommendationSubmit = async (formData: any) => {
    setIsLoading(true);
    setApiError(null);
    
    try {
      const response = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Failed to get recommendations");
      }
      
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setActiveTab("recommend");
    } catch (error: any) {
      setApiError(error.message);
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100 4m0-4a2 2 0 110 4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100 4m0-4a2 2 0 110 4m0-4v2m0-6V4" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">AgriBrain</h1>
            </div>
            <nav className="flex gap-4">
              <Link href="/simulate" className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Simulation</Link>
              <Link href="/calendar" className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Calendar</Link>
              <Link href="/expert-chat" className="px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">Expert Chat</Link>
            </nav>
          </div>
        </div>
      </header>
      
      {/* Simulate page content - shown when on /simulate route */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            {activeTab === "chat" ? <ChatAssistant /> : <InputPanel onSubmit={handleRecommendationSubmit} isLoading={isLoading} hasRecommendations={recommendations.length > 0} districts={districts} soilTypes={soilTypes} />}
            {apiError && <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-sm text-red-600 dark:text-red-400">{apiError}</p></div>}
          </div>
          <div className="lg:col-span-2 space-y-6">
            {activeTab === "recommend" && <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6"><h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">Crop Recommendations</h2>{recommendations.length === 0 ? <div className="text-center py-12"><svg className="w-16 h-16 mx-auto text-slate-300 dark:text-slate-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg><p className="text-slate-600 dark:text-slate-400">Configure your farm parameters and click "Get Crop Recommendations" to see ML-powered suggestions.</p></div> : <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{recommendations.map((rec, index) => <CropCard key={`${rec.crop_name}-${index}`} recommendation={rec} rank={index + 1} />)}</div>}</div>}
            {activeTab === "simulate" && <SimulationPanel recommendations={recommendations} />}
            {activeTab === "chat" && <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6"><h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6">AI Assistant</h2><p className="text-slate-600 dark:text-slate-400">Switch to the AI Assistant tab to chat with our farming expert.</p></div>}
          </div>
        </div>
      </main>
    </div>
  );
}
