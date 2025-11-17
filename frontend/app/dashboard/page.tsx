"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

const DashboardPage = () => {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null; // Or a loading spinner
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-lg shadow-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-xl">💼</span>
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  AI Job Matching
                </h1>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={logout}
                className="bg-gradient-to-r from-red-500 to-pink-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:from-red-600 hover:to-pink-700 transform hover:scale-105 transition-all shadow-md hover:shadow-lg"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-3">
            Welcome back! 👋
          </h2>
          <p className="text-gray-600 text-lg">
            Manage your resume and discover your perfect job matches
          </p>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Resume Card */}
          <div 
            className="group bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all cursor-pointer border border-gray-100 transform hover:scale-[1.02] hover:-translate-y-1"
            onClick={() => router.push('/resume')}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <span className="text-3xl">📄</span>
              </div>
              <div className="text-green-600 opacity-0 group-hover:opacity-100 transition-opacity">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">My Resume</h2>
            <p className="text-gray-600 leading-relaxed">
              Upload and manage your resume. Let AI analyze your skills and experience.
            </p>
            <div className="mt-6 inline-flex items-center text-green-600 font-medium group-hover:gap-2 transition-all">
              <span>Manage Resume</span>
              <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </div>

          {/* Job Matches Card */}
          <div 
            className="group bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-all cursor-pointer border border-gray-100 transform hover:scale-[1.02] hover:-translate-y-1"
            onClick={() => router.push('/matches')}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <span className="text-3xl">🎯</span>
              </div>
              <div className="text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">My Job Matches</h2>
            <p className="text-gray-600 leading-relaxed">
              Discover AI-powered job recommendations tailored to your profile.
            </p>
            <div className="mt-6 inline-flex items-center text-blue-600 font-medium group-hover:gap-2 transition-all">
              <span>View Matches</span>
              <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
          </div>
        </div>

        {/* Info Banner */}
        <div className="mt-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl p-8 text-white shadow-xl">
          <div className="flex items-start gap-4">
            <div className="text-4xl">💡</div>
            <div>
              <h3 className="text-xl font-bold mb-2">How it works</h3>
              <p className="text-blue-100 leading-relaxed">
                Upload your resume, and our AI will analyze your skills and experience to find the best job matches for you. 
                New opportunities are updated daily!
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;
