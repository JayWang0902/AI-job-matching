# AI Job Matching

AI-powered job matching platform with resume parsing, job scraping, and intelligent matching using vector embeddings.

## 🎯 项目概述

- **技术栈**: FastAPI + SQLAlchemy + Celery + PostgreSQL + Redis + OpenAI + Next.js
- **核心功能**:
  - 用户注册/登录 (JWT 认证)
  - 简历上传与解析 (S3 + OpenAI)
  - 职位爬取与存储 (多源爬虫 + pgvector)
  - AI 驱动的职位匹配 (向量搜索 + GPT 分析)
  - 每日自动匹配任务

## 📚 完整文档

| 文档 | 说明 | 使用场景 |
|------|------|---------|
| **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** | 本地开发指南 | 开发新功能、调试代码 |
| **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** | EC2 部署指南 | 首次部署、更新部署 |
| **[DATABASE.md](docs/DATABASE.md)** | 数据库迁移 | 修改数据库结构 |
| **[MAINTENANCE.md](docs/MAINTENANCE.md)** | 运维维护 | 日常维护、故障排查 |
| **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** | 命令速查 | 快速查找命令 |

## 🚀 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/JayWang0902/AI-job-matching.git
cd AI-job-matching

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填写必要的配置

# 3. 启动服务
docker compose up -d

# 4. 初始化数据库
docker compose exec backend alembic upgrade head

# 5. 验证
curl http://localhost:8000/health
```

**详细说明**: 查看 [DEVELOPMENT.md](docs/DEVELOPMENT.md)

### 部署到 EC2

```bash
# 1. 准备 EC2 环境
# - 安装 Docker & Docker Compose
# - 配置安全组 (开放端口 22, 8000, 3000)

# 2. 在 EC2 上克隆代码
git clone https://github.com/JayWang0902/AI-job-matching.git
cd AI-job-matching

# 3. 配置生产环境变量
cp .env.example .env
# 编辑 .env，配置 RDS、S3、OpenAI 等

# 4. 启动服务
docker compose up -d

# 5. 初始化数据库
docker compose exec backend alembic upgrade head

# 6. 验证
curl http://localhost:8000/health
```

**详细说明**: 查看 [DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 🏗️ 项目结构

```
AI-job-matching/
├── app/                        # 后端应用
│   ├── api/                    # FastAPI 路由
│   │   ├── auth.py             # 认证接口
│   │   ├── resume.py           # 简历管理
│   │   └── matches.py          # 匹配结果
│   ├── services/               # 业务逻辑
│   │   ├── job_matching_service.py      # 职位匹配
│   │   ├── job_scraper_service.py       # 职位爬取
│   │   ├── resume_processing_service.py # 简历处理
│   │   └── s3_service.py                # S3 存储
│   ├── models/                 # SQLAlchemy 模型
│   ├── tasks.py                # Celery 任务
│   └── main.py                 # FastAPI 应用
├── frontend/                   # Next.js 前端
│   └── app/                    # 页面组件
├── alembic/                    # 数据库迁移
├── docs/                       # 项目文档
├── scripts/                    # 运维脚本
├── docker-compose.yml          # Docker 编排
└── requirements.txt            # Python 依赖
```

## 📋 核心流程

### 用户流程

```
1. 用户注册/登录 (JWT)
   ↓
2. 上传简历 (S3 预签名 URL)
   ↓
3. 简历解析 (OpenAI) → 生成向量 (pgvector)
   ↓
4. 查看匹配结果 (每日自动匹配)
   ↓
5. AI 分析说明每个匹配的原因
```

### 后台任务流程

```
Celery Beat 定时触发
   ↓
1. 爬取职位 (scrape_all_jobs)
   ├── Indeed
   ├── LinkedIn
   └── Glassdoor
   ↓
2. 生成职位向量 (OpenAI embedding)
   ↓
3. 为所有用户匹配 (match_jobs_for_user)
   ├── 向量搜索 (pgvector)
   ├── AI 分析 (OpenAI GPT)
   └── 存储匹配结果
```

## 🔧 常用命令

### 开发

```bash
# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f backend

# 进入容器
docker compose exec backend bash

# 运行测试
docker compose exec backend pytest
```

### 数据库

```bash
# 生成迁移
docker compose exec backend alembic revision --autogenerate -m "description"

# 应用迁移
docker compose exec backend alembic upgrade head

# 回滚迁移
docker compose exec backend alembic downgrade -1
```

### 任务管理

```bash
# 手动触发匹配
curl -X POST http://localhost:8000/debug/trigger-daily-flow

# 查看 Celery 状态
docker compose exec celery celery -A app.celery_app.celery_app inspect active

# 清空任务队列
docker compose exec redis redis-cli del celery
```

**更多命令**: 查看 [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

## 🛠️ 环境变量

必需的环境变量（在 `.env` 中配置）：

```bash
# 数据库
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT 认证
SECRET_KEY=your_secret_key
ALGORITHM=HS256

