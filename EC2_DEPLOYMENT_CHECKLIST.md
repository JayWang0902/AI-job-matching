# 🚀 EC2 部署前检查清单

## ✅ 部署前必须完成的任务

### 1. GitHub Secrets 配置
在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中添加：

```bash
# SSH 配置
EC2_SSH_KEY          # EC2 私钥内容（完整的 .pem 文件内容）
EC2_HOST             # EC2 公网 IP 或域名
EC2_USER             # SSH 用户名（通常是 ubuntu 或 ec2-user）
EC2_PROJECT_DIR      # 项目部署路径（如：/home/ubuntu/AI-job-matching）

# 健康检查
HEALTH_URL           # 健康检查 URL（如：http://your-ec2-ip:8000/health）
```

#### 📝 如何获取这些值？

**EC2_SSH_KEY**:
```bash
# 本地已有 key.pem 文件，读取内容：
cat key.pem

# 复制输出的完整内容到 GitHub Secret
```

**EC2_HOST**:
```bash
# 方法 1: 从 AWS Console 获取 EC2 公网 IP
# 方法 2: 如果已 SSH 到 EC2，运行：
curl -s http://169.254.169.254/latest/meta-data/public-ipv4

# 示例：54.123.45.67
```

**EC2_USER**:
```bash
# Ubuntu 系统: ubuntu
# Amazon Linux: ec2-user
# 检查当前用户：
ssh -i key.pem ubuntu@your-ec2-ip whoami
```

**EC2_PROJECT_DIR**:
```bash
# 推荐路径: /home/ubuntu/AI-job-matching
# 或: /opt/AI-job-matching
```

**HEALTH_URL**:
```bash
# 格式: http://EC2_HOST:8000/health
# 示例: http://54.123.45.67:8000/health
```

---

### 2. EC2 环境准备

#### 2.1 SSH 到 EC2
```bash
ssh -i key.pem ubuntu@your-ec2-ip
```

#### 2.2 安装必要软件
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y

# 验证安装
docker --version
docker compose version

# 重新登录使 docker 用户组生效
exit
ssh -i key.pem ubuntu@your-ec2-ip
```

#### 2.3 创建项目目录
```bash
mkdir -p ~/AI-job-matching
cd ~/AI-job-matching
```

#### 2.4 配置 .env 文件
```bash
# 创建 .env 文件
cat > .env << 'EOF'
# Database (使用 AWS RDS)
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname

# Redis (本地 Docker)
REDIS_URL=redis://redis:6379/0

# S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# OpenAI
OPENAI_API_KEY=your_openai_key

# JWT Secret (生成新的！)
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
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

#### 2.5 配置防火墙（安全组）
在 AWS Console 中为 EC2 安全组添加入站规则：

> 💡 **什么是入站规则？** 入站规则控制**外部流量如何访问你的 EC2**。详见 `docs/SECURITY_GROUP_EXPLAINED.md`

| 类型 | 协议 | 端口 | 源 | 说明 | 必需？ |
|------|------|------|-----|------|-------|
| SSH | TCP | 22 | Your IP | SSH 管理访问 | ✅ 是 |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Backend API（用户访问） | ✅ 是 |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Frontend（用户访问） | ✅ 是 |
| Custom TCP | TCP | 6379 | - | Redis（❌ 不要添加！） | ❌ 否 |

**重要说明**:
- **8000 和 3000**: 必须开放，因为用户浏览器需要访问
- **6379 (Redis)**: 不要开放！Redis 仅供 Docker 容器内部通信
- **SSH (22)**: 建议仅允许你的 IP，不要用 0.0.0.0/0

---

### 3. 本地配置验证

#### 3.1 检查本地构建成功
```bash
# 确认本地服务正常运行
docker compose ps

# 应该看到 4 个服务都是 healthy 状态
```

