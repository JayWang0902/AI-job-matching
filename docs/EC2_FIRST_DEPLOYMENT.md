# 🚀 EC2 首次部署快速设置指南

## 问题背景

如果你看到这个错误：
```
fatal: not a git repository (or any of the parent directories): .git
Error: Process completed with exit code 128.
```

说明 EC2 上还没有初始化项目。现在 GitHub Actions 已经更新，会自动初始化！

---

## ✅ 已自动化的内容

最新的 GitHub Actions workflow 现在会自动：

1. ✅ 创建项目目录（如果不存在）
2. ✅ 初始化 Git 仓库（如果不存在）
3. ✅ 添加 remote origin
4. ✅ 拉取最新代码
5. ✅ 拉取 Docker 镜像
6. ✅ 启动服务

---

## 📋 EC2 首次部署前的必要准备

### 1. 配置 GitHub Secrets

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中添加：

```bash
EC2_SSH_KEY          # EC2 私钥内容（key.pem 文件的完整内容）
EC2_HOST             # EC2 公网 IP（如：54.123.45.67）
EC2_USER             # SSH 用户名（ubuntu 或 ec2-user）
EC2_PROJECT_DIR      # 项目路径（如：/home/ubuntu/AI-job-matching）
HEALTH_URL           # 健康检查 URL（如：http://54.123.45.67:8000/health）
```

#### 如何获取 EC2_SSH_KEY？

```bash
# 在本地读取 key.pem 文件内容
cat key.pem

# 复制从 -----BEGIN RSA PRIVATE KEY----- 到 -----END RSA PRIVATE KEY----- 的完整内容
# 包括开始和结束的标记行
```

### 2. EC2 基础环境准备

SSH 到 EC2 并安装必要软件：

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@your-ec2-ip

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y

# 安装 Git（通常已预装）
sudo apt install git -y

# 验证安装
docker --version
docker compose version
git --version

# 重新登录使 docker 用户组生效
exit
ssh -i key.pem ubuntu@your-ec2-ip
```

### 3. 配置 .env 文件

在 EC2 上创建项目目录和 .env 文件：

```bash
# 创建项目目录
mkdir -p ~/AI-job-matching
cd ~/AI-job-matching

# 创建 .env 文件
cat > .env << 'EOF'
# Database (使用 AWS RDS)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/jobmatcherdb

# Redis (本地 Docker)
REDIS_URL=redis://redis:6379/0

# S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# JWT Secret (生成新的密钥！)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=False
LOG_LEVEL=INFO
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://your-ec2-ip:8000
EOF

# 保护 .env 文件
chmod 600 .env
```

**生成 SECRET_KEY**:
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### 4. 配置 AWS 安全组

在 AWS Console 中为 EC2 添加入站规则：

| 类型 | 协议 | 端口 | 源 | 说明 |
|------|------|------|-----|------|
| SSH | TCP | 22 | Your IP | SSH 访问 |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Backend API |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Frontend |

**不要开放 6379 (Redis) 端口！**

---

## 🚀 首次部署流程

完成上述准备后：

### 1. 推送代码触发部署

```bash
# 在本地
git add .
git commit -m "feat: prepare for first deployment"
git push origin main
```

### 2. 监控 GitHub Actions

访问: https://github.com/JayWang0902/AI-job-matching/actions

你应该看到两个 jobs：
- ✅ **Build & Push Images** - 构建并推送 Docker 镜像
- 🚀 **Deploy to EC2** - 自动部署到 EC2

### 3. 部署成功后，运行数据库迁移

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@your-ec2-ip

# 进入项目目录
cd ~/AI-job-matching

# 检查服务状态
docker compose ps

# 应该看到 4 个服务运行中：
# - redis (healthy)
# - backend (healthy)
# - celery (running)
# - frontend (running)

# 运行数据库迁移（创建所有表）
docker compose exec backend alembic upgrade head

# 验证表已创建
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
print('Tables:', inspect(engine).get_table_names())
"

# 应该看到：
# Tables: ['users', 'resumes', 'jobs', 'job_matches', 'alembic_version']
```

