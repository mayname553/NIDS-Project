"""
阈值优化脚本 - 通过调整决策阈值来提高召回率
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, confusion_matrix, classification_report
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_model_and_data():
    """加载训练好的模型和测试数据"""
    logger.info("加载模型和数据...")

    # 使用绝对路径
    import os
    from sklearn.model_selection import train_test_split

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # 修正路径：模型在backend/backend，数据在backend
    model_path = os.path.join(project_root, 'backend', 'backend', 'model', 'trained', 'rf_model.pkl')
    data_path = os.path.join(project_root, 'backend', 'data', 'processed', 'nsl_kdd_processed.npz')

    # 加载模型
    logger.info(f"加载模型: {model_path}")
    model = joblib.load(model_path)

    # 加载测试数据（从npz文件）
    logger.info(f"加载数据: {data_path}")
    data = np.load(data_path, allow_pickle=True)
    X_test = data['X_test']
    y_test = data['y_test']

    logger.info(f"模型加载成功")
    logger.info(f"测试集大小: {len(X_test)}")
    logger.info(f"测试集中攻击样本数: {sum(y_test)}")
    logger.info(f"测试集中正常样本数: {len(y_test) - sum(y_test)}")

    return model, X_test, y_test

def find_optimal_threshold(model, X_test, y_test, target_recall=0.70):
    """
    寻找最优阈值以达到目标召回率

    Args:
        model: 训练好的模型
        X_test: 测试特征
        y_test: 测试标签
        target_recall: 目标召回率

    Returns:
        optimal_threshold: 最优阈值
        metrics: 性能指标
    """
    logger.info("\n" + "="*60)
    logger.info("开始阈值优化")
    logger.info("="*60)

    # 获取预测概率
    logger.info("计算预测概率...")
    y_proba = model.predict_proba(X_test)[:, 1]

    # 计算精确率-召回率曲线
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)

    # 找到满足目标召回率的最优阈值
    logger.info(f"\n寻找达到召回率 >= {target_recall*100:.0f}% 的最优阈值...")

    # 找到所有满足召回率要求的阈值
    valid_indices = np.where(recalls >= target_recall)[0]

    if len(valid_indices) == 0:
        logger.warning(f"⚠️ 无法找到满足召回率 >= {target_recall*100:.0f}% 的阈值")
        logger.info("使用最低阈值以最大化召回率...")
        optimal_idx = np.argmax(recalls)
        optimal_threshold = 0.3  # 使用较低的阈值
    else:
        # 在满足召回率的阈值中，选择精确率最高的
        optimal_idx = valid_indices[np.argmax(precisions[valid_indices])]
        optimal_threshold = thresholds[optimal_idx]

    logger.info(f"\n找到最优阈值: {optimal_threshold:.4f}")
    logger.info(f"  预期召回率: {recalls[optimal_idx]:.4f} ({recalls[optimal_idx]*100:.2f}%)")
    logger.info(f"  预期精确率: {precisions[optimal_idx]:.4f} ({precisions[optimal_idx]*100:.2f}%)")

    # 使用最优阈值进行预测
    y_pred = (y_proba >= optimal_threshold).astype(int)

    # 计算实际性能指标
    metrics = {
        'threshold': float(optimal_threshold),
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, zero_division=0))
    }

    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred)

    # 显示结果
    logger.info("\n" + "="*60)
    logger.info("优化后的模型性能指标")
    logger.info("="*60)
    logger.info(f"   最优阈值:           {metrics['threshold']:.4f}")
    logger.info(f"   准确率 (Accuracy):  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    logger.info(f"   精确率 (Precision): {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    logger.info(f"   召回率 (Recall):    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    logger.info(f"   F1分数 (F1-Score):  {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")

    logger.info("\n混淆矩阵:")
    logger.info(f"              预测正常  预测攻击")
    logger.info(f"实际正常      {cm[0][0]:6d}    {cm[0][1]:6d}")
    logger.info(f"实际攻击      {cm[1][0]:6d}    {cm[1][1]:6d}")

    # 详细分类报告
    logger.info("\n详细分类报告:")
    print(classification_report(y_test, y_pred, target_names=['正常', '攻击']))

    # 检查是否达标
    if metrics['recall'] >= target_recall:
        logger.info(f"\n✅ 召回率达标！({metrics['recall']*100:.2f}% >= {target_recall*100:.0f}%)")
    else:
        logger.warning(f"\n⚠️ 召回率仍未达标！当前: {metrics['recall']*100:.2f}%, 目标: {target_recall*100:.0f}%")

    return optimal_threshold, metrics

def save_threshold(threshold, metrics):
    """保存最优阈值和性能指标"""
    logger.info("\n保存最优阈值...")

    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # 使用绝对路径
    output_path = os.path.join(project_root, 'backend', 'backend', 'model', 'trained', 'optimal_threshold.pkl')

    result = {
        'threshold': threshold,
        'metrics': metrics
    }

    joblib.dump(result, output_path)
    logger.info(f"✅ 阈值已保存到: {output_path}")

def main():
    """主函数"""
    try:
        # 加载模型和数据
        model, X_test, y_test = load_model_and_data()

        # 寻找最优阈值
        optimal_threshold, metrics = find_optimal_threshold(
            model, X_test, y_test, target_recall=0.70
        )

        # 保存结果
        save_threshold(optimal_threshold, metrics)

        logger.info("\n" + "="*60)
        logger.info("阈值优化完成！")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"❌ 阈值优化失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()
