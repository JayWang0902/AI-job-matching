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

const ResumePage = () => {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [resumeStatus, setResumeStatus] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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
        } else {
          setResumeStatus('No resume uploaded');
        }
      } catch (err) {
        console.error(err);
        setResumeStatus('No resume uploaded');
      }
    };

    fetchResumeStatus();
  }, [isAuthenticated, router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
  if (!selectedFile) return;

  setUploading(true);
  setError('');

  try {
    // 1) 拿预签名
    const resp = await api.post('/api/resume/upload-url', {
      filename: selectedFile.name,
      file_size: selectedFile.size,
      content_type: selectedFile.type,
    });

    // —— 充分打印，终端/控制台都清楚 —— //
    console.log('[presign] status:', resp.status);
    console.log('[presign] headers:', resp.headers);
    console.log('[presign] raw data:', resp.data);
    try {
      console.log('[presign] pretty:\n', JSON.stringify(resp.data, null, 2));
      if (resp.data?.upload_fields) console.table(resp.data.upload_fields);
    } catch {}

    // 期望结构：{ resume_id, upload_url, upload_fields, expires_in }
    const { resume_id, upload_url, upload_fields } = resp.data || {};
    if (!upload_url || !upload_fields) {
      throw new Error('预签名响应缺少 upload_url 或 upload_fields');
    }

    // 2) 组装和 Postman 一样的 multipart/form-data
    const formData = new FormData();

    // 必须先把后端给的所有字段原样 append（key/policy/x-amz-*/Content-Type/x-amz-meta-*…）
    Object.entries(upload_fields).forEach(([k, v]) => {
      formData.append(k, v as string);
    });

    // 最后 append 文件（字段名必须是 "file"）
    formData.append('file', selectedFile);

    // 3) 发到 S3（不要手动设置 Content-Type，让浏览器自动带 boundary）
    const s3Resp = await fetch(upload_url, { method: 'POST', body: formData });

    if (!s3Resp.ok) {
      const text = await s3Resp.text(); // S3 错误多为 XML，打印原文最有用
      console.error('[S3 POST] failed:', s3Resp.status, text);
      throw new Error(`S3 POST failed: ${s3Resp.status}`);
    }

    // 4) 通知后端
    await api.put(`/api/resume/${resume_id}/status?status=uploaded`);

    setResumeStatus('Processing');
    setSelectedFile(null);
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
          <div className="mb-6">
            <h2 className="text-xl font-semibold">Current Status</h2>
            <p className="text-gray-700">{resumeStatus || 'Loading...'}</p>
          </div>
          <div>
            <h2 className="text-xl font-semibold mb-2">Upload New Resume</h2>
            <input type="file" onChange={handleFileChange} className="mb-4" accept=".pdf,.doc,.docx" />
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