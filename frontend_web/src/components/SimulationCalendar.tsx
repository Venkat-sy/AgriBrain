"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ChevronRight, Calendar, Droplets, Leaf, AlertTriangle } from "lucide-react";

interface TimelineStage {
  stage_name: string;
  estimated_days: number;
  agronomy_advice: string;
}

interface TimelineResponse {
  crop_name: string;
  stages: Array<{
    stage_name: string;
    estimated_days: number;
    agronomy_advice: string;
  }>;
}

interface SimulationCalendarProps {
  cropName: string | null;
  className?: string;
}

export function SimulationCalendar({ cropName, className = "" }: SimulationCalendarProps) {
  const [timeline, setTimeline] = useState<Array<{
    stage_name: string;
    estimated_days: number;
    agronomy_advice: string;
  }> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  useEffect(() => {
    if (!cropName) {
      setTimeline(null);
      return;
    }

    const fetchTimeline = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "https://agribrain-35zr.onrender.com";
        const response = await fetch(`${backendUrl}/api/v1/simulation/timeline?crop_name=${encodeURIComponent(cropName)}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch timeline: ${response.status}`);
        }
        const data = await response.json();
        setTimeline(data.stages);
      } catch (err: any) {
        console.error("Failed to fetch cultivation timeline:", err);
        setError(err.message || "Failed to load cultivation timeline");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTimeline();
  }, [cropName]);

  if (!cropName) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 mx-auto text-slate-400 mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Cultivation Timeline</h3>
          <p className="text-slate-500 dark:text-slate-400">Select a crop from recommendations to view its cultivation timeline</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
              <Calendar className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <h3 className="font-semibold text-white">Cultivation Timeline</h3>
              <p className="text-sm text-slate-400">Loading timeline data...</p>
            </div>
          </div>
          <div className="animate-pulse space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-white/10 dark:bg-slate-800/50" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 bg-white/10 dark:bg-slate-800/50 rounded" />
                  <div className="h-3 w-1/2 bg-white/10 dark:bg-slate-800/50 rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <div className="flex items-center gap-3 text-red-400">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <div>
            <p className="font-medium">Failed to load timeline</p>
            <p className="text-sm text-slate-400">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!timeline || timeline.length === 0) {
    return (
      <div className={`glass-card p-6 ${className}`}>
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 mx-auto text-slate-400 mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No Timeline Data</h3>
          <p className="text-slate-500 dark:text-slate-400">No cultivation timeline available for {cropName}</p>
        </div>
      </div>
    );
  }

  const totalDays = timeline.reduce((sum, stage) => sum + stage.estimated_days, 0);

  return (
    <div className={`glass-card p-6 ${className}`}>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
            <Calendar className="w-6 h-6 text-green-500" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Cultivation Timeline: {cropName}</h3>
            <p className="text-sm text-slate-400">Total Duration: {totalDays} days ({Math.round(totalDays / 30)} months)</p>
          </div>
        </div>
        <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </div>

      <div className="relative">
        {/* Vertical timeline line */}
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gradient-to-b from-green-500 via-green-400 to-green-600" />

        <div className="space-y-6 ml-10">
          {timeline.map((stage, index) => (
            <div
              key={stage.stage_name}
              className="relative group"
              style={{ zIndex: expandedIndex === index ? 10 : 1 }}
            >
              {/* Timeline dot */}
              <div className="absolute left-0 top-2 w-3 h-3 rounded-full border-2 border-green-500 bg-slate-900 z-10 transition-all duration-300 group-hover:scale-125" />

              {/* Stage card */}
              <div
                className={`bg-white/5 dark:bg-slate-800/50 backdrop-blur-sm rounded-xl border border-white/10 dark:border-slate-700/50 p-5 transition-all duration-300 hover:border-green-500/50 hover:shadow-lg hover:shadow-green-500/10 ${expandedIndex === index ? "ring-2 ring-green-500/30" : ""}`}
                onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
              >
                <div className="flex items-start gap-4">
                  {/* Stage number */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                    <span className="text-green-400 font-bold text-lg">{index + 1}</span>
                  </div>

                  {/* Stage content */}
                  <div className="flex-1">
                    <div className="flex items-center justify-between gap-4 mb-2">
                      <h4 className="text-lg font-semibold text-white truncate">{stage.stage_name}</h4>
                      <span className="flex-shrink-0 px-3 py-1 text-xs font-medium text-green-400 bg-green-500/10 rounded-full">
                        ~{stage.estimated_days} days
                      </span>
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed">{stage.agronomy_advice}</p>
                  </div>

                  {/* Expand/collapse indicator */}
                  <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center text-slate-400">
                    <ChevronRight className={`w-5 h-5 transition-transform duration-200 ${expandedIndex === index ? "rotate-90" : ""}`} />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary footer */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-3 bg-green-500/10 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{timeline.length}</div>
            <div className="text-xs text-slate-400">Growth Stages</div>
          </div>
          <div className="text-center p-3 bg-blue-500/10 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">{timeline.reduce((sum, s) => sum + s.estimated_days, 0)}</div>
            <div className="text-xs text-slate-400">Total Days</div>
          </div>
          <div className="text-center p-3 bg-purple-500/10 rounded-lg">
            <Link
              href="/calendar"
              className="block text-center"
            >
              <div className="text-sm font-medium text-purple-400">View Detailed Calendar</div>
              <div className="text-xs text-slate-400">Full schedule & activities</div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}