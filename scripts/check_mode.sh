#!/bin/bash

# 检查当前运行的是开发模式还是生产模式

echo "🔍 Checking Docker Compose Mode..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查是否有容器在运行
RUNNING=$(docker compose ps -q 2>/dev/null | wc -l | tr -d ' ')

if [ "$RUNNING" -eq 0 ]; then
    echo "❌ No containers are running"
    echo ""
    echo "Start with:"
    echo "  Development: ./scripts/dev.sh"
    echo "  Production:  docker compose up -d"
    exit 0
fi

echo ""
echo "📊 Running Containers:"
docker compose ps --format "table {{.Name}}\t{{.Image}}\t{{.Status}}" 2>/dev/null

echo ""
echo "🔎 Mode Detection:"

# 检查镜像标签
DEV_IMAGES=$(docker compose ps --format "{{.Image}}" 2>/dev/null | grep -c ":dev" || true)

if [ "$DEV_IMAGES" -gt 0 ]; then
    echo "✅ Running in DEVELOPMENT mode (:dev tag detected)"
    echo ""
    echo "Characteristics:"
    echo "  - Using local images (ai-job-matching-*:dev)"
    echo "  - Hot reload enabled (code changes reflect immediately)"
    echo "  - Reading from .env.local"
    echo "  - DEBUG=true, ENV=development"
    echo ""
    echo "Stop with: ./scripts/dev.sh down"
else
    echo "🚀 Running in PRODUCTION mode"
    echo ""
    echo "Characteristics:"
    echo "  - Using registry images (ghcr.io/...)"
    echo "  - No hot reload (rebuild needed for changes)"
    echo "  - Reading from .env"
    echo "  - DEBUG=false, ENV=production"
    echo ""
    echo "Stop with: docker compose down"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 显示环境变量（可选）
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    echo ""
    echo "📋 Backend Environment Variables:"
    docker compose exec backend printenv | grep -E "ENV=|DEBUG=|DATABASE_URL=|OPENAI_API_KEY=" | sort
fi
