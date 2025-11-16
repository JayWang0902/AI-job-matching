#!/bin/bash

# EC2 日志查看脚本
# Usage: ./scripts/view_logs.sh [service] [options]

EC2_IP="54.234.134.61"
KEY_PATH="./key.pem"
PROJECT_DIR="~/AI-job-matching"

SERVICE=${1:-""}
TAIL=${2:-100}

if [ -z "$SERVICE" ]; then
    echo "📊 Viewing all services logs..."
    ssh -i "$KEY_PATH" ubuntu@"$EC2_IP" "cd $PROJECT_DIR && docker compose logs --tail=$TAIL"
else
    echo "📊 Viewing $SERVICE logs..."
    ssh -i "$KEY_PATH" ubuntu@"$EC2_IP" "cd $PROJECT_DIR && docker compose logs --tail=$TAIL $SERVICE"
fi
