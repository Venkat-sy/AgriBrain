import type { Metadata } from "next";
import "./globals.css";

import { FarmProvider } from "@/context/FarmContext";

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
      <body className="min-h-full flex flex-col">
        <FarmProvider>
          {children}
        </FarmProvider>
      </body>
    </html>
  );
}
