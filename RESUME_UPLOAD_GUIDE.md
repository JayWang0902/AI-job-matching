# 简历上传系统 - 前端集成指南

## API 接口说明

### 1. 获取预签名上传URL
```http
POST /resume/upload-url
Authorization: Bearer <token>
Content-Type: application/json

{
    "filename": "我的简历.pdf",
    "content_type": "application/pdf",
    "file_size": 1024000
}
```

**响应:**
```json
{
    "resume_id": 123,
    "upload_url": "https://s3.amazonaws.com/bucket-name",
    "upload_fields": {
        "key": "resumes/user_1/uuid.pdf",
        "Content-Type": "application/pdf",
        "policy": "...",
        "x-amz-algorithm": "...",
        "x-amz-credential": "...",
        "x-amz-date": "...",
        "x-amz-signature": "..."
    },
    "expires_in": 3600
}
```

### 2. 直接上传到S3
使用返回的 `upload_url` 和 `upload_fields` 直接上传文件到S3：

```javascript
async function uploadToS3(file, uploadResponse) {
    const formData = new FormData();
    
    // 添加S3必需的字段
    Object.keys(uploadResponse.upload_fields).forEach(key => {
        formData.append(key, uploadResponse.upload_fields[key]);
    });
    
    // 最后添加文件
    formData.append('file', file);
    
    // 上传到S3
    const response = await fetch(uploadResponse.upload_url, {
        method: 'POST',
        body: formData
    });
    
    return response.ok;
}
```

### 3. 更新上传状态
```http
PUT /resume/{resume_id}/status?status=uploaded&progress=1.0
Authorization: Bearer <token>
```

### 4. 获取简历列表
```http
GET /resume/?skip=0&limit=10
Authorization: Bearer <token>
```

### 5. 下载简历
```http
GET /resume/{resume_id}/download
Authorization: Bearer <token>
```

