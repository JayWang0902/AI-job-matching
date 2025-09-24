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
          <h1 className="text-2xl font-bold mb-6">My Resume</h1>

          <div className="mb-8">
            <h2 className="text-xl font-semibold">Current Status</h2>
            <p className="text-gray-700">{resumeStatus || 'Loading...'}</p>

            {latestResume ? (
              <div className="mt-3 flex flex-col sm:flex-row sm:items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-gray-600">Latest:</span>
                  <span className="font-medium truncate max-w-xs">{latestResume.original_filename}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700 border">
                    {latestResume.status}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleDownload(latestResume.id)}
                    className="text-blue-600 hover:underline"
                  >
                    Download
                  </button>
                </div>
              </div>
            ) : (
              <p className="mt-2 text-gray-500">No resume uploaded.</p>
            )}
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">Upload New Resume</h2>
            <input
              type="file"
              onChange={handleFileChange}
              className="mb-4 block"
              accept=".pdf,.doc,.docx"
            />
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:bg-gray-400"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
            {error && <p className="text-red-500 mt-4">{error}</p>}
          </div>
        </div>
      </main>
    </div>
  );
};
export default ResumePage;