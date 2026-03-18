import unittest
import pandas as pd
import numpy as np
import sys
import os

# 将 backend 目录加入路径，以便导入 src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.features.fusion import fuse_multimodal_features
from src.modules.features.analysis import analyze_feature_importance
from src.modules.features.selector import select_and_save_features
from src.utils.feature_engineering.transform import encode_features, scale_features

class TestFeatureEngineering(unittest.TestCase):
    def setUp(self):
        # 准备测试数据
        self.df = pd.DataFrame({
            'feat1': np.random.rand(20),
            'feat2': np.random.rand(20),
            'cat_feat': ['A', 'B'] * 10,
            'label': [0, 1] * 10
        })

    def test_encode_features(self):
        """测试特征编码"""
        df_encoded, encoders = encode_features(self.df)
        self.assertIn('cat_feat', encoders)
        self.assertTrue(np.issubdtype(df_encoded['cat_feat'].dtype, np.integer))

    def test_scale_features(self):
        """测试特征标准化"""
        df_encoded, _ = encode_features(self.df.drop('label', axis=1))
        df_scaled, scaler = scale_features(df_encoded)
        self.assertAlmostEqual(df_scaled.mean().mean(), 0, places=5)
        self.assertAlmostEqual(df_scaled.std().mean(), 1, places=1)

    def test_feature_fusion(self):
        """测试多模态特征融合 (统计+时间窗口)"""
        df_encoded, _ = encode_features(self.df.drop('label', axis=1))
        fused_df = fuse_multimodal_features(df_encoded, window_size=3)
        # 原始特征 + row_mean/std/max/min + window_mean/std
        self.assertGreater(fused_df.shape[1], df_encoded.shape[1])
        self.assertIn('row_mean', fused_df.columns)
        self.assertIn('win_mean_feat1', fused_df.columns)

    def test_feature_importance(self):
        """测试特征重要性分析"""
        X = self.df.drop(['label', 'cat_feat'], axis=1)
        y = self.df['label']
        importance_df = analyze_feature_importance(X, y)
        self.assertEqual(len(importance_df), X.shape[1])
        self.assertIn('RF_Importance', importance_df.columns)
        self.assertIn('Chi2_Score', importance_df.columns)

    def test_feature_selection_save(self):
        """测试特征选择与数据库保存"""
        X = self.df.drop(['label', 'cat_feat'], axis=1)
        y = self.df['label']
        importance_df = analyze_feature_importance(X, y)
        selected = select_and_save_features(importance_df, top_k=2)
        self.assertEqual(len(selected), 2)
        
        # 验证数据库文件是否存在
        db_path = "backend/config/features/feature_selection_database.json"
        self.assertTrue(os.path.exists(db_path))

if __name__ == '__main__':
    unittest.main()