## 完整前端示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>简历上传系统</title>
    <style>
        .upload-container { max-width: 600px; margin: 50px auto; padding: 20px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; }
        .progress-bar { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; }
        .progress-fill { height: 100%; background: #4CAF50; border-radius: 10px; transition: width 0.3s; }
        .resume-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .status-uploaded { color: #4CAF50; }
        .status-failed { color: #f44336; }
        .status-pending { color: #ff9800; }
    </style>
</head>
<body>
    <div class="upload-container">
        <h2>简历上传系统</h2>
        
        <!-- 文件上传区域 -->
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" accept=".pdf,.doc,.docx" style="display: none;" onchange="handleFileSelect(event)">
            <p>点击选择简历文件</p>
            <p>支持格式：PDF, DOC, DOCX（最大10MB）</p>
        </div>
        
        <!-- 上传进度 -->
        <div id="uploadProgress" style="display: none;">
            <h3>上传进度</h3>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width: 0%"></div>
            </div>
            <p id="progressText">0%</p>
        </div>
        
        <!-- 简历列表 -->
        <div id="resumeList">
            <h3>我的简历</h3>
            <div id="resumes"></div>
        </div>
    </div>

    <script>
        // 全局变量
        let authToken = 'your-jwt-token'; // 实际使用中从登录获取
        const API_BASE = 'http://localhost:8000';

        // 文件选择处理
        async function handleFileSelect(event) {
            const file = event.target.files[0];
            if (!file) return;

            // 验证文件
            if (!validateFile(file)) return;

            // 显示进度条
            showProgress();

            try {
                // 1. 获取预签名上传URL
                const uploadResponse = await getUploadUrl(file);
                updateProgress(20, '获取上传URL成功');

                // 2. 上传到S3
                const uploadSuccess = await uploadToS3(file, uploadResponse);
                if (!uploadSuccess) throw new Error('上传失败');
                updateProgress(80, '文件上传成功');

                // 3. 更新状态
                await updateResumeStatus(uploadResponse.resume_id, 'uploaded', 1.0);
                updateProgress(100, '上传完成');

                // 4. 刷新列表
                setTimeout(() => {
                    hideProgress();
                    loadResumeList();
                }, 1000);

            } catch (error) {
                console.error('上传失败:', error);
                updateProgress(0, '上传失败: ' + error.message);
            }
        }

        // 文件验证
        function validateFile(file) {
            const allowedTypes = ['application/pdf', 'application/msword', 
                                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            const maxSize = 10 * 1024 * 1024; // 10MB

            if (!allowedTypes.includes(file.type)) {
                alert('不支持的文件格式！请选择PDF或Word文档。');
                return false;
            }

            if (file.size > maxSize) {
                alert('文件大小不能超过10MB！');
                return false;
            }

            return true;
        }

        // 获取预签名上传URL
        async function getUploadUrl(file) {
            const response = await fetch(`${API_BASE}/resume/upload-url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify({
                    filename: file.name,
                    content_type: file.type,
                    file_size: file.size
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '获取上传URL失败');
            }

            return await response.json();
        }

        // 上传到S3
        async function uploadToS3(file, uploadResponse) {
            const formData = new FormData();
            
            // 添加S3字段
            Object.keys(uploadResponse.upload_fields).forEach(key => {
                formData.append(key, uploadResponse.upload_fields[key]);
            });
            
            // 添加文件（必须最后添加）
            formData.append('file', file);
            
            const response = await fetch(uploadResponse.upload_url, {
                method: 'POST',
                body: formData
            });
            
            return response.ok;
        }

        // 更新简历状态
        async function updateResumeStatus(resumeId, status, progress) {
            const params = new URLSearchParams({
                status: status,
                progress: progress
            });

            const response = await fetch(`${API_BASE}/resume/${resumeId}/status?${params}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (!response.ok) {
                throw new Error('更新状态失败');
            }

            return await response.json();
        }

        // 进度条控制
        function showProgress() {
            document.getElementById('uploadProgress').style.display = 'block';
        }

        function hideProgress() {
            document.getElementById('uploadProgress').style.display = 'none';
        }

        function updateProgress(percent, text) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressText').textContent = text || (percent + '%');
        }

        // 加载简历列表
        async function loadResumeList() {
            try {
                const response = await fetch(`${API_BASE}/resume/?skip=0&limit=20`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                if (!response.ok) throw new Error('获取简历列表失败');

                const data = await response.json();
                displayResumeList(data.resumes);

            } catch (error) {
                console.error('加载简历列表失败:', error);
            }
        }

        // 显示简历列表
        function displayResumeList(resumes) {
            const container = document.getElementById('resumes');
            
            if (resumes.length === 0) {
                container.innerHTML = '<p>暂无简历</p>';
                return;
            }

            container.innerHTML = resumes.map(resume => `
                <div class="resume-item">
                    <h4>${resume.original_filename}</h4>
                    <p>状态: <span class="status-${resume.status}">${getStatusText(resume.status)}</span></p>
                    <p>大小: ${formatFileSize(resume.file_size)}</p>
                    <p>上传时间: ${new Date(resume.uploaded_at).toLocaleString()}</p>
                    <div>
                        ${resume.status === 'uploaded' ? 
                            `<button onclick="downloadResume(${resume.id})">下载</button>` : ''}
                        <button onclick="deleteResume(${resume.id})" style="color: red;">删除</button>
                    </div>
                </div>
            `).join('');
        }

        // 状态文本转换
        function getStatusText(status) {
            const statusMap = {
                'pending': '等待上传',
                'uploaded': '已上传',
                'processing': '处理中',
                'parsed': '已解析',
                'failed': '失败'
            };
            return statusMap[status] || status;
        }

        // 文件大小格式化
        function formatFileSize(bytes) {
            if (!bytes) return '未知';
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(1024));
            return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
        }

        // 下载简历
        async function downloadResume(resumeId) {
            try {
                const response = await fetch(`${API_BASE}/resume/${resumeId}/download`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                if (!response.ok) throw new Error('获取下载链接失败');

                const data = await response.json();
                window.open(data.download_url, '_blank');

            } catch (error) {
                alert('下载失败: ' + error.message);
            }
        }

        // 删除简历
        async function deleteResume(resumeId) {
            if (!confirm('确定要删除这份简历吗？')) return;

            try {
                const response = await fetch(`${API_BASE}/resume/${resumeId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                if (!response.ok) throw new Error('删除失败');

                alert('删除成功');
                loadResumeList();

            } catch (error) {
                alert('删除失败: ' + error.message);
            }
        }

        // 页面加载时获取简历列表
        window.onload = function() {
            loadResumeList();
        };
    </script>
</body>
</html>
```

## 环境变量配置说明

创建 `.env` 文件（基于 `.env.example`）：

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
nano .env
```

必需配置项：
- `AWS_ACCESS_KEY_ID`: AWS访问密钥ID
- `AWS_SECRET_ACCESS_KEY`: AWS秘密访问密钥
- `S3_BUCKET_NAME`: S3存储桶名称
- `SECRET_KEY`: JWT密钥（建议使用强随机字符串）

## 部署检查清单

1. ✅ 安装依赖: `pip install -r requirements.txt`
2. ✅ 配置环境变量（`.env` 文件）
3. ✅ 创建S3存储桶并设置CORS
4. ✅ 初始化数据库: `python init_db.py`
5. ✅ 启动服务: `uvicorn app.main:app --reload`
6. ✅ 测试API: 访问 `http://localhost:8000/docs`

## 安全注意事项

- 预签名URL有效期：1小时
- 文件大小限制：10MB
- 支持文件类型：PDF, DOC, DOCX
- 文件名自动去重（使用UUID）
- 用户隔离（每个用户只能访问自己的文件）