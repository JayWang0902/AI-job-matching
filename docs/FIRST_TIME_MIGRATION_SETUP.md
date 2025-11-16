# 🚀 首次部署生成迁移脚本指南

## 问题

你的项目目前 `alembic/versions/` 目录是空的，需要生成初始迁移脚本。

## 解决方案

### 方法 1: 在 EC2 首次部署后生成（推荐）

```bash
# 1. SSH 到 EC2
ssh -i key.pem ubuntu@your-ec2-ip

# 2. 进入项目目录
cd ~/AI-job-matching

# 3. 确保 backend 容器已启动
docker compose ps

# 4. 生成初始迁移脚本
docker compose exec backend alembic revision --autogenerate -m "Initial migration: create all tables"

# 输出：
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Generating /app/alembic/versions/abc123_initial_migration_create_all_tables.py ...  done

# 5. 查看生成的文件
docker compose exec backend ls -la alembic/versions/

# 6. 应用迁移（创建表）
docker compose exec backend alembic upgrade head

# 7. 提交到 Git（重要！）
git add alembic/versions/
git commit -m "feat: add initial database migration"
git push origin main
```

### 方法 2: 本地生成（如果你本地有 PostgreSQL）

```bash
# 1. 确保 .env 中的 DATABASE_URL 正确
# DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# 2. 激活虚拟环境
source ai-job-matching/bin/activate

# 3. 生成迁移
alembic revision --autogenerate -m "Initial migration: create all tables"

# 4. 查看生成的文件
ls -la alembic/versions/

# 5. 提交到 Git
git add alembic/versions/
git commit -m "feat: add initial database migration"
git push origin main
```

### 方法 3: 手动创建迁移脚本（备选）

如果自动生成失败，可以手动创建：

```bash
# 1. 创建空的迁移文件
docker compose exec backend alembic revision -m "Initial migration: create all tables"

# 2. 编辑生成的文件，添加表创建逻辑
# 文件位置: alembic/versions/xxxxx_initial_migration_create_all_tables.py
```

查看下一节的示例迁移脚本。

---

## 示例：初始迁移脚本

创建文件: `alembic/versions/001_initial_migration.py`

```python
"""Initial migration: create all tables

Revision ID: 001
Revises: 
Create Date: 2025-11-16 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
import uuid

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create resumes table
    op.create_table('resumes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(length=100), nullable=False, server_default='application/pdf'),
        sa.Column('s3_key', sa.String(length=500), nullable=False),
        sa.Column('s3_bucket', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('upload_progress', sa.Float(), server_default='0.0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('parsed_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('job_titles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('parsed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_id'), 'resumes', ['id'], unique=False)
    
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('job_type', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('posted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(length=10), nullable=True),
        sa.Column('skills_required', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('scraped_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source', 'external_id', name='uq_job_source_external_id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_source'), 'jobs', ['source'], unique=False)
    op.create_index(op.f('ix_jobs_external_id'), 'jobs', ['external_id'], unique=False)
    op.create_index('idx_jobs_embedding', 'jobs', ['embedding'], unique=False, postgresql_using='ivfflat', postgresql_ops={'embedding': 'vector_l2_ops'})
    
    # Create job_matches table
    op.create_table('job_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('ai_analysis', sa.Text(), nullable=True),
        sa.Column('matched_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('user_feedback', sa.String(length=50), nullable=True),
        sa.Column('is_applied', sa.Boolean(), server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'job_id', name='uq_user_job_match')
    )
    op.create_index(op.f('ix_job_matches_id'), 'job_matches', ['id'], unique=False)
    op.create_index(op.f('ix_job_matches_user_id'), 'job_matches', ['user_id'], unique=False)
    op.create_index(op.f('ix_job_matches_match_score'), 'job_matches', ['match_score'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_job_matches_match_score'), table_name='job_matches')
    op.drop_index(op.f('ix_job_matches_user_id'), table_name='job_matches')
    op.drop_index(op.f('ix_job_matches_id'), table_name='job_matches')
    op.drop_table('job_matches')
    
    op.drop_index('idx_jobs_embedding', table_name='jobs')
    op.drop_index(op.f('ix_jobs_external_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_source'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
    
    op.drop_index(op.f('ix_resumes_id'), table_name='resumes')
    op.drop_table('resumes')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    op.execute('DROP EXTENSION IF EXISTS vector')
```

---

## 部署后的首次迁移流程

### 完整步骤

```bash
# 1. 本地提交代码（包括迁移脚本）
git add alembic/versions/001_initial_migration.py
git commit -m "feat: add initial database migration"
git push origin main

# 2. GitHub Actions 自动部署到 EC2

# 3. SSH 到 EC2
ssh -i key.pem ubuntu@your-ec2-ip
cd ~/AI-job-matching

# 4. 检查容器状态
docker compose ps

# 5. 应用迁移（创建所有表）
docker compose exec backend alembic upgrade head

# 6. 验证表已创建
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"

# 应该看到:
# Tables: ['users', 'resumes', 'jobs', 'job_matches', 'alembic_version']
```

---

## 常见问题

### Q: 为什么 alembic/versions/ 是空的？

A: 因为还没有生成初始迁移。这是正常的，首次部署时需要生成。

### Q: 能否在本地生成后提交？

A: **可以**，但需要：
1. 本地有 PostgreSQL 数据库
2. `.env` 中的 `DATABASE_URL` 指向本地数据库
3. 安装了 `pgvector` 扩展

否则建议在 EC2 上生成。

### Q: 生成迁移后需要立即应用吗？

A: **首次生成后必须应用**，否则表不存在，应用无法运行。

### Q: 如何回滚迁移？

A: 
```bash
# 回滚到上一个版本
docker compose exec backend alembic downgrade -1

# 完全回滚
docker compose exec backend alembic downgrade base
```

---

## 后续开发流程

修改模型后：

```bash
# 1. 修改 app/models/*.py
# 2. 生成新的迁移
docker compose exec backend alembic revision --autogenerate -m "描述变更"
# 3. 提交代码
git add .
git commit -m "feat: 描述变更"
git push origin main
# 4. 部署到 EC2 后运行
docker compose exec backend alembic upgrade head
```

---

## 总结

1. ✅ 首次部署前/后需要生成初始迁移脚本
2. ✅ 可以在 EC2 上生成，或本地生成后提交
3. ✅ 生成后必须运行 `alembic upgrade head` 创建表
4. ❌ 不需要手动建表，Alembic 会自动创建
5. ✅ 后续开发时，修改模型后生成新的迁移脚本
