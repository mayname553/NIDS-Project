"""
AI模型集成测试脚本
验证所有组件是否正常工作
"""

import os
import sys
import io

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_imports():
    """测试依赖导入"""
    print("="*60)
    print("测试 1: 检查依赖库")
    print("="*60)

    try:
        import pandas
        print("✅ pandas:", pandas.__version__)
    except ImportError as e:
        print("❌ pandas 未安装:", e)
        return False

    try:
        import numpy
        print("✅ numpy:", numpy.__version__)
    except ImportError as e:
        print("❌ numpy 未安装:", e)
        return False

    try:
        import sklearn
        print("✅ scikit-learn:", sklearn.__version__)
    except ImportError as e:
        print("❌ scikit-learn 未安装:", e)
        return False

    try:
        import joblib
        print("✅ joblib:", joblib.__version__)
    except ImportError as e:
        print("❌ joblib 未安装:", e)
        return False

    print("\n✅ 所有依赖库已安装\n")
    return True

def test_modules():
    """测试模块导入"""
    print("="*60)
    print("测试 2: 检查模块文件")
    print("="*60)

    modules = [
        'download_dataset.py',
        'data_preprocessor.py',
        'train_model.py',
        'train_and_save.py',
        'ai_detector.py',
        'network_attack_detector.py',
        'api_server.py'
    ]

    for module in modules:
        if os.path.exists(module):
            print(f"✅ {module}")
        else:
            print(f"❌ {module} 不存在")
            return False

    print("\n✅ 所有模块文件存在\n")
    return True

def test_model_files():
    """测试模型文件"""
    print("="*60)
    print("测试 3: 检查模型文件")
    print("="*60)

    if not os.path.exists('model'):
        print("⚠️ model/ 目录不存在")
        print("   请运行: python train_and_save.py")
        return False

    model_files = [
        'model/nids_model.pkl',
        'model/preprocessor.pkl',
        'model/model_metrics.json'
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
        print("   请运行: python train_and_save.py")
        return False

    print("\n✅ 模型文件完整\n")
    return True

def test_ai_detector():
    """测试AI检测器"""
    print("="*60)
    print("测试 4: 测试AI检测器")
    print("="*60)

    if not os.path.exists('model/nids_model.pkl'):
        print("⚠️ 模型文件不存在，跳过测试")
        return False

    try:
        from ai_detector import AIDetector

        detector = AIDetector('model/nids_model.pkl', 'model/preprocessor.pkl')
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
    print("测试 5: 测试网络检测器集成")
    print("="*60)

    try:
        from network_attack_detector import NetworkAttackDetector

        detector = NetworkAttackDetector()
        print(f"✅ 网络检测器初始化成功")
        print(f"   - AI模式: {'启用' if detector.use_ai else '禁用'}")

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

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("    NIDS AI模型集成测试")
    print("="*60 + "\n")

    results = []

    # 运行测试
    results.append(("依赖库检查", test_imports()))
    results.append(("模块文件检查", test_modules()))
    results.append(("模型文件检查", test_model_files()))
    results.append(("AI检测器测试", test_ai_detector()))
    results.append(("网络检测器测试", test_network_detector()))

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
        print("  1. 如果模型未训练，运行: python train_and_save.py")
        print("  2. 启动API服务器: python api_server.py")
        print("  3. 启动前端: cd ../frontend/nids-dashboard && npm run dev")
    else:
        print("\n⚠️ 部分测试失败，请检查上述错误信息。")
        if not os.path.exists('model/nids_model.pkl'):
            print("\n建议: 运行 python train_and_save.py 训练模型")

    return failed == 0

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = main()
    sys.exit(0 if success else 1)
