import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from data_preprocessor import DataPreprocessor
from models.hybrid_model import create_hybrid_model
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_hybrid():
    # 1. 下载和预处理数据
    train_path = 'dataset/KDDTrain+.txt'
    test_path = 'dataset/KDDTest+.txt'
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        logger.info("正在下载数据集...")
        from download_dataset import download_nsl_kdd
        download_nsl_kdd()
    
    preprocessor = DataPreprocessor()
    
    logger.info("正在加载并预处理训练数据...")
    df_train = preprocessor.load_data(train_path)
    X_train, y_train = preprocessor.preprocess(df_train, fit=True)
    
    logger.info("正在加载并预处理测试数据...")
    df_test = preprocessor.load_data(test_path)
    X_test, y_test = preprocessor.preprocess(df_test, fit=False)
    
    # 2. 构建模型
    input_dim = X_train.shape[1]
    logger.info(f"输入特征维度: {input_dim}")
    
    model = create_hybrid_model((input_dim,))
    model.summary()
    
    # 3. 训练模型
    os.makedirs('model', exist_ok=True)
    
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    checkpoint = ModelCheckpoint('model/hybrid_nids_model.keras', monitor='val_accuracy', save_best_only=True)
    
    logger.info("开始训练混合模型...")
    history = model.fit(
        X_train, y_train,
        epochs=2,
        batch_size=64,
        validation_split=0.2,
        callbacks=[early_stopping, checkpoint],
        verbose=1
    )
    
    # 4. 评估模型
    logger.info("开始评估模型性能...")
    loss, accuracy = model.evaluate(X_test, y_test)
    logger.info(f"测试集准确率: {accuracy:.4f}")
    
    # 预测并生成报告
    y_pred = (model.predict(X_test) > 0.5).astype(int)
    from sklearn.metrics import classification_report, confusion_matrix
    
    report = classification_report(y_test, y_pred, target_names=['正常', '攻击'], output_dict=True)
    logger.info("\n详细分类报告:\n" + classification_report(y_test, y_pred, target_names=['正常', '攻击']))
    
    # 5. 保存结果
    # 保存预处理器（如果之前没保存过）
    preprocessor_path = 'model/preprocessor.pkl'
    preprocessor.save_preprocessor(preprocessor_path)
    
    # 保存指标
    metrics = {
        'accuracy': float(accuracy),
        'precision': report['攻击']['precision'],
        'recall': report['攻击']['recall'],
        'f1-score': report['攻击']['f1-score'],
        'training_history': {k: [float(x) for x in v] for k, v in history.history.items()}
    }
    
    with open('model/hybrid_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)
    
    logger.info("✅ 混合模型训练并保存完成！")

if __name__ == "__main__":
    train_hybrid()
