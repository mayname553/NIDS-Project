"""
AI模型训练模块
使用随机森林训练入侵检测模型
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import json
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, n_estimators=100, max_depth=20, random_state=42):
        """初始化模型"""
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,  # 使用所有CPU核心
            verbose=1
        )
        self.metrics = {}

    def train(self, X_train, y_train):
        """训练模型"""
        logger.info("="*50)
        logger.info("开始训练随机森林模型")
        logger.info(f"训练样本数: {X_train.shape[0]}")
        logger.info(f"特征数: {X_train.shape[1]}")
        logger.info("="*50)

        self.model.fit(X_train, y_train)

        logger.info("模型训练完成！")

    def evaluate(self, X_test, y_test):
        """评估模型"""
        logger.info("="*50)
        logger.info("开始评估模型")
        logger.info("="*50)

        # 预测
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        # 计算指标
        self.metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0))
        }

        # 混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        self.metrics['confusion_matrix'] = cm.tolist()

        # 显示结果
        logger.info(f"准确率 (Accuracy):  {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)")
        logger.info(f"精确率 (Precision): {self.metrics['precision']:.4f} ({self.metrics['precision']*100:.2f}%)")
        logger.info(f"召回率 (Recall):    {self.metrics['recall']:.4f} ({self.metrics['recall']*100:.2f}%)")
        logger.info(f"F1分数 (F1-Score):  {self.metrics['f1_score']:.4f} ({self.metrics['f1_score']*100:.2f}%)")

        logger.info("\n混淆矩阵:")
        logger.info(f"              预测正常  预测攻击")
        logger.info(f"实际正常      {cm[0][0]:6d}    {cm[0][1]:6d}")
        logger.info(f"实际攻击      {cm[1][0]:6d}    {cm[1][1]:6d}")

        # 分类报告
        logger.info("\n详细分类报告:")
        logger.info(classification_report(y_test, y_pred, target_names=['正常', '攻击']))

        logger.info("="*50)

        return self.metrics

    def get_feature_importance(self, feature_names, top_n=10):
        """获取特征重要性"""
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]

        logger.info(f"\n前{top_n}个最重要的特征:")
        for i in range(min(top_n, len(feature_names))):
            idx = indices[i]
            logger.info(f"{i+1}. {feature_names[idx]}: {importances[idx]:.4f}")

        return {feature_names[i]: float(importances[i]) for i in range(len(feature_names))}

    def save_model(self, model_path, metrics_path=None):
        """保存模型"""
        logger.info(f"保存模型: {model_path}")
        joblib.dump(self.model, model_path)

        if metrics_path and self.metrics:
            logger.info(f"保存性能指标: {metrics_path}")
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)

        logger.info("模型保存完成！")

    def load_model(self, model_path):
        """加载模型"""
        logger.info(f"加载模型: {model_path}")
        self.model = joblib.load(model_path)
        logger.info("模型加载完成！")

if __name__ == '__main__':
    from data_preprocessor import DataPreprocessor

    # 1. 准备数据
    preprocessor = DataPreprocessor()
    X_train, y_train, X_test, y_test = preprocessor.prepare_data(
        'dataset/KDDTrain+.txt',
        'dataset/KDDTest+.txt'
    )

    # 2. 训练模型
    trainer = ModelTrainer(n_estimators=100, max_depth=20)
    trainer.train(X_train, y_train)

    # 3. 评估
    metrics = trainer.evaluate(X_test, y_test)

    # 4. 保存模型和预处理器
    import os
    os.makedirs('models', exist_ok=True)   # 确保 models 目录存在
    trainer.save_model('models/rf_model.pkl')
    preprocessor.save_preprocessor('models/preprocessor.pkl')
    print("✅ RandomForest 模型已保存到 models/rf_model.pkl")