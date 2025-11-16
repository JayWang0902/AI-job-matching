# AWS ElastiCache Redis 配置指南

## 📋 推荐配置（基于你的应用场景）

### 1️⃣ 基本配置

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| **Engine** | Redis | Celery 标准消息代理 |
| **Version** | 7.1 | 最新稳定版 |
| **Port** | 6379 | 默认 Redis 端口 |
| **Region** | us-east-1 | 与你的 S3/EC2 保持一致 |

### 2️⃣ 集群配置

#### Cluster Mode (集群模式)
- **推荐**: **Disabled** ❌
- **原因**:
  - 你的 Celery 任务量不需要集群的水平扩展
  - 简化配置，降低成本
  - 单节点+副本足够应对日常负载
  - 未来可轻松升级到集群模式

### 3️⃣ 节点类型选择

#### 开发/测试环境（成本优化）
```
节点类型: cache.t4g.micro
├── vCPU: 2
├── Memory: 0.5 GB
├── Network Performance: 低到中等
├── 价格: ~$0.017/hour (~$12/月)
└── 适用场景: 开发测试，低流量
```

#### 生产环境（推荐）
```
节点类型: cache.t4g.small
├── vCPU: 2
├── Memory: 1.37 GB
├── Network Performance: 中等到高
├── 价格: ~$0.034/hour (~$25/月)
└── 适用场景: 中小型生产环境
```

#### 高性能生产环境
```
节点类型: cache.r7g.large
├── vCPU: 2
├── Memory: 13.07 GB
├── Network Performance: 高达 10 Gbps
├── 价格: ~$0.20/hour (~$146/月)
└── 适用场景: 高并发，大量任务
```

### 4️⃣ 高可用性配置

#### Number of Replicas (副本数量)
- **开发环境**: **0 replicas** (节省成本)
- **生产环境**: **1 replica** ✅ (强烈推荐)
  - 提供自动故障转移
  - 提高可用性到 99.99%
  - 成本翻倍但值得

#### Multi-AZ (多可用区)
- **开发环境**: Disabled
- **生产环境**: **Enabled** ✅
  - 自动故障转移
  - 主节点故障时自动切换到副本
  - 跨可用区部署，提高容错能力

### 5️⃣ 网络配置

#### VPC Configuration
```
1. 选择与 EC2 相同的 VPC
2. 创建 ElastiCache Subnet Group:
   名称: ai-job-matching-redis-subnet-group
   
3. 选择私有子网（不要用公有子网！）:
   - subnet-xxxxxx (us-east-1a) - 私有子网 1
   - subnet-yyyyyy (us-east-1b) - 私有子网 2
   
4. 如果启用 Multi-AZ，至少选择 2 个不同 AZ 的子网
```

#### Security Group
```
创建新的 Security Group: ai-job-matching-redis-sg

Inbound Rules:
┌─────────────────────────────────────────────────┐
│ Type        │ Protocol │ Port  │ Source          │
├─────────────────────────────────────────────────┤
│ Custom TCP  │ TCP      │ 6379  │ sg-xxxxxx       │
│             │          │       │ (EC2 Security   │
│             │          │       │  Group)         │
└─────────────────────────────────────────────────┘

Outbound Rules:
- 保持默认 (All traffic)
```

**使用脚本创建 Security Group:**
```bash
cd scripts
./create-elasticache-sg.sh
```

### 6️⃣ 安全配置

#### Encryption (加密)
- **Encryption at-rest**: **Enable** ✅
  - 选择: AWS managed key (aws/elasticache)
  - 无额外成本
  - 保护静态数据

- **Encryption in-transit**: **Enable** ✅
  - 启用 TLS
  - 客户端连接使用 SSL
  - 需要在连接字符串中添加 `?ssl_cert_reqs=required`

#### Authentication (身份验证)
- **AUTH token**: **Enable** ✅
  - ElastiCache 会生成一个强密码
  - 或者自己创建一个复杂密码
  - 密码要求:
    - 16-128 字符
    - 包含字母、数字、特殊字符
    - 不能包含 @, ", /

