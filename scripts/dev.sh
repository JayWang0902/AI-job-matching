#!/bin/bash

# 本地开发环境启动脚本 - 支持热重载
# Usage: ./scripts/dev.sh [up|down|restart|logs]

set -e

ACTION=${1:-up}

echo "🚀 AI Job Matching - Local Development Mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 .env.local 是否存在
if [ ! -f .env.local ]; then
    echo "⚠️  .env.local not found. Creating from example..."
    if [ -f .env.local.example ]; then
        cp .env.local.example .env.local
        echo "✅ Created .env.local - Please update with your local settings"
        echo "📝 Edit .env.local before continuing"
        exit 1
    else
        echo "❌ .env.local.example not found!"
        exit 1
    fi
fi

case $ACTION in
    up)
        echo "📦 Starting development environment with hot reload..."
        echo "   - Backend will restart on Python file changes"
        echo "   - Frontend will use Next.js Fast Refresh"
        echo "   - Celery will auto-restart on changes"
        echo ""
        docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
        ;;
    
    down)
        echo "🛑 Stopping development environment..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml down
        ;;
    
    restart)
        echo "🔄 Restarting development environment..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml restart
        ;;
    
    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
        else
            docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f $SERVICE
        fi
        ;;
    
    build)
        echo "🔨 Rebuilding containers..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml build
        ;;
    
    shell)
        SERVICE=${2:-backend}
        echo "🐚 Opening shell in $SERVICE container..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml exec $SERVICE sh
        ;;
    
    *)
        echo "Usage: ./scripts/dev.sh [up|down|restart|logs|build|shell]"
        echo ""
        echo "Commands:"
        echo "  up       - Start development environment (default)"
        echo "  down     - Stop development environment"
        echo "  restart  - Restart all services"
        echo "  logs     - View logs (add service name for specific service)"
        echo "  build    - Rebuild containers"
        echo "  shell    - Open shell in container (default: backend)"
        exit 1
        ;;
esac
