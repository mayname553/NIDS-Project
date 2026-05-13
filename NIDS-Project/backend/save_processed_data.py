"""
保存预处理后的数据为.npz格式
"""
import numpy as np
from data_preprocessor import DataPreprocessor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 初始化预处理器
    preprocessor = DataPreprocessor()

    # 加载和预处理数据
    X_train, y_train, X_test, y_test = preprocessor.prepare_data(
        'dataset/KDDTrain+.txt',
        'dataset/KDDTest+.txt'
    )

    # 转换为numpy数组
    X_train = X_train.values
    y_train = y_train.values
    X_test = X_test.values
    y_test = y_test.values

    # 创建输出目录
    import os
    output_dir = 'backend/data/processed'
    os.makedirs(output_dir, exist_ok=True)

    # 保存为.npz格式
    output_path = os.path.join(output_dir, 'nsl_kdd_processed.npz')
    np.savez(
        output_path,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test
    )

    logger.info(f"数据已保存到: {output_path}")
    logger.info(f"训练集: {X_train.shape}, 测试集: {X_test.shape}")

    # 保存预处理器
    preprocessor.save_preprocessor('backend/data/processed/preprocessor.pkl')
    logger.info("预处理器已保存")

if __name__ == "__main__":
    main()
