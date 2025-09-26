#!/bin/bash
set -e

# 加载配置
source "$(dirname "$0")/.env"

echo "🔐 SSH into EC2 and stopping Docker services..."
ssh -i "$EC2_SSH_KEY_PATH" "$EC2_USER@$EC2_PUBLIC_IP" << EOF
  cd "$PROJECT_DIR"
  echo "🛑 Running docker compose down..."
  docker compose down
EOF

echo "🔴 Stopping EC2 instance..."
aws ec2 stop-instances --instance-ids "$EC2_INSTANCE_ID"
echo "✅ EC2 stop command sent."

echo "🟠 Stopping RDS instance..."
aws rds stop-db-instance --db-instance-identifier "$RDS_INSTANCE_ID"
echo "✅ RDS stop command sent."

echo "✅ All services stopped successfully!"
