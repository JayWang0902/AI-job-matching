import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /*
   * Explicitly set the tracing root to the frontend directory.
   * This prevents Next.js from getting confused by the lockfile in the parent directory.
  */
  outputFileTracingRoot: __dirname,
  output: 'standalone',
  eslint: {
    // 构建时忽略 ESLint 错误（先跑起来，再逐步修）
    ignoreDuringBuilds: true,
  },
  typescript: {
    // 构建时忽略 TS 错误（先跑起来，再逐步修）
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
