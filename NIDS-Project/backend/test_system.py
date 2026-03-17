"""
系统测试脚本 - 验证各个模块是否正常工作
"""

import sys
import os
import importlib

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_imports():
    """测试必要的库是否已安装"""
    print("="*50)
    print("测试Python依赖...")
    print("="*50)

    required_modules = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'psutil': 'psutil',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests'
    }

    missing = []
    for module, name in required_modules.items():
        try:
            importlib.import_module(module)
            print(f"✅ {name} - 已安装")
        except ImportError:
            print(f"❌ {name} - 未安装")
            missing.append(name)

    if missing:
        print(f"\n缺少以下依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False

    print("\n所有依赖已安装！")
    return True

def test_detector():
    """测试检测器模块"""
    print("\n" + "="*50)
    print("测试检测器模块...")
    print("="*50)

    try:
        from network_attack_detector import NetworkAttackDetector
        detector = NetworkAttackDetector()
        print("✅ NetworkAttackDetector 初始化成功")

        # 测试生成报告
        report = detector.generate_report()
        print(f"✅ 报告生成成功")
        print(f"   状态: {report['status']}")

        return True
    except Exception as e:
        print(f"❌ 检测器测试失败: {e}")
        return False

def test_api_server():
    """测试API服务器配置"""
    print("\n" + "="*50)
    print("测试API服务器...")
    print("="*50)

    try:
        import api_server
        print("✅ API服务器模块加载成功")
        print(f"   Flask应用: {api_server.app}")
        print(f"   路由数量: {len(api_server.app.url_map._rules)}")

        # 列出所有路由
        print("\n可用的API端点:")
        for rule in api_server.app.url_map.iter_rules():
            if rule.endpoint != 'static':
                print(f"   {rule.methods} {rule.rule}")

        return True
    except Exception as e:
        print(f"❌ API服务器测试失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n" + "="*50)
    print("测试文件结构...")
    print("="*50)

    import os

    required_files = [
        'api_server.py',
        'network_attack_detector.py',
        'requirements.txt'
    ]

    required_dirs = [
        'preprocess',
        '../frontend/nids-dashboard'
    ]

    all_ok = True

    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 缺失")
            all_ok = False

    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"✅ {dir}/")
        else:
            print(f"❌ {dir}/ - 缺失")
            all_ok = False

    return all_ok

def main():
    """主测试函数"""
    print("\n[NIDS] 网络入侵检测系统 - 系统测试\n")

    results = []

    # 运行所有测试
    results.append(("依赖检查", test_imports()))
    results.append(("文件结构", test_file_structure()))
    results.append(("检测器模块", test_detector()))
    results.append(("API服务器", test_api_server()))

    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n[SUCCESS] 所有测试通过！系统可以正常运行。")
        print("\n启动系统:")
        print("  1. 运行后端: python api_server.py")
        print("  2. 运行前端: cd ../frontend/nids-dashboard && npm run dev")
        print("  3. 访问: http://localhost:5173")
    else:
        print("\n[WARNING] 部分测试失败，请检查上述错误信息。")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
