#!/usr/bin/env python3
"""
数据库初始化脚本
运行此脚本来创建数据库表
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import create_tables

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")