# 数据库迁移指南

## 🎯 什么是 Alembic

Alembic 是 SQLAlchemy 的数据库迁移工具，用于管理数据库结构变化的版本控制。

**类比**: Git 管理代码版本，Alembic 管理数据库结构版本。

## 📋 工作原理

```
SQLAlchemy Models (代码)
    ↓
Alembic 生成迁移脚本
    ↓
应用到数据库
    ↓
数据库表结构创建/更新
```

## 🚀 首次部署

### ❓ 需要手动建表吗？

**答案: 不需要！** Alembic 会自动创建所有表。

### 完整流程

```bash
# 1. 部署代码到 EC2（GitHub Actions 自动完成）

# 2. SSH 到 EC2
ssh -i key.pem ubuntu@<EC2_IP>
cd ~/AI-job-matching

# 3. 运行迁移（创建所有表）
docker compose exec backend alembic upgrade head

# 输出示例：
# INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial
# INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_add_vectors
# ✅ 完成！所有表已创建
```

### 验证表已创建

```bash
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
print('Tables:', inspect(engine).get_table_names())
"

# 应该看到:
# Tables: ['users', 'resumes', 'jobs', 'job_matches', 'alembic_version']
```

## 🔄 开发流程

### 场景: 添加新字段

#### 1. 修改模型

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    phone_number = Column(String(20), nullable=True)  # ← 新字段
```

#### 2. 生成迁移脚本

```bash
# 本地开发环境
docker compose exec backend alembic revision --autogenerate -m "add phone number to users"

# 生成文件: alembic/versions/003_add_phone_number_to_users.py
```

生成的文件内容：
```python
def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone_number')
```

#### 3. 本地测试

```bash
# 应用迁移
docker compose exec backend alembic upgrade head

# 验证
docker compose exec backend python -c "
from app.models.user import User
print(User.__table__.columns.keys())
"
```

#### 4. 提交代码

```bash
git add app/models/user.py
git add alembic/versions/003_add_phone_number_to_users.py
git commit -m "feat: add phone number field to users"
git push origin main
```

#### 5. 部署并运行迁移

```bash
# GitHub Actions 自动部署代码

# SSH 到 EC2 运行迁移
ssh -i key.pem ubuntu@<EC2_IP>
cd ~/AI-job-matching
docker compose exec backend alembic upgrade head

# 输出:
# INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add phone number to users
# ✅ 完成！
```

## 📝 常用命令

### 查看迁移状态

```bash
# 查看当前版本
docker compose exec backend alembic current

# 查看迁移历史
docker compose exec backend alembic history

# 查看详细信息
docker compose exec backend alembic history --verbose
```

### 应用迁移

```bash
# 升级到最新版本
docker compose exec backend alembic upgrade head

# 升级一个版本
docker compose exec backend alembic upgrade +1

# 升级到指定版本
docker compose exec backend alembic upgrade <revision_id>
```

### 回滚迁移

```bash
# 回滚一个版本
docker compose exec backend alembic downgrade -1

# 回滚到指定版本
docker compose exec backend alembic downgrade <revision_id>

# 回滚所有
docker compose exec backend alembic downgrade base
```

### 生成迁移

```bash
# 自动检测变化生成迁移
docker compose exec backend alembic revision --autogenerate -m "description"

# 手动创建空迁移
docker compose exec backend alembic revision -m "description"
```

## 🎯 高级用法

### 数据迁移

修改数据而不只是结构：

```python
# alembic/versions/004_migrate_user_data.py
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

def downgrade():
    # 反向操作
    op.add_column('users', sa.Column('first_name', sa.String(100)))
    op.add_column('users', sa.Column('last_name', sa.String(100)))
    
    connection = op.get_bind()
    # 分割 full_name
    connection.execute("""
        UPDATE users 
        SET first_name = split_part(full_name, ' ', 1),
            last_name = split_part(full_name, ' ', 2)
    """)
    
    op.drop_column('users', 'full_name')