#### 3.2 检查 GitHub Container Registry 权限
```bash
# 测试推送权限（需要 GITHUB_TOKEN）
echo $GITHUB_TOKEN | docker login ghcr.io -u JayWang0902 --password-stdin

# 或使用 Personal Access Token
# 创建 token: https://github.com/settings/tokens
# 需要权限: write:packages, read:packages
```

#### 3.3 检查 workflow 文件
```bash
# 确认 workflow 文件存在
ls -la .github/workflows/deploy.yml

# 检查语法
grep -E "EC2_SSH_KEY|EC2_HOST|EC2_USER" .github/workflows/deploy.yml
```

---

### 4. 数据库准备

#### 4.1 RDS 配置（如果使用 AWS RDS）
```sql
-- 连接到 RDS
psql -h your-rds-endpoint -U username -d postgres

-- 创建数据库
CREATE DATABASE jobmatcherdb;

-- 创建用户（如果需要）
CREATE USER jobmatcher WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE jobmatcherdb TO jobmatcher;

-- 启用 pgvector 扩展
\c jobmatcherdb
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 4.2 运行数据库迁移（首次部署）

> 💡 **什么是数据库迁移？** Alembic 是 SQLAlchemy 的数据库迁移工具，会自动创建所有表。详见 `docs/ALEMBIC_MIGRATION_GUIDE.md`

```bash
# 在 EC2 上，等待第一次部署完成后运行：
docker compose exec backend alembic upgrade head

# 这个命令会：
# 1. 读取 alembic/versions/ 中的所有迁移脚本
# 2. 在数据库中创建 users, resumes, jobs, job_matches 等表
# 3. 创建必要的索引和约束
# 4. 启用 pgvector 扩展

# ❌ 不需要手动建表！
# ✅ Alembic 会自动创建所有表结构
```

**何时需要运行迁移？**
- ✅ 首次部署到 EC2（必须）
- ✅ 代码中修改了数据库模型后（每次）
- ❌ 不需要在每次部署时都运行（除非有新的迁移脚本）

---

### 5. 部署流程

#### 5.1 提交代码触发部署
```bash
# 确保所有更改已提交
git status

# 提交并推送
git add .
git commit -m "feat: 准备生产环境部署"
git push origin main
```

#### 5.2 监控 GitHub Actions
1. 访问 https://github.com/JayWang0902/AI-job-matching/actions
2. 查看最新的 workflow 运行
3. 检查每个阶段的日志：
   - **Build and Push**: 构建镜像并推送到 ghcr.io
   - **Deploy to EC2**: SSH 到 EC2 并部署

#### 5.3 常见失败原因

**构建阶段失败**:
- Docker 构建错误 → 检查 Dockerfile 语法
- 依赖安装失败 → 检查 requirements.txt / package.json

**推送阶段失败**:
- 认证失败 → GITHUB_TOKEN 权限不足
- 镜像过大 → 优化 Dockerfile

**部署阶段失败**:
- SSH 连接失败 → 检查 EC2_SSH_KEY 和 EC2_HOST
- 权限错误 → 检查 EC2_USER 和文件权限
- 健康检查超时 → 检查服务启动日志

---

### 6. 部署后验证

#### 6.1 SSH 到 EC2 检查服务
```bash
ssh -i key.pem ubuntu@your-ec2-ip

# 检查容器状态
cd ~/AI-job-matching
docker compose ps

# 查看日志
docker compose logs -f --tail=100
```

#### 6.2 测试 API 端点
```bash
# 健康检查
curl http://your-ec2-ip:8000/health

# API 根路径
curl http://your-ec2-ip:8000/

# 前端
curl -I http://your-ec2-ip:3000
```

#### 6.3 检查 Redis
```bash
# 进入 Redis 容器
docker exec -it ai-job-matching-redis-1 redis-cli

# 测试连接
PING
# 应返回: PONG

# 查看 Celery 任务
KEYS celery*

# 退出
exit
```

#### 6.4 检查 Celery 任务
```bash
# 查看 Celery 日志
docker logs -f ai-job-matching-celery-1

