# 运维维护指南

## 🎯 日常维护

### 健康检查

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@<EC2_IP>
cd ~/AI-job-matching

# 检查所有服务状态
docker compose ps

# 应该看到:
# NAME                STATUS              PORTS
# backend             Up 5 minutes        0.0.0.0:8000->8000/tcp
# celery              Up 5 minutes        
# redis               Up 5 minutes        0.0.0.0:6379->6379/tcp
```

### 查看日志

```bash
# 所有服务日志
docker compose logs

# 特定服务
docker compose logs backend
docker compose logs celery
docker compose logs redis

# 实时跟踪
docker compose logs -f backend

# 最近 100 行
docker compose logs --tail=100 backend

# 带时间戳
docker compose logs -t backend
```

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 查看 Docker 磁盘使用
docker system df

# 详细信息
docker system df -v
```

## 🧹 Docker 清理

### 为什么需要清理？

Docker 会积累大量未使用的资源：
- **旧镜像**: 每次构建产生新镜像，旧镜像不会自动删除
- **停止的容器**: 容器停止后仍占用空间
- **未使用的卷**: 数据卷不会自动删除
- **构建缓存**: 每层缓存都占用空间

**典型问题**:
```bash
df -h
# /dev/xvda1        20G   19G   1G   95%   # ← 磁盘快满！
```

### 清理策略

#### 1. 安全清理（推荐）

```bash
# 删除未使用的镜像
docker image prune -a

# 删除停止的容器
docker container prune

# 删除未使用的卷
docker volume prune

# 删除未使用的网络
docker network prune
```

#### 2. 一键清理

```bash
# 清理所有未使用资源（危险！）
docker system prune -a --volumes

# 会删除:
# - 所有停止的容器
# - 所有未使用的镜像
# - 所有未使用的卷
# - 所有未使用的网络
# - 所有构建缓存
```

#### 3. 选择性清理

```bash
# 只清理 30 天前的镜像
docker image prune -a --filter "until=720h"

# 只清理构建缓存
docker builder prune

# 保留最近 3 个版本的镜像
docker images | grep "ai-job-matching-backend" | tail -n +4 | awk '{print $3}' | xargs docker rmi
```

### 清理前检查

```bash
# 1. 检查磁盘使用
docker system df

# 输出示例:
# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          15        3         2.5GB     1.8GB (72%)
# Containers      3         3         1.2MB     0B (0%)
# Local Volumes   2         2         150MB     0B (0%)
# Build Cache     25        0         500MB     500MB (100%)

# 2. 列出所有镜像
docker images

# 3. 列出所有容器（包括停止的）
docker ps -a
```

### 清理后验证

```bash
# 1. 再次检查磁盘
docker system df

# 2. 确认服务正常
docker compose ps

# 3. 测试 API
curl http://localhost:8000/health
```

### 清理脚本

创建 `scripts/docker-cleanup.sh`:

```bash
#!/bin/bash

echo "🔍 检查磁盘使用..."
df -h /
docker system df

read -p "🤔 是否继续清理？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消清理"
    exit 1
fi

echo "🧹 清理构建缓存..."
docker builder prune -f

echo "🗑️  清理未使用的镜像..."
docker image prune -a -f

echo "🧼 清理停止的容器..."
docker container prune -f

echo "📦 清理未使用的卷..."
docker volume prune -f

echo "🌐 清理未使用的网络..."
docker network prune -f

echo "✅ 清理完成！"
df -h /
docker system df
```

使用：
```bash
chmod +x scripts/docker-cleanup.sh
./scripts/docker-cleanup.sh
```

## 🔥 紧急问题处理

### 服务无响应

```bash
# 1. 检查服务状态
docker compose ps

# 2. 查看错误日志
docker compose logs --tail=100 backend

# 3. 重启特定服务
docker compose restart backend

# 4. 如果还是不行，完全重启
docker compose down
docker compose up -d

# 5. 验证
curl http://localhost:8000/health
```

### 内存不足

```bash
# 1. 检查内存使用
free -h
docker stats --no-stream

# 2. 停止非关键服务
docker compose stop celery  # 临时停止 Celery

# 3. 清理缓存
echo 3 | sudo tee /proc/sys/vm/drop_caches

# 4. 重启服务
docker compose restart backend

# 长期解决: 升级 EC2 实例类型
```

### 磁盘已满

```bash
# 1. 确认磁盘使用
df -h
du -sh /home/ubuntu/AI-job-matching/*

# 2. 立即清理 Docker
docker system prune -a --volumes -f

# 3. 清理日志
sudo truncate -s 0 /var/log/syslog
sudo truncate -s 0 /var/log/kern.log

# 4. 如果仍然不够
# 选项 A: 扩展 EBS 卷（AWS Console）
# 选项 B: 挂载新 EBS 卷

# 5. 恢复服务
docker compose up -d
```

### 数据库连接失败

```bash
# 1. 检查 RDS 状态（AWS Console）

# 2. 测试连接
docker compose exec backend python -c "
from app.core.database import engine
try:
    with engine.connect() as conn:
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
"

# 3. 检查环境变量
docker compose exec backend env | grep DATABASE_URL

# 4. 检查安全组规则（AWS Console）
# - RDS 安全组是否允许 EC2 的入站流量？
# - 端口 5432 是否开放？

# 5. 重启服务
docker compose restart backend
```

### Redis 问题

```bash
# 1. 测试 Redis 连接
docker compose exec redis redis-cli ping
# 应该返回: PONG

# 2. 查看 Redis 信息
docker compose exec redis redis-cli info

# 3. 清空 Redis（慎用！）
docker compose exec redis redis-cli FLUSHALL

# 4. 重启 Redis
docker compose restart redis
```

