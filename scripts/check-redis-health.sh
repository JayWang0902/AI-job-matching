#!/bin/bash
# Redis 健康监控脚本

REDIS_CONTAINER="ai-job-matching-redis-1"

echo "🔍 Redis Health Check"
echo "===================="

# 检查容器是否运行
if ! docker ps | grep -q $REDIS_CONTAINER; then
    echo "❌ Redis container is not running!"
    exit 1
fi

echo "✅ Redis container is running"

# 获取 Redis 信息
echo ""
echo "📊 Memory Usage:"
docker exec $REDIS_CONTAINER redis-cli INFO memory | grep -E "used_memory_human|used_memory_peak_human|maxmemory_human"

echo ""
echo "📈 Stats:"
docker exec $REDIS_CONTAINER redis-cli INFO stats | grep -E "total_connections_received|total_commands_processed|instantaneous_ops_per_sec"

echo ""
echo "🔑 Keyspace:"
docker exec $REDIS_CONTAINER redis-cli INFO keyspace

echo ""
echo "💾 Persistence:"
docker exec $REDIS_CONTAINER redis-cli INFO persistence | grep -E "aof_enabled|rdb_last_save_time|rdb_changes_since_last_save"

echo ""
echo "👥 Connected Clients:"
docker exec $REDIS_CONTAINER redis-cli INFO clients | grep -E "connected_clients|blocked_clients"

echo ""
echo "⚡ Test PING:"
PING_RESULT=$(docker exec $REDIS_CONTAINER redis-cli PING)
if [ "$PING_RESULT" = "PONG" ]; then
    echo "✅ Redis is responding (PONG)"
else
    echo "❌ Redis is not responding properly"
    exit 1
fi

echo ""
echo "✅ All checks passed!"
