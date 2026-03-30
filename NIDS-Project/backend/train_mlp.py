"""
训练 MLP 模型 (scikit-learn)
"""
import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from data_preprocessor import DataPreprocessor
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_mlp():
    # 准备数据
    preprocessor = DataPreprocessor()
    X_train, y_train, X_test, y_test = preprocessor.prepare_data(
        'dataset/KDDTrain+.txt',
        'dataset/KDDTest+.txt'
    )

    # 定义 MLP 模型（轻量级）
    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        alpha=0.0001,
        batch_size=128,
        learning_rate='adaptive',
        max_iter=300,
        random_state=42,
        verbose=True
    )

    logger.info("开始训练 MLP 模型...")
    mlp.fit(X_train, y_train)

    # 评估
    y_pred = mlp.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"MLP 测试准确率: {acc:.4f}")
    logger.info("\n分类报告:\n" + classification_report(y_test, y_pred))

    # 保存模型
    os.makedirs('models', exist_ok=True)
    joblib.dump(mlp, 'models/mlp_model.pkl')
    logger.info("✅ MLP 模型已保存到 models/mlp_model.pkl")

    # 预处理器已在 prepare_data 中保存，无需重复
    logger.info("✅ 预处理器已存在，无需重复保存")

if __name__ == '__main__':
    train_mlp()