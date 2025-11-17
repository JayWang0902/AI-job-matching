# 文档目录

欢迎查阅 AI Job Matching 项目文档！

## 📖 文档列表

| 文档 | 说明 | 何时使用 |
|------|------|---------|
| **[DEVELOPMENT.md](./DEVELOPMENT.md)** | 本地开发指南 | 开发新功能、本地调试、热重载开发 |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | EC2 部署指南 | 首次部署、更新部署、CI/CD 配置 |
| **[DATABASE.md](./DATABASE.md)** | 数据库迁移指南 | 修改数据库结构、运行迁移、回滚迁移 |
| **[MAINTENANCE.md](./MAINTENANCE.md)** | 运维维护指南 | 日常维护、故障排查、Docker 清理 |
| **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** | 快速命令参考 | 快速查找常用命令 |

## 🎯 快速导航

### 我想...

- **在本地开发新功能** → [DEVELOPMENT.md](./DEVELOPMENT.md)
- **第一次部署到 EC2** → [DEPLOYMENT.md](./DEPLOYMENT.md)
- **修改数据库表结构** → [DATABASE.md](./DATABASE.md)
- **解决线上问题** → [MAINTENANCE.md](./MAINTENANCE.md)
- **查找某个命令** → [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

## 📋 快速开始流程

### 本地开发

```bash
# 1. 启动服务
docker compose up -d

# 2. 查看日志
docker compose logs -f backend

# 3. 运行迁移
docker compose exec backend alembic upgrade head

# 4. 测试
curl http://localhost:8000/health
```

详见: [DEVELOPMENT.md](./DEVELOPMENT.md)

### 部署到生产

```bash
# 1. 在 EC2 上拉取代码
git pull origin main

# 2. 重新构建并启动
docker compose build
docker compose up -d

# 3. 运行迁移
docker compose exec backend alembic upgrade head

# 4. 验证
curl http://localhost:8000/health
```

详见: [DEPLOYMENT.md](./DEPLOYMENT.md)

### 数据库迁移

```bash
# 1. 修改模型
vim app/models/user.py

# 2. 生成迁移
docker compose exec backend alembic revision --autogenerate -m "add phone field"

# 3. 应用迁移
docker compose exec backend alembic upgrade head
```

详见: [DATABASE.md](./DATABASE.md)

## 🔧 常见任务

<details>
<summary><b>查看日志</b></summary>

```bash
# 查看所有日志
docker compose logs

# 查看特定服务
docker compose logs backend

# 实时跟踪
docker compose logs -f backend

# 最近 100 行
docker compose logs --tail=100 backend
```

</details>

<details>
<summary><b>重启服务</b></summary>

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart backend

# 完全重启（停止并重新启动）
docker compose down
docker compose up -d
```

</details>

<details>
<summary><b>清理 Docker</b></summary>

```bash
# 安全清理
docker image prune -a
docker container prune
docker volume prune

# 一键清理（危险！）
docker system prune -a --volumes
```

</details>

<details>
<summary><b>数据库操作</b></summary>

```bash
# 查看迁移状态
docker compose exec backend alembic current

# 应用迁移
docker compose exec backend alembic upgrade head

# 回滚迁移
docker compose exec backend alembic downgrade -1
```

</details>

## 🆘 紧急问题

### API 无响应
```bash
docker compose restart backend
docker compose logs --tail=100 backend
```

### 磁盘已满
```bash
docker system prune -a --volumes -f
df -h
```

### 数据库连接失败
```bash
docker compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

### Celery 任务堆积
```bash
docker compose restart celery
docker compose exec redis redis-cli llen celery
```

详见: [MAINTENANCE.md](./MAINTENANCE.md)

## 📚 其他资源

- **主 README**: [../README.md](../README.md) - 项目概述和快速开始
- **Copilot 指南**: [../.github/copilot-instructions.md](../.github/copilot-instructions.md) - AI 开发助手使用指南

## 💡 文档阅读建议

1. **首次使用**: 按顺序阅读 DEVELOPMENT → DEPLOYMENT → DATABASE
2. **日常开发**: 参考 DEVELOPMENT + QUICK_REFERENCE
3. **部署上线**: 参考 DEPLOYMENT + DATABASE + MAINTENANCE
4. **故障处理**: 直接查看 MAINTENANCE 的相关章节

---

**提示**: 所有文档都包含详细的命令示例和故障排查步骤。如果遇到问题，先查看相关文档的"常见问题"或"故障排查"部分。
