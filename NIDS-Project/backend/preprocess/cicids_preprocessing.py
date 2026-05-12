"""
CICIDS2017数据集预处理脚本
作者：张子城
任务：将5天的CSV文件合并、清洗、平衡，生成可用于训练的数据集
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CICIDS2017Preprocessor:
    def __init__(self, data_dir='backend/dataset/cicids2017'):
        """
        初始化预处理器
        Args:
            data_dir: CICIDS2017数据集目录
        """
        self.data_dir = data_dir
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

        # CICIDS2017的5个CSV文件
        self.csv_files = [
            'Monday-WorkingHours.pcap_ISCX.csv',
            'Tuesday-WorkingHours.pcap_ISCX.csv',
            'Wednesday-workingHours.pcap_ISCX.csv',
            'Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv',
            'Friday-WorkingHours-Morning.pcap_ISCX.csv'
        ]

    def load_all_data(self):
        """
        加载并合并所有CSV文件
        Returns:
            合并后的DataFrame
        """
        logger.info("="*60)
        logger.info("开始加载CICIDS2017数据集...")
        logger.info("="*60)

        all_data = []
        for csv_file in self.csv_files:
            file_path = os.path.join(self.data_dir, csv_file)

            if not os.path.exists(file_path):
                logger.warning(f"⚠️ 文件不存在: {csv_file}")
                logger.info(f"   请从以下地址下载: https://www.unb.ca/cic/datasets/ids-2017.html")
                continue

            logger.info(f"正在加载: {csv_file}")
            try:
                df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
                logger.info(f"  ✅ 加载成功: {len(df)} 条记录")
                all_data.append(df)
            except Exception as e:
                logger.error(f"  ❌ 加载失败: {e}")
                continue

        if not all_data:
            raise FileNotFoundError("未找到任何数据文件，请先下载CICIDS2017数据集")

        # 合并所有数据
        logger.info("\n正在合并数据...")
        df_combined = pd.concat(all_data, ignore_index=True)
        logger.info(f"✅ 合并完成: 总共 {len(df_combined)} 条记录")

        return df_combined

    def clean_data(self, df):
        """
        数据清洗：处理缺失值、无穷值、重复值
        Args:
            df: 原始DataFrame
        Returns:
            清洗后的DataFrame
        """
        logger.info("\n" + "="*60)
        logger.info("开始数据清洗...")
        logger.info("="*60)

        original_size = len(df)

        # 1. 删除完全重复的行
        df = df.drop_duplicates()
        logger.info(f"1. 删除重复行: {original_size - len(df)} 条")

        # 2. 处理列名（去除空格）
        df.columns = df.columns.str.strip()

        # 3. 处理无穷值和NaN
        logger.info("2. 处理无穷值和缺失值...")
        df = df.replace([np.inf, -np.inf], np.nan)

        # 统计缺失值
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            logger.info(f"   发现缺失值: {missing_counts.sum()} 个")
            # 删除缺失值过多的列（>50%）
            threshold = len(df) * 0.5
            df = df.dropna(thresh=threshold, axis=1)
            # 填充剩余缺失值
            df = df.fillna(0)

        # 4. 确保Label列存在
        if 'Label' not in df.columns and ' Label' in df.columns:
            df.rename(columns={' Label': 'Label'}, inplace=True)

        logger.info(f"✅ 清洗完成: 剩余 {len(df)} 条记录")

        return df

    def encode_labels(self, df):
        """
        标签编码：BENIGN→0, 所有攻击→1（二分类）
        Args:
            df: DataFrame
        Returns:
            df: 编码后的DataFrame
            label_mapping: 标签映射字典
        """
        logger.info("\n" + "="*60)
        logger.info("开始标签编码...")
        logger.info("="*60)

        # 统计原始标签分布
        logger.info("原始标签分布:")
        label_counts = df['Label'].value_counts()
        for label, count in label_counts.items():
            logger.info(f"  {label}: {count} ({count/len(df)*100:.2f}%)")

        # 二分类映射：BENIGN→0, 其他→1
        df['Label_Binary'] = df['Label'].apply(lambda x: 0 if x == 'BENIGN' else 1)

        label_mapping = {
            0: 'BENIGN (正常流量)',
            1: 'ATTACK (攻击流量)'
        }

        logger.info("\n二分类标签分布:")
        binary_counts = df['Label_Binary'].value_counts()
        for label, count in binary_counts.items():
            logger.info(f"  {label_mapping[label]}: {count} ({count/len(df)*100:.2f}%)")

        return df, label_mapping

    def extract_features(self, df):
        """
        特征提取：选择数值型特征
        Args:
            df: DataFrame
        Returns:
            X: 特征矩阵
            y: 标签向量
            feature_names: 特征名称列表
        """
        logger.info("\n" + "="*60)
        logger.info("开始特征提取...")
        logger.info("="*60)

        # 分离特征和标签
        y = df['Label_Binary'].values

        # 删除非特征列
        drop_columns = ['Label', 'Label_Binary']
        # 添加可能存在的其他非数值列
        for col in df.columns:
            if df[col].dtype == 'object':
                drop_columns.append(col)

        X = df.drop(columns=drop_columns, errors='ignore')

        # 确保所有特征都是数值型
        X = X.select_dtypes(include=[np.number])

        feature_names = X.columns.tolist()
        logger.info(f"✅ 提取特征数: {len(feature_names)}")
        logger.info(f"   样本数: {len(X)}")

        return X.values, y, feature_names

    def balance_data(self, X, y):
        """
        使用SMOTE过采样平衡数据
        Args:
            X: 特征矩阵
            y: 标签向量
        Returns:
            X_balanced: 平衡后的特征矩阵
            y_balanced: 平衡后的标签向量
        """
        logger.info("\n" + "="*60)
        logger.info("开始数据平衡（SMOTE过采样）...")
        logger.info("="*60)

        # 统计平衡前的分布
        unique, counts = np.unique(y, return_counts=True)
        logger.info("平衡前:")
        for label, count in zip(unique, counts):
            logger.info(f"  类别 {label}: {count} ({count/len(y)*100:.2f}%)")

        # SMOTE过采样
        logger.info("\n正在执行SMOTE过采样...")
        smote = SMOTE(random_state=42, k_neighbors=5)
        X_balanced, y_balanced = smote.fit_resample(X, y)

        # 统计平衡后的分布
        unique, counts = np.unique(y_balanced, return_counts=True)
        logger.info("\n平衡后:")
        for label, count in zip(unique, counts):
            logger.info(f"  类别 {label}: {count} ({count/len(y_balanced)*100:.2f}%)")

        logger.info(f"\n✅ 数据平衡完成: {len(X)} → {len(X_balanced)} 条记录")

        return X_balanced, y_balanced

    def normalize_features(self, X):
        """
        特征标准化
        Args:
            X: 特征矩阵
        Returns:
            X_normalized: 标准化后的特征矩阵
        """
        logger.info("\n" + "="*60)
        logger.info("开始特征标准化...")
        logger.info("="*60)

        X_normalized = self.scaler.fit_transform(X)

        logger.info(f"✅ 标准化完成")
        logger.info(f"   均值: {X_normalized.mean():.4f}")
        logger.info(f"   标准差: {X_normalized.std():.4f}")

        return X_normalized

    def save_processed_data(self, X, y, feature_names, output_path='backend/dataset/cicids_processed.npz'):
        """
        保存处理后的数据
        Args:
            X: 特征矩阵
            y: 标签向量
            feature_names: 特征名称列表
            output_path: 输出文件路径
        """
        logger.info("\n" + "="*60)
        logger.info("保存处理后的数据...")
        logger.info("="*60)

        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存为npz格式（压缩）
        np.savez_compressed(
            output_path,
            X=X,
            y=y,
            feature_names=feature_names
        )

        logger.info(f"✅ 数据已保存到: {output_path}")
        logger.info(f"   文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

    def run_full_pipeline(self):
        """
        运行完整的预处理流程
        """
        start_time = datetime.now()
        logger.info("\n" + "="*60)
        logger.info("🚀 开始CICIDS2017数据预处理流程")
        logger.info("="*60)

        try:
            # 1. 加载数据
            df = self.load_all_data()

            # 2. 数据清洗
            df = self.clean_data(df)

            # 3. 标签编码
            df, label_mapping = self.encode_labels(df)

            # 4. 特征提取
            X, y, feature_names = self.extract_features(df)

            # 5. 数据平衡
            X_balanced, y_balanced = self.balance_data(X, y)

            # 6. 特征标准化
            X_normalized = self.normalize_features(X_balanced)

            # 7. 保存数据
            self.save_processed_data(X_normalized, y_balanced, feature_names)

            # 8. 生成统计报告
            self.generate_report(df, X_normalized, y_balanced, feature_names)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info("\n" + "="*60)
            logger.info(f"✅ 预处理流程完成！耗时: {duration:.2f} 秒")
            logger.info("="*60)

        except Exception as e:
            logger.error(f"\n❌ 预处理失败: {e}")
            raise

    def generate_report(self, df, X, y, feature_names):
        """
        生成数据处理报告
        """
        report_path = 'backend/reports/数据处理报告.md'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# CICIDS2017数据处理报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 1. 数据集概览\n\n")
            f.write(f"- 原始记录数: {len(df)}\n")
            f.write(f"- 处理后记录数: {len(X)}\n")
            f.write(f"- 特征数: {len(feature_names)}\n\n")

            f.write("## 2. 标签分布\n\n")
            unique, counts = np.unique(y, return_counts=True)
            for label, count in zip(unique, counts):
                f.write(f"- 类别 {label}: {count} ({count/len(y)*100:.2f}%)\n")

            f.write("\n## 3. 特征列表\n\n")
            for i, name in enumerate(feature_names[:20], 1):  # 只显示前20个
                f.write(f"{i}. {name}\n")
            if len(feature_names) > 20:
                f.write(f"... (共{len(feature_names)}个特征)\n")

        logger.info(f"✅ 报告已生成: {report_path}")


if __name__ == '__main__':
    # 运行预处理流程
    preprocessor = CICIDS2017Preprocessor()
    preprocessor.run_full_pipeline()
