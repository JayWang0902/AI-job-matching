# 快速命令参考

## 🚀 本地开发

### 启动服务

```bash
# 启动所有服务（后台）
docker compose up -d

# 启动并查看日志
docker compose up

# 仅启动特定服务
docker compose up backend redis

# 重新构建并启动
docker compose up --build
```

### 停止服务

```bash
# 停止所有服务
docker compose down

# 停止并删除卷（危险！会删除数据）
docker compose down -v

# 仅停止特定服务
docker compose stop backend
```

### 查看日志

```bash
# 所有服务
docker compose logs

# 特定服务
docker compose logs backend
docker compose logs celery
docker compose logs redis

# 实时跟踪
docker compose logs -f backend

# 最近 100 行
docker compose logs --tail=100 backend
```

### 进入容器

```bash
# 进入 backend 容器
docker compose exec backend bash

# 运行 Python shell
docker compose exec backend python

# 运行单个命令
docker compose exec backend python -c "print('hello')"
```

## 🗄️ 数据库操作

### Alembic 迁移

```bash
# 查看当前版本
docker compose exec backend alembic current

# 查看迁移历史
docker compose exec backend alembic history

# 生成新迁移
docker compose exec backend alembic revision --autogenerate -m "description"

# 应用迁移
docker compose exec backend alembic upgrade head

# 回滚一个版本
docker compose exec backend alembic downgrade -1

# 回滚到指定版本
docker compose exec backend alembic downgrade <revision_id>
```

### 数据库连接

```bash
# 测试连接
docker compose exec backend python -c "
from app.core.database import engine
with engine.connect() as conn:
    print('✅ Connected')
"

# 查看所有表
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
print(inspect(engine).get_table_names())
"
```

## 📦 Redis 操作

```bash
# 进入 Redis CLI
docker compose exec redis redis-cli

# 测试连接
docker compose exec redis redis-cli ping

# 查看信息
docker compose exec redis redis-cli info

# 查看所有键
docker compose exec redis redis-cli keys '*'

# 获取键值
docker compose exec redis redis-cli get <key>

# 删除键
docker compose exec redis redis-cli del <key>

# 清空所有数据（危险！）
docker compose exec redis redis-cli FLUSHALL
```

## 🔄 Celery 操作

```bash
# 查看活跃任务
docker compose exec celery celery -A app.celery_app.celery_app inspect active

# 查看已注册任务
docker compose exec celery celery -A app.celery_app.celery_app inspect registered

# 查看 worker 状态
docker compose exec celery celery -A app.celery_app.celery_app inspect stats

# 清空任务队列
docker compose exec redis redis-cli del celery

# 重启 Celery
docker compose restart celery
```

## 🧪 测试与调试

### API 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 用户注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 用户登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 带认证的请求
TOKEN="your_jwt_token"
curl http://localhost:8000/api/resume \
  -H "Authorization: Bearer $TOKEN"
```

### 手动触发任务

```bash
# 触发每日流程
curl -X POST http://localhost:8000/debug/trigger-daily-flow

# Python shell 中手动触发
docker compose exec backend python -c "
from app.tasks import run_daily_flow
result = run_daily_flow.delay()
print(f'Task ID: {result.id}')
"
```

### 查看错误

```bash
# API 错误日志
docker compose logs backend | grep ERROR

# Celery 错误日志
docker compose logs celery | grep ERROR

# 系统错误日志
sudo tail -f /var/log/syslog
```

## 🚢 部署相关

### SSH 连接

```bash
# 连接到 EC2
ssh -i key.pem ubuntu@<EC2_IP>

# 传输文件到 EC2
scp -i key.pem local_file ubuntu@<EC2_IP>:~/remote_path

# 从 EC2 下载文件
scp -i key.pem ubuntu@<EC2_IP>:~/remote_file ./local_path
```

### 部署流程

```bash
# 在 EC2 上

# 1. 拉取最新代码
cd ~/AI-job-matching
git pull origin main

# 2. 重新构建
docker compose build

# 3. 重启服务
docker compose down
docker compose up -d

# 4. 应用数据库迁移
docker compose exec backend alembic upgrade head

# 5. 验证
curl http://localhost:8000/health
docker compose ps
```

### 回滚部署

```bash
# 1. 查看 commit 历史
git log --oneline

# 2. 回滚到指定版本
git reset --hard <commit_hash>

# 3. 强制更新远程（慎用！）
git push origin main --force

# 4. 重新部署
docker compose build
docker compose down
docker compose up -d
```

## 🧹 Docker 清理

### 基本清理

```bash
# 删除停止的容器
docker container prune

