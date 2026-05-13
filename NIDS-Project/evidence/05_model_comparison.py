"""
模型对比脚本 - 05_model_comparison.py
负责人：黄子权
功能：对比 RandomForest、MLP(Hybrid)、CNN-LSTM 三个模型的性能
输出：性能对比表、混淆矩阵、特征重要性图、性能雷达图
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加 backend 目录到路径
backend_path = Path(__file__).parent.parent / 'backend'
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

from data_preprocessor import DataPreprocessor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def load_models():
    """加载三个训练好的模型"""
    models = {}

    # 查找模型文件路径
    possible_base_paths = [
        Path('backend/models'),
        Path('models'),
        Path('../backend/models'),
        Path(__file__).parent.parent / 'backend' / 'models'
    ]

    model_files = {
        'RandomForest': 'rf_model.pkl',
        'MLP(Hybrid)': 'hybrid_nids_model.keras',
        'CNN-LSTM': 'cnn_lstm_model.keras'
    }

    models_dir = None
    for base_path in possible_base_paths:
        if base_path.exists() and (base_path / 'rf_model.pkl').exists():
            models_dir = base_path
            break

    if not models_dir:
        logger.error("找不到模型文件目录！")
        logger.error("请确保已训练模型并保存在 backend/models/ 目录下")
        return None

    logger.info(f"模型目录: {models_dir}")

    # 加载 RandomForest
    try:
        rf_path = models_dir / 'rf_model.pkl'
        with open(rf_path, 'rb') as f:
            models['RandomForest'] = pickle.load(f)
        logger.info(f"✅ 加载 RandomForest 模型: {rf_path}")
    except Exception as e:
        logger.warning(f"⚠️ 无法加载 RandomForest: {e}")

    # 加载深度学习模型
    try:
        from tensorflow import keras

        # 加载 Hybrid 模型
        try:
            hybrid_path = models_dir / 'hybrid_nids_model.keras'
            models['MLP(Hybrid)'] = keras.models.load_model(hybrid_path)
            logger.info(f"✅ 加载 MLP(Hybrid) 模型: {hybrid_path}")
        except Exception as e:
            logger.warning(f"⚠️ 无法加载 MLP(Hybrid): {e}")

        # 加载 CNN-LSTM 模型
        try:
            cnn_lstm_path = models_dir / 'cnn_lstm_model.keras'
            models['CNN-LSTM'] = keras.models.load_model(cnn_lstm_path)
            logger.info(f"✅ 加载 CNN-LSTM 模型: {cnn_lstm_path}")
        except Exception as e:
            logger.warning(f"⚠️ 无法加载 CNN-LSTM: {e}")

    except ImportError:
        logger.warning("⚠️ TensorFlow 未安装，无法加载深度学习模型")

    if not models:
        logger.error("❌ 没有成功加载任何模型！")
        return None

    return models

def load_test_data():
    """加载测试数据"""
    possible_paths = [
        ('dataset/KDDTrain+.txt', 'dataset/KDDTest+.txt'),
        ('backend/dataset/KDDTrain+.txt', 'backend/dataset/KDDTest+.txt'),
        ('../backend/dataset/KDDTrain+.txt', '../backend/dataset/KDDTest+.txt'),
        (str(Path(__file__).parent.parent / 'backend' / 'dataset' / 'KDDTrain+.txt'),
         str(Path(__file__).parent.parent / 'backend' / 'dataset' / 'KDDTest+.txt'))
    ]

    train_path, test_path = None, None
    for tr, te in possible_paths:
        if os.path.exists(tr) and os.path.exists(te):
            train_path, test_path = tr, te
            break

    if not train_path:
        logger.error("找不到数据集文件！")
        return None, None

    logger.info(f"数据集路径: {test_path}")

    preprocessor = DataPreprocessor()
    _, _, X_test, y_test = preprocessor.prepare_data(train_path, test_path)

    logger.info(f"测试集大小: {X_test.shape}")
    logger.info(f"测试集标签分布: Normal={np.sum(y_test == 0)}, Attack={np.sum(y_test == 1)}")

    return X_test, y_test

def evaluate_model(model, model_name, X_test, y_test):
    """评估单个模型"""
    logger.info(f"\n评估模型: {model_name}")

    # 预测
    if model_name == 'RandomForest':
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    else:
        # 深度学习模型
        X_test_reshaped = X_test.values.reshape(X_test.shape[0], X_test.shape[1], 1)
        y_pred_proba = model.predict(X_test_reshaped, verbose=0).flatten()
        y_pred = (y_pred_proba > 0.5).astype(int)

    # 计算指标
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    logger.info(f"  准确率: {accuracy:.4f}")
    logger.info(f"  精确率: {precision:.4f}")
    logger.info(f"  召回率: {recall:.4f}")
    logger.info(f"  F1分数: {f1:.4f}")

    return {
        'Model': model_name,
        'Accuracy': accuracy,
        'Precision': precision,
        'Recall': recall,
        'F1_Score': f1,
        'Confusion_Matrix': cm,
        'Predictions': y_pred,
        'Probabilities': y_pred_proba
    }

def generate_comparison_table(results):
    """生成模型对比表"""
    df = pd.DataFrame([
        {
            'Model': r['Model'],
            'Accuracy': r['Accuracy'],
            'Precision': r['Precision'],
            'Recall': r['Recall'],
            'F1_Score': r['F1_Score']
        }
        for r in results
    ])

    return df

def save_results(df_results, results, output_dir='evidence/output'):
    """保存结果"""
    os.makedirs(output_dir, exist_ok=True)

    # 保存对比表
    csv_path = os.path.join(output_dir, 'model_comparison_results.csv')
    df_results.to_csv(csv_path, index=False)
    logger.info(f"✅ 对比表已保存: {csv_path}")

    # 保存详细结果（包含混淆矩阵）
    detailed_results = []
    for r in results:
        detailed_results.append({
            'Model': r['Model'],
            'Accuracy': r['Accuracy'],
            'Precision': r['Precision'],
            'Recall': r['Recall'],
            'F1_Score': r['F1_Score'],
            'TN': int(r['Confusion_Matrix'][0, 0]),
            'FP': int(r['Confusion_Matrix'][0, 1]),
            'FN': int(r['Confusion_Matrix'][1, 0]),
            'TP': int(r['Confusion_Matrix'][1, 1])
        })

    df_detailed = pd.DataFrame(detailed_results)
    detailed_path = os.path.join(output_dir, 'model_comparison_detailed.csv')
    df_detailed.to_csv(detailed_path, index=False)
    logger.info(f"✅ 详细结果已保存: {detailed_path}")

    return csv_path, detailed_path

def generate_charts(df_results, results, output_dir='evidence/output/charts'):
    """生成所有图表"""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        os.makedirs(output_dir, exist_ok=True)

        # 设置样式
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        sns.set_style("whitegrid")

        # 图1: 性能对比柱状图
        fig, ax = plt.subplots(figsize=(12, 6))
        df_melted = df_results.melt(
            id_vars='Model',
            value_vars=['Accuracy', 'Precision', 'Recall', 'F1_Score'],
            var_name='Metric',
            value_name='Score'
        )
        sns.barplot(data=df_melted, x='Metric', y='Score', hue='Model', ax=ax)
        ax.set_title('Model Performance Comparison', fontsize=16, fontweight='bold')
        ax.set_ylim(0.5, 1.0)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_xlabel('Metric', fontsize=12)
        ax.legend(title='Model', fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # 添加数值标签
        for container in ax.containers:
            ax.bar_label(container, fmt='%.3f', fontsize=8)

        plt.tight_layout()
        chart1_path = os.path.join(output_dir, 'model_performance_comparison.png')
        plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ 性能对比图已保存: {chart1_path}")
        plt.close()

        # 图2: 混淆矩阵（3个模型）
        fig, axes = plt.subplots(1, len(results), figsize=(5*len(results), 4))
        if len(results) == 1:
            axes = [axes]

        for idx, result in enumerate(results):
            cm = result['Confusion_Matrix']
            sns.heatmap(
                cm,
                annot=True,
                fmt='d',
                cmap='Blues',
                ax=axes[idx],
                cbar=True,
                xticklabels=['Normal', 'Attack'],
                yticklabels=['Normal', 'Attack']
            )
            axes[idx].set_title(f"{result['Model']}\nAccuracy: {result['Accuracy']:.4f}",
                               fontsize=12, fontweight='bold')
            axes[idx].set_ylabel('True Label', fontsize=10)
            axes[idx].set_xlabel('Predicted Label', fontsize=10)

        plt.suptitle('Confusion Matrices Comparison', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        chart2_path = os.path.join(output_dir, 'confusion_matrices.png')
        plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ 混淆矩阵已保存: {chart2_path}")
        plt.close()

        # 图3: 性能雷达图
        categories = ['Accuracy', 'Precision', 'Recall', 'F1_Score']
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

        for idx, (_, row) in enumerate(df_results.iterrows()):
            values = row[categories].tolist()
            values += values[:1]  # 闭合
            ax.plot(angles, values, 'o-', linewidth=2, label=row['Model'], color=colors[idx % len(colors)])
            ax.fill(angles, values, alpha=0.15, color=colors[idx % len(colors)])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
        ax.set_title('Model Performance Radar Chart', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        chart3_path = os.path.join(output_dir, 'performance_radar.png')
        plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
        logger.info(f"✅ 性能雷达图已保存: {chart3_path}")
        plt.close()

        # 图4: 特征重要性（仅 RandomForest）
        rf_result = next((r for r in results if r['Model'] == 'RandomForest'), None)
        if rf_result:
            # 需要重新加载模型以获取特征重要性
            models_dir = Path('backend/models')
            if not models_dir.exists():
                models_dir = Path(__file__).parent.parent / 'backend' / 'models'

            rf_path = models_dir / 'rf_model.pkl'
            if rf_path.exists():
                with open(rf_path, 'rb') as f:
                    rf_model = pickle.load(f)

                if hasattr(rf_model, 'feature_importances_'):
                    importances = rf_model.feature_importances_
                    indices = np.argsort(importances)[::-1][:20]  # Top 20

                    fig, ax = plt.subplots(figsize=(10, 8))
                    ax.barh(range(len(indices)), importances[indices], color='steelblue')
                    ax.set_yticks(range(len(indices)))
                    ax.set_yticklabels([f'Feature {i}' for i in indices], fontsize=9)
                    ax.set_xlabel('Importance', fontsize=12)
                    ax.set_title('Top 20 Feature Importances (RandomForest)', fontsize=14, fontweight='bold')
                    ax.invert_yaxis()
                    ax.grid(axis='x', linestyle='--', alpha=0.7)

                    plt.tight_layout()
                    chart4_path = os.path.join(output_dir, 'feature_importance.png')
                    plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
                    logger.info(f"✅ 特征重要性图已保存: {chart4_path}")
                    plt.close()

        logger.info(f"\n✅ 所有图表已生成至: {os.path.abspath(output_dir)}")

    except ImportError as e:
        logger.warning(f"⚠️ 无法生成图表: {e}")
        logger.warning("请安装: pip install matplotlib seaborn")
    except Exception as e:
        logger.error(f"❌ 生成图表时出错: {e}", exc_info=True)

def main():
    """主函数"""
    logger.info("="*70)
    logger.info("模型对比实验 - NSL-KDD 入侵检测")
    logger.info("="*70)

    # 1. 加载模型
    models = load_models()
    if not models:
        logger.error("无法加载模型，退出")
        return

    # 2. 加载测试数据
    X_test, y_test = load_test_data()
    if X_test is None:
        logger.error("无法加载测试数据，退出")
        return

    # 3. 评估所有模型
    results = []
    for model_name, model in models.items():
        try:
            result = evaluate_model(model, model_name, X_test, y_test)
            results.append(result)
        except Exception as e:
            logger.error(f"评估 {model_name} 时出错: {e}", exc_info=True)

    if not results:
        logger.error("没有成功评估任何模型")
        return

    # 4. 生成对比表
    df_results = generate_comparison_table(results)

    print("\n" + "="*70)
    print("模型性能对比表")
    print("="*70)
    print(df_results.to_string(index=False))
    print("="*70)

    # 5. 保存结果
    save_results(df_results, results)

    # 6. 生成图表
    generate_charts(df_results, results)

    # 7. 总结
    print("\n" + "="*70)
    print("实验总结")
    print("="*70)

    best_idx = df_results['F1_Score'].idxmax()
    best_model = df_results.iloc[best_idx]

    print(f"最佳模型: {best_model['Model']}")
    print(f"  - Accuracy: {best_model['Accuracy']:.4f}")
    print(f"  - Precision: {best_model['Precision']:.4f}")
    print(f"  - Recall: {best_model['Recall']:.4f}")
    print(f"  - F1 Score: {best_model['F1_Score']:.4f}")

    print("\n模型排名（按 F1 Score）:")
    df_sorted = df_results.sort_values('F1_Score', ascending=False)
    for idx, (_, row) in enumerate(df_sorted.iterrows(), 1):
        print(f"  {idx}. {row['Model']}: {row['F1_Score']:.4f}")

    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n实验被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n\n实验失败: {e}", exc_info=True)
        sys.exit(1)