---

## 🔍 验证部署

### 1. 检查容器状态
```bash
docker compose ps
```

### 2. 测试 Backend API
```bash
curl http://localhost:8000/health
# 应返回: {"status":"healthy"}

curl http://localhost:8000/
# 应返回: {"message":"Welcome to AI Job Matching API","version":"1.0.0"}
```

### 3. 测试 Frontend
```bash
curl -I http://localhost:3000
# 应返回: HTTP/1.1 200 OK
```

### 4. 检查 Redis
```bash
docker exec ai-job-matching-redis-1 redis-cli PING
# 应返回: PONG
```

### 5. 查看日志
```bash
# Backend 日志
docker compose logs backend --tail=50

# Celery 日志
docker compose logs celery --tail=50

# 所有日志
docker compose logs -f --tail=100
```

---

## ⚠️ 常见问题

### Q1: GitHub Actions 部署阶段跳过了？

**A**: 检查是否配置了所有 GitHub Secrets。部署只在 secrets 存在时运行。

### Q2: 健康检查失败？

**A**: 
```bash
# 检查 backend 日志
docker compose logs backend

# 常见原因：
# - DATABASE_URL 配置错误
# - 数据库连接失败
# - 端口被占用
```

### Q3: 能 SSH 到 EC2 但 GitHub Actions 连接失败？

**A**: 检查 `EC2_SSH_KEY` secret 是否包含完整的私钥内容（包括开始和结束标记）。

### Q4: 镜像拉取失败？

**A**: 
```bash
# 在 EC2 上手动登录到 ghcr.io
echo $GITHUB_TOKEN | docker login ghcr.io -u JayWang0902 --password-stdin

# 然后重新运行部署
```

---

## 📊 首次部署检查清单

- [ ] GitHub Secrets 已配置（5 个）
- [ ] EC2 已安装 Docker、Docker Compose、Git
- [ ] EC2 安全组已配置端口（22, 8000, 3000）
- [ ] EC2 上已创建 .env 文件
- [ ] 数据库（RDS）已创建并可访问
- [ ] 推送代码到 main 分支
- [ ] GitHub Actions 两个 jobs 都成功
- [ ] 运行 `alembic upgrade head` 创建表
- [ ] 健康检查通过
- [ ] 可以访问 Frontend 和 Backend

---

## 🎉 部署成功后

恭喜！你的应用已成功部署到 EC2。

### 后续更新流程

```bash
# 1. 本地修改代码
# 2. 提交并推送
git add .
git commit -m "feat: your changes"
git push origin main

# 3. GitHub Actions 自动：
#    - 构建新镜像
#    - 推送到 ghcr.io
#    - 部署到 EC2
#    - 健康检查

# 4. 如果有数据库变更：
ssh -i key.pem ubuntu@your-ec2-ip
cd ~/AI-job-matching
docker compose exec backend alembic upgrade head
```

### 访问你的应用

- **Backend API**: `http://your-ec2-ip:8000`
- **API 文档**: `http://your-ec2-ip:8000/docs`
- **Frontend**: `http://your-ec2-ip:3000`
- **健康检查**: `http://your-ec2-ip:8000/health`

---

## 📚 相关文档

- [EC2_DEPLOYMENT_CHECKLIST.md](../EC2_DEPLOYMENT_CHECKLIST.md) - 详细部署检查清单
- [docs/FAQ.md](../docs/FAQ.md) - 常见问题解答
- [docs/SECURITY_GROUP_EXPLAINED.md](../docs/SECURITY_GROUP_EXPLAINED.md) - 安全组详解
- [docs/ALEMBIC_MIGRATION_GUIDE.md](../docs/ALEMBIC_MIGRATION_GUIDE.md) - 数据库迁移指南

---

## 🆘 需要帮助？

如果遇到问题，提供以下信息：
1. GitHub Actions 失败的完整日志
2. EC2 上 `docker compose logs` 输出
3. `docker compose ps` 状态
4. `.env` 文件配置（隐藏敏感信息）
