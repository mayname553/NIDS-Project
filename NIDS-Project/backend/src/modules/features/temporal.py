"""
时序特征提取模块
作者：黄博波
任务：实现时间窗口特征和包间隔时间特征提取
"""

import numpy as np
import pandas as pd
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemporalFeatureExtractor:
    """
    时序特征提取器
    实现滑动窗口和时间序列特征
    """

    def __init__(self, window_size=10):
        """
        初始化
        Args:
            window_size: 滑动窗口大小
        """
        self.window_size = window_size
        logger.info(f"初始化时序特征提取器，窗口大小: {window_size}")

    def extract_packet_interval_features(self, timestamps):
        """
        提取包间隔时间特征
        Args:
            timestamps: 时间戳数组
        Returns:
            features: 包间隔特征字典
        """
        if len(timestamps) < 2:
            return {
                'avg_packet_interval': 0,
                'std_packet_interval': 0,
                'min_packet_interval': 0,
                'max_packet_interval': 0
            }

        # 计算包间隔时间
        intervals = np.diff(timestamps)

        features = {
            'avg_packet_interval': float(np.mean(intervals)),
            'std_packet_interval': float(np.std(intervals)),
            'min_packet_interval': float(np.min(intervals)),
            'max_packet_interval': float(np.max(intervals)),
            'median_packet_interval': float(np.median(intervals))
        }

        return features

    def extract_sliding_window_features(self, data, feature_col='packet_length'):
        """
        提取滑动窗口特征
        Args:
            data: 流量数据DataFrame
            feature_col: 要提取特征的列名
        Returns:
            window_features: 滑动窗口特征DataFrame
        """
        logger.info(f"提取滑动窗口特征，窗口大小: {self.window_size}")

        if feature_col not in data.columns:
            logger.warning(f"列 {feature_col} 不存在")
            return pd.DataFrame()

        values = data[feature_col].values
        window_features = []

        # 滑动窗口
        for i in range(len(values) - self.window_size + 1):
            window = values[i:i + self.window_size]

            features = {
                'window_id': i,
                'window_mean': np.mean(window),
                'window_std': np.std(window),
                'window_min': np.min(window),
                'window_max': np.max(window),
                'window_median': np.median(window),
                'window_range': np.max(window) - np.min(window),
                'window_variance': np.var(window)
            }

            window_features.append(features)

        return pd.DataFrame(window_features)

    def extract_flow_duration_features(self, data):
        """
        提取流持续时间特征
        Args:
            data: 流量数据DataFrame
        Returns:
            features: 流持续时间特征字典
        """
        if 'timestamp' not in data.columns:
            return {}

        timestamps = data['timestamp'].values
        duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0

        features = {
            'flow_duration': float(duration),
            'flow_packets_per_second': len(data) / duration if duration > 0 else 0
        }

        return features

    def extract_burst_features(self, timestamps, threshold=0.1):
        """
        提取突发流量特征
        Args:
            timestamps: 时间戳数组
            threshold: 突发阈值（秒）
        Returns:
            features: 突发特征字典
        """
        if len(timestamps) < 2:
            return {
                'burst_count': 0,
                'avg_burst_size': 0,
                'max_burst_size': 0
            }

        intervals = np.diff(timestamps)
        bursts = []
        current_burst = 1

        for interval in intervals:
            if interval < threshold:
                current_burst += 1
            else:
                if current_burst > 1:
                    bursts.append(current_burst)
                current_burst = 1

        if current_burst > 1:
            bursts.append(current_burst)

        features = {
            'burst_count': len(bursts),
            'avg_burst_size': float(np.mean(bursts)) if bursts else 0,
            'max_burst_size': float(np.max(bursts)) if bursts else 0
        }

        return features

    def extract_all_temporal_features(self, data):
        """
        提取所有时序特征
        Args:
            data: 流量数据DataFrame
        Returns:
            all_features: 所有时序特征字典
        """
        logger.info("提取所有时序特征...")

        all_features = {}

        # 1. 包间隔特征
        if 'timestamp' in data.columns:
            all_features.update(self.extract_packet_interval_features(data['timestamp'].values))

        # 2. 流持续时间特征
        all_features.update(self.extract_flow_duration_features(data))

        # 3. 突发流量特征
        if 'timestamp' in data.columns:
            all_features.update(self.extract_burst_features(data['timestamp'].values))

        logger.info(f"✅ 提取完成，共 {len(all_features)} 个时序特征")

        return all_features


# 测试代码
if __name__ == '__main__':
    # 生成模拟数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'timestamp': np.cumsum(np.random.exponential(0.01, 1000)),
        'packet_length': np.random.randint(64, 1500, 1000)
    })

    # 提取时序特征
    extractor = TemporalFeatureExtractor(window_size=10)
    features = extractor.extract_all_temporal_features(test_data)

    print("\n提取的时序特征:")
    for key, value in features.items():
        print(f"  {key}: {value}")

    # 提取滑动窗口特征
    window_features = extractor.extract_sliding_window_features(test_data, 'packet_length')
    print(f"\n滑动窗口特征数: {len(window_features)}")
    print(window_features.head())
