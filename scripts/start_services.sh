#!/bin/bash
set -e

# 加载配置
source "$(dirname "$0")/.env"

echo "🔵 Starting EC2 instance..."
aws ec2 start-instances --instance-ids "$EC2_INSTANCE_ID"
echo "✅ EC2 start command sent."

echo "🟢 Starting RDS instance..."
aws rds start-db-instance --db-instance-identifier "$RDS_INSTANCE_ID"
echo "✅ RDS start command sent."

echo "⏳ Waiting for EC2 to be ready (sleeping 60s)..."
sleep 60

echo "🔐 SSH into EC2 and starting Docker services..."
ssh -i "$EC2_SSH_KEY_PATH" "$EC2_USER@$EC2_PUBLIC_IP" << EOF
  cd "$PROJECT_DIR"
  echo "🚀 Running docker compose up..."
  docker compose up -d
EOF

echo "✅ All services started successfully!"
