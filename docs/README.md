# 文档索引

## 📚 完整文档列表

本目录包含 AI Job Matching 项目的所有运维和部署文档。

---

## 🚀 部署相关

### [GitHub Secrets 配置指南](./GITHUB_SECRETS_SETUP.md) ⭐ **开始这里**
**适用场景**: 首次配置 GitHub Actions CI/CD  
**内容**:
- 需要配置的 5 个 GitHub Secrets (EC2_SSH_KEY, EC2_HOST, EC2_USER, EC2_PROJECT_DIR, HEALTH_URL)
- 详细的获取和配置步骤
- Web UI 和 CLI 两种配置方式
- 常见问题和解决方案

### [EC2 首次部署指南](./EC2_FIRST_DEPLOYMENT.md)
**适用场景**: 第一次在 EC2 上部署项目  
**内容**:
- EC2 环境准备 (Docker, Docker Compose, Git)
- 安全组配置
- 环境变量 (.env) 设置
- 首次部署完整检查清单
- 部署后验证步骤

### [安全组配置说明](./SECURITY_GROUP_EXPLAINED.md)
**适用场景**: 配置 AWS EC2 安全组  
**内容**:
- 详细的端口配置 (22, 8000, 3000, 6379)
- 每个端口的作用和访问权限
- 安全最佳实践
- 常见错误和解决方案

---

## 🗄️ 数据库相关

### [Alembic 迁移指南](./ALEMBIC_MIGRATION_GUIDE.md)
**适用场景**: 修改数据库 schema 后需要迁移  
**内容**:
- 什么是 Alembic 数据库迁移
- 如何生成和应用迁移
- 本地和 EC2 的迁移步骤
- 常见问题 (表已存在、迁移冲突等)
- 回滚操作

### [首次数据库迁移设置](./FIRST_TIME_MIGRATION_SETUP.md)
**适用场景**: 全新项目首次创建数据库表  
**内容**:
- 为什么需要 Alembic
- 首次迁移的特殊步骤
- 从 init_db.py 迁移到 Alembic
- 详细的命令和解释

---

## 📖 快速参考

### FAQ (常见问题)
*即将推出*

**将包含**:
- 为什么安全组要开放这些端口?
- Alembic 和 init_db.py 的区别?
- 如何调试部署失败?
- Redis 连接问题?
- S3 配置问题?

---

## 📁 文档组织

```
docs/
├── README.md                          # 本文件 - 文档索引
├── GITHUB_SECRETS_SETUP.md            # GitHub Secrets 配置 (7.4KB)
├── EC2_FIRST_DEPLOYMENT.md            # EC2 部署指南 (待测量)
├── SECURITY_GROUP_EXPLAINED.md        # 安全组说明 (7.5KB)
├── ALEMBIC_MIGRATION_GUIDE.md         # 数据库迁移 (11.6KB)
└── FIRST_TIME_MIGRATION_SETUP.md      # 首次迁移 (11.6KB)
```

---

## 🎯 快速导航

### 我想...
- **首次部署到 EC2** → [GitHub Secrets](./GITHUB_SECRETS_SETUP.md) → [EC2 部署](./EC2_FIRST_DEPLOYMENT.md)
- **修改数据库结构** → [Alembic 指南](./ALEMBIC_MIGRATION_GUIDE.md)
- **解决安全组问题** → [安全组说明](./SECURITY_GROUP_EXPLAINED.md)
- **全新项目创建表** → [首次迁移](./FIRST_TIME_MIGRATION_SETUP.md)
- **配置 CI/CD** → [GitHub Secrets](./GITHUB_SECRETS_SETUP.md)

---

## 🔄 文档更新日志

- **2024-01-XX**: 新增 GitHub Secrets 配置指南
- **2024-01-XX**: 新增 EC2 首次部署指南
- **2024-01-XX**: 新增安全组配置说明
- **2024-01-XX**: 新增 Alembic 迁移指南
- **2024-01-XX**: 新增首次数据库迁移设置

---

## 📞 需要帮助?

- 查看各文档中的"常见问题"部分
- 检查 GitHub Actions 的日志输出
- 查看 EC2 上的 Docker 日志: `docker compose logs`
- 联系项目维护者

---

**提示**: 所有文档都包含详细的命令示例和故障排查步骤，建议完整阅读相关章节。
