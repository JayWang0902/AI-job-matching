#!/bin/bash

# Stop Development Environment

echo "🛑 Stopping development environment..."

docker compose -f docker-compose.yml -f docker-compose.dev.yml down

echo "✅ Development environment stopped"
echo ""
echo "💡 To remove volumes as well, run:"
echo "   docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v"
