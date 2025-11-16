# 🔥 热重载开发 vs 🐳 生产模式测试

## TL;DR（太长不看版）

```bash
# 日常开发（修改代码立即看到效果）
./scripts/dev.sh up

# 推送前验证（完全模拟生产环境）
./scripts/pre_push.sh
```

---

## 📋 两种模式详细对比

### 🔥 模式 1：热重载开发模式

**一句话：** 修改代码 → 保存 → 自动重启 → 浏览器刷新（1-3秒）

#### 工作原理
```
你修改 app/api/auth.py
    ↓
保存文件
    ↓
Docker 容器检测到文件变化（通过 volume 挂载）
    ↓
Uvicorn 自动重启服务（--reload 参数）
    ↓
浏览器刷新 → 看到新代码效果
```

#### 技术实现
```yaml
# docker-compose.dev.yml
services:
  backend:
    volumes:
      - ./app:/app/app  # 挂载代码目录到容器
    command: uvicorn app.main:app --reload  # 启用热重载
```

#### 优点
- ✅ **快速迭代**：修改代码立即生效
- ✅ **开发效率高**：无需等待重新构建
- ✅ **前端自动刷新**：Next.js Fast Refresh
- ✅ **节省时间**：每次修改节省 1-2 分钟

#### 缺点
- ⚠️ **不完全等同生产**：使用的是挂载的代码，不是构建的镜像
- ⚠️ **性能略低**：文件监控有额外开销
- ⚠️ **可能漏掉问题**：某些构建时的问题检测不到

#### 使用场景
- ✅ 日常功能开发
- ✅ API 接口调试
- ✅ 前端样式调整
- ✅ 快速验证想法

---

### 🐳 模式 2：生产模式本地测试

**一句话：** 完全模拟生产环境，修改代码 → 重新构建镜像 → 运行测试（2-5分钟）

#### 工作原理
```
你修改 app/api/auth.py
    ↓
运行 ./scripts/pre_push.sh
    ↓
Docker 完整构建镜像（COPY 代码到镜像内）
    ↓
启动容器运行健康检查
    ↓
所有测试通过 → 确认可以推送
```

#### 技术实现
```yaml
# docker-compose.test.yml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile  # 完整的多阶段构建
    # 没有 volumes 挂载！代码在镜像内部
```

#### 优点
- ✅ **完全等同生产**：使用相同的 Dockerfile 构建
- ✅ **提前发现问题**：构建失败、依赖缺失等
- ✅ **保证一致性**：本地通过 = 生产环境通过

#### 缺点
- ⚠️ **构建慢**：每次修改需 2-5 分钟重新构建
- ⚠️ **不适合频繁修改**：降低开发效率

#### 使用场景
- ✅ 推送代码前最终验证
- ✅ 修改 Dockerfile 或 requirements.txt
- ✅ 重要功能上线前测试
- ✅ CI/CD 流程调试

---

## 🎯 推荐工作流

### Step 1: 开发阶段（使用热重载）

```bash
# 早上开始工作
./scripts/dev.sh up

# 编码...修改代码...保存
# 刷新浏览器立即看到效果

# 查看日志调试
./scripts/dev.sh logs backend

# 晚上下班
./scripts/dev.sh down
```

**预期效果：**
- 修改 Python 文件 → 2-3 秒后生效
- 修改 React 组件 → 不到 1 秒自动刷新
- 无需手动重启任何服务

---

### Step 2: 推送前验证（生产模式）

```bash
# 功能开发完成，准备提交
git status

# 运行完整测试
./scripts/pre_push.sh

# ✅ 如果测试通过
git add .
git commit -m "feat: add new feature"
git push

# ❌ 如果测试失败
# 查看错误信息，修复问题
# 再次运行 ./scripts/pre_push.sh
```

**检查项：**
- ✅ Docker 镜像构建成功
- ✅ 所有容器启动正常
- ✅ 健康检查通过
- ✅ 依赖完整无缺失

---

## 💡 实际例子

### 例子 1：添加新的 API 端点

```bash
# 1. 启动热重载模式
./scripts/dev.sh up

# 2. 修改代码
# vim app/api/users.py
@router.get("/users/profile")
async def get_profile():
    return {"name": "John"}

# 3. 保存文件，等待 2 秒
# 4. 浏览器访问 http://localhost:8000/users/profile
# 5. 立即看到结果！

# 6. 继续修改，快速迭代...

# 7. 功能完成，运行生产测试
./scripts/dev.sh down
./scripts/pre_push.sh

# 8. 测试通过，推送
git push
```

