"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import api from "@/services/api";

// —— 后端对齐的类型 —— //
type UUID = string;

interface JobInMatch {
  // 你没贴出具体字段，这里按常见命名做兼容兜底
  title?: string;
  job_title?: string;
  company_name?: string;
  company?: string;
  // 还有别的字段可以继续补
}

interface JobMatchResponse {
  id: UUID;
  job: JobInMatch;
  similarity_score: number;
  analysis?: string | null;
  created_at: string; // ISO string
}

interface JobMatchListResponse {
  matches: JobMatchResponse[];
  total: number;
}

const MatchesPage = () => {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [matches, setMatches] = useState<JobMatchResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

    const fetchMatches = async () => {
      try {
        // ⚠️ 路径说明：
        // 如果你的 api.defaults.baseURL 已经是 "http://.../api"
        // 这里就用 "/matches/"；若 baseURL 没有 /api，则这里用 "/api/matches/"
        // 建议先 console.log 一下 baseURL
        console.log("[api.baseURL]", (api as any)?.defaults?.baseURL);

        const { data } = await api.get<JobMatchListResponse>("/api/matches/", {
          params: { skip: 0, limit: 10 },
        });

        // 后端返回 { matches: [...], total: n }
        setMatches(data.matches ?? []);
      } catch (err: any) {
        console.error("[fetchMatches] error:", err?.message || err);
        if (err?.response) {
          console.error("[fetchMatches] status:", err.response.status);
          console.error("[fetchMatches] data:", err.response.data);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-lg shadow-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => router.push("/dashboard")}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors group"
              >
                <svg className="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Dashboard
              </button>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="bg-gradient-to-r from-red-500 to-pink-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-red-600 hover:to-pink-700 transform hover:scale-105 transition-all shadow-md"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-3xl">🎯</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">My Job Matches</h1>
              <p className="text-gray-600">AI-powered recommendations just for you</p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="bg-white p-12 rounded-2xl shadow-lg border border-gray-100">
            <div className="flex flex-col items-center justify-center">
              <div className="animate-spin w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
              <p className="text-gray-600 text-lg">Loading your matches...</p>
            </div>
          </div>
        ) : matches.length > 0 ? (
          <div className="space-y-6">
            {matches.map((m) => {
              const title = m.job?.title ?? m.job?.job_title ?? "Untitled job";
              const company = m.job?.company_name ?? m.job?.company ?? "Unknown company";
              const analysis = m.analysis ?? "No analysis available yet.";
              const score = Number.isFinite(m.similarity_score)
                ? (m.similarity_score * 100).toFixed(1)
                : null;
              const created = m.created_at
                ? new Date(m.created_at).toLocaleDateString()
                : "";

              return (
                <div 
                  key={m.id} 
                  className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all"
                >
                  {/* Header */}
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
                    <div className="flex-1">
                      <h2 className="text-2xl font-bold text-gray-800 mb-2">{title}</h2>
                      <div className="flex items-center gap-3 text-gray-600">
                        <span className="flex items-center gap-1">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                          {company}
                        </span>
                      </div>
                    </div>
                    
                    {/* Match Score Badge */}
                    {score && (
                      <div className="flex flex-col items-end gap-2">
                        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-lg shadow-md ${
                          parseFloat(score) >= 80 ? 'bg-gradient-to-r from-green-400 to-emerald-500 text-white' :
                          parseFloat(score) >= 60 ? 'bg-gradient-to-r from-blue-400 to-indigo-500 text-white' :
                          'bg-gradient-to-r from-yellow-400 to-orange-500 text-white'
                        }`}>
                          <span>{score}%</span>
                          <span className="text-sm font-normal">match</span>
                        </div>
                        {created && (
                          <span className="text-xs text-gray-500">{created}</span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Analysis */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm">
                        <span className="text-lg">🤖</span>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-800 mb-2">AI Analysis</h3>
                        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                          {analysis}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white p-12 rounded-2xl shadow-lg border border-gray-100">
            <div className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-5xl">🔍</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-3">
                No matches yet
              </h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Your job matches are being generated. Our AI is analyzing your profile to find the perfect opportunities. Check back soon!
              </p>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-xl text-sm">
                <div className="animate-pulse w-2 h-2 bg-blue-500 rounded-full"></div>
                Processing in background
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default MatchesPage;
