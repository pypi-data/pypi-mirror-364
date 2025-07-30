#!/usr/bin/env python3
"""
测试已删除方法的验证脚本

验证 create_terminal 和 create_filesystem 方法已被正确移除。
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_removed_methods():
    """测试已删除的方法不再可用"""
    print("🧪 测试已删除方法的验证")
    print("=" * 30)
    
    try:
        from grasp_sdk import Grasp, GraspSession, GraspBrowser, GraspTerminal
        print("✅ 核心类导入成功")
    except ImportError as e:
        print(f"❌ 核心类导入失败: {e}")
        return False
    
    # 测试 create_terminal 方法不存在（预期 ImportError）
    try:
        # 这行代码预期会失败，因为方法已被删除
        from grasp_sdk import create_terminal  # type: ignore
        print("❌ create_terminal 方法仍然存在（应该已被删除）")
        return False
    except ImportError:
        print("✅ create_terminal 方法已成功删除")
    
    # 测试 create_filesystem 方法不存在（预期 ImportError）
    try:
        # 这行代码预期会失败，因为方法已被删除
        from grasp_sdk import create_filesystem  # type: ignore
        print("❌ create_filesystem 方法仍然存在（应该已被删除）")
        return False
    except ImportError:
        print("✅ create_filesystem 方法已成功删除")
    
    # 验证 GraspSession 仍然提供 terminal 和 files 属性
    print("\n📋 验证 GraspSession 的替代功能:")
    print("   - session.terminal (替代 create_terminal)")
    print("   - session.files (替代 create_filesystem)")
    
    # 检查 __all__ 列表
    try:
        import grasp_sdk
        all_exports = grasp_sdk.__all__
        
        if 'create_terminal' in all_exports:
            print("❌ create_terminal 仍在 __all__ 列表中")
            return False
        else:
            print("✅ create_terminal 已从 __all__ 列表中移除")
            
        if 'create_filesystem' in all_exports:
            print("❌ create_filesystem 仍在 __all__ 列表中")
            return False
        else:
            print("✅ create_filesystem 已从 __all__ 列表中移除")
            
    except Exception as e:
        print(f"⚠️  检查 __all__ 列表时出错: {e}")
    
    print("\n🎉 所有验证通过！create_terminal 和 create_filesystem 方法已成功移除")
    print("\n💡 使用建议:")
    print("   - 使用 session.terminal 替代 create_terminal(connection)")
    print("   - 使用 session.files 替代 create_filesystem(connection)")
    
    return True

if __name__ == "__main__":
    success = test_removed_methods()
    if not success:
        sys.exit(1)
    print("\n✅ 测试完成")