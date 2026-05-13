"""
样本平衡实验脚本 - NSL-KDD 数据集
负责人: 黄子权
功能: 对比不同样本平衡策略对模型性能的影响
"""

import pandas as pd
import numpy as np
from data_preprocessor import DataPreprocessor
from train_model import ModelTrainer
import logging
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def random_undersample(X, y):
    """
    随机欠采样：减少多数类样本到与少数类相同数量

    Args:
        X: 特征数据 (DataFrame)
        y: 标签数据 (Series)

    Returns:
        X_resampled, y_resampled: 重采样后的数据
    """
    logger.info("执行随机欠采样...")

    classes = np.unique(y)
    counts = {cls: np.sum(y == cls) for cls in classes}
    min_count = min(counts.values())

    logger.info(f"原始类别分布: {counts}")
    logger.info(f"目标样本数: {min_count}")

    indices = []
    for cls in classes:
        cls_indices = np.where(y == cls)[0]
        selected_indices = np.random.choice(cls_indices, min_count, replace=False)
        indices.extend(selected_indices)

    # 打乱顺序
    np.random.shuffle(indices)

    return X.iloc[indices].reset_index(drop=True), y.iloc[indices].reset_index(drop=True)


def random_oversample(X, y):
    """
    随机过采样：增加少数类样本到与多数类相同数量（简单复制）

    Args:
        X: 特征数据 (DataFrame)
        y: 标签数据 (Series)

    Returns:
        X_resampled, y_resampled: 重采样后的数据
    """
    logger.info("执行随机过采样...")

    classes = np.unique(y)
    counts = {cls: np.sum(y == cls) for cls in classes}
    max_count = max(counts.values())

    logger.info(f"原始类别分布: {counts}")
    logger.info(f"目标样本数: {max_count}")

    indices = []
    for cls in classes:
        cls_indices = np.where(y == cls)[0]
        selected_indices = np.random.choice(cls_indices, max_count, replace=True)
        indices.extend(selected_indices)

    # 打乱顺序
    np.random.shuffle(indices)

    return X.iloc[indices].reset_index(drop=True), y.iloc[indices].reset_index(drop=True)


def find_dataset_path():
    """查找数据集路径"""
    possible_paths = [
        ('dataset/KDDTrain+.txt', 'dataset/KDDTest+.txt'),
        ('backend/dataset/KDDTrain+.txt', 'backend/dataset/KDDTest+.txt'),
        ('../dataset/KDDTrain+.txt', '../dataset/KDDTest+.txt'),
        ('NIDS-Project/backend/dataset/KDDTrain+.txt', 'NIDS-Project/backend/dataset/KDDTest+.txt')
    ]

    for train_path, test_path in possible_paths:
        if os.path.exists(train_path) and os.path.exists(test_path):
            return train_path, test_path

    return None, None