**密码管理最佳实践:**
```bash
# 选项 1: 使用 AWS Secrets Manager (推荐)
aws secretsmanager create-secret \
  --name ai-job-matching/redis/auth-token \
  --secret-string "your-generated-password" \
  --region us-east-1

# 选项 2: 存储在 .env 文件中
REDIS_PASSWORD=your-generated-password
```

### 7️⃣ 高级设置

#### Parameter Group
- **默认使用**: `default.redis7`
- **或创建自定义 Parameter Group** (如果需要调优)

**推荐的参数调整:**
```
Parameter Group: ai-job-matching-redis-params

关键参数:
├── maxmemory-policy: allkeys-lru
│   └── 内存满时，移除最近最少使用的 key
│   └── 适合 Celery 任务队列场景
│
├── timeout: 300
│   └── 客户端空闲 5 分钟后断开
│   └── 防止僵尸连接
│
├── tcp-keepalive: 300
│   └── 每 5 分钟发送 TCP keepalive
│   └── 保持长连接活跃
│
└── notify-keyspace-events: ""
    └── 默认禁用事件通知（节省资源）
```

#### Backup Configuration (备份)
```
开发环境:
├── Enable automatic backups: Yes
├── Retention period: 1 day
├── Backup window: 02:00-03:00 AM (低峰时段)
└── Final snapshot: 可选

生产环境:
├── Enable automatic backups: Yes
├── Retention period: 7 days
├── Backup window: 02:00-03:00 AM
└── Final snapshot: 创建 (删除集群时保留最后快照)
```

#### Maintenance Window (维护窗口)
```
推荐时间: Sun:03:00-Sun:04:00 (UTC)
├── 对应北京时间: 周日 11:00-12:00
├── 对应美东时间: 周六 22:00-23:00
└── 选择流量最低的时段
```

#### Logs (日志)
```
启用日志收集:
├── Slow log: Enable
│   └── Format: JSON
│   └── Destination: CloudWatch Logs
│   └── Log Group: /aws/elasticache/ai-job-matching/slow-log
│
└── Engine log: Enable
    └── Format: JSON
    └── Destination: CloudWatch Logs
    └── Log Group: /aws/elasticache/ai-job-matching/engine-log
```

### 8️⃣ 通知设置

#### SNS Topic Configuration
```bash
# 创建 SNS Topic
aws sns create-topic \
  --name elasticache-alerts \
  --region us-east-1

# 订阅邮箱
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:elasticache-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region us-east-1
```

**告警场景:**
- CPU 利用率高
- 内存使用率高
- 网络带宽使用高
- 节点故障
- 维护计划通知

---

## 🚀 创建步骤

### Step 1: 创建 Subnet Group

在 AWS Console:
1. 导航到: **ElastiCache → Subnet Groups → Create Subnet Group**
2. 填写:
   ```
   Name: ai-job-matching-redis-subnet-group
   Description: Subnet group for AI job matching Redis
   VPC: 选择你的 VPC (与 EC2 相同)
   Subnets: 选择至少 2 个私有子网（不同 AZ）
   ```
3. 点击 **Create**

### Step 2: 创建 Redis Cluster

在 AWS Console:
1. 导航到: **ElastiCache → Redis clusters → Create Redis cluster**
2. 填写配置:

**Cluster settings:**
```
Cluster mode: Disabled
Name: ai-job-matching-redis
Description: Redis for Celery and caching
Engine version: 7.1
Port: 6379
Parameter group: default.redis7 (或自定义)
Node type: cache.t4g.small (生产) / cache.t4g.micro (开发)
Number of replicas: 1 (生产) / 0 (开发)
Multi-AZ: Enabled (生产) / Disabled (开发)
```

**Connectivity:**
```
Network type: IPv4
Subnet group: ai-job-matching-redis-subnet-group
Security groups: ai-job-matching-redis-sg
```

