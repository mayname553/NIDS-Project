"""
佐证材料 2：模型训练与评估脚本
运行方式：在项目根目录执行 python evidence/02_model_evaluation.py
输出：evidence/output/ 目录下的模型评估报告
"""

import os
import sys
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)


def train_and_evaluate():
    from data_preprocessor import DataPreprocessor
    from train_model import ModelTrainer

    dataset_base = os.path.join(os.path.dirname(__file__), '..', 'dataset')
    train_file = os.path.join(dataset_base, 'KDDTrain+.txt')
    test_file  = os.path.join(dataset_base, 'KDDTest+.txt')

    print("=" * 60)
    print("  随机森林模型训练与评估")
    print("=" * 60)

    # 1. 数据预处理
    print("\n[步骤 1/4] 数据预处理...")
    t0 = time.time()
    preprocessor = DataPreprocessor()
    X_train, y_train, X_test, y_test = preprocessor.prepare_data(train_file, test_file)
    preprocess_time = time.time() - t0
    print(f"  训练集：{X_train.shape[0]:,} 条，{X_train.shape[1]} 个特征")
    print(f"  测试集：{X_test.shape[0]:,} 条，{X_test.shape[1]} 个特征")
    print(f"  耗时：{preprocess_time:.2f} 秒")

    # 2. 模型训练
    print("\n[步骤 2/4] 训练随机森林模型（100棵树，最大深度20）...")
    t1 = time.time()
    trainer = ModelTrainer(n_estimators=100, max_depth=20, random_state=42)
    trainer.train(X_train, y_train)
    train_time = time.time() - t1
    print(f"  训练耗时：{train_time:.2f} 秒")

    # 3. 模型评估
    print("\n[步骤 3/4] 在测试集上评估模型...")
    metrics = trainer.evaluate(X_test, y_test)

    # 4. 特征重要性
    print("\n[步骤 4/4] 计算特征重要性...")
    feature_names = preprocessor.feature_columns
    importance = trainer.get_feature_importance(feature_names, top_n=10)

    # 保存模型
    model_path = os.path.join(MODEL_DIR, 'rf_model.pkl')
    prep_path  = os.path.join(MODEL_DIR, 'preprocessor.pkl')
    trainer.save_model(model_path)
    preprocessor.save_preprocessor(prep_path)

    return metrics, importance, feature_names, {
        'preprocess_time': preprocess_time,
        'train_time': train_time,
        'train_samples': int(X_train.shape[0]),
        'test_samples':  int(X_test.shape[0]),
        'n_features':    int(X_train.shape[1]),
    }


def generate_evaluation_report(metrics, importance, feature_names, timing):
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
    sep  = "=" * 60
    sep2 = "-" * 60
    cm   = metrics['confusion_matrix']  # [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

    lines = [
        sep,
        "  随机森林入侵检测模型 — 训练与评估报告",
        f"  生成时间：{now}",
        sep, "",
        "一、模型配置",
        sep2,
        "  算法：Random Forest（随机森林）",
        "  决策树数量：100 棵",
        "  最大深度：20 层",
        "  并行计算：使用全部 CPU 核心（n_jobs=-1）",
        "  随机种子：42",
        "",
        "二、数据规模",
        sep2,
        f"  训练样本数：{timing['train_samples']:,} 条",
        f"  测试样本数：{timing['test_samples']:,} 条",
        f"  特征维度：{timing['n_features']} 个",
        f"  数据预处理耗时：{timing['preprocess_time']:.2f} 秒",
        f"  模型训练耗时：{timing['train_time']:.2f} 秒",
        "",
        "三、性能指标",
        sep2,
        f"  准确率  (Accuracy) ：{metrics['accuracy']*100:.2f}%",
        f"  精确率  (Precision)：{metrics['precision']*100:.2f}%",
        f"  召回率  (Recall)   ：{metrics['recall']*100:.2f}%",
        f"  F1 分数 (F1-Score) ：{metrics['f1_score']*100:.2f}%",
        "",
        "四、混淆矩阵",
        sep2,
        "                  预测：正常    预测：攻击",
        f"  实际：正常      {tn:>8,}    {fp:>8,}",
        f"  实际：攻击      {fn:>8,}    {tp:>8,}",
        "",
        "  说明：",
        f"  · 正确识别正常流量（TN）：{tn:,} 条",
        f"  · 正确识别攻击流量（TP）：{tp:,} 条",
        f"  · 误报（FP，正常被判为攻击）：{fp:,} 条",
        f"  · 漏报（FN，攻击未被检出）：{fn:,} 条",
        f"  · 漏报率：{fn/(fn+tp)*100:.2f}%",
        "",
        "五、Top 10 重要特征",
        sep2,
        f"  {'排名':<5} {'特征名称':<35} {'重要性分数':>12}",
        "  " + "-" * 55,
    ]

    sorted_imp = sorted(importance.items(), key=lambda x: -x[1])[:10]
    for rank, (feat, score) in enumerate(sorted_imp, 1):
        lines.append(f"  {rank:<5} {feat:<35} {score:>12.4f}")

    lines += [
        "",
        "六、结论",
        sep2,
        f"  本模型在 NSL-KDD 测试集上达到 {metrics['accuracy']*100:.2f}% 的准确率，",
        f"  精确率高达 {metrics['precision']*100:.2f}%，说明误报率较低。",
        f"  召回率为 {metrics['recall']*100:.2f}%，存在一定漏报，",
        "  后续将通过 SMOTE 过采样和超参数调优进一步提升。",
        "",
        sep,
        "  报告结束",
        sep,
    ]

    out_path = os.path.join(OUTPUT_DIR, 'model_evaluation_report.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\n  → 文本报告已保存：{out_path}")

    # 同时保存 JSON
    json_out = {
        'model_config': {
            'algorithm': 'RandomForest',
            'n_estimators': 100,
            'max_depth': 20,
            'random_state': 42,
        },
        'timing': timing,
        'metrics': metrics,
        'top10_feature_importance': dict(sorted_imp),
    }
    json_path = os.path.join(OUTPUT_DIR, 'model_metrics.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_out, f, ensure_ascii=False, indent=2)
    print(f"  → JSON 指标已保存：{json_path}")

    # 同时复制到 model/ 目录供 API 使用
    api_metrics_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'model_metrics.json')
    os.makedirs(os.path.dirname(api_metrics_path), exist_ok=True)
    with open(api_metrics_path, 'w', encoding='utf-8') as f:
        json.dump(json_out, f, ensure_ascii=False, indent=2)
    print(f"  → API 指标已同步：{api_metrics_path}")


def main():
    metrics, importance, feature_names, timing = train_and_evaluate()
    generate_evaluation_report(metrics, importance, feature_names, timing)
    print("\n[完成] 模型评估完成！")


if __name__ == '__main__':
    main()