def run_experiment():
    """运行样本平衡实验"""

    logger.info("="*70)
    logger.info("样本平衡实验 - NSL-KDD 二分类任务")
    logger.info("="*70)

    # 1. 查找数据集
    train_path, test_path = find_dataset_path()

    if not train_path:
        logger.error("❌ 找不到数据集文件！")
        logger.error("请确保数据集位于以下路径之一:")
        logger.error("  - dataset/KDDTrain+.txt")
        logger.error("  - backend/dataset/KDDTrain+.txt")
        logger.error("  - ../dataset/KDDTrain+.txt")
        return

    logger.info(f"✅ 找到数据集: {train_path}")

    # 2. 加载和预处理数据
    preprocessor = DataPreprocessor()
    logger.info("正在加载和预处理数据...")

    try:
        X_train_raw, y_train_raw, X_test, y_test = preprocessor.prepare_data(
            train_path, test_path
        )
    except Exception as e:
        logger.error(f"❌ 数据加载失败: {e}")
        return

    logger.info(f"训练集大小: {X_train_raw.shape}")
    logger.info(f"测试集大小: {X_test.shape}")

    # 3. 显示原始类别分布
    original_counts = np.bincount(y_train_raw)
    logger.info(f"\n原始训练集类别分布:")
    logger.info(f"  Normal (0): {original_counts[0]} ({original_counts[0]/len(y_train_raw)*100:.2f}%)")
    logger.info(f"  Attack (1): {original_counts[1]} ({original_counts[1]/len(y_train_raw)*100:.2f}%)")

    # 4. 准备实验
    logger.info("\n准备实验数据...")
    X_under, y_under = random_undersample(X_train_raw, y_train_raw)
    X_over, y_over = random_oversample(X_train_raw, y_train_raw)

    experiments = [
        ("Baseline (Original)", X_train_raw, y_train_raw),
        ("Random Undersampling", X_under, y_under),
        ("Random Oversampling", X_over, y_over)
    ]

    results = []

    # 5. 运行实验
    for name, X_train, y_train in experiments:
        logger.info("\n" + "="*70)
        logger.info(f">>> 实验项目: {name}")
        logger.info("="*70)

        # 显示类别分布
        counts = np.bincount(y_train)
        logger.info(f"训练集大小: {X_train.shape}")
        logger.info(f"类别分布: Normal={counts[0]}, Attack={counts[1]}")

        # 训练模型 (使用较小的参数以加快速度)
        logger.info("开始训练随机森林模型...")
        trainer = ModelTrainer(n_estimators=50, max_depth=15, random_state=42)

        try:
            trainer.train(X_train, y_train)
            logger.info("✅ 模型训练完成")
        except Exception as e:
            logger.error(f"❌ 模型训练失败: {e}")
            continue

        # 评估模型
        logger.info("正在评估模型...")
        try:
            metrics = trainer.evaluate(X_test, y_test)
            logger.info("✅ 模型评估完成")
        except Exception as e:
            logger.error(f"❌ 模型评估失败: {e}")
            continue

        # 记录结果
        results.append({
            'Experiment': name,
            'Train_Size': len(y_train),
            'Normal_Count': counts[0],
            'Attack_Count': counts[1],
            'Accuracy': metrics['accuracy'],
            'Precision': metrics['precision'],
            'Recall': metrics['recall'],
            'F1_Score': metrics['f1_score']
        })

        logger.info(f"准确率: {metrics['accuracy']:.4f}")
        logger.info(f"精确率: {metrics['precision']:.4f}")
        logger.info(f"召回率: {metrics['recall']:.4f}")
        logger.info(f"F1分数: {metrics['f1_score']:.4f}")

    # 6. 输出结果对比
    if not results:
        logger.error("❌ 没有成功完成的实验")
        return

    df_results = pd.DataFrame(results)

    print("\n" + "="*80)
    print("样本平衡实验结果对比 (NSL-KDD Binary Classification)")
    print("="*80)
    print(df_results.to_string(index=False))
    print("="*80)

    # 7. 保存结果
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, 'balance_experiment_results.csv')
    df_results.to_csv(csv_path, index=False)
    logger.info(f"\n✅ 结果已保存至: {csv_path}")

    # 8. 生成可视化图表
    try:
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        import matplotlib.pyplot as plt
        import seaborn as sns

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 图1: 指标对比图
        fig, ax = plt.subplots(figsize=(12, 6))

        metrics_to_plot = ['Accuracy', 'Precision', 'Recall', 'F1_Score']
        x = np.arange(len(df_results))
        width = 0.2

        for i, metric in enumerate(metrics_to_plot):
            offset = (i - 1.5) * width
            ax.bar(x + offset, df_results[metric], width, label=metric)

        ax.set_xlabel('Experiment', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Sample Balancing Strategy Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(df_results['Experiment'], rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.set_ylim(0.5, 1.0)

        plt.tight_layout()
        chart_path = os.path.join(output_dir, 'experiment_comparison.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"✅ 指标对比图已生成: {chart_path}")

        # 图2: 类别分布对比
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        for idx, (name, X_train, y_train) in enumerate(experiments):
            counts = np.bincount(y_train)
            axes[idx].pie(
                counts,
                labels=['Normal', 'Attack'],
                autopct='%1.1f%%',
                colors=['#66b3ff', '#ff9999'],
                startangle=90
            )
            axes[idx].set_title(name, fontsize=12, fontweight='bold')

        plt.tight_layout()
        dist_path = os.path.join(output_dir, 'class_distribution_comparison.png')
        plt.savefig(dist_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"✅ 类别分布图已生成: {dist_path}")

        # 图3: F1分数对比
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#3498db', '#e74c3c', '#2ecc71']
        bars = ax.barh(df_results['Experiment'], df_results['F1_Score'], color=colors)

        ax.set_xlabel('F1 Score', fontsize=12)
        ax.set_title('F1 Score Comparison', fontsize=14, fontweight='bold')
        ax.set_xlim(0.5, 1.0)
        ax.grid(axis='x', linestyle='--', alpha=0.7)

        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{width:.4f}',
                   ha='left', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        f1_path = os.path.join(output_dir, 'f1_score_comparison.png')
        plt.savefig(f1_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"✅ F1分数对比图已生成: {f1_path}")

        print(f"\n📊 图表已生成至: {os.path.abspath(output_dir)}")
        print(f"  - 指标对比图: experiment_comparison.png")
        print(f"  - 类别分布图: class_distribution_comparison.png")
        print(f"  - F1分数对比: f1_score_comparison.png")

    except ImportError as e:
        logger.warning(f"\n⚠️ 无法生成图表: {e}")
        logger.warning("请安装: pip install matplotlib seaborn")
    except Exception as e:
        logger.error(f"\n❌ 图表生成失败: {e}")

    # 9. 实验总结
    print("\n" + "="*80)
    print("实验总结与建议")
    print("="*80)

    best_f1_idx = df_results['F1_Score'].idxmax()
    best_exp = df_results.iloc[best_f1_idx]

    print(f"\n1. 最佳策略: {best_exp['Experiment']}")
    print(f"   - F1 Score: {best_exp['F1_Score']:.4f}")
    print(f"   - Accuracy: {best_exp['Accuracy']:.4f}")
    print(f"   - Precision: {best_exp['Precision']:.4f}")
    print(f"   - Recall: {best_exp['Recall']:.4f}")

    if best_exp['Experiment'] == "Baseline (Original)":
        print("\n2. 分析:")
        print("   - NSL-KDD 数据集在二分类任务上已经相对平衡")
        print("   - 样本平衡策略对性能提升有限")
        print("   - 建议直接使用原始数据集进行训练")
    else:
        print(f"\n2. 分析:")
        print(f"   - {best_exp['Experiment']} 策略有效提升了模型性能")
        print(f"   - 相比 Baseline 提升了 {(best_exp['F1_Score'] - df_results.iloc[0]['F1_Score'])*100:.2f}% (F1)")
        print(f"   - 建议在生产环境中使用该策略")

    print("\n3. 注意事项:")
    print("   - 过采样可能导致过拟合（重复样本）")
    print("   - 欠采样会丢失部分信息（样本减少）")
    print("   - 可考虑更高级的方法: SMOTE, ADASYN 等")

    print("\n" + "="*80)
    logger.info("✅ 实验完成！")


if __name__ == "__main__":
    # 设置随机种子以保证可重复性
    np.random.seed(42)

    try:
        run_experiment()
    except KeyboardInterrupt:
        logger.info("\n⚠️ 实验被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ 实验失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
