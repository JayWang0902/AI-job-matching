# 📚 项目文档索引

## 🚀 快速开始

| 文档 | 用途 | 阅读时机 |
|------|------|---------|
| [FAQ.md](docs/FAQ.md) | **常见问题快速解答** | ⭐ 优先阅读 |
| [EC2_DEPLOYMENT_CHECKLIST.md](EC2_DEPLOYMENT_CHECKLIST.md) | **部署前完整检查清单** | 部署前必读 |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 常用命令速查 | 日常开发参考 |

---

## 📖 详细指南

### 部署相关
- [EC2_DEPLOYMENT_CHECKLIST.md](EC2_DEPLOYMENT_CHECKLIST.md) - EC2 部署完整检查清单
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 详细部署指南
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - 从旧架构迁移指南

### 安全和网络
- [docs/SECURITY_GROUP_EXPLAINED.md](docs/SECURITY_GROUP_EXPLAINED.md) - AWS 安全组详解
  - 什么是入站规则？
  - 为什么要开放 8000、3000 端口？
  - Redis 6379 端口要不要开放？

### 数据库相关
- [docs/ALEMBIC_MIGRATION_GUIDE.md](docs/ALEMBIC_MIGRATION_GUIDE.md) - Alembic 数据库迁移完整指南
  - Alembic 是什么？
  - 如何生成和应用迁移？
  - 何时需要运行迁移？
- [docs/FIRST_TIME_MIGRATION_SETUP.md](docs/FIRST_TIME_MIGRATION_SETUP.md) - 首次迁移设置指南
  - 如何生成初始迁移脚本？
  - 首次部署流程

### 运维和维护
- [DOCKER_CLEANUP_GUIDE.md](DOCKER_CLEANUP_GUIDE.md) - Docker 清理完整指南
  - 如何查看磁盘使用？
  - 如何清理镜像和容器？
  - 定期维护策略
- [REDIS_SETUP.md](REDIS_SETUP.md) - Redis 配置说明

### 功能指南
- [RESUME_UPLOAD_GUIDE.md](RESUME_UPLOAD_GUIDE.md) - 简历上传功能指南
- [USER_SYSTEM_README.md](USER_SYSTEM_README.md) - 用户系统说明

---

## 🎯 按场景查找文档

### 我要首次部署到 EC2
1. ⭐ [docs/FAQ.md](docs/FAQ.md) - 快速了解关键概念
2. 📋 [EC2_DEPLOYMENT_CHECKLIST.md](EC2_DEPLOYMENT_CHECKLIST.md) - 跟随检查清单操作
3. 🔒 [docs/SECURITY_GROUP_EXPLAINED.md](docs/SECURITY_GROUP_EXPLAINED.md) - 配置安全组
4. 🗄️ [docs/FIRST_TIME_MIGRATION_SETUP.md](docs/FIRST_TIME_MIGRATION_SETUP.md) - 设置数据库

### 我要修改数据库结构
1. 🗄️ [docs/ALEMBIC_MIGRATION_GUIDE.md](docs/ALEMBIC_MIGRATION_GUIDE.md) - 学习 Alembic
2. 参考 "后续开发中的迁移流程" 章节

### 我的 Docker 占用太多空间
1. 🧹 [DOCKER_CLEANUP_GUIDE.md](DOCKER_CLEANUP_GUIDE.md) - 清理指南
2. 运行 `./scripts/cleanup-docker.sh` 交互式清理

### 我遇到部署问题
1. 🆘 [EC2_DEPLOYMENT_CHECKLIST.md](EC2_DEPLOYMENT_CHECKLIST.md) - 故障排查章节
2. 🔍 [docs/FAQ.md](docs/FAQ.md) - 常见问题
3. 📖 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 详细步骤

### 日常开发参考
1. ⚡ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 常用命令
2. 💾 [REDIS_SETUP.md](REDIS_SETUP.md) - Redis 操作

---

## 🛠️ 脚本工具

| 脚本 | 功能 | 使用方法 |
|------|------|---------|
| `scripts/cleanup-docker.sh` | Docker 清理工具 | `./scripts/cleanup-docker.sh` |
| `scripts/check-redis-health.sh` | Redis 健康检查 | `./scripts/check-redis-health.sh` |
| `scripts/backup-redis.sh` | Redis 数据备份 | `./scripts/backup-redis.sh` |
| `scripts/start_services.sh` | 启动所有服务 | `./scripts/start_services.sh` |
| `scripts/stop_services.sh` | 停止所有服务 | `./scripts/stop_services.sh` |

