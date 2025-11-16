#!/bin/bash
# Monitor GitHub Container Registry usage

REGISTRY="ghcr.io"
IMAGE_PREFIX="jaywang0902/ai-job-matching"
SERVICES=("backend" "celery" "frontend")

echo "📊 Checking image storage usage..."
echo "===================================="

for service in "${SERVICES[@]}"; do
    echo ""
    echo "🔍 $service:"
    
    # List all tags for this image
    tags=$(docker images "${REGISTRY}/${IMAGE_PREFIX}-${service}" --format "{{.Tag}}" 2>/dev/null)
    count=$(echo "$tags" | wc -l)
    
    echo "   Versions: $count"
    
    # Estimate size (this requires pulling images, so commented out)
    # size=$(docker images "${REGISTRY}/${IMAGE_PREFIX}-${service}" --format "{{.Size}}" | head -1)
    # echo "   Size per version: ~$size"
done

echo ""
echo "===================================="
echo "💡 Tip: Run cleanup if you have more than 10 versions"
echo "   GitHub Actions: Manual trigger 'Cleanup Old Container Images'"
echo ""
echo "📦 View all packages:"
echo "   https://github.com/JayWang0902?tab=packages"
