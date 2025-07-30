#!/usr/bin/env python3
"""Grasp 异步上下文管理器使用示例"""

import asyncio
import os
from grasp_sdk import Grasp

async def example_with_context_manager():
    """使用异步上下文管理器的完整示例"""
    print("🚀 Grasp 异步上下文管理器使用示例")
    
    # 初始化 Grasp SDK
    grasp = Grasp({
        'apiKey': os.environ.get('GRASP_KEY', 'your-api-key-here')
    })
    
    try:
        # 使用异步上下文管理器启动会话
        print("\n📱 启动浏览器会话...")
        async with grasp.launch_context({
            'browser': {
                'type': 'chromium',
                'headless': True,
                'timeout': 30000
            }
        }) as session:
            print(f"✅ 会话已启动: {type(session).__name__}")
            
            # 访问浏览器
            print(f"🌐 浏览器端点: {session.browser.get_endpoint()}")
            
            # 创建终端
            print("💻 创建终端...")
            terminal = session.terminal.create()
            print(f"✅ 终端已创建: {type(terminal).__name__}")
            
            # 访问文件系统
            print(f"📁 文件系统可用: {type(session.files).__name__}")
            
            print("\n🔄 在这里可以进行各种操作...")
            print("   - 浏览器自动化")
            print("   - 终端命令执行")
            print("   - 文件系统操作")
            
            # 模拟一些工作
            await asyncio.sleep(0.1)
            
        # 会话会在这里自动关闭
        print("\n🔒 会话已自动关闭")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请确保设置了有效的 GRASP_KEY 环境变量")

async def example_multiple_sessions():
    """演示多个会话的使用"""
    print("\n\n🔄 多会话使用示例")
    
    grasp = Grasp({
        'apiKey': os.environ.get('GRASP_KEY', 'your-api-key-here')
    })
    
    try:
        # 第一个会话
        print("\n📱 启动第一个会话...")
        async with grasp.launch_context({
            'browser': {'type': 'chromium', 'headless': True}
        }) as session1:
            print("✅ 第一个会话已启动")
            await asyncio.sleep(0.1)
        
        print("🔒 第一个会话已关闭")
        
        # 第二个会话
        print("\n📱 启动第二个会话...")
        async with grasp.launch_context({
            'browser': {'type': 'chromium', 'headless': False}
        }) as session2:
            print("✅ 第二个会话已启动")
            await asyncio.sleep(0.1)
        
        print("🔒 第二个会话已关闭")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

async def example_error_handling():
    """演示错误处理"""
    print("\n\n⚠️  错误处理示例")
    
    grasp = Grasp({'apiKey': 'test-key'})
    
    # 尝试重复使用同一个实例
    try:
        grasp.launch_context({'browser': {'type': 'chromium'}})
        
        async with grasp as session1:
            print("第一个会话启动")
            # 尝试在已有会话时启动新会话
            async with grasp.launch_context({'browser': {'type': 'firefox'}}) as session2:
                print("这不应该被执行")
                
    except RuntimeError as e:
        print(f"✅ 正确捕获错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

async def main():
    """主函数"""
    await example_with_context_manager()
    await example_multiple_sessions()
    await example_error_handling()
    
    print("\n\n📚 总结:")
    print("✅ 异步上下文管理器已成功实现")
    print("✅ 支持 async with grasp.launch_context(options) as session 语法")
    print("✅ 自动管理会话生命周期")
    print("✅ 提供适当的错误处理")
    print("\n🎉 所有功能测试完成!")

if __name__ == '__main__':
    asyncio.run(main())