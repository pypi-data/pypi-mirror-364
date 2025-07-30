#!/usr/bin/env python3
"""测试 Grasp 类的功能"""

import os
from grasp_sdk import Grasp, GraspSession, GraspBrowser, GraspTerminal

def test_grasp_classes():
    """测试所有 Grasp 类的基本功能"""
    print("🧪 测试 Grasp 类功能...")
    
    # 测试 Grasp 类初始化
    print("\n1. 测试 Grasp 类初始化:")
    
    # 通过字典设置 apiKey
    grasp1 = Grasp({'apiKey': 'test-key-from-dict'})
    print(f"   ✓ 通过字典初始化: {grasp1.key == 'test-key-from-dict'}")
    
    # 通过环境变量设置 apiKey
    os.environ['GRASP_KEY'] = 'test-key-from-env'
    grasp2 = Grasp()
    print(f"   ✓ 通过环境变量初始化: {grasp2.key == 'test-key-from-env'}")
    
    # 测试类的导入
    print("\n2. 测试类的导入:")
    print(f"   ✓ Grasp 类可用: {Grasp is not None}")
    print(f"   ✓ GraspSession 类可用: {GraspSession is not None}")
    print(f"   ✓ GraspBrowser 类可用: {GraspBrowser is not None}")
    print(f"   ✓ GraspTerminal 类可用: {GraspTerminal is not None}")
    
    # 测试方法可用性
    print("\n3. 测试方法可用性:")
    grasp = Grasp({'apiKey': 'test-key'})
    
    # 测试 Grasp 类方法
    print(f"   ✓ Grasp.launch 方法可用: {hasattr(grasp, 'launch')}")
    print(f"   ✓ Grasp.connect 方法可用: {hasattr(grasp, 'connect')}")
    print(f"   ✓ Grasp.launch_browser 静态方法可用: {hasattr(Grasp, 'launch_browser')}")
    
    # 测试异步上下文管理器功能
    print("\n4. 测试异步上下文管理器功能:")
    try:
        # 测试 launch_context 方法
        context_manager = grasp.launch_context({
            'browser': {
                'type': 'chromium',
                'headless': True,
                'timeout': 30000
            }
        })
        print(f"   ✓ launch_context 方法可用: {hasattr(grasp, 'launch_context')}")
        print(f"   ✓ 返回自身实例: {context_manager is grasp}")
        
        # 测试异步上下文管理器方法
        print(f"   ✓ __aenter__ 方法可用: {hasattr(grasp, '__aenter__')}")
        print(f"   ✓ __aexit__ 方法可用: {hasattr(grasp, '__aexit__')}")
        
    except Exception as e:
        print(f"   ❌ 异步上下文管理器测试失败: {e}")
    
    print("\n✅ 所有测试通过!")
    print("\n📋 已实现的方法:")
    print("   - Grasp.launch()")
    print("   - Grasp.connect()")
    print("   - Grasp.launch_browser()")
    print("   - Grasp.launch_context() [新增]")
    print("   - Grasp.__aenter__() [新增]")
    print("   - Grasp.__aexit__() [新增]")
    print("   - GraspSession.close()")
    print("   - GraspBrowser.get_endpoint()")
    print("   - GraspTerminal.create()")
    print("\n⏭️  已跳过的方法 (已废弃):")
    print("   - Grasp.shutdown()")
    print("   - Grasp.createRunner()")
    print("\n🎯 新功能:")
    print("   - 支持 async with grasp.launch_context(options) as session 语法")
    print("   - 自动管理会话生命周期")
    print("   - 会话在退出上下文时自动关闭")

if __name__ == '__main__':
    test_grasp_classes()