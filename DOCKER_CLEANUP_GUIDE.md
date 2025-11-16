# Docker 清理命令速查表

## 📊 查看磁盘使用

```bash
# 查看总体使用情况
docker system df

# 查看详细使用情况（包括每个镜像/容器大小）
docker system df -v

# 查看所有镜像
docker images

# 查看所有容器（包括停止的）
docker ps -a
```

## 🧹 清理命令

### 轻度清理（推荐定期执行）
```bash
# 删除悬空镜像（<none> 标签）
docker image prune -f

# 删除未使用的构建缓存
docker builder prune -f

# 或使用脚本（选项 1）
./scripts/cleanup-docker.sh
```

### 中度清理
```bash
# 删除所有停止的容器
docker container prune -f

# 删除所有未使用的镜像
docker image prune -a -f

# 删除未使用的网络
docker network prune -f

# 或使用脚本（选项 2）
./scripts/cleanup-docker.sh
```

### 深度清理（⚠️ 谨慎使用）
```bash
# 删除所有未使用的 Docker 资源（包括 volumes）
docker system prune -a -f --volumes

# 或使用脚本（选项 3）
./scripts/cleanup-docker.sh
```

### 智能清理（保留最新版本）
```bash
# 使用脚本保留每个服务最新的 3 个版本
./scripts/cleanup-docker.sh  # 选择选项 4
```

## 🎯 针对性清理

### 删除特定镜像
```bash
# 按名称删除
docker rmi ghcr.io/jaywang0902/ai-job-matching-backend:old-tag

# 删除 2 个月前的旧镜像
docker images "ghcr.io/jaywang0902/ai-job-matching-*" --format "{{.ID}} {{.CreatedAt}}" | \
  awk '$2 < "2025-09-01" {print $1}' | xargs docker rmi -f
```

### 删除特定容器
```bash
# 停止并删除所有容器
docker compose down

# 删除特定容器
docker rm -f ai-job-matching-backend-1
```

### 清理构建缓存
```bash
# 删除所有构建缓存
docker builder prune -a -f

# 查看构建缓存使用情况
docker buildx du
```

## 📅 定期维护建议

### 每周执行（自动化）
```bash
# 添加到 cron (每周日凌晨 3 点)
# 编辑 crontab: crontab -e
0 3 * * 0 cd /path/to/AI-job-matching && docker image prune -f && docker builder prune -f
```

### 每月执行
```bash
# 深度清理，保留正在使用的资源
docker system prune -a -f
```

### 开发时
```bash
# 重新构建前先清理
docker compose down
docker builder prune -f
docker compose up --build -d
```

## 🔍 故障排查

### 镜像占用过多空间
```bash
# 查看最大的镜像
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -h

# 删除特定大小以上的未使用镜像
docker images --format "{{.ID}} {{.Size}}" | awk '$2 ~ /GB/ && $2 > 1 {print $1}' | xargs docker rmi -f
```

### 构建缓存过大
```bash
# 查看缓存使用情况
docker buildx du --verbose

# 完全重置 buildx
docker buildx prune -a -f
```

### 容器日志占用空间
```bash
# 查看容器日志大小
docker ps -a --format "{{.Names}}" | xargs -I {} sh -c 'echo -n "{}: "; docker inspect --format="{{.LogPath}}" {} | xargs ls -lh 2>/dev/null | awk "{print \$5}"'

# 清空特定容器日志
truncate -s 0 $(docker inspect --format='{{.LogPath}}' ai-job-matching-backend-1)

# 限制日志大小（在 docker-compose.yml 中添加）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 💡 空间优化建议

### 1. 使用 .dockerignore
```bash
# 在项目根目录创建 .dockerignore
cat > .dockerignore << EOF
.git
.github
*.md
.env.example
node_modules
__pycache__
*.pyc
.DS_Store
ai-job-matching/
EOF
```

### 2. 多阶段构建优化
已在 Dockerfile 中实现：
- Backend: 428 MB
- Celery: 418 MB  
- Frontend: 311 MB

### 3. 使用更小的基础镜像
```dockerfile
# 已使用轻量级镜像
FROM python:3.11-slim    # 而不是 python:3.11
FROM node:22-alpine      # 而不是 node:22
FROM redis:7.2-alpine    # 仅 41.4 MB
```

## 🚀 最佳实践

### 本地开发
```bash
# 1. 启动服务
docker compose up -d

# 2. 开发完成后停止但不删除
docker compose stop

# 3. 完全清理（删除容器和网络，保留镜像）
docker compose down

# 4. 完全清理（包括镜像和 volumes）
docker compose down --rmi all -v
```

### CI/CD 环境
GitHub Actions 已配置自动清理：
- 保留最新 10 个未标记的镜像版本
- 保留所有带标签的版本
- 每周自动执行清理

## 📈 监控脚本

```bash
#!/bin/bash
# 检查 Docker 空间使用，超过阈值发送通知

THRESHOLD=80  # 使用率阈值（%）
USAGE=$(docker system df --format "{{.Type}}\t{{.Size}}\t{{.Reclaimable}}" | awk '/Images/ {print $3}' | sed 's/%//')

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "⚠️  Docker 镜像使用率 ${USAGE}% 超过阈值 ${THRESHOLD}%"
    echo "建议执行清理：./scripts/cleanup-docker.sh"
fi
```

---

## 🆘 紧急清理（空间严重不足）

```bash
# 1. 停止所有容器
docker stop $(docker ps -aq)

# 2. 删除所有容器
docker rm $(docker ps -aq)

# 3. 删除所有镜像
docker rmi $(docker images -q)

# 4. 清理所有资源
docker system prune -a -f --volumes

# 5. 重新构建
docker compose up --build -d
```

**⚠️ 警告**: 这将删除所有 Docker 数据，包括 volumes 中的数据！
