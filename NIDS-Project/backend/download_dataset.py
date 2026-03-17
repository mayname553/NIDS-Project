"""
NSL-KDD数据集下载工具
自动下载网络入侵检测数据集
"""

import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NSL-KDD数据集URL（使用GitHub镜像）
DATASET_URLS = {
    'train': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt',
    'test': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt',
    'columns': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/Field%20Names.txt'
}

DATASET_DIR = 'dataset'

def download_file(url, filename):
    """下载文件"""
    filepath = os.path.join(DATASET_DIR, filename)

    if os.path.exists(filepath):
        logger.info(f"文件已存在: {filename}")
        return filepath

    try:
        logger.info(f"正在下载: {filename}")
        urllib.request.urlretrieve(url, filepath)
        logger.info(f"下载完成: {filename}")
        return filepath
    except Exception as e:
        logger.error(f"下载失败 {filename}: {e}")
        raise

def download_nsl_kdd():
    """下载NSL-KDD数据集"""
    # 创建数据集目录
    os.makedirs(DATASET_DIR, exist_ok=True)

    logger.info("="*50)
    logger.info("开始下载NSL-KDD数据集")
    logger.info("="*50)

    # 下载训练集
    train_file = download_file(DATASET_URLS['train'], 'KDDTrain+.txt')

    # 下载测试集
    test_file = download_file(DATASET_URLS['test'], 'KDDTest+.txt')

    # 下载列名（可选）
    try:
        columns_file = download_file(DATASET_URLS['columns'], 'columns.txt')
    except Exception as e:
        logger.warning(f"列名文件下载失败（可选文件）: {e}")
        columns_file = None

    logger.info("="*50)
    logger.info("数据集下载完成！")
    logger.info(f"训练集: {train_file}")
    logger.info(f"测试集: {test_file}")
    if columns_file:
        logger.info(f"列名: {columns_file}")
    logger.info("="*50)

    return train_file, test_file, columns_file

if __name__ == '__main__':
    download_nsl_kdd()
