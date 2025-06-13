#!/usr/bin/env python3
"""
用户系统测试脚本
测试注册、登录、JWT认证等功能
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

def test_user_system():
    print("🧪 开始测试用户系统...")
    
    # 测试数据
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print("\n1️⃣ 测试用户注册...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ 用户注册成功")
            user_data = response.json()
            print(f"   用户ID: {user_data['id']}")
            print(f"   用户名: {user_data['username']}")
            print(f"   邮箱: {user_data['email']}")
        else:
            print(f"❌ 用户注册失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return
    
    print("\n2️⃣ 测试用户登录...")
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ 用户登录成功")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   访问令牌: {access_token[:50]}...")
        else:
            print(f"❌ 用户登录失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return
    
    print("\n3️⃣ 测试受保护的路由...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ 受保护路由访问成功")
            user_info = response.json()
            print(f"   当前用户: {user_info['username']}")
            print(f"   用户状态: {'活跃' if user_info['is_active'] else '不活跃'}")
        else:
            print(f"❌ 受保护路由访问失败: {response.text}")
    except Exception as e:
        print(f"❌ 受保护路由请求失败: {e}")
    
    print("\n4️⃣ 测试简历上传（需要认证）...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        files = {"file": ("test_resume.pdf", b"fake pdf content", "application/pdf")}
        response = requests.post(f"{BASE_URL}/resume/upload", files=files, headers=headers)
        if response.status_code == 200:
            print("✅ 简历上传成功")
            upload_result = response.json()
            print(f"   上传用户: {upload_result['username']}")
        else:
            print(f"❌ 简历上传失败: {response.text}")
    except Exception as e:
        print(f"❌ 简历上传请求失败: {e}")
    
    print("\n🎉 用户系统测试完成!")

if __name__ == "__main__":
    test_user_system()