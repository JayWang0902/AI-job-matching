#!/usr/bin/env python3
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

"""
初始化数据库脚本
只能用于初次设置数据库或在开发环境中使用。
更改表结构需先删除表再重新创建。
"""

def test_connection():
    """测试数据库连接"""
    try:
        from sqlalchemy import create_engine, text
        from app.core.config import settings
        
        DATABASE_URL = settings.DATABASE_URL
        print(f"尝试连接: {DATABASE_URL}")
        
        engine = create_engine(DATABASE_URL)
        
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
            return engine
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def create_tables(engine):
    """创建数据表"""
    try:
        from app.models.base import Base
        from app.models import user, job, job_match
        Base.metadata.create_all(bind=engine)
        print("✅ 数据表创建成功")
        return True
    except Exception as e:
        print(f"❌ 数据表创建失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    
    # 测试连接
    engine = test_connection()
    if not engine:
        print("❌ 数据库连接失败，请检查配置")
        sys.exit(1)
    
    # 创建表
    if create_tables(engine):
        print("🎉 数据库初始化完成!")
    else:
        print("❌ 数据库初始化失败")
        sys.exit(1)