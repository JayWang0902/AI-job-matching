"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/services/api';

type ResumeItem = {
  id: string;
  original_filename: string;
  file_size?: number;
  status: 'pending' | 'uploaded' | 'processing' | 'parsed' | 'failed';
  upload_progress: number;
  uploaded_at: string;
};

type ResumeListResponse = {
  resumes: ResumeItem[];
  total: number;
  user_id: string;
};

type UploadUrlResponse = {
  resume_id: string;
  upload_url: string;
  upload_fields: Record<string, string>;
  expires_in: number;
};

type DownloadUrlResponse = {
  download_url: string;
  expires_in: number;
  filename?: string;
  content_type?: string;
};

const ResumePage = () => {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [resumeStatus, setResumeStatus] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [latestResume, setLatestResume] = useState<ResumeItem | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchResumeStatus = async () => {
      try {
        const { data } = await api.get<ResumeListResponse>('/api/resume/', {
          params: { skip: 0, limit: 1 },
        });
        if (data?.resumes?.length > 0) {
          setResumeStatus(data.resumes[0].status);
          setLatestResume(data.resumes[0]);
        } else {
          setResumeStatus('No resume uploaded');
          setLatestResume(null);
        }
      } catch (err) {
        console.error(err);
        setResumeStatus('No resume uploaded');
        setLatestResume(null);
      }
    };

    fetchResumeStatus();
  }, [isAuthenticated, router]);

  const refetchLatest = async () => {
    try {
      const { data } = await api.get<ResumeListResponse>('/api/resume/', {
        params: { skip: 0, limit: 1 },
      });
      if (data?.resumes?.length > 0) {
        setResumeStatus(data.resumes[0].status);
        setLatestResume(data.resumes[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDownload = async (resumeId: string) => {
    try {
      const { data } = await api.get<DownloadUrlResponse>(`/api/resume/${resumeId}/download`);
      const url = data.download_url || (data as any).url;
      if (!url) throw new Error('No download URL from backend');
      window.open(url, '_blank', 'noopener,noreferrer');
    } catch (err) {
      console.error(err);
      setError('Failed to get download link.');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError('');

    try {
      // 1) 获取预签名
      const resp = await api.post<UploadUrlResponse>('/api/resume/upload-url', {
        filename: selectedFile.name,
        file_size: selectedFile.size,
        content_type: selectedFile.type,
      });

      try {
        console.log('[presign] pretty:\n', JSON.stringify(resp.data, null, 2));
        if (resp.data?.upload_fields) console.table(resp.data.upload_fields);
      } catch {}

      const { resume_id, upload_url, upload_fields } = resp.data || {};
      if (!upload_url || !upload_fields) {
        throw new Error('预签名响应缺少 upload_url 或 upload_fields');
      }

      // 2) 组装 multipart/form-data
      const formData = new FormData();
      Object.entries(upload_fields).forEach(([k, v]) => {
        formData.append(k, v as string);
      });
      formData.append('file', selectedFile);

      // 3) 发到 S3
      const s3Resp = await fetch(upload_url, { method: 'POST', body: formData });
      if (!s3Resp.ok) {
        const text = await s3Resp.text();
        console.error('[S3 POST] failed:', s3Resp.status, text);
        throw new Error(`S3 POST failed: ${s3Resp.status}`);
      }

      // 4) 通知后端上传完成（带 query 参数）
      await api.put(
        `/api/resume/${resume_id}/status`,
        null,
        { params: { status: 'uploaded', progress: 1.0 } }
      );

      setResumeStatus('processing'); // 后端会异步解析
      setSelectedFile(null);
      await refetchLatest(); // 刷新最新简历，显示下载按钮
    } catch (err: any) {
      console.error('[handleUpload] error:', err?.message || err);
      if (err?.response) {
        console.error('[handleUpload] error.response.status:', err.response.status);
        console.error('[handleUpload] error.response.data:', err.response.data);
      }
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-lg shadow-lg border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-4">
              <button 
                onClick={() => router.push('/dashboard')} 
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

      <main className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 bg-gradient-to-br from-green-400 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-3xl">📄</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">My Resume</h1>
              <p className="text-gray-600">Manage your professional profile</p>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          {/* Current Resume Status Card */}
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <span className="text-xl">📊</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800">Current Status</h2>
            </div>

            {latestResume ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-5 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl border border-green-200">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-medium text-gray-500">Latest Resume:</span>
                      <span className="font-semibold text-gray-800 truncate max-w-md">
                        {latestResume.original_filename}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                        latestResume.status === 'parsed' ? 'bg-green-100 text-green-700' :
                        latestResume.status === 'processing' ? 'bg-yellow-100 text-yellow-700' :
                        latestResume.status === 'uploaded' ? 'bg-blue-100 text-blue-700' :
                        latestResume.status === 'failed' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {latestResume.status === 'parsed' ? '✓ ' : ''}
                        {latestResume.status.charAt(0).toUpperCase() + latestResume.status.slice(1)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(latestResume.uploaded_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDownload(latestResume.id)}
                    className="ml-4 flex items-center gap-2 bg-white text-green-600 px-4 py-2 rounded-xl font-medium hover:bg-green-50 border border-green-200 transition-all shadow-sm hover:shadow"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Download
                  </button>
                </div>
                
                {latestResume.status === 'processing' && (
                  <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-xl border border-blue-200">
                    <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                    <span className="text-sm text-blue-700">Your resume is being processed by AI...</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-4xl opacity-50">📄</span>
                </div>
                <p className="text-gray-500 text-lg">No resume uploaded yet</p>
                <p className="text-gray-400 text-sm mt-1">Upload your resume below to get started</p>
              </div>
            )}
          </div>

          {/* Upload New Resume Card */}
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center">
                <span className="text-xl">📤</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800">Upload New Resume</h2>
            </div>

            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 hover:border-green-400 transition-colors">
                <label htmlFor="file-upload" className="cursor-pointer block">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <span className="text-3xl">📎</span>
                    </div>
                    <p className="text-gray-700 font-medium mb-1">
                      {selectedFile ? selectedFile.name : 'Click to select a file or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-500">PDF, DOC, or DOCX (Max 10MB)</p>
                  </div>
                  <input
                    id="file-upload"
                    type="file"
                    onChange={handleFileChange}
                    className="hidden"
                    accept=".pdf,.doc,.docx"
                  />
                </label>
              </div>

              {selectedFile && (
                <div className="flex items-center gap-3 p-4 bg-green-50 rounded-xl border border-green-200">
                  <span className="text-2xl">✓</span>
                  <div className="flex-1">
                    <p className="font-medium text-gray-800">{selectedFile.name}</p>
                    <p className="text-sm text-gray-600">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}

              <button
                onClick={handleUpload}
                disabled={!selectedFile || uploading}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 rounded-xl font-medium hover:from-green-600 hover:to-emerald-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transform hover:scale-[1.02] transition-all shadow-lg hover:shadow-xl disabled:transform-none"
              >
                {uploading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                    Uploading...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    Upload Resume
                  </span>
                )}
              </button>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm flex items-start gap-2">
                  <span className="text-lg">⚠️</span>
                  <span>{error}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
export default ResumePage;