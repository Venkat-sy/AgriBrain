"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Leaf, BarChart3, Calendar, MessageSquare, Wifi, WifiOff, MapPin, Sparkles, Loader2 } from "lucide-react";
import { useFarm } from "@/context/FarmContext";

interface BackendStatus {
  status: "online" | "waking" | "offline";
  lastChecked: Date | null;
}

export function Navbar() {
  const pathname = usePathname();
  const { coordinates, selectedCrop, farmParams, simulationResults } = useFarm();
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({ status: "offline", lastChecked: null });
  const [showFarmBadge, setShowFarmBadge] = useState(false);

  // Poll backend health
  useEffect(() => {
    let cancelled = false;
    let intervalId: NodeJS.Timeout;

    const checkHealth = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || "https://agribrain-backend.onrender.com"}/health`, {
          method: "GET",
          cache: "no-store",
        });
        if (!cancelled) {
          if (res.ok) {
            const data = await res.json();
            setBackendStatus({ 
              status: data.database === "connected" ? "online" : "waking", 
              lastChecked: new Date() 
            });
          } else {
            setBackendStatus({ status: "waking", lastChecked: new Date() });
          }
        }
      } catch {
        if (!cancelled) {
          setBackendStatus({ status: "offline", lastChecked: new Date() });
        }
      }
    };

    checkHealth();
    intervalId = setInterval(checkHealth, 30000); // Poll every 30 seconds
    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, []);

  const getStatusPill = () => {
    switch (backendStatus.status) {
      case "online":
        return <span className="pill-online"><Wifi className="w-3 h-3" /> Engine Online</span>;
      case "waking":
        return <span className="pill-waking"><Loader2 className="w-3 h-3 animate-spin" /> Waking Engine...</span>;
      default:
        return <span className="pill-offline"><WifiOff className="w-3 h-3" /> Offline</span>;
    }
  };

  const navItems = [
    { href: "/", label: "Home", icon: Leaf },
    { href: "/simulate", label: "Simulate", icon: BarChart3 },
    { href: "/calendar", label: "Calendar", icon: Calendar },
    { href: "/expert-chat", label: "Expert Chat", icon: MessageSquare },
  ];

  const isActive = (href: string) => pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <header className="navbar">
      <div className="page-container">
        <div className="flex items-center justify-between h-16">
          {/* Left: Brand + Navigation */}
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-3" aria-label="AgriBrain Home">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">AgriBrain</span>
            </Link>

            <nav className="hidden md:flex items-center gap-1" role="navigation" aria-label="Main navigation">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`navbar-link ${isActive(item.href) ? "navbar-link-active" : ""}`}
                  aria-current={isActive(item.href) ? "page" : undefined}
                >
                  <item.icon className="w-4 h-4" aria-hidden="true" />
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* Right: Backend Status + Farm Context Badge */}
          <div className="flex items-center gap-4">
            {/* Backend Status */}
            <div className="hidden sm:flex items-center">
              {getStatusPill()}
            </div>

            {/* Farm Context Badge */}
            <div className="relative">
              <button
                onClick={() => setShowFarmBadge(!showFarmBadge)}
                className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:bg-slate-700/50 transition-colors text-sm font-medium text-slate-300"
                aria-expanded={showFarmBadge}
                aria-haspopup="true"
              >
                <MapPin className="w-4 h-4 text-emerald-400" aria-hidden="true" />
                <span>{coordinates ? `${coordinates.lat.toFixed(2)}, ${coordinates.lon.toFixed(2)}` : "No Farm Pinned"}</span>
                {selectedCrop && (
                  <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-xs">
                    <Sparkles className="w-3 h-3" aria-hidden="true" />
                    {selectedCrop}
                  </span>
                )}
              </button>

              {showFarmBadge && (
                <div className="absolute right-0 mt-2 w-72 glass-card py-2 shadow-2xl z-50 animate-fade-in">
                  <div className="px-4 py-3 border-b border-white/10">
                    <p className="text-xs font-medium text-slate-400">Active Farm Context</p>
                  </div>
                  <div className="p-3 space-y-3 text-sm">
                    {coordinates ? (
                      <>
                        <div className="flex items-center gap-2 text-slate-300">
                          <MapPin className="w-4 h-4 text-emerald-400" />
                          <span>{coordinates.lat.toFixed(4)}°N, {coordinates.lon.toFixed(4)}°E</span>
                        </div>
                        {farmParams && (
                          <div className="flex items-center gap-2 text-slate-300">
                            <span className="w-4 h-4 text-blue-400">🌾</span>
                            <span>{farmParams.soil_type}, District {farmParams.district_id}</span>
                          </div>
                        )}
                      </>
                    ) : (
                      <p className="text-slate-400">No farm location pinned</p>
                    )}
                    {selectedCrop && (
                      <div className="p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                        <p className="text-xs text-emerald-400 mb-1">Selected Crop</p>
                        <p className="font-medium text-emerald-300 capitalize">{selectedCrop}</p>
                      </div>
                    )}
                    {simulationResults && (
                      <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                        <p className="text-xs text-purple-400 mb-1">Simulation</p>
                        <p className="font-medium text-purple-300">Yield: {simulationResults.expected_yield_tons?.toFixed(1) || 0}t | ROI: {simulationResults.roi_percent?.toFixed(1) || 0}%</p>
                      </div>
                    )}
                  </div>
                  <div className="px-4 py-2 border-t border-white/10">
                    <Link
                      href="/simulate"
                      onClick={() => setShowFarmBadge(false)}
                      className="w-full text-center text-sm font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
                    >
                      Manage Farm →
                    </Link>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button className="md:hidden p-2 bg-slate-800/50 border border-slate-700/50 rounded-lg hover:bg-slate-700/50 transition-colors" aria-label="Open menu">
              <MessageSquare className="w-5 h-5 text-slate-300" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {pathname !== "/" && (
        <div className="md:hidden border-t border-slate-800/50 bg-slate-950/95">
          <nav className="px-4 py-3 flex flex-wrap gap-2" role="navigation" aria-label="Mobile navigation">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`navbar-link ${isActive(item.href) ? "navbar-link-active" : ""} w-full justify-center`}
                aria-current={isActive(item.href) ? "page" : undefined}
              >
                <item.icon className="w-4 h-4" aria-hidden="true" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}