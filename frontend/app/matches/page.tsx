"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/services/api';

interface JobMatch {
  id: number;
  job_title: string;
  company_name: string;
  ai_analysis: string;
}

const MatchesPage = () => {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchMatches = async () => {
      try {
        const response = await api.get('/api/matches/');
        setMatches(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 text-black">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
                <button onClick={() => router.push('/dashboard')} className="text-blue-500 hover:underline">
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
              {matches.map(match => (
                <div key={match.id} className="border p-4 rounded-lg">
                  <h2 className="text-xl font-semibold">{match.job_title}</h2>
                  <p className="text-gray-600 mb-2">{match.company_name}</p>
                  <div className="prose max-w-none">
                    <p className="text-gray-800 whitespace-pre-wrap">{match.ai_analysis}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>Your job matches are being generated. Please check back later.</p>
          )}
        </div>
      </main>
    </div>
  );
};

export default MatchesPage;