```

### 条件迁移

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 检查列是否存在
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'phone_number' not in columns:
        op.add_column('users', sa.Column('phone_number', sa.String(20)))
```

## ⚠️ 常见问题

### Q1: 表已存在怎么办？

**错误**: `relation "users" already exists`

**原因**: 之前手动创建了表

**解决**:
```bash
# 标记迁移为已应用（不实际运行）
docker compose exec backend alembic stamp head
```

### Q2: 迁移冲突

**错误**: `Can't locate revision identified by 'abc123'`

**原因**: 多人并行开发创建了相同序号的迁移

**解决**:
```bash
# 重命名冲突的迁移文件
mv alembic/versions/003_feature_b.py alembic/versions/004_feature_b.py

# 编辑文件，更新 revision 和 down_revision
# revision = '004'
# down_revision = '003'
```

### Q3: 如何检查哪些表会被创建？

```bash
# 查看迁移脚本
cat alembic/versions/001_initial.py

# 或在 Python 中检查
docker compose exec backend python -c "
from app.models import Base
for table in Base.metadata.sorted_tables:
    print(f'Table: {table.name}')
    for column in table.columns:
        print(f'  - {column.name}: {column.type}')
"
```

### Q4: 生产环境迁移出错怎么办？

```bash
# 1. 立即回滚
docker compose exec backend alembic downgrade -1

# 2. 重启服务
docker compose restart backend celery

# 3. 检查日志
docker compose logs backend

# 4. 修复迁移脚本，重新部署
```

## 📊 最佳实践

### 1. 迁移命名规范

```bash
# 好的命名
001_create_users_table
002_add_email_verification
003_create_jobs_table

# 差的命名
abc123_migration
update
```

### 2. 总是生成迁移

```bash
# ❌ 不要直接执行 SQL
psql -c "CREATE TABLE users (...)"

# ✅ 使用 Alembic
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

### 3. 测试迁移可逆性

```bash
# 应用迁移
alembic upgrade head

# 测试回滚
alembic downgrade -1

# 再次应用
alembic upgrade head
```

### 4. 生产环境前备份

```bash
# 备份数据库
pg_dump -h <RDS_ENDPOINT> -U user dbname > backup_$(date +%Y%m%d).sql

# 应用迁移
alembic upgrade head

# 如果出错，可以恢复
psql -h <RDS_ENDPOINT> -U user dbname < backup_YYYYMMDD.sql
```

### 5. 小步迭代

```bash
# ❌ 不要一次变更太多
# - 添加 10 个表
# - 修改 20 个字段
# - 迁移大量数据

# ✅ 分步进行
# 迁移 1: 添加新字段
# 迁移 2: 迁移数据
# 迁移 3: 删除旧字段
```

## 🔧 故障排查

### 检查迁移状态

```bash
# 数据库当前版本
docker compose exec backend alembic current

# 代码中的最新版本
ls -lt alembic/versions/ | head -5

# 比较差异
docker compose exec backend alembic history
```

### 查看迁移 SQL

```bash
# 预览将要执行的 SQL
docker compose exec backend alembic upgrade head --sql

# 预览回滚 SQL
docker compose exec backend alembic downgrade -1 --sql
```

### 手动修复

```bash
# 进入数据库
docker compose exec backend python

>>> from app.core.database import engine
>>> with engine.connect() as conn:
...     # 查看 alembic_version 表
...     result = conn.execute("SELECT * FROM alembic_version")
...     print(list(result))
...     
...     # 手动设置版本（谨慎！）
...     conn.execute("UPDATE alembic_version SET version_num = 'abc123'")
```

## 📚 相关文档

- [DEVELOPMENT.md](./DEVELOPMENT.md) - 本地开发
- [DEPLOYMENT.md](./DEPLOYMENT.md) - EC2 部署
- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
