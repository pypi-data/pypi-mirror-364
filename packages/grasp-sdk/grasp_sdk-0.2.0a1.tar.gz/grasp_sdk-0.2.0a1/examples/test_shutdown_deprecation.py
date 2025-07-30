#!/usr/bin/env python3
"""
测试 shutdown 方法的废弃警告
"""

import warnings
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grasp_sdk import shutdown

def test_shutdown_deprecation():
    """测试 shutdown 方法是否正确发出废弃警告"""
    print("🧪 测试 shutdown 方法的废弃警告...")
    
    # 设置警告过滤器显示所有警告
    warnings.filterwarnings("always")
    
    # 捕获警告
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        print("📞 调用 shutdown(None)...")
        
        # 调用废弃的 shutdown 方法
        try:
            shutdown(None)
            print("✅ shutdown 方法调用完成")
        except SystemExit:
            print("⚠️  shutdown 方法触发了系统退出")
        except Exception as e:
            print(f"⚠️  shutdown 方法调用出现异常: {e}")
        
        # 检查是否有废弃警告
        print(f"\n📊 捕获到 {len(w)} 个警告")
        deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
        
        if deprecation_warnings:
            print(f"✅ 检测到 {len(deprecation_warnings)} 个废弃警告:")
            for warning in deprecation_warnings:
                print(f"   - {warning.message}")
                print(f"     文件: {warning.filename}:{warning.lineno}")
        else:
            print("❌ 未检测到废弃警告")
            if w:
                print("其他警告:")
                for warning in w:
                    print(f"   - {warning.category.__name__}: {warning.message}")
    
    print("\n📋 废弃方法迁移指南:")
    print("   旧方式: shutdown(connection)")
    print("   新方式: await session.close()")
    print("\n💡 建议:")
    print("   - 使用 grasp.launch() 获取 session")
    print("   - 使用 await session.close() 关闭会话")
    print("   - 避免直接使用 shutdown() 方法")

if __name__ == '__main__':
    test_shutdown_deprecation()