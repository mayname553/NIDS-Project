"""
统一训练脚本 - 训练所有NIDS模型
包括: RF模型、MLP模型、混合模型和预处理器
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models

# 导入数据预处理器
from data_preprocessor import DataPreprocessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, data_dir='dataset', model_dir='../models'):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.preprocessor = DataPreprocessor()

        # 确保模型目录存在
        os.makedirs(model_dir, exist_ok=True)

    def load_and_preprocess_data(self):
        """加载和预处理数据"""
        logger.info("=" * 60)
        logger.info("步骤 1: 加载和预处理数据")
        logger.info("=" * 60)

        train_file = os.path.join(self.data_dir, 'KDDTrain+.txt')
        test_file = os.path.join(self.data_dir, 'KDDTest+.txt')

        X_train, y_train, X_test, y_test = self.preprocessor.prepare_data(train_file, test_file)

        logger.info(f"训练集: X={X_train.shape}, y={y_train.shape}")
        logger.info(f"测试集: X={X_test.shape}, y={y_test.shape}")

        return X_train, y_train, X_test, y_test

    def save_preprocessor(self):
        """保存预处理器"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤 2: 保存预处理器")
        logger.info("=" * 60)

        preprocessor_path = os.path.join(self.model_dir, 'preprocessor.pkl')
        self.preprocessor.save_preprocessor(preprocessor_path)
        logger.info(f"✓ 预处理器已保存: {preprocessor_path}")

    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """训练随机森林模型"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤 3: 训练随机森林模型")
        logger.info("=" * 60)

        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )

        logger.info("开始训练随机森林...")
        rf_model.fit(X_train, y_train)

        # 评估
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"随机森林准确率: {accuracy:.4f}")

        # 保存模型
        rf_path = os.path.join(self.model_dir, 'rf_model.pkl')
        joblib.dump(rf_model, rf_path)
        logger.info(f"✓ 随机森林模型已保存: {rf_path}")

        return rf_model

    def train_mlp(self, X_train, y_train, X_test, y_test):
        """训练MLP模型"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤 4: 训练MLP模型")
        logger.info("=" * 60)

        mlp_model = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            max_iter=50,
            random_state=42,
            verbose=True,
            early_stopping=True,
            validation_fraction=0.1
        )

        logger.info("开始训练MLP...")
        mlp_model.fit(X_train, y_train)

        # 评估
        y_pred = mlp_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"MLP准确率: {accuracy:.4f}")

        # 保存模型
        mlp_path = os.path.join(self.model_dir, 'mlp_model.pkl')
        joblib.dump(mlp_model, mlp_path)
        logger.info(f"✓ MLP模型已保存: {mlp_path}")

        return mlp_model

    def train_hybrid_model(self, X_train, y_train, X_test, y_test):
        """训练混合深度学习模型"""
        logger.info("\n" + "=" * 60)
        logger.info("步骤 5: 训练混合深度学习模型")
        logger.info("=" * 60)

        input_dim = X_train.shape[1]

        # 构建模型
        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
        )

        logger.info("模型架构:")
        model.summary()

        # 训练
        logger.info("开始训练混合模型...")
        history = model.fit(
            X_train, y_train,
            epochs=20,
            batch_size=256,
            validation_split=0.1,
            verbose=1,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2)
            ]
        )

        # 评估
        test_loss, test_acc, test_precision, test_recall = model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"混合模型 - 准确率: {test_acc:.4f}, 精确率: {test_precision:.4f}, 召回率: {test_recall:.4f}")

        # 保存模型
        hybrid_path = os.path.join(self.model_dir, 'hybrid_nids_model.keras')
        model.save(hybrid_path)
        logger.info(f"✓ 混合模型已保存: {hybrid_path}")

        return model

    def train_all(self):
        """训练所有模型"""
        logger.info("\n" + "=" * 60)
        logger.info("开始训练所有NIDS模型")
        logger.info("=" * 60)

        try:
            # 1. 加载数据
            X_train, y_train, X_test, y_test = self.load_and_preprocess_data()

            # 2. 保存预处理器
            self.save_preprocessor()

            # 3. 训练随机森林
            rf_model = self.train_random_forest(X_train, y_train, X_test, y_test)

            # 4. 训练MLP
            mlp_model = self.train_mlp(X_train, y_train, X_test, y_test)

            # 5. 训练混合模型
            hybrid_model = self.train_hybrid_model(X_train, y_train, X_test, y_test)

            logger.info("\n" + "=" * 60)
            logger.info("所有模型训练完成！")
            logger.info("=" * 60)
            logger.info(f"模型保存位置: {os.path.abspath(self.model_dir)}")
            logger.info("生成的文件:")
            logger.info("  - preprocessor.pkl")
            logger.info("  - rf_model.pkl")
            logger.info("  - mlp_model.pkl")
            logger.info("  - hybrid_nids_model.keras")

            return True

        except Exception as e:
            logger.error(f"训练过程出错: {e}", exc_info=True)
            return False

if __name__ == '__main__':
    trainer = ModelTrainer()
    success = trainer.train_all()
    sys.exit(0 if success else 1)
