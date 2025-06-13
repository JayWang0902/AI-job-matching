# AI Job Matching - 用户系统使用说明

## 系统概览

我已经为你实现了一个完整的用户认证系统，包含以下功能：

### ✅ 已实现功能

1. **用户注册/登录**
   - 用户注册（用户名、邮箱、密码）
   - 用户登录（JWT Token认证）
   - 密码安全哈希存储（bcrypt）

2. **JWT 鉴权系统**
   - 访问令牌生成和验证
   - 30分钟过期时间（可配置）
   - Bearer Token 认证

3. **数据库设计**
   - User 表：id, username, email, hashed_password, is_active, created_at, last_active_at
   - SQLite 数据库（可通过环境变量配置其他数据库）

4. **身份保护**
   - 受保护的API路由
   - 自动用户认证中间件
   - 活跃用户验证

5. **错误处理**
   - 完整的HTTP状态码
   - 详细的错误信息
   - 输入验证

## 🚀 快速开始

### 1. 启动服务器
```bash
cd /Users/jaywang/Desktop/GoValley/AI-job-matching
uvicorn app.main:app --reload
```

### 2. 访问API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. API 端点

#### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户信息
- `PUT /auth/me` - 更新用户活跃时间
- `POST /auth/logout` - 用户登出
- `GET /auth/protected` - 受保护路由示例

#### 简历相关（需要认证）
- `POST /resume/upload` - 上传简历
- `GET /resume/` - 获取用户简历列表

## 📝 使用示例

### 1. 用户注册
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

### 3. 访问受保护的路由
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 上传简历
```bash
curl -X POST "http://localhost:8000/resume/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@resume.pdf"
```

## 🔧 配置说明

### 环境变量 (.env)
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./ai_job_matching.db
DEBUG=True
APP_NAME=AI Job Matching API
```

### 数据库初始化
```bash
python init_db.py
```

## 🧪 测试系统

运行测试脚本验证系统功能：
```bash
pip install requests  # 如果没有安装
python test_user_system.py
```

## 🛡️ 安全特性

1. **密码安全**
   - bcrypt 哈希算法
   - 盐值自动生成
   - 明文密码永不存储

2. **JWT 安全**
   - 签名验证
   - 过期时间控制
   - Bearer Token 标准

3. **数据验证**
   - Pydantic 模型验证
   - 邮箱格式验证
   - 用户名唯一性检查

## 📁 项目结构

```
app/
├── main.py                 # 主应用入口
├── api/
│   ├── auth.py            # 认证相关API
│   └── resume.py          # 简历相关API
├── core/
│   ├── database.py        # 数据库配置
│   └── auth_deps.py       # 认证依赖
├── models/
│   └── user.py            # 用户数据模型
├── schemas/
│   └── user.py            # Pydantic 模型
└── services/
    └── auth_service.py    # 认证服务逻辑
```

## 🔄 下一步开发建议

1. **简历管理功能**
   - 简历文件存储
   - 简历内容解析
   - 简历版本管理

2. **职位匹配功能**
   - 职位数据模型
   - AI匹配算法
   - 推荐系统

3. **用户权限系统**
   - 角色管理
   - 权限控制
   - 管理员功能

4. **生产环境优化**
   - PostgreSQL 数据库
   - Redis 缓存
   - Docker 部署
   - 日志系统

## 🚨 生产环境注意事项

1. 修改 `.env` 文件中的 `SECRET_KEY`
2. 使用 PostgreSQL 或 MySQL 替代 SQLite
3. 配置 HTTPS
4. 设置合适的 CORS 域名
5. 添加请求限制和监控

---

用户系统已完成！🎉 可以开始测试和开发其他功能了。