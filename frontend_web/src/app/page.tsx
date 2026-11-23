"use client";

import React from "react";
import Link from "next/link";
import { MessageSquare, Sprout, BarChart3, Calendar, Leaf, Sparkles, ArrowRight } from "lucide-react";
import ChatAssistant from "@/components/ChatAssistant";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-canvas transition-colors">
      {/* HERO */}
      <main className="flex-1">
        <section className="bg-gradient-to-br from-green-500/20 via-emerald-500/10 to-slate-950 text-primary pb-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 pb-8">
            <div className="text-center mb-12">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-4 animate-fade-in">
                Smart Farming Intelligence
              </h1>
              <p className="text-secondary text-lg sm:text-xl max-w-2xl mx-auto animate-fade-in">
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
                <h3 className="font-semibold text-primary mb-2">
                  Simulate Your Farm
                </h3>
                <p className="text-sm text-secondary mb-4">
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
                <h3 className="font-semibold text-primary mb-2">
                  Cultivation Calendar
                </h3>
                <p className="text-sm text-secondary mb-4">
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
                <h3 className="font-semibold text-primary mb-2">
                  Expert Agronomist
                </h3>
                <p className="text-sm text-secondary mb-4">
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
