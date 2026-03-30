"""
训练投票集成模型
"""
import joblib
from sklearn.ensemble import VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from data_preprocessor import DataPreprocessor
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_ensemble():
    # 准备数据
    preprocessor = DataPreprocessor()
    X_train, y_train, X_test, y_test = preprocessor.prepare_data(
        'dataset/KDDTrain+.txt',
        'dataset/KDDTest+.txt'
    )

    # 加载已经训练好的两个模型
    rf = joblib.load('models/rf_model.pkl')
    mlp = joblib.load('models/mlp_model.pkl')

    # 投票分类器（软投票）
    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('mlp', mlp)],
        voting='soft',
        weights=[1, 1]
    )

    logger.info("训练投票集成模型...")
    # 注意：VotingClassifier 在 fit 时会重新训练子模型，但因为我们传入的 estimators 已经是训练好的模型，
    # 设置 refit=False 可以避免重新训练，但 sklearn 中 VotingClassifier 的 fit 会覆盖子模型。
    # 简单方式：直接使用 ensemble 的 predict 方法，而不需要再 fit（因为我们希望使用已训练好的子模型）。
    # 但为了保险，我们还是让 VotingClassifier 重新 fit 一次（时间不长）。
    ensemble.fit(X_train, y_train)

    # 评估
    y_pred = ensemble.predict(X_test)
    from sklearn.metrics import accuracy_score, classification_report
    acc = accuracy_score(y_test, y_pred)
    logger.info(f"集成模型测试准确率: {acc:.4f}")
    logger.info("\n分类报告:\n" + classification_report(y_test, y_pred))

    # 保存集成模型
    os.makedirs('models', exist_ok=True)
    joblib.dump(ensemble, 'models/ensemble_model.pkl')
    logger.info("✅ 集成模型已保存到 models/ensemble_model.pkl")

if __name__ == '__main__':
    train_ensemble()