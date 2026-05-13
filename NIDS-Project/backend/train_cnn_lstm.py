"""
CNN-LSTM深度学习模型训练脚本
作者：黄子权
任务：训练CNN-LSTM混合模型，实现申报书中的"深度学习检测引擎"
目标：准确率>85%, 召回率>75%
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CNNLSTMTrainer:
    """CNN-LSTM混合模型训练器"""

    def __init__(self):
        self.model = None
        self.history = None
        self.metrics = {}

    def load_data(self, data_path='backend/data/processed/nsl_kdd_processed.npz'):
        """加载预处理后的数据"""
        logger.info("="*60)
        logger.info("加载数据...")
        logger.info("="*60)

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"数据文件不存在: {data_path}\n请先运行 nsl_kdd_preprocessing.py")

        # 加载数据
        data = np.load(data_path, allow_pickle=True)
        X_train = data['X_train']
        X_test = data['X_test']
        y_train = data['y_train']
        y_test = data['y_test']

        logger.info(f"✅ 数据加载完成")
        logger.info(f"   训练集样本数: {len(X_train)}")
        logger.info(f"   测试集样本数: {len(X_test)}")
        logger.info(f"   特征数: {X_train.shape[1]}")

        # 为LSTM准备数据：添加时间步维度
        # 将特征reshape为 (samples, timesteps, features)
        # 这里我们将特征分成10个时间步
        n_features = X_train.shape[1]
        n_timesteps = 10
        n_features_per_step = n_features // n_timesteps

        # 截断特征以适应时间步
        X_train = X_train[:, :n_features_per_step * n_timesteps]
        X_test = X_test[:, :n_features_per_step * n_timesteps]

        # Reshape为3D
        X_train = X_train.reshape((X_train.shape[0], n_timesteps, n_features_per_step))
        X_test = X_test.reshape((X_test.shape[0], n_timesteps, n_features_per_step))

        logger.info(f"\n数据集划分:")
        logger.info(f"   训练集: {X_train.shape}")
        logger.info(f"   测试集: {X_test.shape}")

        return X_train, X_test, y_train, y_test

    def build_model(self, input_shape):
        """
        构建CNN-LSTM混合模型
        Args:
            input_shape: 输入形状 (timesteps, features)
        Returns:
            model: Keras模型
        """
        logger.info("\n" + "="*60)
        logger.info("构建CNN-LSTM混合模型...")
        logger.info("="*60)

        model = models.Sequential([
            # CNN层：提取局部特征
            layers.Conv1D(filters=64, kernel_size=3, activation='relu',
                         input_shape=input_shape, padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            layers.Dropout(0.3),

            layers.Conv1D(filters=128, kernel_size=3, activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            layers.Dropout(0.3),

            # LSTM层：捕获时序依赖
            layers.LSTM(128, return_sequences=True),
            layers.Dropout(0.3),
            layers.LSTM(64),
            layers.Dropout(0.3),

            # 全连接层
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),

            # 输出层
            layers.Dense(1, activation='sigmoid')
        ])

        # 编译模型
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.AUC(name='auc')
            ]
        )

        logger.info("\n模型架构:")
        model.summary()

        return model

    def train(self, X_train, y_train, X_test, y_test, epochs=30, batch_size=64):
        """
        训练模型
        Args:
            X_train: 训练特征
            y_train: 训练标签
            X_test: 测试特征
            y_test: 测试标签
            epochs: 训练轮数
            batch_size: 批次大小
        """
        logger.info("\n" + "="*60)
        logger.info("开始训练模型...")
        logger.info("="*60)

        logger.info(f"训练参数:")
        logger.info(f"   Epochs: {epochs}")
        logger.info(f"   Batch Size: {batch_size}")
        logger.info(f"   Optimizer: Adam (lr=0.001)")

        # 创建回调函数
        model_dir = os.path.abspath('model/trained')
        log_dir = os.path.abspath('logs')
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        callback_list = [
            # 早停
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            # 学习率衰减
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            ),
            # 保存最佳模型
            callbacks.ModelCheckpoint(
                os.path.join(model_dir, 'cnn_lstm_best.keras'),
                monitor='val_recall',
                save_best_only=True,
                verbose=1
            ),
            # TensorBoard 暂时禁用，因为路径问题
            # callbacks.TensorBoard(
            #     log_dir=log_dir,
            #     histogram_freq=1
            # )
        ]

        # 训练模型
        logger.info("\n开始训练（这可能需要10-30分钟）...")
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=callback_list,
            verbose=1
        )

        logger.info("\n✅ 训练完成！")

    def evaluate(self, X_test, y_test):
        """评估模型性能"""
        logger.info("\n" + "="*60)
        logger.info("评估模型性能...")
        logger.info("="*60)

        # 预测
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()

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
        logger.info("\n模型性能指标:")
        logger.info(f"   准确率 (Accuracy):  {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)")
        logger.info(f"   精确率 (Precision): {self.metrics['precision']:.4f} ({self.metrics['precision']*100:.2f}%)")
        logger.info(f"   召回率 (Recall):    {self.metrics['recall']:.4f} ({self.metrics['recall']*100:.2f}%)")
        logger.info(f"   F1分数 (F1-Score):  {self.metrics['f1_score']:.4f} ({self.metrics['f1_score']*100:.2f}%)")

        logger.info("\n混淆矩阵:")
        logger.info(f"              预测正常  预测攻击")
        logger.info(f"实际正常      {cm[0][0]:6d}    {cm[0][1]:6d}")
        logger.info(f"实际攻击      {cm[1][0]:6d}    {cm[1][1]:6d}")

        # 详细分类报告
        logger.info("\n详细分类报告:")
        print(classification_report(y_test, y_pred, target_names=['正常', '攻击']))

        # 检查是否达标
        if self.metrics['accuracy'] >= 0.85:
            logger.info("\n✅ 准确率达标！(>85%)")
        else:
            logger.warning(f"\n⚠️ 准确率未达标！当前: {self.metrics['accuracy']*100:.2f}%, 目标: 85%")

        if self.metrics['recall'] >= 0.75:
            logger.info("✅ 召回率达标！(>75%)")
        else:
            logger.warning(f"⚠️ 召回率未达标！当前: {self.metrics['recall']*100:.2f}%, 目标: 75%")

        return self.metrics

    def plot_training_history(self):
        """绘制训练历史"""
        logger.info("\n" + "="*60)
        logger.info("生成训练历史图表...")
        logger.info("="*60)

        os.makedirs('backend/reports/figures', exist_ok=True)

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # 1. 损失曲线
        axes[0, 0].plot(self.history.history['loss'], label='Train Loss', linewidth=2)
        axes[0, 0].plot(self.history.history['val_loss'], label='Val Loss', linewidth=2)
        axes[0, 0].set_title('Model Loss', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(alpha=0.3)

        # 2. 准确率曲线
        axes[0, 1].plot(self.history.history['accuracy'], label='Train Accuracy', linewidth=2)
        axes[0, 1].plot(self.history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
        axes[0, 1].set_title('Model Accuracy', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        axes[0, 1].grid(alpha=0.3)

        # 3. 召回率曲线
        axes[1, 0].plot(self.history.history['recall'], label='Train Recall', linewidth=2)
        axes[1, 0].plot(self.history.history['val_recall'], label='Val Recall', linewidth=2)
        axes[1, 0].set_title('Model Recall', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Recall')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)

        # 4. 精确率曲线
        axes[1, 1].plot(self.history.history['precision'], label='Train Precision', linewidth=2)
        axes[1, 1].plot(self.history.history['val_precision'], label='Val Precision', linewidth=2)
        axes[1, 1].set_title('Model Precision', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Precision')
        axes[1, 1].legend()
        axes[1, 1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig('backend/reports/figures/cnn_lstm_training_history.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("   ✅ 训练历史: backend/reports/figures/cnn_lstm_training_history.png")

    def plot_confusion_matrix(self, X_test, y_test):
        """绘制混淆矩阵"""
        y_pred = (self.model.predict(X_test, verbose=0) > 0.5).astype(int).flatten()
        cm = confusion_matrix(y_test, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['正常', '攻击'],
                    yticklabels=['正常', '攻击'])
        plt.title('CNN-LSTM Confusion Matrix', fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        plt.savefig('backend/reports/figures/cnn_lstm_confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("   ✅ 混淆矩阵: backend/reports/figures/cnn_lstm_confusion_matrix.png")

    def save_model(self, model_path='backend/model/trained/cnn_lstm_model.keras'):
        """保存模型"""
        logger.info("\n" + "="*60)
        logger.info("保存模型...")
        logger.info("="*60)

        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # 保存模型
        self.model.save(model_path)
        logger.info(f"✅ 模型已保存到: {model_path}")

        # 保存指标
        metrics_path = 'backend/model/trained/cnn_lstm_metrics.json'
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ 指标已保存到: {metrics_path}")

        # 保存训练历史
        history_path = 'backend/model/trained/cnn_lstm_history.json'
        history_dict = {k: [float(v) for v in vals] for k, vals in self.history.history.items()}
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_dict, f, indent=2)
        logger.info(f"✅ 训练历史已保存到: {history_path}")

    def generate_report(self):
        """生成训练报告"""
        report_path = 'backend/reports/模型训练报告-CNN-LSTM.md'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# CNN-LSTM深度学习模型训练报告\n\n")
            f.write(f"**训练时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**负责人**: 黄子权\n\n")

            f.write("## 1. 模型架构\n\n")
            f.write("### CNN层（特征提取）\n")
            f.write("- Conv1D(64) + BatchNorm + MaxPooling + Dropout(0.3)\n")
            f.write("- Conv1D(128) + BatchNorm + MaxPooling + Dropout(0.3)\n\n")

            f.write("### LSTM层（时序建模）\n")
            f.write("- LSTM(128, return_sequences=True) + Dropout(0.3)\n")
            f.write("- LSTM(64) + Dropout(0.3)\n\n")

            f.write("### 全连接层\n")
            f.write("- Dense(64) + BatchNorm + Dropout(0.2)\n")
            f.write("- Dense(32) + Dropout(0.2)\n")
            f.write("- Dense(1, sigmoid)\n\n")

            f.write("## 2. 训练配置\n\n")
            f.write("- Optimizer: Adam (lr=0.001)\n")
            f.write("- Loss: Binary Crossentropy\n")
            f.write("- Batch Size: 64\n")
            f.write(f"- Epochs: {len(self.history.history['loss'])}\n\n")

            f.write("## 3. 性能指标\n\n")
            f.write(f"- **准确率**: {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)\n")
            f.write(f"- **精确率**: {self.metrics['precision']:.4f} ({self.metrics['precision']*100:.2f}%)\n")
            f.write(f"- **召回率**: {self.metrics['recall']:.4f} ({self.metrics['recall']*100:.2f}%)\n")
            f.write(f"- **F1分数**: {self.metrics['f1_score']:.4f} ({self.metrics['f1_score']*100:.2f}%)\n\n")

            f.write("## 4. 可视化结果\n\n")
            f.write("### 训练历史\n")
            f.write("![Training History](figures/cnn_lstm_training_history.png)\n\n")
            f.write("### 混淆矩阵\n")
            f.write("![Confusion Matrix](figures/cnn_lstm_confusion_matrix.png)\n\n")

            f.write("## 5. 结论\n\n")
            达标 = self.metrics['accuracy'] >= 0.85 and self.metrics['recall'] >= 0.75
            if 达标:
                f.write("✅ **模型达标**：准确率>85%，召回率>75%\n")
            else:
                f.write("⚠️ **模型未完全达标**，需要进一步优化\n")

        logger.info(f"✅ 训练报告已生成: {report_path}")


def main():
    """主函数"""
    start_time = datetime.now()

    logger.info("\n" + "="*60)
    logger.info("🚀 CNN-LSTM深度学习模型训练")
    logger.info("="*60)

    try:
        # 创建训练器
        trainer = CNNLSTMTrainer()

        # 1. 加载数据
        X_train, X_test, y_train, y_test = trainer.load_data()

        # 2. 构建模型
        input_shape = (X_train.shape[1], X_train.shape[2])
        trainer.model = trainer.build_model(input_shape)

        # 3. 训练模型
        trainer.train(X_train, y_train, X_test, y_test, epochs=30, batch_size=64)

        # 4. 评估模型
        trainer.evaluate(X_test, y_test)

        # 5. 绘制结果
        trainer.plot_training_history()
        trainer.plot_confusion_matrix(X_test, y_test)

        # 6. 保存模型
        trainer.save_model()

        # 7. 生成报告
        trainer.generate_report()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "="*60)
        logger.info(f"✅ 训练流程完成！耗时: {duration/60:.2f} 分钟")
        logger.info("="*60)

        logger.info("\n📦 交付物:")
        logger.info("   1. 模型文件: backend/model/trained/cnn_lstm_model.keras")
        logger.info("   2. 性能指标: backend/model/trained/cnn_lstm_metrics.json")
        logger.info("   3. 训练报告: backend/reports/模型训练报告-CNN-LSTM.md")
        logger.info("   4. 可视化图表: backend/reports/figures/")

    except Exception as e:
        logger.error(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
