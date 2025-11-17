# EC2 部署指南

## 📋 前置要求

- AWS 账号和 EC2 实例
- GitHub 账号和仓库
- 基础的 Linux/Docker 知识

## 🚀 首次部署

### 1. 配置 GitHub Secrets

在 **GitHub → Settings → Secrets → Actions** 添加：

| Secret | 说明 | 示例 |
|--------|------|------|
| `EC2_SSH_KEY` | 私钥内容 | `cat key.pem` 的完整输出 |
| `EC2_HOST` | EC2 公网IP | `54.123.45.67` |
| `EC2_USER` | SSH 用户名 | `ubuntu` |
| `EC2_PROJECT_DIR` | 项目路径 | `/home/ubuntu/AI-job-matching` |
| `HEALTH_URL` | 健康检查URL | `http://54.123.45.67:8000/health` |

### 2. 准备 EC2 环境

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@<EC2_IP>

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y

# 退出重新登录使 docker 组生效
exit
ssh -i key.pem ubuntu@<EC2_IP>

# 验证安装
docker --version
docker compose version
```

### 3. 配置安全组

在 AWS Console 添加入站规则：

| 类型 | 端口 | 源 | 说明 |
|------|------|-----|------|
| SSH | 22 | Your IP | SSH 访问 |
| Custom TCP | 8000 | 0.0.0.0/0 | Backend API |
| Custom TCP | 3000 | 0.0.0.0/0 | Frontend |

**注意**: 不要开放 6379 (Redis)，仅供内部使用！

### 4. 创建环境变量文件

```bash
# 在 EC2 上创建项目目录
mkdir -p ~/AI-job-matching
cd ~/AI-job-matching

# 创建 .env 文件
nano .env
```

添加以下内容：

```bash
# Database (使用 RDS)
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/dbname

# Redis (Docker 内部)
REDIS_URL=redis://redis:6379/0

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket

# OpenAI
OPENAI_API_KEY=sk-your-key

# JWT 配置
SECRET_KEY=$(openssl rand -base64 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=False
LOG_LEVEL=INFO
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Frontend API URL
NEXT_PUBLIC_API_BASE_URL=http://<EC2_IP>:8000

# 容器镜像配置
DOCKER_REGISTRY=ghcr.io
DOCKER_IMAGE_PREFIX=jaywang0902/ai-job-matching
IMAGE_TAG=latest
```

保存后设置权限：
```bash
chmod 600 .env
```

### 5. 触发首次部署

```bash
# 在本地推送代码
git push origin main
```

GitHub Actions 会自动：
1. 构建 Docker 镜像
2. 推送到 GitHub Container Registry
3. SSH 到 EC2
4. 拉取镜像
5. 启动服务

### 6. 运行数据库迁移

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@<EC2_IP>
cd ~/AI-job-matching

# 运行迁移（创建数据库表）
docker compose exec backend alembic upgrade head

# 验证表已创建
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
print('Tables:', inspect(engine).get_table_names())
"
```

### 7. 验证部署

```bash
# 检查服务状态
docker compose ps

# 测试 Backend
curl http://localhost:8000/health

# 测试 Frontend
curl -I http://localhost:3000

# 检查日志
docker compose logs --tail=50
```

## 🔄 日常部署流程

### 代码更新

```bash
# 1. 本地开发完成
git add .
git commit -m "feat: new feature"
git push origin main

# 2. GitHub Actions 自动部署

# 3. 如果有数据库变更，SSH 到 EC2
ssh -i key.pem ubuntu@<EC2_IP>
cd ~/AI-job-matching
docker compose exec backend alembic upgrade head
```

### 手动部署（如需要）

```bash
# SSH 到 EC2
cd ~/AI-job-matching

# 拉取最新代码和镜像
git pull origin main
docker compose pull

# 重启服务
docker compose up -d

# 检查状态
docker compose ps
```

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker compose logs backend
docker compose logs celery

# 重启服务
docker compose restart backend

# 完全重启
docker compose down
docker compose up -d
```

### 数据库连接失败

```bash
# 检查环境变量
docker compose exec backend env | grep DATABASE_URL

# 测试连接
docker compose exec backend python -c "
from app.core.database import engine
engine.connect()
print('✅ Connected')
"
```

### Redis 连接问题

```bash
# 检查 Redis 状态
docker compose exec redis redis-cli PING

# 应返回 PONG
```

### 健康检查失败

```bash
# 查看 Backend 日志
docker compose logs backend --tail=100

# 手动测试健康端点
docker compose exec backend curl http://localhost:8000/health
```

### GitHub Actions 失败

**Build 阶段失败:**
- 检查 Dockerfile 语法
- 检查 requirements.txt / package.json

**Deploy 阶段失败:**
- 检查 GitHub Secrets 是否正确
- 检查 EC2 SSH 连接: `ssh -i key.pem ubuntu@<EC2_IP>`
- 检查 EC2 磁盘空间: `df -h`

## 🔧 维护操作

### 查看日志

```bash
# 实时日志
docker compose logs -f

# 特定服务
docker compose logs -f backend

# 最近 N 行
docker compose logs --tail=100 backend
```

### 重启服务

```bash
# 单个服务
docker compose restart backend

# 所有服务
docker compose restart

# 完全重启
docker compose down
docker compose up -d
```

### 清理 Docker 资源

```bash
# 清理未使用的镜像
docker image prune -a -f

# 清理构建缓存
docker builder prune -af

# 清理所有未使用资源
docker system prune -a -f
```

### 数据库备份

```bash
# 备份
pg_dump -h <RDS_ENDPOINT> -U user dbname > backup.sql

# 恢复
psql -h <RDS_ENDPOINT> -U user dbname < backup.sql
```

### 更新环境变量

```bash
# 编辑 .env
nano ~/AI-job-matching/.env

# 重启服务使其生效
docker compose restart
```

## 📊 监控

### 检查资源使用

```bash
# 容器资源
docker stats

# 磁盘空间
df -h
docker system df

# 内存
free -h
```

### 健康检查

```bash
# Backend
curl http://localhost:8000/health

# 所有容器状态
docker compose ps
```

## 🚨 紧急回滚

### 方法 1: 使用之前的镜像

```bash
cd ~/AI-job-matching

# 设置之前的版本
export IMAGE_TAG=<previous-commit-sha>

# 拉取旧镜像
docker compose pull

# 重启
docker compose up -d
```

### 方法 2: 回滚代码

```bash
cd ~/AI-job-matching

# 查看提交历史
git log --oneline

# 回滚到之前的提交
git reset --hard <previous-commit>

# 重新部署
docker compose pull
docker compose up -d
```

## 🔐 安全最佳实践

1. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **限制 SSH 访问**
   - 仅允许特定 IP
   - 使用密钥认证（禁用密码）

3. **保护环境变量**
   - `.env` 文件权限 600
   - 不要提交到 Git

4. **定期备份**
   - 数据库定期备份
   - 重要文件备份

5. **监控日志**
   - 定期检查异常日志
   - 设置告警

## 📚 相关文档

- [DEVELOPMENT.md](./DEVELOPMENT.md) - 本地开发
- [DATABASE.md](./DATABASE.md) - 数据库迁移
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 常用命令
- [MAINTENANCE.md](./MAINTENANCE.md) - 运维维护
