#!/bin/bash

# Pre-push validation script
# Run this before pushing to ensure everything works

set -e

echo "🧪 Running pre-push validation..."
echo "=================================="

# 1. Check if dev environment is running
if ! docker compose ps | grep -q "backend"; then
    echo "❌ Development environment is not running"
    echo "   Run ./scripts/dev_start.sh first"
    exit 1
fi

# 2. Test backend health
echo "✅ Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Backend is healthy"
else
    echo "   ✗ Backend health check failed"
    exit 1
fi

# 3. Test database connection
echo "✅ Testing database connection..."
if docker compose exec -T backend python -c "from app.core.database import engine; engine.connect()" 2>&1 | grep -q "Error"; then
    echo "   ✗ Database connection failed"
    exit 1
else
    echo "   ✓ Database connection successful"
fi

# 4. Check for migration status
echo "✅ Checking migration status..."
docker compose exec -T backend alembic current

# 5. Run Python linting (optional)
echo "✅ Checking Python code style..."
if command -v ruff &> /dev/null; then
    ruff check app/ || echo "   ⚠️  Linting warnings found (non-blocking)"
else
    echo "   ⚠️  ruff not installed, skipping lint check"
fi

# 6. Test frontend build
echo "✅ Testing frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✓ Frontend is accessible"
else
    echo "   ✗ Frontend is not accessible"
    exit 1
fi

echo ""
echo "✅ All validation checks passed!"
echo "🚀 Safe to push to production"
echo ""
