#!/bin/bash

# 🚀 完整的本地开发演示脚本
# 展示如何使用 Docker 进行高效开发

set -e

echo "======================================"
echo "🎯 AI Job Matching - 本地开发演示"
echo "======================================"
echo ""

# 步骤 1: 启动开发环境
echo "📦 步骤 1: 启动开发环境"
echo "命令: docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
echo ""
read -p "按 Enter 继续..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo ""
echo "✅ 开发环境已启动！"
echo ""

# 步骤 2: 查看服务状态
echo "📊 步骤 2: 查看服务状态"
echo "命令: docker compose -f docker-compose.yml -f docker-compose.dev.yml ps"
echo ""
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps

echo ""
read -p "按 Enter 继续..."

# 步骤 3: 查看日志
echo "📝 步骤 3: 查看 Backend 日志（最近 20 行）"
echo "命令: docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=20 backend"
echo ""
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs --tail=20 backend

echo ""
read -p "按 Enter 继续..."

# 步骤 4: 测试 API
echo "🧪 步骤 4: 测试 API 健康检查"
echo "命令: curl http://localhost:8000/health"
echo ""
sleep 2  # 等待服务完全启动
curl http://localhost:8000/health
echo ""

echo ""
echo "✅ API 正常运行！"
echo ""
read -p "按 Enter 继续..."

# 步骤 5: 演示热重载
echo "⚡️ 步骤 5: 代码热重载演示"
echo ""
echo "现在你可以："
echo "  1. 修改 app/main.py（例如添加一个新的 endpoint）"
echo "  2. 保存文件"
echo "  3. 1-2 秒后，uvicorn 自动重载"
echo "  4. 立即访问 http://localhost:8000/docs 查看变化"
echo ""
echo "查看实时日志："
echo "  docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend"
echo ""

read -p "按 Enter 继续..."

# 步骤 6: 开发工具
echo "🛠️  步骤 6: 开发工具"
echo ""
echo "可用命令："
echo ""
echo "  # 进入 Backend 容器"
echo "  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend bash"
echo ""
echo "  # 运行测试"
echo "  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend pytest"
echo ""
echo "  # 查看数据库"
echo "  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend python -c \"from app.core.database import engine; print(engine.url)\""
echo ""
echo "  # 运行 Alembic 迁移"
echo "  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head"
echo ""

read -p "按 Enter 继续..."

# 步骤 7: 推送前验证
echo "🔍 步骤 7: 推送前验证（模拟生产环境）"
echo ""
echo "停止开发环境..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml down

echo ""
echo "构建生产镜像..."
echo "命令: docker compose build"
echo ""
read -p "按 Enter 开始构建..."
docker compose build

echo ""
echo "✅ 镜像构建完成！"
echo ""
echo "启动生产模式（本地）..."
echo "命令: docker compose up -d"
echo ""
docker compose up -d

echo ""
echo "等待服务启动..."
sleep 5

echo ""
echo "测试生产环境..."
curl http://localhost:8000/health
echo ""

echo ""
echo "✅ 生产环境验证通过！"
echo ""

# 步骤 8: 清理
echo "🧹 步骤 8: 清理"
echo ""
echo "停止服务..."
docker compose down

echo ""
echo "======================================"
echo "✅ 演示完成！"
echo "======================================"
echo ""
echo "📚 开发流程总结："
echo ""
echo "1. 日常开发："
echo "   ./scripts/dev.sh"
echo "   修改代码 → 自动重载 → 立即看到效果"
echo ""
echo "2. 推送前验证："
echo "   docker compose build"
echo "   docker compose up -d"
echo "   测试通过 → git push"
echo ""
echo "3. 查看文档："
echo "   docs/WHY_DOCKER_DEVELOPMENT.md"
echo "   docs/LOCAL_DEVELOPMENT_GUIDE.md"
echo ""