# 手动触发任务测试
docker compose exec backend python -c "from app.tasks import run_daily_flow; run_daily_flow.delay()"
```

---

### 7. 监控和维护

#### 7.1 设置日志轮转
在 `docker-compose.yml` 中为每个服务添加：
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### 7.2 定期备份
```bash
# Redis 数据备份
docker exec ai-job-matching-redis-1 redis-cli BGSAVE

# 数据库备份
pg_dump -h your-rds-endpoint -U username dbname > backup_$(date +%Y%m%d).sql
```

#### 7.3 监控资源使用
```bash
# 查看 Docker 资源使用
docker stats

# 查看磁盘使用
df -h
docker system df
```

---

## 🔍 故障排查

### 问题 1: 服务无法启动
```bash
# 查看具体错误
docker compose logs backend
docker compose logs celery

# 重启服务
docker compose restart backend celery
```

### 问题 2: 数据库连接失败
```bash
# 检查 DATABASE_URL 配置
docker compose exec backend env | grep DATABASE_URL

# 测试数据库连接
docker compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

### 问题 3: Redis 连接失败
```bash
# 检查 Redis 状态
docker compose exec redis redis-cli PING

# 检查 Redis URL
docker compose exec backend env | grep REDIS_URL
```

### 问题 4: S3 上传失败
```bash
# 测试 S3 连接
docker compose exec backend python -c "from app.services.s3_service import s3_client; print(s3_client.list_buckets())"
```

---

## 📊 清理和优化

### EC2 磁盘清理
```bash
# 清理 Docker 资源
docker system prune -a -f

# 清理旧日志
sudo journalctl --vacuum-time=7d

# 清理 apt 缓存
sudo apt clean
```

### 镜像更新策略
```yaml
# docker-compose.yml 中使用特定标签
image: ghcr.io/jaywang0902/ai-job-matching-backend:${IMAGE_TAG:-latest}

# 部署时指定版本
IMAGE_TAG=v1.2.3 docker compose up -d
```

---

## 🎯 生产环境最佳实践

### 1. 环境隔离
- 本地开发: `docker-compose.yml`
- 生产环境: `docker-compose.prod.yml` （如果需要不同配置）

### 2. 秘钥管理
- 使用 AWS Secrets Manager 或 Parameter Store
- 定期轮换 API keys 和数据库密码
- 绝不在代码中硬编码秘钥

### 3. 监控告警
- 使用 CloudWatch 监控 EC2 资源
- 设置 CPU/内存/磁盘告警
- 配置健康检查失败通知

### 4. 备份策略
- RDS 自动备份（每日）
- Redis 数据定期导出
- 代码通过 Git 版本控制

### 5. 滚动更新
```bash
# 零停机更新
docker compose pull
docker compose up -d --no-deps --build backend
docker compose up -d --no-deps --build celery
docker compose up -d --no-deps --build frontend
```

---

## ✅ 最终检查清单

- [ ] GitHub Secrets 已配置（5 个）
- [ ] EC2 已安装 Docker 和 Docker Compose
- [ ] EC2 安全组已配置端口
- [ ] .env 文件已在 EC2 上创建
- [ ] 数据库已创建并启用 pgvector
- [ ] 本地 docker compose up 成功运行
- [ ] GitHub 推送触发 workflow
- [ ] workflow 所有阶段通过
- [ ] 健康检查返回 healthy
- [ ] 可以访问前端和后端
- [ ] Celery 任务正常执行

---

## 🆘 需要帮助？

如果遇到问题，提供以下信息：
1. GitHub Actions 失败的阶段和错误日志
2. EC2 上 `docker compose logs` 的输出
3. 健康检查的响应
4. EC2 系统资源使用情况 `docker stats`

参考文档：
- `DEPLOYMENT_GUIDE.md` - 详细部署指南
- `DOCKER_CLEANUP_GUIDE.md` - Docker 清理指南
- `QUICK_REFERENCE.md` - 常用命令速查
