import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/v1/spatial/:path*",
        destination: "http://localhost:8000/api/v1/spatial/:path*",
      },
    ];
  },
};

export default nextConfig;
