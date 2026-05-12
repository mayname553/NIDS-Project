"""
特征融合模块
作者：黄博波
任务：实现PCA降维、t-SNE可视化、特征重要性分析
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureFusion:
    """特征融合器"""

    def __init__(self):
        self.pca = None
        self.tsne = None

    def apply_pca(self, X, n_components=0.95):
        """应用PCA降维"""
        logger.info("="*60)
        logger.info("应用PCA降维...")
        logger.info("="*60)

        self.pca = PCA(n_components=n_components, random_state=42)
        X_pca = self.pca.fit_transform(X)

        logger.info(f"原始特征数: {X.shape[1]}")
        logger.info(f"降维后特征数: {X_pca.shape[1]}")
        logger.info(f"保留方差比例: {self.pca.explained_variance_ratio_.sum():.4f}")

        return X_pca

    def apply_tsne(self, X, n_components=2, perplexity=30):
        """应用t-SNE降维"""
        logger.info("="*60)
        logger.info("应用t-SNE降维...")
        logger.info("="*60)

        if len(X) > 10000:
            logger.info(f"样本数过多({len(X)})，采样10000个样本")
            indices = np.random.choice(len(X), 10000, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X

        self.tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42, verbose=1)
        X_tsne = self.tsne.fit_transform(X_sample)

        logger.info(f"✅ t-SNE降维完成")
        return X_tsne

    def calculate_feature_importance(self, X, y, feature_names):
        """计算特征重要性"""
        logger.info("="*60)
        logger.info("计算特征重要性...")
        logger.info("="*60)

        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)

        importances = rf.feature_importances_
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        logger.info(f"✅ 特征重要性计算完成")
        logger.info(f"\nTop 10 最重要的特征:")
        for i, row in importance_df.head(10).iterrows():
            logger.info(f"  {i+1}. {row['feature']}: {row['importance']:.6f}")

        return importance_df

    def plot_pca_variance(self, save_path='backend/reports/figures/pca_variance.png'):
        """绘制PCA方差解释图"""
        if self.pca is None:
            logger.warning("PCA未训练，无法绘图")
            return

        logger.info("绘制PCA方差解释图...")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 方差解释比例
        axes[0].bar(range(1, len(self.pca.explained_variance_ratio_) + 1),
                    self.pca.explained_variance_ratio_)
        axes[0].set_xlabel('Principal Component', fontsize=12)
        axes[0].set_ylabel('Explained Variance Ratio', fontsize=12)
        axes[0].set_title('PCA Explained Variance Ratio', fontsize=14, fontweight='bold')
        axes[0].grid(alpha=0.3)

        # 累积方差解释比例
        cumsum = np.cumsum(self.pca.explained_variance_ratio_)
        axes[1].plot(range(1, len(cumsum) + 1), cumsum, marker='o')
        axes[1].axhline(y=0.95, color='r', linestyle='--', label='95% Variance')
        axes[1].set_xlabel('Number of Components', fontsize=12)
        axes[1].set_ylabel('Cumulative Explained Variance', fontsize=12)
        axes[1].set_title('Cumulative Explained Variance', fontsize=14, fontweight='bold')
        axes[1].legend()
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"✅ PCA方差图已保存: {save_path}")

    def plot_tsne_2d(self, X_tsne, y, save_path='backend/reports/figures/tsne_2d.png'):
        """绘制2D t-SNE可视化"""
        logger.info("绘制2D t-SNE可视化...")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=y, cmap='coolwarm', alpha=0.6, s=10)
        plt.colorbar(scatter, label='Label (0=Normal, 1=Attack)')
        plt.xlabel('t-SNE Component 1', fontsize=12)
        plt.ylabel('t-SNE Component 2', fontsize=12)
        plt.title('t-SNE 2D Visualization', fontsize=16, fontweight='bold')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"✅ 2D t-SNE图已保存: {save_path}")

    def plot_feature_importance(self, importance_df, top_n=20, save_path='backend/reports/figures/feature_importance.png'):
        """绘制特征重要性图"""
        logger.info(f"绘制特征重要性图（Top {top_n}）...")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        plt.figure(figsize=(12, 8))
        top_features = importance_df.head(top_n)
        plt.barh(range(len(top_features)), top_features['importance'].values, color='steelblue')
        plt.yticks(range(len(top_features)), top_features['feature'].values)
        plt.xlabel('Importance', fontsize=12)
        plt.title(f'Top {top_n} Feature Importance', fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"✅ 特征重要性图已保存: {save_path}")


# 测试代码
if __name__ == '__main__':
    np.random.seed(42)
    X = np.random.randn(1000, 50)
    y = np.random.randint(0, 2, 1000)
    feature_names = [f'feature_{i}' for i in range(50)]

    fusion = FeatureFusion()
    X_pca = fusion.apply_pca(X, n_components=0.95)
    fusion.plot_pca_variance()

    X_tsne = fusion.apply_tsne(X, n_components=2)
    fusion.plot_tsne_2d(X_tsne, y)

    importance_df = fusion.calculate_feature_importance(X, y, feature_names)
    fusion.plot_feature_importance(importance_df, top_n=20)

    print("\n✅ 特征融合测试完成！")