# OpenAI
OPENAI_API_KEY=sk-xxx

# AWS S3
S3_BUCKET_NAME=your-bucket
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1

# Redis
REDIS_URL=redis://redis:6379/0

# 前端
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 测试

```bash
# 运行所有测试
docker compose exec backend pytest

# 测试特定模块
docker compose exec backend pytest app/tests/test_auth.py

# 测试用户系统
python test_user_system.py

# 测试职位爬取
python scrape_jobs.py
```

## 📊 监控与维护

### 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# Redis 健康检查
docker compose exec redis redis-cli ping

# 查看服务状态
docker compose ps
```

### 日志管理

```bash
# 查看所有日志
docker compose logs

# 查看特定服务
docker compose logs backend
docker compose logs celery

# 实时跟踪
docker compose logs -f backend
```

### 资源监控

```bash
# Docker 资源使用
docker stats

# 磁盘使用
docker system df

# 清理未使用资源
docker system prune -a
```

**详细维护指南**: 查看 [MAINTENANCE.md](docs/MAINTENANCE.md)

## 🚨 故障排查

### API 无响应

```bash
# 1. 检查服务状态
docker compose ps

# 2. 查看日志
docker compose logs --tail=100 backend

# 3. 重启服务
docker compose restart backend
```

### 数据库连接失败

```bash
# 1. 测试连接
docker compose exec backend python -c "
from app.core.database import engine
with engine.connect() as conn:
    print('Connected')
"

# 2. 检查环境变量
docker compose exec backend env | grep DATABASE_URL

# 3. 验证 RDS 安全组配置
```

### Celery 任务不执行

```bash
# 1. 检查 Celery 状态
docker compose exec celery celery -A app.celery_app.celery_app inspect active

# 2. 查看任务队列
docker compose exec redis redis-cli llen celery

# 3. 重启 Celery
docker compose restart celery
```

**完整故障排查清单**: 查看 [MAINTENANCE.md](docs/MAINTENANCE.md)

## 🤝 开发指南

### 添加新 API 端点

1. 在 `app/api/` 创建路由
2. 在 `app/services/` 实现业务逻辑
3. 在 `app/main.py` 注册路由
4. 编写测试

详见: [DEVELOPMENT.md](docs/DEVELOPMENT.md#添加新功能)

### 修改数据库模型

1. 修改 `app/models/` 中的模型
2. 生成迁移: `alembic revision --autogenerate`
3. 本地测试: `alembic upgrade head`
4. 提交代码和迁移文件
5. 部署后运行迁移

详见: [DATABASE.md](docs/DATABASE.md#开发流程)

### 添加新爬虫

1. 在 `app/services/job_scrapers/` 创建爬虫
2. 实现 `scrape()` 方法
3. 在 `job_scraper_service.py` 注册
4. 测试爬虫: `python scrape_jobs.py`

详见: [DEVELOPMENT.md](docs/DEVELOPMENT.md#添加新爬虫)

## 📖 技术文档

### 架构设计

- **API 层**: FastAPI 路由，处理请求/响应
- **服务层**: 业务逻辑，与外部服务交互
- **数据层**: SQLAlchemy 模型，数据库操作
- **任务层**: Celery 异步任务，定时任务

### 关键技术

- **向量搜索**: 使用 pgvector 进行职位匹配
- **AI 分析**: OpenAI GPT 生成匹配说明
- **异步任务**: Celery + Redis 处理后台任务
- **文件存储**: AWS S3 存储简历文件
- **认证**: JWT token 认证

### 数据流

```
用户请求 → FastAPI → 服务层 → 数据库/外部服务
                              ↓
后台任务 ← Celery ← Redis ← 定时触发
```

## 🔐 安全注意事项

- 所有敏感信息存储在 `.env` 中
- 生产环境使用 AWS RDS（不使用 SQLite）
- JWT token 有过期时间
- S3 使用预签名 URL 上传文件
- API 端点需要认证

## 🚀 CI/CD

项目使用 GitHub Actions 自动部署：

```yaml
# .github/workflows/deploy.yml
触发条件: push to main
流程:
  1. 检出代码
  2. SSH 到 EC2
  3. 拉取最新代码
  4. 重新构建镜像
  5. 重启服务
  6. 应用数据库迁移
  7. 健康检查
```

**部署配置**: 查看 [DEPLOYMENT.md](docs/DEPLOYMENT.md#cicd-配置)

## 📞 获取帮助

- **开发问题**: 查看 [DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **部署问题**: 查看 [DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **数据库问题**: 查看 [DATABASE.md](docs/DATABASE.md)
- **运维问题**: 查看 [MAINTENANCE.md](docs/MAINTENANCE.md)
- **命令查找**: 查看 [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**提示**: 这是项目的主入口文档，详细的操作指南请查看 `docs/` 目录下的各个文档。
