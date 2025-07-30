#!/usr/bin/env python3
"""测试 get_replay_screenshots 功能的示例脚本

这个脚本演示如何使用 get_replay_screenshots 函数获取截图目录路径。
"""

import asyncio
import os
from grasp_sdk import launch_browser, get_replay_screenshots


async def test_get_replay_screenshots():
    """测试 get_replay_screenshots 功能"""
    print("🚀 启动浏览器服务...")
    
    try:
        # 启动浏览器并获取连接信息
        connection = await launch_browser({
            'headless': True,
            'type': 'chromium'
        })
        
        print(f"✅ 浏览器启动成功!")
        print(f"连接 ID: {connection.id}")
        print(f"WebSocket URL: {connection.ws_url or connection.ws_url}")
        print(f"HTTP URL: {connection.http_url}")
        
        # 获取截图目录路径
        print("\n📸 获取截图目录路径...")
        screenshots_dir = await get_replay_screenshots(connection)
        
        print(f"✅ 截图目录路径: {screenshots_dir}")
        
        # 检查目录是否存在
        if os.path.exists(screenshots_dir):
            print(f"📁 目录已存在")
            
            # 列出目录中的文件
            files = os.listdir(screenshots_dir)
            if files:
                print(f"📋 目录中有 {len(files)} 个文件:")
                for file in files[:5]:  # 只显示前5个文件
                    print(f"  - {file}")
                if len(files) > 5:
                    print(f"  ... 还有 {len(files) - 5} 个文件")
            else:
                print("📂 目录为空")
        else:
            print(f"⚠️  目录不存在，将在首次使用时创建")
        
        # 测试错误处理
        print("\n🧪 测试错误处理...")
        
        # 测试缺少 id 字段的情况
        try:
            invalid_connection = {
                'ws_url': connection.ws_url,
                'http_url': connection.http_url
                # 缺少 'id' 字段
            }
            await get_replay_screenshots(invalid_connection)
        except ValueError as e:
            print(f"✅ 正确捕获 ValueError: {e}")
        
        # 测试无效 ID 的情况
        try:
            invalid_connection = {
                'id': 'invalid-id-123',
                'ws_url': connection.ws_url,
                'http_url': connection.http_url
            }
            await get_replay_screenshots(invalid_connection)
        except KeyError as e:
            print(f"✅ 正确捕获 KeyError: {e}")
        
        print("\n🎉 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    # 检查环境变量
    if not os.getenv('GRASP_KEY'):
        print("⚠️  警告: 未设置 GRASP_KEY 环境变量")
        print("请设置: export GRASP_KEY=your_api_key")
    
    # 运行测试
    asyncio.run(test_get_replay_screenshots())