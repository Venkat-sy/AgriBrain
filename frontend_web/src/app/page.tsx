"use client";

import Link from "next/link";
import { MessageSquare, Sprout, BarChart3, Calendar, Leaf, Sparkles } from "lucide-react";
import ChatAssistant from "@/components/ChatAssistant";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-digital-twin transition-colors">
      {/* ── HEADER ── */}
      <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-green-600 flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900 dark:text-white">
                AgriBrain
              </span>
            </div>

            {/* Nav */}
            <nav className="flex items-center gap-1">
              <Link
                href="/simulate"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                <BarChart3 className="w-4 h-4" />
                Simulation
              </Link>
              <Link
                href="/calendar"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                <Calendar className="w-4 h-4" />
                Calendar
              </Link>
              <Link
                href="/expert-chat"
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
              >
                <MessageSquare className="w-4 h-4" />
                Expert Chat
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* ── HERO ── */}
      <div className="bg-gradient-to-br from-green-500/20 via-emerald-500/10 to-slate-950 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 pb-8">
          <div className="text-center mb-6">
            <h1 className="text-3xl sm:text-4xl font-bold mb-3">
              Smart Farming Intelligence
            </h1>
            <p className="text-green-100 text-lg max-w-2xl mx-auto">
              Ask anything about crops, soil, rainfall, or fertilizers — then jump
              into the simulation engine to plan your season.
            </p>
          </div>
        </div>
      </div>

      {/* ── PRIMARY: GENERAL Q&A CHATBOT ── */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6 pb-12">
        <div className="h-[600px] glass-card overflow-hidden">
          <ChatAssistant is_context_aware={false} />
        </div>

        {/* ── NAVIGATION CARDS ── */}
        <div className="mt-8">
          <h2 className="text-center text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-4">
            Jump into the journey
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link
              href="/simulate"
              className="group glass-card p-6 card-hover"
            >
              <div className="w-11 h-11 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Sprout className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                Simulate Your Farm
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
                Pick a district on the map, get ML crop recommendations, and run a
                digital twin simulation.
              </p>
              <span className="text-sm font-medium text-green-600 group-hover:gap-2 inline-flex items-center gap-1 transition-all">
                Start simulation →
              </span>
            </Link>

            <Link
              href="/calendar"
              className="group glass-card p-6 card-hover"
            >
              <div className="w-11 h-11 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                Cultivation Calendar
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
                See unlockable growth stages from land prep through harvest for
                your chosen crop.
              </p>
              <span className="text-sm font-medium text-blue-600 group-hover:gap-2 inline-flex items-center gap-1 transition-all">
                View calendar →
              </span>
            </Link>

            <Link
              href="/expert-chat"
              className="group glass-card p-6 card-hover"
            >
              <div className="w-11 h-11 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-1">
                Expert Agronomist
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-3">
                Chat with an AI expert that knows your coordinates, soil, rainfall,
                crop, and calendar.
              </p>
              <span className="text-sm font-medium text-purple-600 group-hover:gap-2 inline-flex items-center gap-1 transition-all">
                Talk to expert →
              </span>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}