**Security:**
```
Encryption at-rest: Enabled
Encryption key: (default) aws/elasticache
Encryption in-transit: Enabled
AUTH token: Enabled
Redis AUTH token: <自动生成或手动输入>
```

**Backup:**
```
Enable automatic backups: Yes
Retention period: 1 day (开发) / 7 days (生产)
Backup window: 02:00-03:00 AM
```

**Maintenance:**
```
Maintenance window: Sun:03:00-Sun:04:00
Topic for SNS notification: elasticache-alerts
```

**Logs:**
```
Slow log: Enabled → CloudWatch Logs
Engine log: Enabled → CloudWatch Logs
```

3. 点击 **Create**

### Step 3: 等待创建完成

```
创建时间: 约 10-15 分钟
状态: Creating → Available
```

在创建过程中，可以:
- 查看 CloudFormation 堆栈（如果使用）
- 准备更新应用配置
- 测试连接脚本

---

## 🔌 应用配置更新

### 1. 获取连接信息

创建完成后，在 ElastiCache Console 查看:
```
Primary endpoint: 
  xxx.cache.amazonaws.com:6379
  
Reader endpoint (如果有副本):
  xxx-ro.cache.amazonaws.com:6379
```

### 2. 更新 .env 文件

**无 AUTH token 的连接字符串:**
```bash
# 无加密
REDIS_URL=redis://your-endpoint.cache.amazonaws.com:6379/0

# 有 in-transit 加密
REDIS_URL=rediss://your-endpoint.cache.amazonaws.com:6379/0?ssl_cert_reqs=required
```

**有 AUTH token 的连接字符串:**
```bash
# 无加密
REDIS_URL=redis://:your-auth-token@your-endpoint.cache.amazonaws.com:6379/0

# 有 in-transit 加密 (推荐)
REDIS_URL=rediss://:your-auth-token@your-endpoint.cache.amazonaws.com:6379/0?ssl_cert_reqs=required
```

**完整示例 (.env):**
```properties
# Redis配置 (ElastiCache)
REDIS_URL=rediss://:AbCdEf123456@ai-job-matching-redis.abc123.0001.use1.cache.amazonaws.com:6379/0?ssl_cert_reqs=required

# 或者分开配置
REDIS_HOST=ai-job-matching-redis.abc123.0001.use1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=AbCdEf123456
REDIS_SSL=true
```

### 3. 测试连接

创建测试脚本:

```python
# scripts/test_elasticache_connection.py
import redis
import sys
from urllib.parse import urlparse

def test_redis_connection(redis_url: str):
    """测试 ElastiCache Redis 连接"""
    try:
        # 解析 Redis URL
        parsed = urlparse(redis_url)
        
        # 创建 Redis 客户端
        client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # 测试 PING
        print("🔗 Testing connection...")
        response = client.ping()
        print(f"✅ PING response: {response}")
        
        # 测试写入
        print("\n📝 Testing SET operation...")
        client.set("test_key", "hello_elasticache", ex=60)
        print("✅ SET operation successful")
        
        # 测试读取
        print("\n📖 Testing GET operation...")
        value = client.get("test_key")
        print(f"✅ GET operation successful: {value}")
        
        # 测试删除
        print("\n🗑️ Testing DEL operation...")
        client.delete("test_key")
        print("✅ DEL operation successful")
        
        # 获取服务器信息
        print("\n📊 Server Info:")
        info = client.info()
        print(f"  Redis Version: {info['redis_version']}")
        print(f"  Used Memory: {info['used_memory_human']}")
        print(f"  Connected Clients: {info['connected_clients']}")
        print(f"  Total Commands Processed: {info['total_commands_processed']}")
        
        print("\n✅ All tests passed! ElastiCache connection is working.")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("\nPossible issues:")
        print("1. Security Group not allowing traffic from your IP/EC2")
        print("2. Subnet Group configuration issue")
        print("3. AUTH token incorrect")
        print("4. SSL/TLS configuration mismatch")
        return False
    except redis.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("\nCheck your AUTH token in the REDIS_URL")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    redis_url = os.getenv("REDIS_URL")
    
    if not redis_url:
        print("❌ REDIS_URL not found in .env file")
        sys.exit(1)
    
    print(f"Testing Redis URL: {redis_url.split('@')[0]}@***")
    success = test_redis_connection(redis_url)
    sys.exit(0 if success else 1)
```

