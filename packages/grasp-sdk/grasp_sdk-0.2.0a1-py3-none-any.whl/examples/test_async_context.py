#!/usr/bin/env python3
"""测试 Grasp 异步上下文管理器功能"""

import asyncio
import os
from grasp_sdk import Grasp

async def test_async_context_manager():
    """测试异步上下文管理器功能"""
    print("测试 Grasp 异步上下文管理器...")
    
    # 初始化 Grasp SDK
    grasp = Grasp({'apiKey': 'test-key'})
    
    # 测试 launch_context 方法
    print("\n1. 测试 launch_context 方法:")
    context_manager = grasp.launch_context({
        'browser': {
            'type': 'chromium',
            'headless': True,
            'timeout': 30000
        }
    })
    print(f"   ✓ launch_context 返回类型: {type(context_manager).__name__}")
    print(f"   ✓ 是否为同一实例: {context_manager is grasp}")
    
    # 测试异步上下文管理器方法存在性
    print("\n2. 测试异步上下文管理器方法:")
    print(f"   ✓ 具有 __aenter__ 方法: {hasattr(grasp, '__aenter__')}")
    print(f"   ✓ 具有 __aexit__ 方法: {hasattr(grasp, '__aexit__')}")
    
    # 测试错误情况
    print("\n3. 测试错误处理:")
    try:
        # 尝试在没有设置 launch_options 的情况下使用上下文管理器
        fresh_grasp = Grasp({'apiKey': 'test-key'})
        async with fresh_grasp as session:
            pass
    except RuntimeError as e:
        print(f"   ✓ 正确捕获错误: {e}")
    
    # 模拟使用异步上下文管理器的语法（不实际连接）
    print("\n4. 异步上下文管理器语法示例:")
    print("   代码示例:")
    print("   async with grasp.launch_context({")
    print("       'browser': {")
    print("           'type': 'chromium',")
    print("           'headless': True,")
    print("           'timeout': 30000")
    print("       }")
    print("   }) as session:")
    print("       # 使用 session 进行操作")
    print("       browser = session.browser")
    print("       terminal = session.terminal")
    print("       files = session.files")
    
    print("\n✅ 异步上下文管理器功能测试完成!")
    print("\n📝 使用说明:")
    print("   - 使用 grasp.launch_context(options) 设置启动选项")
    print("   - 然后使用 async with 语法自动管理会话生命周期")
    print("   - 会话将在退出上下文时自动关闭")

if __name__ == '__main__':
    asyncio.run(test_async_context_manager())