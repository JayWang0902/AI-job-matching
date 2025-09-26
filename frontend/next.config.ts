import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /*
   * Explicitly set the tracing root to the frontend directory.
   * This prevents Next.js from getting confused by the lockfile in the parent directory.
  */
  outputFileTracingRoot: __dirname,
  output: 'standalone',
};

export default nextConfig;