# 删除未使用的镜像
docker image prune -a

# 删除未使用的卷
docker volume prune

# 删除未使用的网络
docker network prune

# 删除构建缓存
docker builder prune
```

### 彻底清理

```bash
# 一键清理所有未使用资源（危险！）
docker system prune -a --volumes

# 查看磁盘占用
docker system df

# 停止所有容器
docker stop $(docker ps -aq)

# 删除所有容器
docker rm $(docker ps -aq)

# 删除所有镜像
docker rmi $(docker images -q)
```

## 📊 监控命令

### 资源使用

```bash
# Docker 容器资源
docker stats

# CPU 使用
top -bn1 | head -20

# 内存使用
free -h

# 磁盘使用
df -h

# Docker 磁盘占用
docker system df
```

### 进程监控

```bash
# 查看所有容器
docker ps -a

# 查看容器详情
docker inspect <container_id>

# 查看容器日志大小
docker ps -q | xargs docker inspect --format='{{.Name}}: {{.LogPath}}' | xargs ls -lh
```

## 🔐 环境变量

### 查看环境变量

```bash
# 在容器中
docker compose exec backend env

# 特定变量
docker compose exec backend env | grep DATABASE_URL

# 加载 .env 文件
export $(cat .env | xargs)
```

### 更新环境变量

```bash
# 1. 编辑 .env 文件
nano .env

# 2. 重启服务
docker compose down
docker compose up -d

# 3. 验证
docker compose exec backend env | grep <VARIABLE>
```

## 🛠️ 常用脚本

### 完整重启

```bash
#!/bin/bash
# scripts/full-restart.sh

echo "停止服务..."
docker compose down

echo "清理旧镜像..."
docker image prune -f

echo "重新构建..."
docker compose build

echo "启动服务..."
docker compose up -d

echo "等待服务就绪..."
sleep 10

echo "检查状态..."
docker compose ps

echo "✅ 完成！"
```

### 备份数据

```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# 备份数据库
echo "备份数据库..."
pg_dump -h $RDS_ENDPOINT -U $DB_USER -d $DB_NAME > \
  $BACKUP_DIR/db_$DATE.sql

# 备份 Redis
echo "备份 Redis..."
docker compose exec redis redis-cli BGSAVE
docker cp $(docker compose ps -q redis):/data/dump.rdb \
  $BACKUP_DIR/redis_$DATE.rdb

# 备份配置文件
echo "备份配置..."
cp .env $BACKUP_DIR/env_$DATE
cp docker-compose.yml $BACKUP_DIR/docker-compose_$DATE.yml

echo "✅ 备份完成: $BACKUP_DIR"
```

### 健康检查

```bash
#!/bin/bash
# scripts/health-check.sh

echo "🔍 健康检查..."

# API 健康检查
echo "检查 API..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API 正常"
else
    echo "❌ API 异常"
fi

# Redis 健康检查
echo "检查 Redis..."
if docker compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 正常"
else
    echo "❌ Redis 异常"
fi

# 数据库健康检查
echo "检查数据库..."
if docker compose exec backend python -c "from app.core.database import engine; engine.connect()" > /dev/null 2>&1; then
    echo "✅ 数据库正常"
else
    echo "❌ 数据库异常"
fi

# 容器状态
echo "容器状态:"
docker compose ps
```

## 🆘 紧急命令

### 服务无响应

```bash
# 立即重启所有服务
docker compose restart

# 或完全重启
docker compose down && docker compose up -d

# 查看最近错误
docker compose logs --tail=50 backend | grep ERROR
```

### 磁盘已满

```bash
# 紧急清理
docker system prune -a --volumes -f
sudo journalctl --vacuum-size=100M
find /var/log -name "*.log" -exec truncate -s 0 {} \;

# 查看占用
du -sh /* | sort -h
```

### 内存不足

```bash
# 释放内存
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches

# 重启占用大的服务
docker compose restart celery

# 查看内存占用
docker stats --no-stream
```

## 📚 相关文档

- [DEVELOPMENT.md](./DEVELOPMENT.md) - 本地开发详细指南
- [DEPLOYMENT.md](./DEPLOYMENT.md) - EC2 部署详细指南
- [DATABASE.md](./DATABASE.md) - 数据库迁移详细指南
- [MAINTENANCE.md](./MAINTENANCE.md) - 运维维护详细指南

## 💡 提示

- 开发时使用 `-f` 跟踪日志: `docker compose logs -f backend`
- 生产环境重启前先 `docker compose ps` 确认状态
- 清理前先 `docker system df` 查看可回收空间
- 数据库操作前先备份
- 定期查看日志，及时发现问题
