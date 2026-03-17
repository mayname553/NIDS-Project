"""
一键训练脚本
下载数据集、训练模型、保存模型
"""

import os
import sys
import io
from download_dataset import download_nsl_kdd
from data_preprocessor import DataPreprocessor
from train_model import ModelTrainer
import logging

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("\n" + "="*60)
    print("    NIDS AI Model Training System")
    print("    Network Intrusion Detection System")
    print("="*60 + "\n")

    try:
        # 步骤1: 下载数据集
        print("[1/5] Downloading NSL-KDD Dataset...")
        print("-"*60)
        train_file, test_file, columns_file = download_nsl_kdd()
        print("[OK] Dataset downloaded\n")

        # 步骤2: 数据预处理
        print("[2/5] Data Preprocessing...")
        print("-"*60)
        preprocessor = DataPreprocessor()
        X_train, y_train, X_test, y_test = preprocessor.prepare_data(train_file, test_file)
        print("[OK] Data preprocessing completed\n")

        # 步骤3: 训练模型
        print("[3/5] Training Random Forest Model...")
        print("-"*60)
        trainer = ModelTrainer(n_estimators=100, max_depth=20)
        trainer.train(X_train, y_train)
        print("[OK] Model training completed\n")

        # 步骤4: 评估模型
        print("[4/5] Evaluating Model Performance...")
        print("-"*60)
        metrics = trainer.evaluate(X_test, y_test)
        print("[OK] Model evaluation completed\n")

        # 显示特征重要性
        print("Feature Importance Analysis")
        print("-"*60)
        trainer.get_feature_importance(preprocessor.feature_columns, top_n=10)
        print()

        # 步骤5: 保存模型
        print("[5/5] Saving Model and Preprocessor...")
        print("-"*60)

        # 创建模型目录
        os.makedirs('model', exist_ok=True)

        # 保存模型
        trainer.save_model('model/nids_model.pkl', 'model/model_metrics.json')

        # 保存预处理器
        preprocessor.save_preprocessor('model/preprocessor.pkl')

        print("[OK] Model saved\n")

        # 最终总结
        print("="*60)
        print("Training Complete! Model Performance Summary:")
        print("="*60)
        print(f"  Accuracy:  {metrics['accuracy']*100:.2f}%")
        print(f"  Precision: {metrics['precision']*100:.2f}%")
        print(f"  Recall:    {metrics['recall']*100:.2f}%")
        print(f"  F1-Score:  {metrics['f1_score']*100:.2f}%")
        print("="*60)
        print("\nOutput Files:")
        print(f"  - model/nids_model.pkl       (Model file)")
        print(f"  - model/preprocessor.pkl     (Preprocessor)")
        print(f"  - model/model_metrics.json   (Performance metrics)")
        print("\nNext Step: Restart API server to load the new model")
        print("  Command: python api_server.py\n")

    except Exception as e:
        logger.error(f"训练过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
