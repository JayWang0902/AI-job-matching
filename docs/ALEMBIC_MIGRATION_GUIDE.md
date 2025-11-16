# 🗄️ 数据库迁移（Alembic）完全指南

## 什么是数据库迁移？

**数据库迁移** = 管理数据库结构（表、列、索引等）变化的版本控制系统

类比：
- Git 管理代码版本
- Alembic 管理数据库结构版本

---

## Alembic 工作原理

### 基本概念

```
代码中的模型 (SQLAlchemy Models)
    ↓
Alembic 生成迁移脚本
    ↓
应用到数据库 (PostgreSQL)
    ↓
数据库表结构创建/更新
```

### 迁移脚本示例

```python
# alembic/versions/001_create_users_table.py
def upgrade():
    """应用这个迁移时执行"""
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True),
        sa.Column('hashed_password', sa.String(255)),
        sa.Column('created_at', sa.DateTime())
    )

def downgrade():
    """回滚这个迁移时执行"""
    op.drop_table('users')
```

---

## 你的项目中的情况

### 现有的迁移脚本

让我检查你的项目：

```bash
# 查看现有迁移
ls -la alembic/versions/
```

你应该已经有这些迁移脚本（根据你的模型）：
- 创建 `users` 表
- 创建 `resumes` 表
- 创建 `jobs` 表
- 创建 `job_matches` 表
- 添加 pgvector 扩展
- 创建向量索引

---

## 首次部署流程

### ❓ 需要手动建表吗？

**答案: 不需要！** Alembic 会帮你创建所有表。

### 完整的首次部署流程

#### 1️⃣ 部署前（代码已准备好）

```bash
# 你的项目已经有这些文件：
alembic/
  ├── env.py                    # Alembic 配置
  ├── versions/                 # 迁移脚本文件夹
  │   ├── 001_initial.py       # 第一个迁移（创建所有表）
  │   ├── 002_add_vectors.py   # 添加向量支持（如果有）
  │   └── ...
  └── script.py.mako
```

#### 2️⃣ 首次部署到 EC2

```bash
# GitHub Actions 会自动：
1. 构建镜像
2. 推送到 ghcr.io
3. SSH 到 EC2
4. docker compose pull
5. docker compose up -d

# 此时容器启动，但数据库表还不存在！
```

#### 3️⃣ 运行数据库迁移（首次必须手动）

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@your-ec2-ip

# 进入项目目录
cd ~/AI-job-matching

# 运行迁移（创建所有表）
docker compose exec backend alembic upgrade head

# 输出示例：
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial, Create initial tables
# INFO  [alembic.runtime.migration] Running upgrade 001_initial -> 002_add_vectors, Add vector support
# ✅ 完成！所有表已创建
```

### 这个命令的含义

```bash
docker compose exec backend alembic upgrade head
│                  │         │       │        │
│                  │         │       │        └─ 目标版本（head = 最新）
│                  │         │       └────────── 升级到指定版本
│                  │         └────────────────── Alembic 命令
│                  └──────────────────────────── backend 容器
└─────────────────────────────────────────────── Docker Compose 执行命令
```

**等价于在容器内运行**:
```bash
# 如果你进入容器内部
docker compose exec backend bash
alembic upgrade head
```

---

## 后续开发中的迁移流程

### 场景：添加新字段

假设你要给 `users` 表添加一个 `phone_number` 字段：

#### 1️⃣ 修改 SQLAlchemy 模型

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(String(255))
    phone_number = Column(String(20), nullable=True)  # ← 新字段
```

#### 2️⃣ 生成迁移脚本

```bash
# 本地开发环境
docker compose exec backend alembic revision --autogenerate -m "add phone number to users"

# Alembic 会自动检测变化，生成新的迁移文件：
# alembic/versions/003_add_phone_number_to_users.py
```

生成的文件内容：
```python
def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone_number')
```

#### 3️⃣ 提交代码

```bash
git add app/models/user.py
git add alembic/versions/003_add_phone_number_to_users.py
git commit -m "feat: add phone number field to users"
git push origin main
```

#### 4️⃣ 部署到 EC2

```bash
# GitHub Actions 自动部署新代码
# 但此时数据库表还没更新！
```

#### 5️⃣ 运行迁移（更新表结构）

```bash
# SSH 到 EC2
ssh -i key.pem ubuntu@your-ec2-ip
cd ~/AI-job-matching

# 应用新的迁移
docker compose exec backend alembic upgrade head

# 输出：
# INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add phone number to users
# ✅ 完成！phone_number 字段已添加
```

---

## ❓ 每次 Workflow 都需要运行 Alembic 吗？

### 答案：不是自动的，但可以自动化

### 当前流程（手动）

```yaml
# .github/workflows/deploy.yml (当前)
- name: Deploy to EC2
  run: |
    docker compose pull
    docker compose up -d
    # ❌ 没有运行 alembic upgrade head
```

**问题**: 每次部署后需要手动 SSH 到 EC2 运行迁移

### 推荐流程（自动化）

我可以更新 workflow 让它自动运行迁移：

```yaml
# .github/workflows/deploy.yml (改进版)
- name: Deploy to EC2
  run: |
    docker compose pull
    docker compose up -d
    
    # 等待 backend 启动
    sleep 10
    
    # 自动运行数据库迁移
    docker compose exec -T backend alembic upgrade head
```

---

## 迁移的版本控制

### 迁移历史追踪

```bash
# 查看当前数据库版本
docker compose exec backend alembic current

# 输出：
# 003_add_phone_number_to_users (head)

# 查看迁移历史
docker compose exec backend alembic history

# 输出：
# 001 -> 002 (head), Create initial tables
# 002 -> 003, Add vector support
# 003 (head), add phone number to users
```

