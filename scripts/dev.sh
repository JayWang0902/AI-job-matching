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
        echo "💡 Tip: Images are cached. First run builds, subsequent runs start fast."
        echo "   To force rebuild: ./scripts/dev.sh build"
        echo ""
        docker compose -f docker-compose.yml -f docker-compose.dev.yml up
        ;;
    
    down)
        echo "🛑 Stopping development environment..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml down
        echo "✅ All containers stopped and removed"
        ;;
    
    stop)
        echo "⏸️  Stopping containers (keeping them for quick restart)..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml stop
        echo "✅ Containers stopped (use './scripts/dev.sh up' to resume)"
        ;;
    
    clean)
        echo "🧹 Cleaning up dangling images and stopped containers..."
        docker compose -f docker-compose.yml -f docker-compose.dev.yml down
        echo "  Removing dangling images (tagged as <none>)..."
        docker image prune -f
        echo "  Removing unused build cache..."
        docker builder prune -f
        echo "✅ Cleanup complete!"
        echo ""
        echo "💾 Disk space saved:"
        docker system df
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
        echo "Usage: ./scripts/dev.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  up       - Start development environment (default)"
        echo "  down     - Stop and remove containers"
        echo "  stop     - Stop containers without removing (faster restart)"
        echo "  restart  - Restart all services"
        echo "  build    - Rebuild containers (only when dependencies change)"
        echo "  clean    - Clean up dangling images and cache"
        echo "  logs     - View logs (add service name for specific service)"
        echo "  shell    - Open shell in container (default: backend)"
        echo ""
        echo "Examples:"
        echo "  ./scripts/dev.sh              # Start dev environment"
        echo "  ./scripts/dev.sh logs backend # View backend logs"
        echo "  ./scripts/dev.sh clean        # Free up disk space"
        echo "  ./scripts/dev.sh down         # Stop and cleanup"
        exit 1
        ;;
esac