### Celery 任务堆积

```bash
# 1. 检查任务队列
docker compose exec redis redis-cli llen celery

# 2. 查看 worker 状态
docker compose exec celery celery -A app.celery_app.celery_app inspect active

# 3. 清空队列（慎用！）
docker compose exec redis redis-cli del celery

# 4. 重启 Celery
docker compose restart celery

# 5. 手动触发任务测试
curl -X POST http://localhost:8000/debug/trigger-daily-flow
```

## 📊 性能优化

### 监控关键指标

```bash
# CPU 使用
top -bn1 | grep "Cpu(s)"

# 内存使用
free -h

# 磁盘 I/O
iostat -x 1 3

# 网络流量
ifstat -t 1 3
```

### 优化建议

#### 1. 数据库连接池

检查 `app/core/config.py`:
```python
# 合理设置连接池大小
pool_size=10          # 正常连接数
max_overflow=20       # 突发连接数
pool_pre_ping=True    # 健康检查
```

#### 2. Redis 内存管理

```bash
# 查看 Redis 内存使用
docker compose exec redis redis-cli info memory

# 设置最大内存
docker compose exec redis redis-cli CONFIG SET maxmemory 256mb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. 日志轮转

添加到 `docker-compose.yml`:
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🔐 安全维护

### 定期更新

```bash
# 1. 更新系统包
sudo apt update && sudo apt upgrade -y

# 2. 更新 Docker
sudo apt install docker-ce docker-ce-cli containerd.io

# 3. 更新 Python 依赖
# 在 requirements.txt 更新版本后
docker compose build backend
docker compose up -d backend
```

### 检查漏洞

```bash
# 扫描 Docker 镜像漏洞
docker scout cves ai-job-matching-backend:latest

# 检查 Python 依赖漏洞
docker compose exec backend pip list --outdated
docker compose exec backend pip install safety
docker compose exec backend safety check
```

### 密钥轮换

```bash
# 1. 生成新的 JWT Secret
openssl rand -hex 32

# 2. 更新 .env 文件
nano .env
# SECRET_KEY=<新密钥>

# 3. 重启服务
docker compose restart backend

# 注意: 所有现有 token 会失效，用户需要重新登录
```

## 📦 备份与恢复

### 数据库备份

```bash
# 手动备份
pg_dump -h <RDS_ENDPOINT> -U <DB_USER> -d <DB_NAME> > backup_$(date +%Y%m%d).sql

# 自动备份脚本
cat > scripts/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -h $RDS_ENDPOINT -U $DB_USER -d $DB_NAME > \
  $BACKUP_DIR/db_backup_$DATE.sql

# 保留最近 7 天的备份
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete

echo "✅ 备份完成: db_backup_$DATE.sql"
EOF

chmod +x scripts/backup-db.sh

# 添加到 crontab（每天凌晨 2 点）
crontab -e
# 0 2 * * * /home/ubuntu/scripts/backup-db.sh
```

### Redis 备份

```bash
# 手动备份
docker compose exec redis redis-cli BGSAVE
docker cp $(docker compose ps -q redis):/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb

# 恢复
docker compose stop redis
docker cp redis_backup_YYYYMMDD.rdb $(docker compose ps -q redis):/data/dump.rdb
docker compose start redis
```

### 恢复数据库

```bash
# 停止服务
docker compose stop backend celery

# 恢复备份
psql -h <RDS_ENDPOINT> -U <DB_USER> -d <DB_NAME> < backup_YYYYMMDD.sql

# 重启服务
docker compose start backend celery

# 验证
curl http://localhost:8000/health
```

## 📈 容量规划

### 何时需要扩容？

监控这些指标：
- **CPU 持续 > 70%**: 考虑升级实例
- **内存使用 > 80%**: 增加内存或优化代码
- **磁盘 > 85%**: 清理或扩展 EBS
- **数据库连接池满**: 增加连接数或优化查询
- **API 响应时间 > 2s**: 优化代码或扩容

### 扩容选项

#### 垂直扩容（升级实例）
```bash
# AWS Console:
# EC2 → 实例 → 操作 → 实例类型 → 更改类型
# t2.micro → t3.small → t3.medium
```

#### 水平扩容（负载均衡）
需要设置:
- Application Load Balancer
- Auto Scaling Group
- 共享 Redis 和 RDS
- Session 持久化

## 🛠️ 故障排查清单

### 问题: API 无响应
- [ ] `docker compose ps` - 所有服务运行中？
- [ ] `docker compose logs backend` - 有错误日志？
- [ ] `curl http://localhost:8000/health` - 健康检查通过？
- [ ] `free -h` - 内存足够？
- [ ] `df -h` - 磁盘足够？

### 问题: 数据库错误
- [ ] RDS 实例状态 - 可用？
- [ ] 安全组规则 - EC2 能访问 RDS？
- [ ] 环境变量 - DATABASE_URL 正确？
- [ ] 连接池 - 连接数未超限？
- [ ] Alembic 版本 - 迁移已应用？

### 问题: 任务不执行
- [ ] Celery 容器 - 运行中？
- [ ] Redis 连接 - `redis-cli ping` 成功？
- [ ] Celery logs - 有错误信息？
- [ ] 任务队列 - `llen celery` 有堆积？
- [ ] Celery Beat - 定时任务配置正确？

## 📚 相关文档

- [DEVELOPMENT.md](./DEVELOPMENT.md) - 本地开发
- [DEPLOYMENT.md](./DEPLOYMENT.md) - EC2 部署
- [DATABASE.md](./DATABASE.md) - 数据库迁移
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 命令速查