### 回滚迁移（如果出错）

```bash
# 回滚到上一个版本
docker compose exec backend alembic downgrade -1

# 回滚到特定版本
docker compose exec backend alembic downgrade 002

# 回滚所有
docker compose exec backend alembic downgrade base
```

---

## 常见问题

### Q1: 首次部署时忘记运行迁移会怎样？

**A**: 应用会报错，因为表不存在

```bash
# Backend 日志会显示：
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) 
relation "users" does not exist
```

**解决方法**:
```bash
docker compose exec backend alembic upgrade head
docker compose restart backend celery
```

### Q2: 如何检查表是否已创建？

```bash
# 方法 1: 连接到 RDS
psql -h your-rds-endpoint -U username -d jobmatcherdb

# 查看所有表
\dt

# 应该看到：
#  public | users       | table | jobmatcher
#  public | resumes     | table | jobmatcher
#  public | jobs        | table | jobmatcher
#  public | job_matches | table | jobmatcher
#  public | alembic_version | table | jobmatcher  ← 迁移版本追踪表

# 方法 2: 在容器内检查
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print(inspector.get_table_names())
"
```

### Q3: 生产环境和开发环境的数据库不同怎么办？

**A**: Alembic 迁移脚本是通用的，同一个脚本可以：
- 本地 SQLite 数据库
- 本地 PostgreSQL 数据库
- EC2 上的 RDS PostgreSQL 数据库

### Q4: 如何处理数据迁移（不只是结构）？

```python
# 例如：重命名字段并迁移数据
def upgrade():
    # 1. 添加新字段
    op.add_column('users', sa.Column('full_name', sa.String(255)))
    
    # 2. 迁移数据
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = first_name || ' ' || last_name"
    )
    
    # 3. 删除旧字段
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
```

### Q5: 多人协作时如何避免迁移冲突？

**A**: 使用分支合并策略
```bash
# 团队成员 A 创建了迁移 003
# 团队成员 B 创建了迁移 003（冲突！）

# 合并时手动重命名
git mv alembic/versions/003_feature_b.py alembic/versions/004_feature_b.py

# 或使用 Alembic 的依赖系统
```

---

## 最佳实践

### 1. 迁移脚本命名规范

```bash
✅ 好的命名:
001_create_users_table.py
002_add_email_verification.py
003_create_jobs_table.py

❌ 差的命名:
abc123_migration.py
update.py
```

### 2. 总是生成迁移而不是手动创建表

```bash
❌ 不要这样做:
# 直接在数据库执行 SQL
psql -c "CREATE TABLE users (...)"

✅ 应该这样:
# 使用 Alembic 生成和应用迁移
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

### 3. 在应用迁移前先备份数据库

```bash
# 生产环境应用迁移前
pg_dump -h rds-endpoint -U username dbname > backup_before_migration.sql

# 然后应用迁移
docker compose exec backend alembic upgrade head

# 如果出错，可以恢复
psql -h rds-endpoint -U username dbname < backup_before_migration.sql
```

### 4. 测试迁移的可逆性

```bash
# 应用迁移
alembic upgrade head

# 测试回滚
alembic downgrade -1

# 再次应用
alembic upgrade head
```

---

## 自动化迁移（可选）

### 更新 GitHub Actions Workflow

让我帮你更新 workflow 让它自动运行迁移：

```yaml
- name: Run Database Migration
  env:
    HOST: ${{ secrets.EC2_HOST }}
    USER: ${{ secrets.EC2_USER }}
    PROJECT_DIR: ${{ secrets.EC2_PROJECT_DIR }}
  run: |
    ssh ${USER}@${HOST} << 'EOF'
      cd ${PROJECT_DIR}
      
      # 等待 backend 容器健康
      timeout 60 bash -c 'until docker compose exec -T backend curl -f http://localhost:8000/health; do sleep 2; done'
      
      # 运行数据库迁移
      echo "==> Running database migrations"
      docker compose exec -T backend alembic upgrade head
      
      # 验证迁移成功
      docker compose exec -T backend alembic current
    EOF
```

---

## 快速参考

| 命令 | 用途 | 何时使用 |
|------|------|---------|
| `alembic upgrade head` | 应用所有未应用的迁移 | 首次部署、每次更新数据库结构 |
| `alembic current` | 查看当前数据库版本 | 检查迁移状态 |
| `alembic history` | 查看所有迁移历史 | 了解变更历史 |
| `alembic downgrade -1` | 回滚最后一次迁移 | 迁移出错需要回滚 |
| `alembic revision --autogenerate -m "..."` | 生成新的迁移脚本 | 修改模型后生成迁移 |

---

## 总结

### 首次部署流程

1. ✅ 代码中已有迁移脚本（在 `alembic/versions/`）
2. ✅ GitHub Actions 部署代码和容器
3. ⚠️ **手动 SSH 到 EC2 运行**: `docker compose exec backend alembic upgrade head`
4. ✅ 表结构创建完成

### 后续开发流程

1. 修改模型 → 生成迁移脚本 → 提交到 Git
2. 推送代码 → GitHub Actions 自动部署
3. SSH 到 EC2 → 运行 `alembic upgrade head`（或自动化）
4. 数据库结构更新完成

### 关键点

- ❌ 不需要手动建表
- ✅ Alembic 自动管理表结构
- ⚠️ 首次部署和每次结构变更后都需要运行 `alembic upgrade head`
- 💡 可以通过更新 GitHub Actions 实现自动化迁移