---

### 例子 2：修改前端样式

```bash
# 1. 热重载模式
./scripts/dev.sh up

# 2. 修改 CSS
# vim frontend/app/globals.css
.button {
  background: blue;  /* 改成 red */
}

# 3. 保存，浏览器**自动刷新**
# 4. 不到 1 秒看到新颜色！

# 5. 满意后，生产测试
./scripts/pre_push.sh
git push
```

---

### 例子 3：添加新的 Python 依赖

```bash
# 1. 修改 requirements.txt
echo "pandas==2.0.0" >> requirements.txt

# 2. 这次必须重新构建！
./scripts/dev.sh down
./scripts/dev.sh build
./scripts/dev.sh up

# 3. 或者直接运行生产测试
./scripts/pre_push.sh

# 4. 确认依赖安装成功后推送
git add requirements.txt
git commit -m "feat: add pandas dependency"
git push
```

---

## 🔍 关键问题解答

### Q: 热重载模式下，代码是在容器内还是容器外？

**A: 代码在容器外，通过 Docker Volume 挂载到容器内**

```yaml
volumes:
  - ./app:/app/app  # 本地 ./app 映射到容器 /app/app
```

```
你的本地目录：          容器内目录：
./app/api/auth.py  →  /app/app/api/auth.py
       ↑                      ↑
    修改这个              容器读取这个
```

---

### Q: 那镜像什么时候被构建？

**A: 两个时机**

1. **开发模式首次启动**：构建一次基础镜像
2. **每次推送到 GitHub**：CI/CD 完整构建

```bash
# 开发模式 - 只构建一次
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
# 后续修改代码不需要重新构建

# 生产测试 - 每次都构建
./scripts/pre_push.sh
# 每次都重新构建镜像
```

---

### Q: 本地通过了，推送后还会失败吗？

**A: 如果你推送前运行了 `./scripts/pre_push.sh`，几乎不会失败**

因为：
- ✅ 使用相同的 Dockerfile
- ✅ 使用相同的 docker-compose.yml
- ✅ 运行相同的健康检查
- ✅ EC2 只是换了个地方运行

**可能的例外：**
- 环境变量不同（EC2 的 .env 配置不同）
- 网络问题（RDS 连接、S3 权限）
- 资源不足（EC2 内存不够）

---

### Q: 我应该多久运行一次生产测试？

**A: 推荐策略：**

```
✅ 每次推送前必须运行
✅ 修改 Dockerfile/requirements.txt 后立即运行
✅ 重要功能完成后运行
✅ 一天开发结束前运行一次

❌ 不要每修改一行代码就运行（太慢）
```

---

## 📊 性能对比

| 操作 | 热重载模式 | 生产模式 |
|------|-----------|----------|
| 首次启动 | ~30 秒 | ~2-3 分钟 |
| 修改代码生效 | 2-3 秒 | 需重新构建（2-3分钟） |
| 适合场景 | 日常开发 | 推送前验证 |
| 使用频率 | 每天 N 次 | 推送前 1 次 |

---

## 🎓 最佳实践总结

### ✅ DO（推荐做法）

```bash
# 1. 早上启动热重载模式
./scripts/dev.sh up

# 2. 开发一整天，快速迭代

# 3. 下午提交前运行生产测试
./scripts/pre_push.sh

# 4. 测试通过后推送
git push

# 5. 晚上关闭开发环境
./scripts/dev.sh down
```

### ❌ DON'T（不推荐做法）

```bash
# ❌ 不要每次修改都重新构建
# 修改一行代码
docker compose build  # 太慢！

# ❌ 不要不测试就直接推送
git push  # 危险！可能线上炸了

# ❌ 不要在生产模式下开发
# 每次修改等 3 分钟重新构建  # 效率太低！
```

---

## 🚀 总结

**记住这个公式：**

```
日常开发 = 热重载（快）
推送验证 = 生产模式（慢但安全）

开发效率 + 部署安全 = 完美工作流 ✨
```

**一句话版本：**
> 开发时用热重载爽快迭代，推送前用生产模式保证质量！

---

需要帮助？查看完整文档：
- [本地开发详细指南](./LOCAL_DEVELOPMENT.md)
- [部署指南](./EC2_FIRST_DEPLOYMENT.md)
