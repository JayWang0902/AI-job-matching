#!/bin/bash
# Docker 清理脚本 - 释放本地磁盘空间

set -e

echo "🧹 Docker 清理工具"
echo "=================="
echo ""

# 显示当前磁盘使用
echo "📊 当前 Docker 磁盘使用："
docker system df
echo ""

# 询问清理级别
echo "请选择清理级别："
echo "1) 轻度清理 - 删除悬空镜像和未使用的构建缓存"
echo "2) 中度清理 - 删除所有未使用的镜像和容器"
echo "3) 深度清理 - 删除所有停止的容器、未使用的镜像、网络和构建缓存"
echo "4) 保留最新 - 仅保留最新的 3 个版本的镜像"
echo "5) 取消"
echo ""
read -p "选择 (1-5): " choice

case $choice in
  1)
    echo ""
    echo "🔸 执行轻度清理..."
    echo "删除悬空镜像（<none> 标签）..."
    docker image prune -f
    echo "删除未使用的构建缓存..."
    docker builder prune -f
    ;;
  
  2)
    echo ""
    echo "🔸 执行中度清理..."
    echo "删除所有停止的容器..."
    docker container prune -f
    echo "删除所有未使用的镜像..."
    docker image prune -a -f
    echo "删除未使用的网络..."
    docker network prune -f
    ;;
  
  3)
    echo ""
    echo "🔸 执行深度清理..."
    read -p "⚠️  这将删除所有未使用的 Docker 资源，确认继续？(y/N): " confirm
    if [[ $confirm == [yY] ]]; then
      docker system prune -a -f --volumes
      echo "✅ 深度清理完成"
    else
      echo "❌ 已取消"
      exit 0
    fi
    ;;
  
  4)
    echo ""
    echo "🔸 保留最新 3 个版本..."
    
    # 保留最新的 backend 镜像
    echo "清理旧的 backend 镜像..."
    docker images "ghcr.io/jaywang0902/ai-job-matching-backend" --format "{{.ID}} {{.CreatedAt}}" | \
      sort -k2 -r | tail -n +4 | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true
    
    # 保留最新的 celery 镜像
    echo "清理旧的 celery 镜像..."
    docker images "ghcr.io/jaywang0902/ai-job-matching-celery" --format "{{.ID}} {{.CreatedAt}}" | \
      sort -k2 -r | tail -n +4 | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true
    
    # 保留最新的 frontend 镜像
    echo "清理旧的 frontend 镜像..."
    docker images "ghcr.io/jaywang0902/ai-job-matching-frontend" --format "{{.ID}} {{.CreatedAt}}" | \
      sort -k2 -r | tail -n +4 | awk '{print $1}' | xargs -r docker rmi -f 2>/dev/null || true
    
    # 清理悬空镜像
    docker image prune -f
    
    echo "✅ 已保留每个服务最新的 3 个版本"
    ;;
  
  5)
    echo "❌ 已取消清理"
    exit 0
    ;;
  
  *)
    echo "❌ 无效选择"
    exit 1
    ;;
esac

echo ""
echo "📊 清理后的磁盘使用："
docker system df
echo ""

# 计算释放的空间
echo "💾 可回收空间详情："
docker system df -v | grep -E "RECLAIMABLE|SIZE"

echo ""
echo "✅ 清理完成！"
echo ""
echo "💡 提示："
echo "   - 运行 'docker system df' 查看当前使用情况"
echo "   - 运行 'docker images' 查看所有镜像"
echo "   - 运行 'docker ps -a' 查看所有容器"
