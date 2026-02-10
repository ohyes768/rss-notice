#!/usr/bin/env python3
"""
本地测试脚本
测试RSS Notice Service的API接口
"""
import requests
import json
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8020"


def print_response(title: str, response: requests.Response):
    """打印响应结果"""
    print(f"\n{'='*60}")
    print(f"📌 {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容: {response.text}")


def test_health():
    """测试健康检查接口"""
    print("\n🏥 测试健康检查接口...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("健康检查", response)
    return response.status_code == 200


def test_check_rss():
    """测试RSS检查接口"""
    print("\n📰 测试RSS检查接口...")
    response = requests.get(f"{BASE_URL}/api/rss/check")
    print_response("RSS检查", response)

    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 检测到 {data['new_count']} 篇新文章")
        if data['new_count'] > 0:
            print("\n文章列表:")
            for i, article in enumerate(data['articles'], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   链接: {article['link']}")
                if article.get('published'):
                    print(f"   发布: {article['published']}")
                if article.get('author'):
                    print(f"   作者: {article['author']}")

    return response.status_code == 200


def test_refresh():
    """测试强制刷新接口"""
    print("\n🔄 测试强制刷新接口...")
    response = requests.post(f"{BASE_URL}/api/rss/refresh")
    print_response("强制刷新", response)
    return response.status_code == 200


def main():
    """主测试函数"""
    print("="*60)
    print("🚀 RSS Notice Service 本地测试")
    print("="*60)
    print(f"\n📍 API地址: {BASE_URL}")
    print("\n开始测试...")

    results = {}

    try:
        # 测试1: 健康检查
        results['健康检查'] = test_health()

        # 测试2: 检查新文章
        results['RSS检查'] = test_check_rss()

        # 测试3: 强制刷新
        results['强制刷新'] = test_refresh()

        # 打印测试结果汇总
        print("\n" + "="*60)
        print("📊 测试结果汇总")
        print("="*60)
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")

        all_passed = all(results.values())
        if all_passed:
            print("\n🎉 所有测试通过！")
        else:
            print("\n⚠️  部分测试失败，请检查日志")

    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败！请确保服务已启动:")
        print("   cd backend/rss_notice_service")
        print("   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8020")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")


if __name__ == "__main__":
    main()
