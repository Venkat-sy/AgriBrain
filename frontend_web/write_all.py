import os
os.chdir('C:/Users/USER/Downloads/FinalYearProject/frontend_web')

# Part 1: Header and imports
with open('src/app/simulate/page.tsx', 'w', encoding='utf-8') as f:
    f.write('''"use client";
import React, { useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";

const MapUI = dynamic(() => import("@/components/MapUI"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[320px] sm:h-[390px] lg:h-[430px] rounded-2xl bg-slate-900 animate-pulse flex items-center justify-center text-slate-400 border border-slate-800">
      Loading Interactive India Map...
    </div>
  ),
});

// 8 Standard Indian Soil Profiles for User Confirmation & Override
const SOIL_PROFILES: Record<string, { N: number; P: number; K: number; pH: number; desc: string }> = {
  "Indo-Gangetic Alluvial": { N: 215, P: 58, K: 155, pH: 7.1, desc: "Fertile riverine silt; ideal for cereals, pulses & sugarcane" },
  "Deccan Black Cotton (Regur)": { N: 160, P: 48, K: 185, pH: 7.4, desc: "High clay moisture retention; ideal for cotton, soybean, citrus" },
  "Coastal Lateritic / Alluvial": { N: 150, P: 38, K: 165, pH: 5.7, desc: "Acidic, well-drained coastal soil; ideal for paddy, coconut, arecanut" },
  "Southern Red Loam": { N: 145, P: 42, K: 135, pH: 6.4, desc: "Porous friable loam; ideal for millets, groundnut, mango, pulses" },
  "Arid Sandy / Calcareous": { N: 95, P: 28, K: 115, pH: 7.9, desc: "Low organic matter, fast draining; suitable for bajra, mustard, pomegranate" },
  "Mountain Forest / Podzolic": { N: 185, P: 52, K: 150, pH: 6.0, desc: "Humus-rich temperate soil; ideal for apple, spices, potato" },
  "Deltaic Clay Loam": { N: 195, P: 54, K: 170, pH: 6.6, desc: "Moisture-retentive delta soil; high yield for rice, jute, banana" },
  "Saline / Alkaline Usar": { N: 110, P: 32, K: 125, pH: 8.2, desc: "High salt profile; requires gypsum & salt-tolerant varieties" },
};

// 25 Short-Term Seasonal Crops + 20 Long-Term Orchard/Plantation Crops (45 Total)
const CROP_DATABASE = [''')
print("Part 1 written")