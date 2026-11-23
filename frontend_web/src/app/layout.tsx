import React from "react";
import type { Metadata } from "next";
import "./globals.css";

import { FarmProvider } from "@/context/FarmContext";
import { Navbar } from "@/components/Navbar";

export const metadata: Metadata = {
  title: "AgriBrain - Smart Agriculture Platform",
  description: "AI-powered crop recommendations, digital twin simulation, and expert agronomist chat",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col bg-canvas text-primary">
        <FarmProvider>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
        </FarmProvider>
      </body>
    </html>
  );
}
