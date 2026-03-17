"""
数据预处理模块
处理NSL-KDD数据集，进行特征工程
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = None

        # NSL-KDD数据集的列名
        self.column_names = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
            'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
            'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
            'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
            'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
            'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
            'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
            'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type', 'difficulty'
        ]

        # 类别特征
        self.categorical_features = ['protocol_type', 'service', 'flag']

        # 数值特征
        self.numerical_features = [col for col in self.column_names
                                   if col not in self.categorical_features + ['attack_type', 'difficulty']]

    def load_data(self, filepath):
        """加载数据集"""
        logger.info(f"加载数据: {filepath}")
        df = pd.read_csv(filepath, names=self.column_names, header=None)
        logger.info(f"数据形状: {df.shape}")
        return df

    def preprocess(self, df, fit=True):
        """预处理数据"""
        logger.info("开始预处理数据...")

        # 复制数据
        data = df.copy()

        # 1. 处理标签（二分类：正常=0，攻击=1）
        data['label'] = data['attack_type'].apply(lambda x: 0 if x == 'normal' else 1)

        # 2. 编码类别特征
        for col in self.categorical_features:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                data[col] = self.label_encoders[col].fit_transform(data[col].astype(str))
            else:
                # 处理未见过的类别
                data[col] = data[col].apply(
                    lambda x: self.label_encoders[col].transform([str(x)])[0]
                    if str(x) in self.label_encoders[col].classes_
                    else -1
                )

        # 3. 提取特征和标签
        X = data[self.numerical_features + self.categorical_features]
        y = data['label']

        # 4. 标准化数值特征
        if fit:
            X[self.numerical_features] = self.scaler.fit_transform(X[self.numerical_features])
        else:
            X[self.numerical_features] = self.scaler.transform(X[self.numerical_features])

        # 保存特征列名
        if fit:
            self.feature_columns = X.columns.tolist()

        logger.info(f"预处理完成 - 特征数: {X.shape[1]}, 样本数: {X.shape[0]}")
        logger.info(f"正常样本: {(y==0).sum()}, 攻击样本: {(y==1).sum()}")

        return X, y

    def prepare_data(self, train_file, test_file):
        """准备训练和测试数据"""
        # 加载数据
        train_df = self.load_data(train_file)
        test_df = self.load_data(test_file)

        # 预处理训练集
        X_train, y_train = self.preprocess(train_df, fit=True)

        # 预处理测试集
        X_test, y_test = self.preprocess(test_df, fit=False)

        return X_train, y_train, X_test, y_test

    def save_preprocessor(self, path):
        """保存预处理器"""
        logger.info(f"保存预处理器: {path}")
        preprocessor_data = {
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'categorical_features': self.categorical_features,
            'numerical_features': self.numerical_features
        }
        joblib.dump(preprocessor_data, path)
        logger.info("预处理器保存完成")

    def load_preprocessor(self, path):
        """加载预处理器"""
        logger.info(f"加载预处理器: {path}")
        preprocessor_data = joblib.load(path)
        self.scaler = preprocessor_data['scaler']
        self.label_encoders = preprocessor_data['label_encoders']
        self.feature_columns = preprocessor_data['feature_columns']
        self.categorical_features = preprocessor_data['categorical_features']
        self.numerical_features = preprocessor_data['numerical_features']
        logger.info("预处理器加载完成")

if __name__ == '__main__':
    # 测试预处理器
    preprocessor = DataPreprocessor()
    X_train, y_train, X_test, y_test = preprocessor.prepare_data(
        'dataset/KDDTrain+.txt',
        'dataset/KDDTest+.txt'
    )
    print(f"训练集: {X_train.shape}, {y_train.shape}")
    print(f"测试集: {X_test.shape}, {y_test.shape}")
