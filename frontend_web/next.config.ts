import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
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
