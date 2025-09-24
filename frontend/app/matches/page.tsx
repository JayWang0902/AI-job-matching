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
    <div className="min-h-screen bg-gray-100 text-black">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-blue-500 hover:underline"
              >
                &larr; Back to Dashboard
              </button>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="bg-red-500 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-2xl font-bold mb-6">My Job Matches</h1>

          {loading ? (
            <p>Loading matches...</p>
          ) : matches.length > 0 ? (
            <div className="space-y-6">
              {matches.map((m) => {
                const title =
                  m.job?.title ?? m.job?.job_title ?? "Untitled job";
                const company =
                  m.job?.company_name ?? m.job?.company ?? "Unknown company";
                const analysis =
                  m.analysis ?? "No analysis available yet.";
                const score = Number.isFinite(m.similarity_score)
                  ? `${(m.similarity_score * 100).toFixed(1)}% match`
                  : "";
                const created = m.created_at
                  ? new Date(m.created_at).toLocaleString()
                  : "";

                return (
                  <div key={m.id} className="border p-4 rounded-lg">
                    <h2 className="text-xl font-semibold">{title}</h2>
                    <p className="text-gray-600 mb-1">{company}</p>
                    <p className="text-sm text-gray-500 mb-2">
                      {score}
                      {score && created ? " • " : ""}
                      {created}
                    </p>
                    <div className="prose max-w-none">
                      <p className="text-gray-800 whitespace-pre-wrap">
                        {analysis}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p>
              Your job matches are being generated. Please check back later.
            </p>
          )}
        </div>
      </main>
    </div>
  );
};

export default MatchesPage;
