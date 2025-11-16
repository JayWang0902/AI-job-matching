#!/bin/bash
# Redis 数据备份脚本

BACKUP_DIR="/home/ubuntu/redis-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="redis-backup-${TIMESTAMP}.rdb"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 触发 Redis BGSAVE
docker exec ai-job-matching-redis-1 redis-cli BGSAVE

# 等待备份完成
echo "⏳ Waiting for Redis to complete background save..."
sleep 5

# 复制 dump.rdb 到备份目录
docker cp ai-job-matching-redis-1:/data/dump.rdb "${BACKUP_DIR}/${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ Redis backup created: ${BACKUP_DIR}/${BACKUP_FILE}"
    
    # 只保留最近 7 天的备份
    find $BACKUP_DIR -name "redis-backup-*.rdb" -mtime +7 -delete
    echo "🧹 Cleaned up old backups (keeping last 7 days)"
else
    echo "❌ Redis backup failed!"
    exit 1
fi

# 显示备份大小
du -h "${BACKUP_DIR}/${BACKUP_FILE}"
