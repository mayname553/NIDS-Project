"""
统一测试套件 - 验证 NIDS 系统所有组件
合并了 test_system.py 和 test_ai_integration.py 的功能
"""

import os
import sys
import io
import importlib

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_imports():
    """测试依赖库"""
    print("="*60)
    print("测试 1: 检查依赖库")
    print("="*60)

    required_modules = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'joblib': 'joblib',
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'psutil': 'psutil',
        'requests': 'requests'
    }

    missing = []
    for module, name in required_modules.items():
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {name}: {version}")
        except ImportError:
            print(f"❌ {name} - 未安装")
            missing.append(name)

    if missing:
        print(f"\n缺少以下依赖: {', '.join(missing)}")
        print(f"请运行: pip install {' '.join(missing)}")
        return False

    print("\n✅ 所有依赖库已安装\n")
    return True

def test_modules():
    """测试模块文件"""
    print("="*60)
    print("测试 2: 检查模块文件")
    print("="*60)

    modules = [
        'download_dataset.py',
        'data_preprocessor.py',
        'train_model.py',
        'ai_detector.py',
        'network_attack_detector.py',
        'api_server.py'
    ]

    all_exist = True
    for module in modules:
        if os.path.exists(module):
            print(f"✅ {module}")
        else:
            print(f"❌ {module} 不存在")
            all_exist = False

    if not all_exist:
        return False

    print("\n✅ 所有模块文件存在\n")
    return True

def test_file_structure():
    """测试文件结构"""
    print("="*60)
    print("测试 3: 检查文件结构")
    print("="*60)

    required_dirs = [
        'preprocess',
        '../dataset',
        '../frontend/nids-dashboard'
    ]

    all_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - 缺失")
            all_ok = False

    if all_ok:
        print("\n✅ 文件结构完整\n")

    return all_ok

def test_model_files():
    """测试模型文件"""
    print("="*60)
    print("测试 4: 检查模型文件")
    print("="*60)

    if not os.path.exists('models'):
        print("⚠️ models/ 目录不存在")
        print("   请运行: python train_model.py")
        return False

    model_files = [
        'models/nids_model.pkl',
        'models/preprocessor.pkl',
        'models/model_metrics.json'
    ]

    all_exist = True
    for file in model_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024 * 1024)  # MB
            print(f"✅ {file} ({size:.2f} MB)")
        else:
            print(f"❌ {file} 不存在")
            all_exist = False

    if not all_exist:
        print("\n⚠️ 模型文件不完整")
        print("   请运行: python train_model.py")
        return False

    print("\n✅ 模型文件完整\n")
    return True

def test_ai_detector():
    """测试AI检测器"""
    print("="*60)
    print("测试 5: 测试AI检测器")
    print("="*60)

    if not os.path.exists('models/nids_model.pkl'):
        print("⚠️ 模型文件不存在，跳过测试")
        return False

    try:
        from ai_detector import AIDetector

        detector = AIDetector('models/nids_model.pkl', 'models/preprocessor.pkl')
        print("✅ AI检测器加载成功")

        # 测试预测
        result, features = detector.predict()
        if result:
            print(f"✅ 预测功能正常")
            print(f"   - 是否攻击: {result['is_attack']}")
            print(f"   - 置信度: {result['confidence']*100:.2f}%")
        else:
            print("❌ 预测失败")
            return False

        print("\n✅ AI检测器测试通过\n")
        return True

    except Exception as e:
        print(f"❌ AI检测器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_detector():
    """测试网络检测器集成"""
    print("="*60)
    print("测试 6: 测试网络检测器")
    print("="*60)

    try:
        from network_attack_detector import NetworkAttackDetector

        detector = NetworkAttackDetector()
        print(f"✅ 网络检测器初始化成功")
        print(f"   - AI模式: {'启用' if detector.use_ai else '禁用'}")

        # 测试生成报告
        report = detector.generate_report()
        print(f"✅ 报告生成成功")
        print(f"   - 状态: {report['status']}")

        if detector.use_ai:
            print("✅ AI模型已集成到检测器")
        else:
            print("⚠️ AI模型未加载，使用规则检测模式")

        print("\n✅ 网络检测器测试通过\n")
        return True

    except Exception as e:
        print(f"❌ 网络检测器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_server():
    """测试API服务器配置"""
    print("="*60)
    print("测试 7: 测试API服务器")
    print("="*60)

    try:
        import api_server
        print("✅ API服务器模块加载成功")
        print(f"   - Flask应用: {api_server.app}")
        print(f"   - 路由数量: {len(api_server.app.url_map._rules)}")

        # 列出所有路由
        print("\n可用的API端点:")
        for rule in api_server.app.url_map.iter_rules():
            if rule.endpoint != 'static':
                methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                print(f"   [{methods}] {rule.rule}")

        print("\n✅ API服务器测试通过\n")
        return True

    except Exception as e:
        print(f"❌ API服务器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("    NIDS 系统统一测试套件")
    print("    Network Intrusion Detection System")
    print("="*60 + "\n")

    # 切换到backend目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    results = []

    # 运行所有测试
    results.append(("依赖库检查", test_imports()))
    results.append(("模块文件检查", test_modules()))
    results.append(("文件结构检查", test_file_structure()))
    results.append(("模型文件检查", test_model_files()))
    results.append(("AI检测器测试", test_ai_detector()))
    results.append(("网络检测器测试", test_network_detector()))
    results.append(("API服务器测试", test_api_server()))

    # 显示总结
    print("="*60)
    print("测试总结")
    print("="*60)

    passed = 0
    failed = 0

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("="*60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("="*60)

    if failed == 0:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n下一步:")
        print("  1. 启动后端API: python api_server.py")
        print("  2. 启动前端: cd ../frontend/nids-dashboard && npm run dev")
        print("  3. 访问系统: http://localhost:5173")
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息。")
        if not os.path.exists('models/nids_model.pkl'):
            print("\n建议: 运行 python train_model.py 训练模型")

    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