---

## 📝 项目核心信息

### 技术栈
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Database**: PostgreSQL (AWS RDS) + pgvector
- **Task Queue**: Celery + Redis
- **Frontend**: Next.js 14+
- **Deployment**: Docker + GitHub Actions + AWS EC2
- **Storage**: AWS S3 (简历文件)
- **AI**: OpenAI API (GPT + Embeddings)

### 架构模式
- 后端使用 Service 层模式
- 所有配置集中在 `app/core/config.py` (Pydantic Settings)
- 数据库迁移使用 Alembic
- 异步任务通过 Celery 编排
- CI/CD: GitHub Actions → Build → Push to ghcr.io → Deploy to EC2

### 关键端口
- `8000`: Backend API
- `3000`: Frontend
- `6379`: Redis (Docker 内部)
- `22`: SSH (EC2 管理)

### 环境变量
所有配置在 `.env` 文件中：
- `DATABASE_URL`: PostgreSQL 连接
- `REDIS_URL`: Redis 连接
- `AWS_*`: S3 配置
- `OPENAI_API_KEY`: OpenAI API
- `SECRET_KEY`: JWT 密钥

---

## 🔄 工作流程

### 本地开发
```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose stop

# 清理
docker compose down
```

### 部署到 EC2
```bash
# 1. 提交代码
git add .
git commit -m "feat: 描述变更"
git push origin main

# 2. GitHub Actions 自动：
#    - 构建镜像
#    - 推送到 ghcr.io
#    - SSH 到 EC2
#    - 拉取并重启服务

# 3. 如果有数据库变更：
ssh -i key.pem ubuntu@ec2-ip
cd ~/AI-job-matching
docker compose exec backend alembic upgrade head
```

### 数据库迁移
```bash
# 修改模型后生成迁移
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 查看当前版本
alembic current

# 回滚
alembic downgrade -1
```

---

## 🆘 获取帮助

### 问题排查顺序
1. 检查 [docs/FAQ.md](docs/FAQ.md) 常见问题
2. 查看对应的详细文档
3. 检查日志: `docker compose logs [服务名]`
4. 查看健康状态: `docker compose ps`

### 重要日志位置
```bash
# Backend 日志
docker compose logs backend

# Celery 日志
docker compose logs celery

# Redis 日志
docker compose logs redis

# 所有日志
docker compose logs -f --tail=100
```

### 健康检查
```bash
# Backend
curl http://localhost:8000/health

# Redis
docker exec ai-job-matching-redis-1 redis-cli PING

# 数据库连接
docker compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

---

## 📊 文档更新记录

| 日期 | 文档 | 变更 |
|------|------|------|
| 2025-11-16 | docs/FAQ.md | 新增常见问题快速解答 |
| 2025-11-16 | docs/SECURITY_GROUP_EXPLAINED.md | 新增安全组详解 |
| 2025-11-16 | docs/ALEMBIC_MIGRATION_GUIDE.md | 新增 Alembic 完整指南 |
| 2025-11-16 | docs/FIRST_TIME_MIGRATION_SETUP.md | 新增首次迁移设置 |
| 2025-11-16 | DOCKER_CLEANUP_GUIDE.md | 新增 Docker 清理指南 |
| 2025-11-16 | EC2_DEPLOYMENT_CHECKLIST.md | 更新入站规则和迁移说明 |

---

## 💡 提示

- ⭐ 标记的文档是推荐优先阅读的
- 所有脚本在使用前都已添加执行权限
- 遇到问题先查看 FAQ，再看详细文档
- 部署前务必完成 EC2_DEPLOYMENT_CHECKLIST 的所有检查项

---

**快速链接**:
- [GitHub Repository](https://github.com/JayWang0902/AI-job-matching)
- [GitHub Actions](https://github.com/JayWang0902/AI-job-matching/actions)
- [GitHub Container Registry](https://github.com/JayWang0902/AI-job-matching/pkgs/container/ai-job-matching)
