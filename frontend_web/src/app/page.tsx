"use client";

import Link from "next/link";
import { MessageSquare, Sprout, BarChart3, Calendar, Leaf, Sparkles, ArrowRight } from "lucide-react";
import ChatAssistant from "@/components/ChatAssistant";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-digital-twin transition-colors">
      {/* HEADER */}
      <header className="bg-white/5 dark:bg-slate-900/50 backdrop-blur-md border-b border-white/10 dark:border-slate-800/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">AgriBrain</span>
            </div>

            {/* Nav */}
            <nav className="flex items-center gap-1">
              <Link
                href="/simulate"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-slate-800/50 rounded-lg transition-colors"
              >
                <BarChart3 className="w-4 h-4" />
                Simulation
              </Link>
              <Link
                href="/calendar"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-slate-800/50 rounded-lg transition-colors"
              >
                <Calendar className="w-4 h-4" />
                Calendar
              </Link>
              <Link
                href="/expert-chat"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-white/5 dark:hover:bg-slate-800/50 rounded-lg transition-colors"
              >
                <MessageSquare className="w-4 h-4" />
                Expert Chat
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* HERO */}
      <main>
        <section className="bg-gradient-to-br from-green-500/20 via-emerald-500/10 to-slate-950 text-white pb-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 pb-8">
            <div className="text-center mb-12">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-4 animate-fade-in">
                Smart Farming Intelligence
              </h1>
              <p className="text-slate-300 text-lg sm:text-xl max-w-2xl mx-auto animate-fade-in">
                Your digital twin for precision agriculture. From soil analysis to harvest predictions - 
                all powered by ML and localized for Indian farms.
              </p>
            </div>

            {/* Chat Assistant */}
            <div className="max-w-2xl mx-auto mb-16 animate-slide-up">
              <ChatAssistant />
            </div>

            {/* Journey Steps */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <Link
                href="/simulate"
                className="group glass-card p-6 card-hover"
              >
                <div className="w-11 h-11 rounded-lg bg-green-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Sprout className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="font-semibold text-white mb-2">
                  Simulate Your Farm
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  Pick a district on the map, get ML crop recommendations, and run a digital twin simulation.
                </p>
                <span className="text-sm font-medium text-green-400 group-hover:gap-2 inline-flex items-center gap-1 transition-all">
                  Start simulation <ArrowRight className="w-4 h-4" />
                </span>
              </Link>

              <Link
                href="/calendar"
                className="group glass-card p-6 card-hover animate-fade-in"
              >
                <div className="w-11 h-11 rounded-lg bg-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Calendar className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="font-semibold text-white mb-2">
                  Cultivation Calendar
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  See unlockable growth stages from land prep through harvest for your selected crop.
                </p>
                <span className="text-sm font-medium text-blue-400 group-hover:gap-2 inline-flex items-center gap-1 transition-all">
                  View calendar <ArrowRight className="w-4 h-4" />
                </span>
              </Link>

              <Link
                href="/expert-chat"
                className="group glass-card p-6 card-hover animate-fade-in"
              >
                <div className="w-11 h-11 rounded-lg bg-purple-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <Sparkles className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="font-semibold text-white mb-2">
                  Expert Agronomist
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  Chat with an AI expert that knows your coordinates, soil, rainfall, crop, and calendar.
                </p>
                <span className="text-sm font-medium text-purple-400 group-hover:gap-2 inline-flex items-center gap-1 transition-all">
                  Talk to expert <ArrowRight className="w-4 h-4" />
                </span>
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
