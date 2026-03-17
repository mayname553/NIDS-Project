"""
AI检测器模块
使用训练好的机器学习模型进行入侵检测
"""

import joblib
import numpy as np
import pandas as pd
import psutil
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDetector:
    def __init__(self, model_path, preprocessor_path):
        """初始化AI检测器"""
        try:
            # 加载模型
            logger.info(f"加载AI模型: {model_path}")
            self.model = joblib.load(model_path)

            # 加载预处理器
            logger.info(f"加载预处理器: {preprocessor_path}")
            preprocessor_data = joblib.load(preprocessor_path)
            self.scaler = preprocessor_data['scaler']
            self.label_encoders = preprocessor_data['label_encoders']
            self.feature_columns = preprocessor_data['feature_columns']
            self.categorical_features = preprocessor_data['categorical_features']
            self.numerical_features = preprocessor_data['numerical_features']

            logger.info("✅ AI模型加载成功")
            self.is_loaded = True

        except Exception as e:
            logger.error(f"❌ AI模型加载失败: {e}")
            self.is_loaded = False
            raise

    def extract_features_from_system(self):
        """从当前系统状态提取特征"""
        try:
            # 获取网络统计
            net_io = psutil.net_io_counters()
            net_connections = psutil.net_connections()

            # 获取系统资源
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            # 构造特征向量（简化版，映射到NSL-KDD特征空间）
            # 注意：这是一个简化的映射，实际应用中需要更精确的特征提取
            features = {
                # 网络流量特征
                'duration': 0,  # 连接持续时间（简化）
                'src_bytes': net_io.bytes_sent,
                'dst_bytes': net_io.bytes_recv,
                'land': 0,
                'wrong_fragment': 0,
                'urgent': 0,

                # 内容特征
                'hot': 0,
                'num_failed_logins': 0,
                'logged_in': 1,
                'num_compromised': 0,
                'root_shell': 0,
                'su_attempted': 0,
                'num_root': 0,
                'num_file_creations': 0,
                'num_shells': 0,
                'num_access_files': 0,
                'num_outbound_cmds': 0,
                'is_host_login': 0,
                'is_guest_login': 0,

                # 流量统计特征
                'count': len(net_connections),
                'srv_count': len([c for c in net_connections if c.status == 'ESTABLISHED']),
                'serror_rate': 0.0,
                'srv_serror_rate': 0.0,
                'rerror_rate': 0.0,
                'srv_rerror_rate': 0.0,
                'same_srv_rate': 0.5,
                'diff_srv_rate': 0.5,
                'srv_diff_host_rate': 0.0,

                # 主机特征
                'dst_host_count': len(net_connections),
                'dst_host_srv_count': len([c for c in net_connections if c.status == 'ESTABLISHED']),
                'dst_host_same_srv_rate': 0.5,
                'dst_host_diff_srv_rate': 0.5,
                'dst_host_same_src_port_rate': 0.0,
                'dst_host_srv_diff_host_rate': 0.0,
                'dst_host_serror_rate': 0.0,
                'dst_host_srv_serror_rate': 0.0,
                'dst_host_rerror_rate': 0.0,
                'dst_host_srv_rerror_rate': 0.0,

                # 类别特征（使用默认值）
                'protocol_type': 'tcp',
                'service': 'http',
                'flag': 'SF'
            }

            return features

        except Exception as e:
            logger.error(f"特征提取错误: {e}")
            return None

    def preprocess_features(self, features):
        """预处理特征"""
        try:
            # 转换为DataFrame
            df = pd.DataFrame([features])

            # 编码类别特征
            for col in self.categorical_features:
                if col in df.columns:
                    value = str(df[col].iloc[0])
                    if value in self.label_encoders[col].classes_:
                        df[col] = self.label_encoders[col].transform([value])[0]
                    else:
                        df[col] = -1  # 未知类别

            # 确保所有特征都存在
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0

            # 按正确顺序选择特征
            X = df[self.feature_columns]

            # 标准化数值特征
            X[self.numerical_features] = self.scaler.transform(X[self.numerical_features])

            return X

        except Exception as e:
            logger.error(f"特征预处理错误: {e}")
            return None

    def predict(self, features=None):
        """预测是否为攻击"""
        try:
            # 如果没有提供特征，从系统提取
            if features is None:
                features = self.extract_features_from_system()

            if features is None:
                return None, None

            # 预处理特征
            X = self.preprocess_features(features)

            if X is None:
                return None, None

            # 预测
            prediction = self.model.predict(X)[0]
            probability = self.model.predict_proba(X)[0]

            # 返回结果
            result = {
                'is_attack': bool(prediction == 1),
                'confidence': float(probability[1]),  # 攻击的概率
                'normal_probability': float(probability[0]),
                'attack_probability': float(probability[1]),
                'timestamp': datetime.now().isoformat()
            }

            return result, features

        except Exception as e:
            logger.error(f"AI预测错误: {e}")
            return None, None

    def detect_threats(self):
        """检测威胁（返回威胁列表）"""
        result, features = self.predict()

        if result is None:
            return []

        threats = []

        # 如果检测到攻击
        if result['is_attack']:
            threat = {
                'type': 'AI检测到的网络攻击',
                'severity': '高危' if result['confidence'] > 0.9 else '中危',
                'description': f"AI模型检测到可疑活动 (置信度: {result['confidence']*100:.1f}%)",
                'confidence': result['confidence'],
                'details': {
                    'normal_probability': f"{result['normal_probability']*100:.1f}%",
                    'attack_probability': f"{result['attack_probability']*100:.1f}%",
                    'detection_method': 'Random Forest ML Model'
                },
                'solution': self.get_ai_detection_solution()
            }
            threats.append(threat)

        return threats

    def get_ai_detection_solution(self):
        """AI检测到威胁的解决方案"""
        return """
        AI检测到异常活动的应对措施:
        1. 立即检查系统日志和网络连接
        2. 使用防火墙阻止可疑IP地址
        3. 运行完整的安全扫描
        4. 检查是否有未授权的进程
        5. 更新系统和安全软件
        6. 考虑隔离受影响的系统
        """

if __name__ == '__main__':
    # 测试AI检测器
    try:
        detector = AIDetector('model/nids_model.pkl', 'model/preprocessor.pkl')

        print("\n" + "="*50)
        print("测试AI检测器")
        print("="*50)

        # 运行检测
        result, features = detector.predict()

        if result:
            print(f"\n检测结果:")
            print(f"  是否为攻击: {result['is_attack']}")
            print(f"  攻击概率: {result['attack_probability']*100:.2f}%")
            print(f"  正常概率: {result['normal_probability']*100:.2f}%")
            print(f"  置信度: {result['confidence']*100:.2f}%")
        else:
            print("检测失败")

    except Exception as e:
        print(f"错误: {e}")