运行测试:
```bash
python scripts/test_elasticache_connection.py
```

### 4. 更新 docker-compose.yml (可选)

如果你在 Docker 环境中运行，不需要改动 docker-compose.yml，因为它已经通过 `.env` 文件读取 `REDIS_URL`。

只需确保 EC2 上的 `.env` 文件包含正确的 ElastiCache 连接信息。

---

## 📊 监控与告警

### CloudWatch Metrics

关键指标:
```
CPU Utilization:
├── 告警阈值: > 75% for 5 minutes
└── 建议: 升级节点类型

Memory Usage:
├── DatabaseMemoryUsagePercentage
├── 告警阈值: > 90%
└── 建议: 启用 eviction policy 或升级节点

Network:
├── NetworkBytesIn/Out
├── 告警阈值: 接近节点网络限制
└── 建议: 升级到更高网络性能的节点

Commands:
├── GetTypeCmds, SetTypeCmds
├── 监控读写比例
└── 优化应用查询模式

Connections:
├── CurrConnections
├── 告警阈值: > 65000 (接近 65535 限制)
└── 检查连接泄漏
```

### 创建 CloudWatch 告警

```bash
# CPU 告警
aws cloudwatch put-metric-alarm \
  --alarm-name elasticache-high-cpu \
  --alarm-description "ElastiCache CPU > 75%" \
  --metric-name CPUUtilization \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 75 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=CacheClusterId,Value=ai-job-matching-redis-001 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:elasticache-alerts

# 内存告警
aws cloudwatch put-metric-alarm \
  --alarm-name elasticache-high-memory \
  --alarm-description "ElastiCache Memory > 90%" \
  --metric-name DatabaseMemoryUsagePercentage \
  --namespace AWS/ElastiCache \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 90 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=CacheClusterId,Value=ai-job-matching-redis-001 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:elasticache-alerts
```

---

## 💰 成本估算

### 开发环境
```
配置: cache.t4g.micro + 0 replicas
├── 实例费用: $0.017/hour × 730 hours = $12.41/月
├── 备份存储: ~$0.5/月 (1 day retention)
├── 数据传输: 最小 (同 VPC 内免费)
└── 总计: ~$13/月
```

### 生产环境（推荐）
```
配置: cache.t4g.small + 1 replica (Multi-AZ)
├── 主节点: $0.034/hour × 730 hours = $24.82/月
├── 副本节点: $0.034/hour × 730 hours = $24.82/月
├── 备份存储: ~$2/月 (7 days retention)
├── 数据传输: ~$1-5/月 (跨 AZ 有费用)
└── 总计: ~$52-57/月
```

### 高性能生产环境
```
配置: cache.r7g.large + 1 replica (Multi-AZ)
├── 主节点: $0.20/hour × 730 hours = $146/月
├── 副本节点: $0.20/hour × 730 hours = $146/月
├── 备份存储: ~$5/月
├── 数据传输: ~$5-10/月
└── 总计: ~$302-307/月
```

**节省成本小贴士:**
1. 开发环境不使用副本
2. 使用 Reserved Instances (预留实例) 节省 30-40%
3. 定期清理不用的快照
4. 监控内存使用，选择合适的节点类型

---

## 🔧 性能优化建议

### 1. 连接池配置

