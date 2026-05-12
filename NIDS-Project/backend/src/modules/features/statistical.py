"""
统计特征提取模块
作者：黄博波
任务：实现流量统计特征和时间窗口特征提取
"""

import numpy as np
import pandas as pd
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatisticalFeatureExtractor:
    """
    统计特征提取器
    实现申报书中的"智能化特征提取"
    """

    def __init__(self, window_size=5):
        """
        初始化
        Args:
            window_size: 时间窗口大小（秒）
        """
        self.window_size = window_size
        logger.info(f"初始化统计特征提取器，窗口大小: {window_size}秒")

    def extract_basic_stats(self, data):
        """
        提取基础统计特征
        Args:
            data: 流量数据DataFrame
        Returns:
            features: 统计特征字典
        """
        features = {}

        # 1. 包统计特征
        features['packet_count'] = len(data)
        features['packet_rate'] = len(data) / self.window_size if self.window_size > 0 else 0

        # 2. 字节统计特征
        if 'packet_length' in data.columns:
            features['total_bytes'] = data['packet_length'].sum()
            features['byte_rate'] = features['total_bytes'] / self.window_size
            features['avg_packet_size'] = data['packet_length'].mean()
            features['std_packet_size'] = data['packet_length'].std()
            features['min_packet_size'] = data['packet_length'].min()
            features['max_packet_size'] = data['packet_length'].max()

        # 3. 流持续时间特征
        if 'timestamp' in data.columns:
            features['flow_duration'] = (data['timestamp'].max() - data['timestamp'].min())

        return features

    def extract_window_features(self, data, window_size=5):
        """
        提取滑动窗口特征
        Args:
            data: 流量数据DataFrame
            window_size: 窗口大小（秒）
        Returns:
            window_features: 窗口特征DataFrame
        """
        logger.info(f"提取滑动窗口特征，窗口大小: {window_size}秒")

        if 'timestamp' not in data.columns:
            logger.warning("数据中缺少timestamp列，无法提取窗口特征")
            return pd.DataFrame()

        # 按时间窗口分组
        data['window'] = (data['timestamp'] // window_size).astype(int)

        window_features = []
        for window_id, group in data.groupby('window'):
            features = {
                'window_id': window_id,
                'packet_count': len(group),
                'packet_rate': len(group) / window_size,
            }

            if 'packet_length' in group.columns:
                features['total_bytes'] = group['packet_length'].sum()
                features['byte_rate'] = features['total_bytes'] / window_size
                features['avg_packet_size'] = group['packet_length'].mean()
                features['std_packet_size'] = group['packet_length'].std()

            window_features.append(features)

        return pd.DataFrame(window_features)

    def extract_protocol_features(self, data):
        """
        提取协议分布特征
        Args:
            data: 流量数据DataFrame
        Returns:
            protocol_features: 协议特征字典
        """
        features = {}

        if 'protocol' in data.columns:
            protocol_counts = data['protocol'].value_counts()
            total = len(data)

            # TCP/UDP/ICMP占比
            features['tcp_ratio'] = protocol_counts.get(6, 0) / total  # TCP=6
            features['udp_ratio'] = protocol_counts.get(17, 0) / total  # UDP=17
            features['icmp_ratio'] = protocol_counts.get(1, 0) / total  # ICMP=1
            features['other_protocol_ratio'] = 1 - (features['tcp_ratio'] + features['udp_ratio'] + features['icmp_ratio'])

        return features

    def extract_port_features(self, data):
        """
        提取端口特征
        Args:
            data: 流量数据DataFrame
        Returns:
            port_features: 端口特征字典
        """
        features = {}

        if 'dst_port' in data.columns:
            # 唯一目标端口数（端口扫描指标）
            features['unique_dst_ports'] = data['dst_port'].nunique()

            # 常见端口访问次数
            common_ports = [80, 443, 22, 21, 25, 53, 3389]
            for port in common_ports:
                features[f'port_{port}_count'] = (data['dst_port'] == port).sum()

        return features

    def extract_ip_features(self, data):
        """
        提取IP特征
        Args:
            data: 流量数据DataFrame
        Returns:
            ip_features: IP特征字典
        """
        features = {}

        if 'src_ip' in data.columns:
            features['unique_src_ips'] = data['src_ip'].nunique()

        if 'dst_ip' in data.columns:
            features['unique_dst_ips'] = data['dst_ip'].nunique()

        return features

    def extract_all_features(self, data):
        """
        提取所有统计特征
        Args:
            data: 流量数据DataFrame
        Returns:
            all_features: 所有特征字典
        """
        logger.info("开始提取所有统计特征...")

        all_features = {}

        # 1. 基础统计特征
        all_features.update(self.extract_basic_stats(data))

        # 2. 协议特征
        all_features.update(self.extract_protocol_features(data))

        # 3. 端口特征
        all_features.update(self.extract_port_features(data))

        # 4. IP特征
        all_features.update(self.extract_ip_features(data))

        logger.info(f"✅ 提取完成，共 {len(all_features)} 个特征")

        return all_features


# 测试代码
if __name__ == '__main__':
    # 生成模拟数据
    np.random.seed(42)
    test_data = pd.DataFrame({
        'timestamp': np.arange(0, 100, 0.1),
        'packet_length': np.random.randint(64, 1500, 1000),
        'protocol': np.random.choice([6, 17, 1], 1000),
        'src_ip': [f'192.168.1.{np.random.randint(1, 255)}' for _ in range(1000)],
        'dst_ip': [f'10.0.0.{np.random.randint(1, 255)}' for _ in range(1000)],
        'dst_port': np.random.choice([80, 443, 22, 8080], 1000)
    })

    # 提取特征
    extractor = StatisticalFeatureExtractor(window_size=5)
    features = extractor.extract_all_features(test_data)

    print("\n提取的特征:")
    for key, value in features.items():
        print(f"  {key}: {value}")

    # 提取窗口特征
    window_features = extractor.extract_window_features(test_data, window_size=5)
    print(f"\n窗口特征数: {len(window_features)}")
    print(window_features.head())
