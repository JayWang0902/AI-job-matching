# 🎯 三个困惑问题的完整解答

## 1️⃣ 本地容器如何读取 .env.local 而不是 .env？

### 答案：在 docker-compose.dev.yml 中配置

```yaml
# docker-compose.dev.yml (第 11 行)
services:
  backend:
    env_file:
      - .env.local  # ← 这里指定读取 .env.local
```

### 工作原理

```bash
# 开发模式
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
                     ↓                      ↓
                使用 .env              覆盖为 .env.local

# 生产模式
docker compose up
    ↓
使用 .env (默认)
```

### 验证方式

```bash
# 查看 backend 容器的环境变量
docker compose exec backend printenv | grep "ENV="

# 开发模式输出：ENV=development (来自 .env.local)
# 生产模式输出：ENV=production (来自 .env)
```

---

## 2️⃣ 如何区分服务是通过 dev 还是普通 docker compose 启动的？

### 方法 1: 查看镜像名称（最简单）⭐️

```bash
docker compose ps

# 开发模式输出：
# ai-job-matching-backend:dev  ← 有 :dev 标签
# ai-job-matching-celery:dev

# 生产模式输出：
# ghcr.io/jaywang0902/ai-job-matching-backend:2e946b0  ← registry 镜像
# ghcr.io/jaywang0902/ai-job-matching-celery:2e946b0
```

### 方法 2: 查看环境变量

```bash
docker compose exec backend printenv | grep -E "ENV=|DEBUG="

# 开发模式：
# ENV=development
# DEBUG=true

# 生产模式：
# ENV=production
# DEBUG=false
```

### 方法 3: 查看是否有 Volume 挂载

```bash
docker compose exec backend ls -la /app/app

# 开发模式：
# 看到的是你本地的文件（通过 volume mounting）
# 文件时间戳会随本地修改而变化

# 生产模式：
# 看到的是镜像内固定的文件
# 修改本地代码不会影响容器
```

### 方法 4: 使用便捷脚本 ⭐️

```bash
./scripts/check_mode.sh

# 输出：
# ✅ Running in DEVELOPMENT mode (:dev tag detected)
# 或
# 🚀 Running in PRODUCTION mode
```

---

## 3️⃣ Redis 是本地安装还是 Docker？为什么 dev.yml 里没有？

### 答案：Redis 也是 Docker 容器，但不在 dev.yml 中

### 原因：Docker Compose 的继承机制

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
                     ↑                      ↑
                 定义 4 个服务           只覆盖需要改的 3 个
                 (redis + backend        (backend + celery
                  + celery + frontend)    + frontend)
```

### Docker Compose 合并规则

```yaml
# docker-compose.yml (基础配置 - 4 个服务)
services:
  redis:     # 开发和生产配置完全相同
  backend:   # 需要开发模式覆盖
  celery:    # 需要开发模式覆盖  
  frontend:  # 需要开发模式覆盖

# docker-compose.dev.yml (覆盖配置 - 只写 3 个)
services:
  # redis 不写！因为开发和生产配置一样
  backend:   # 覆盖：添加 volumes, 改 env_file, 改 image
  celery:    # 覆盖：添加 volumes, 改 env_file, 改 image
  frontend:  # 覆盖：改成 node 镜像直接运行
```

### 为什么 Redis 不需要覆盖？

**开发和生产环境的 Redis 需求完全相同：**
- ✅ 镜像相同：`redis:7.2-alpine`
- ✅ 端口相同：`6379`
- ✅ 配置相同：maxmemory 256mb, persistence 等
- ✅ 不需要 hot reload (Redis 不是应用代码)
- ✅ 不需要 volume mounting

**Backend/Celery/Frontend 需要覆盖，因为：**
- ❌ 镜像不同：开发 `:dev` vs 生产 registry 镜像
- ❌ 环境变量不同：`.env.local` vs `.env`
- ❌ 需要 volume mounting（开发需要 hot reload）
- ❌ 命令不同：开发用 `--reload`

### 验证 Redis 确实来自 docker-compose.yml

```bash
# 1. 查看 docker-compose.yml 的 Redis 配置
docker compose -f docker-compose.yml config | grep -A 15 "^  redis:"

# 2. 查看合并后的 Redis 配置
docker compose -f docker-compose.yml -f docker-compose.dev.yml config | grep -A 15 "^  redis:"

# 3. 对比两个输出
# 结果：完全相同！证明 dev.yml 没有覆盖 Redis
```

### Redis 是本地安装的吗？不是！

```bash
# 查看 Redis 容器
docker compose ps redis

# 输出：
# NAME                     IMAGE             STATUS
# ai-job-matching-redis-1  redis:7.2-alpine  Up 10 minutes (healthy)
#                          ↑
#                     Docker 镜像，不是本地安装！

# 如果是本地安装的 Redis (不推荐)：
# brew install redis
# redis-server &
# 这样的话容器无法连接到它
```

---

## 📊 配置对比表

| 配置项 | docker-compose.yml | docker-compose.dev.yml | 最终结果 |
|--------|-------------------|----------------------|---------|
| **Redis** |
| image | redis:7.2-alpine | (不写) | redis:7.2-alpine |
| ports | 6379:6379 | (不写) | 6379:6379 |
| config | maxmemory 256mb | (不写) | maxmemory 256mb |
| **Backend** |
| image | ghcr.io/.../backend:latest | backend:dev | **backend:dev** ✅ |
| env_file | .env | .env.local | **.env.local** ✅ |
| volumes | (无) | ./app:/app/app | **有 volumes** ✅ |
| command | uvicorn ... | uvicorn ... --reload | **有 --reload** ✅ |

---

## 🎯 核心要点

### 1. 环境变量文件

```
生产环境：.env (由 docker-compose.yml 指定)
开发环境：.env.local (由 docker-compose.dev.yml 覆盖)
```

### 2. 模式识别

```bash
# 最快速的方式
docker compose ps

# 看镜像名称：
#   :dev 标签 → 开发模式
#   ghcr.io/... → 生产模式
```

### 3. Docker Compose 继承

```
docker-compose.yml       所有服务的基础配置
docker-compose.dev.yml   只写需要改的服务和字段
合并结果               = 基础配置 + 覆盖配置
```

### 4. Redis 来源

```
✅ Docker 容器 (来自 docker-compose.yml)
❌ 不是本地安装
❌ 不需要在 dev.yml 中重复定义
```

---

## 🔧 实用命令速查

```bash
# 查看当前模式
./scripts/check_mode.sh

# 查看环境变量
docker compose exec backend printenv | grep "ENV="

# 查看合并后的完整配置
docker compose -f docker-compose.yml -f docker-compose.dev.yml config

# 只查看服务列表
docker compose -f docker-compose.yml -f docker-compose.dev.yml config --services

# 验证 Redis 配置未被覆盖
docker compose -f docker-compose.yml config | grep -A 10 "redis:"
docker compose -f docker-compose.yml -f docker-compose.dev.yml config | grep -A 10 "redis:"
# 两个输出应该完全相同
```

---

## 📚 相关文档

- `docs/DOCKER_COMPOSE_INHERITANCE.md` - Docker Compose 继承机制详解
- `docker-compose.yml` - 基础配置
- `docker-compose.dev.yml` - 开发环境覆盖配置
