#!/bin/bash

# Local Development Startup Script
# This script starts all services in development mode with hot reload

set -e

echo "🚀 Starting AI Job Matching - Development Mode"
echo "=============================================="

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ Error: .env.local not found"
    echo "📝 Please copy .env.local.example to .env.local and fill in your values:"
    echo "   cp .env.local.example .env.local"
    exit 1
fi

# Load local environment variables
export $(cat .env.local | grep -v '^#' | xargs)

echo "📦 Building development images..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml build

echo "🔧 Starting services in development mode..."
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "📊 Service URLs:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:3000"
echo "   Redis:        localhost:6379"
echo ""
echo "🔍 View logs:"
echo "   All services: docker compose logs -f"
echo "   Backend:      docker compose logs -f backend"
echo "   Frontend:     docker compose logs -f frontend"
echo "   Celery:       docker compose logs -f celery"
echo ""
echo "🛑 Stop services:"
echo "   docker compose -f docker-compose.yml -f docker-compose.dev.yml down"
echo ""
