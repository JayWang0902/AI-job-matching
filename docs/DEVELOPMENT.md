# 本地开发指南

## 🚀 快速开始

### 首次设置

```bash
# 1. 复制环境变量模板
cp .env.local.example .env.local

# 2. 编辑配置（填入真实的 API keys）
nano .env.local

# 3. 启动开发环境
./scripts/dev.sh
```

访问：
- Backend API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Frontend: http://localhost:3000

### 日常开发

```bash
# 启动
./scripts/dev.sh

# 修改代码 → 保存 → 自动重载（1-2秒）

# 查看日志
docker compose logs -f backend

# 停止
./scripts/dev_stop.sh
```

## 🔧 开发特性

### 热重载

- **Backend (FastAPI)**: 修改 Python 代码自动重启
- **Frontend (Next.js)**: React 组件热替换
- **Celery**: 修改任务代码自动重启

### Volume Mounting

代码实时同步到容器，无需重新构建镜像：

```yaml
volumes:
  - ./app:/app/app              # Backend 代码
  - ./frontend:/app             # Frontend 代码
```

## 📝 常用命令

```bash
# 查看服务状态
docker compose ps

# 重启单个服务
docker compose restart backend

# 进入容器
docker compose exec backend bash

# 运行测试
docker compose exec backend pytest

# 数据库迁移
docker compose exec backend alembic upgrade head

# 查看日志
docker compose logs -f backend
docker compose logs -f celery
```

## 🐛 调试技巧

### 查看日志

```bash
# 实时日志
docker compose logs -f backend

# 最近100行
docker compose logs --tail=100 backend

# 特定时间
docker compose logs --since 30m backend
```

### Python 交互式调试

```bash
# 进入容器
docker compose exec backend python

# 测试代码
>>> from app.models.user import User
>>> from app.core.database import SessionLocal
>>> db = SessionLocal()
>>> users = db.query(User).all()
```

### 数据库调试

```bash
# 检查表
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
print(inspect(engine).get_table_names())
"

# 测试连接
docker compose exec backend python -c "
from app.core.database import engine
try:
    engine.connect()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## 🔄 工作流程

### 功能开发

```
1. 启动开发环境
   ./scripts/dev.sh

2. 创建新分支
   git checkout -b feature/new-feature

3. 修改代码
   - 编辑文件
   - 保存后自动重载
   - 浏览器测试

4. 运行测试
   docker compose exec backend pytest

5. 提交代码
   git add .
   git commit -m "feat: add new feature"
```

### 数据库变更

```bash
# 1. 修改 SQLAlchemy 模型
vim app/models/user.py

# 2. 生成迁移脚本
docker compose exec backend alembic revision --autogenerate -m "add new field"

# 3. 应用迁移
docker compose exec backend alembic upgrade head

# 4. 提交迁移脚本
git add alembic/versions/
git commit -m "feat: add new database field"
```

### 推送前验证

```bash
# 1. 运行预检查脚本
./scripts/pre_push.sh

# 2. 如果全部通过，推送代码
git push origin feature/new-feature

# 3. 创建 Pull Request
```

## 🎯 最佳实践

### 环境变量

- **开发**: 使用 `.env.local`（gitignored）
- **生产**: 使用 `.env`（在 EC2 上）
- **不要提交**: 包含真实 secrets 的文件

### 数据库

- **推荐**: 使用与生产相同的 RDS
- **S3**: 创建开发专用 bucket
- **不要**: 在生产库上做破坏性测试

### 代码风格

```bash
# 使用 Black 格式化
docker compose exec backend black app/

# 使用 isort 整理 imports
docker compose exec backend isort app/

# 运行 linter
docker compose exec backend flake8 app/
```

## ⚠️ 常见问题

### Q: 端口已被占用

```bash
# 查看占用端口的进程
lsof -i :8000

# 杀掉进程
kill -9 <PID>
```

### Q: 代码修改不生效

```bash
# 重启服务
docker compose restart backend

# 或清理重启
docker compose down
docker compose up -d
```

### Q: 数据库连接失败

```bash
# 检查 DATABASE_URL
docker compose exec backend env | grep DATABASE_URL

# 测试连接
docker compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

### Q: Docker 镜像太大

```bash
# 清理未使用的镜像
docker image prune -a -f

# 清理构建缓存
docker builder prune -af
```

### Q: Volume 挂载问题（macOS）

```bash
# 确保 Docker Desktop 有权限访问项目目录
# Docker Desktop → Preferences → Resources → File Sharing
# 添加项目目录路径
```

## 📊 性能对比

| 操作 | Docker 开发 | 手动开发 |
|------|------------|---------|
| 首次启动 | 3-5 秒 | 10-15 分钟 |
| 代码重载 | 1-2 秒 | 1-2 秒 |
| 环境一致性 | 100% | 60-70% |
| 新成员上手 | 5 分钟 | 2-3 小时 |

## 🎓 下一步

1. 阅读 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解部署流程
2. 阅读 [DATABASE.md](./DATABASE.md) 了解数据库迁移
3. 查看 [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) 常用命令