更新 Celery 配置:
```python
# app/celery_app.py
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # 连接池配置
    broker_pool_limit=10,  # 最大连接数
    
    # Redis 特定配置
    redis_socket_keepalive=True,
    redis_socket_keepalive_options={
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 5,  # TCP_KEEPCNT
    },
    
    # 结果后端配置
    result_backend_transport_options={
        'master_name': 'mymaster',  # 如果使用 Sentinel
        'socket_keepalive': True,
        'socket_connect_timeout': 5,
        'socket_timeout': 5,
        'retry_on_timeout': True,
        'max_connections': 10,
    }
)
```

### 2. 任务优化

```python
# 设置任务过期时间，避免堆积
@celery_app.task(
    name='app.tasks.some_task',
    expires=3600,  # 1小时后过期
    time_limit=600,  # 10分钟超时
)
def some_task():
    pass
```

### 3. 监控脚本

```python
# scripts/monitor_redis_health.py
import redis
from app.core.config import settings

def check_redis_health():
    client = redis.from_url(settings.REDIS_URL)
    info = client.info()
    
    print("📊 Redis Health Check:")
    print(f"  Memory Used: {info['used_memory_human']} / {info.get('maxmemory_human', 'unlimited')}")
    print(f"  Memory Usage: {info.get('used_memory_rss_human', 'N/A')}")
    print(f"  Connected Clients: {info['connected_clients']}")
    print(f"  Blocked Clients: {info['blocked_clients']}")
    print(f"  Total Commands: {info['total_commands_processed']}")
    print(f"  Ops per Second: {info['instantaneous_ops_per_sec']}")
    print(f"  Keyspace Hits: {info['keyspace_hits']}")
    print(f"  Keyspace Misses: {info['keyspace_misses']}")
    
    if info['keyspace_hits'] + info['keyspace_misses'] > 0:
        hit_rate = info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
        print(f"  Cache Hit Rate: {hit_rate:.2%}")
    
    # 检查慢查询
    slowlog = client.slowlog_get(10)
    if slowlog:
        print("\n⚠️ Recent Slow Queries:")
        for entry in slowlog:
            print(f"    {entry['command'][:100]} - {entry['duration']}μs")

if __name__ == "__main__":
    check_redis_health()
```

---

## ❓ 常见问题

### Q1: 无法连接到 ElastiCache
**A:** 检查以下几点:
1. Security Group 是否允许来自 EC2 的 6379 端口访问
2. EC2 和 ElastiCache 是否在同一个 VPC
3. AUTH token 是否正确（如果启用了）
4. SSL/TLS 配置是否匹配（rediss:// vs redis://）

### Q2: 连接频繁断开
**A:** 
1. 增加 `timeout` 参数（Parameter Group）
2. 启用 TCP keepalive
3. 在应用中使用连接池
4. 检查网络稳定性

### Q3: 内存不足
**A:**
1. 检查 `maxmemory-policy` 设置
2. 升级到更大的节点类型
3. 清理过期的 key
4. 检查是否有内存泄漏

### Q4: 性能下降
**A:**
1. 查看 CloudWatch Metrics (CPU, Network)
2. 检查 Slow Log
3. 优化查询模式（减少大 key）
4. 考虑升级节点或启用集群模式

### Q5: 如何进行故障转移测试？
**A:**
```bash
# 在 ElastiCache Console 手动触发故障转移
# 或使用 AWS CLI
aws elasticache test-failover \
  --replication-group-id ai-job-matching-redis \
  --node-group-id 0001 \
  --region us-east-1
```

---

## 📚 下一步

1. ✅ 创建 ElastiCache Redis 集群
2. ✅ 更新 `.env` 配置文件
3. ✅ 运行连接测试脚本
4. ✅ 部署应用到 EC2
5. ✅ 配置 CloudWatch 告警
6. ✅ 监控性能指标
7. 🔄 定期检查备份和日志

**需要帮助？**
- [AWS ElastiCache 文档](https://docs.aws.amazon.com/elasticache/)
- [Redis 最佳实践](https://redis.io/docs/manual/patterns/)
- [Celery Redis 配置](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)
