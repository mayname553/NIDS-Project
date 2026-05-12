"""
RandomForest基线模型训练脚本
作者：黄子权
任务：训练RandomForest模型，作为深度学习模型的对比基线
目标：召回率>70%
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE
import joblib
import json
import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RandomForestTrainer:
    """RandomForest模型训练器"""

    def __init__(self):
        self.model = None
        self.best_params = None
        self.metrics = {}

    def load_data(self, data_path='backend/data/processed/nsl_kdd_processed.npz'):
        """
        加载预处理后的数据
        Args:
            data_path: 数据文件路径
        Returns:
            X_train, X_test, y_train, y_test
        """
        logger.info("="*60)
        logger.info("加载数据...")
        logger.info("="*60)

        if not os.path.exists(data_path):
            raise FileNotFoundError(f"数据文件不存在: {data_path}")

        # 加载数据
        data = np.load(data_path, allow_pickle=True)
        X_train = data['X_train']
        X_test = data['X_test']
        y_train = data['y_train']
        y_test = data['y_test']

        # 生成特征名称
        feature_names = [f'feature_{i}' for i in range(X_train.shape[1])]

        logger.info(f"✅ 数据加载完成")
        logger.info(f"   训练集: {len(X_train)} 条")
        logger.info(f"   测试集: {len(X_test)} 条")
        logger.info(f"   特征数: {X_train.shape[1]}")

        logger.info(f"\n训练集分布:")
        logger.info(f"   正常流量: {(y_train==0).sum()} ({(y_train==0).sum()/len(y_train)*100:.2f}%)")
        logger.info(f"   攻击流量: {(y_train==1).sum()} ({(y_train==1).sum()/len(y_train)*100:.2f}%)")

        # 应用SMOTE过采样（仅对训练集）
        logger.info(f"\n" + "="*60)
        logger.info("应用SMOTE过采样...")
        logger.info("="*60)

        logger.info(f"过采样前训练集分布:")
        logger.info(f"   正常流量: {(y_train==0).sum()} ({(y_train==0).sum()/len(y_train)*100:.2f}%)")
        logger.info(f"   攻击流量: {(y_train==1).sum()} ({(y_train==1).sum()/len(y_train)*100:.2f}%)")

        # 使用SMOTE进行过采样
        smote = SMOTE(random_state=42, k_neighbors=5)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

        logger.info(f"\n过采样后训练集分布:")
        logger.info(f"   正常流量: {(y_train_resampled==0).sum()} ({(y_train_resampled==0).sum()/len(y_train_resampled)*100:.2f}%)")
        logger.info(f"   攻击流量: {(y_train_resampled==1).sum()} ({(y_train_resampled==1).sum()/len(y_train_resampled)*100:.2f}%)")
        logger.info(f"   训练集大小: {len(X_train)} → {len(X_train_resampled)} (+{len(X_train_resampled)-len(X_train)} 条)")
        logger.info(f"✅ SMOTE过采样完成！")

        return X_train_resampled, X_test, y_train_resampled, y_test, feature_names

    def train_with_grid_search(self, X_train, y_train):
        """
        使用网格搜索训练模型
        Args:
            X_train: 训练特征
            y_train: 训练标签
        """
        logger.info("\n" + "="*60)
        logger.info("开始网格搜索最优参数...")
        logger.info("="*60)

        # 定义参数网格（优化后的参数范围，专注于召回率）
        param_grid = {
            'n_estimators': [300, 400],  # 减少选项
            'max_depth': [30, None],  # 更深的树
            'min_samples_split': [2, 5],  # 减少选项
            'min_samples_leaf': [1, 2],  # 更小的叶子节点
            'max_features': ['sqrt'],  # 只保留一个
            'class_weight': ['balanced_subsample']  # 使用更激进的类权重
        }

        logger.info("参数网格:")
        for key, values in param_grid.items():
            logger.info(f"   {key}: {values}")

        # 计算总的参数组合数
        total_combinations = 1
        for values in param_grid.values():
            total_combinations *= len(values)
        logger.info(f"\n总参数组合数: {total_combinations}")
        logger.info(f"交叉验证折数: 5")
        logger.info(f"预计训练次数: {total_combinations * 5}")

        # 创建基础模型
        rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)

        # 网格搜索（限制并行数以节省内存）
        grid_search = GridSearchCV(
            estimator=rf_base,
            param_grid=param_grid,
            cv=3,  # 减少交叉验证折数
            scoring='recall',  # 优化召回率（检测更多攻击）
            verbose=2,
            n_jobs=4,  # 限制为4个并行任务，避免内存溢出
            return_train_score=True
        )

        logger.info("\n开始网格搜索训练（使用SMOTE过采样后的数据）...")
        logger.info("⚠️ 这可能需要20-40分钟，请耐心等待...")
        grid_search.fit(X_train, y_train)

        # 保存最优参数
        self.best_params = grid_search.best_params_
        self.model = grid_search.best_estimator_

        logger.info("\n✅ 训练完成！")
        logger.info(f"最优参数: {self.best_params}")
        logger.info(f"最优召回率: {grid_search.best_score_:.4f}")

    def train_simple(self, X_train, y_train):
        """
        快速训练（不使用网格搜索）
        Args:
            X_train: 训练特征
            y_train: 训练标签
        """
        logger.info("\n" + "="*60)
        logger.info("开始快速训练...")
        logger.info("="*60)

        # 使用默认参数
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=30,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            verbose=1
        )

        logger.info("训练参数:")
        logger.info(f"   n_estimators: 200")
        logger.info(f"   max_depth: 30")
        logger.info(f"   class_weight: balanced")

        logger.info("\n开始训练...")
        self.model.fit(X_train, y_train)

        logger.info("✅ 训练完成！")

    def evaluate(self, X_test, y_test):
        """
        评估模型性能
        Args:
            X_test: 测试特征
            y_test: 测试标签
        """
        logger.info("\n" + "="*60)
        logger.info("开始模型评估...")
        logger.info("="*60)

        # 预测
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        # 计算指标
        self.metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0))
        }

        # 混淆矩阵
        cm = confusion_matrix(y_test, y_pred)
        self.metrics['confusion_matrix'] = cm.tolist()

        # 显示结果
        logger.info("\n模型性能指标:")
        logger.info(f"   准确率 (Accuracy):  {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)")
        logger.info(f"   精确率 (Precision): {self.metrics['precision']:.4f} ({self.metrics['precision']*100:.2f}%)")
        logger.info(f"   召回率 (Recall):    {self.metrics['recall']:.4f} ({self.metrics['recall']*100:.2f}%)")
        logger.info(f"   F1分数 (F1-Score):  {self.metrics['f1_score']:.4f} ({self.metrics['f1_score']*100:.2f}%)")

        logger.info("\n混淆矩阵:")
        logger.info(f"              预测正常  预测攻击")
        logger.info(f"实际正常      {cm[0][0]:6d}    {cm[0][1]:6d}")
        logger.info(f"实际攻击      {cm[1][0]:6d}    {cm[1][1]:6d}")

        # 详细分类报告
        logger.info("\n详细分类报告:")
        print(classification_report(y_test, y_pred, target_names=['正常', '攻击']))

        # 检查是否达标
        if self.metrics['recall'] >= 0.70:
            logger.info("\n✅ 召回率达标！(>70%)")
        else:
            logger.warning(f"\n⚠️ 召回率未达标！当前: {self.metrics['recall']*100:.2f}%, 目标: 70%")

        return self.metrics

    def get_feature_importance(self, feature_names, top_n=20):
        """
        获取特征重要性
        Args:
            feature_names: 特征名称列表
            top_n: 显示前N个重要特征
        """
        logger.info("\n" + "="*60)
        logger.info(f"特征重要性分析（Top {top_n}）")
        logger.info("="*60)

        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]

        logger.info(f"\n前{top_n}个最重要的特征:")
        for i in range(min(top_n, len(feature_names))):
            idx = indices[i]
            logger.info(f"{i+1:2d}. {feature_names[idx]:30s}: {importances[idx]:.6f}")

        # 保存特征重要性
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        importance_path = 'backend/reports/rf_feature_importance.csv'
        os.makedirs(os.path.dirname(importance_path), exist_ok=True)
        importance_df.to_csv(importance_path, index=False)
        logger.info(f"\n✅ 特征重要性已保存到: {importance_path}")

        return importance_df

    def plot_results(self, X_test, y_test):
        """
        绘制结果图表
        Args:
            X_test: 测试特征
            y_test: 测试标签
        """
        logger.info("\n" + "="*60)
        logger.info("生成可视化图表...")
        logger.info("="*60)

        os.makedirs('backend/reports/figures', exist_ok=True)

        # 预测
        y_pred = self.model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)

        # 图1：混淆矩阵热力图
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['正常', '攻击'],
                    yticklabels=['正常', '攻击'])
        plt.title('RandomForest Confusion Matrix', fontsize=16, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        plt.savefig('backend/reports/figures/rf_confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("   ✅ 混淆矩阵: backend/reports/figures/rf_confusion_matrix.png")

        # 图2：性能指标柱状图
        plt.figure(figsize=(10, 6))
        metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        metrics_values = [
            self.metrics['accuracy'],
            self.metrics['precision'],
            self.metrics['recall'],
            self.metrics['f1_score']
        ]
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
        bars = plt.bar(metrics_names, metrics_values, color=colors, alpha=0.8)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        plt.ylim(0, 1.1)
        plt.ylabel('Score', fontsize=12)
        plt.title('RandomForest Performance Metrics', fontsize=16, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('backend/reports/figures/rf_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("   ✅ 性能指标: backend/reports/figures/rf_metrics.png")

        logger.info("\n✅ 所有图表生成完成！")

    def save_model(self, model_path='backend/model/trained/rf_model.pkl'):
        """
        保存模型
        Args:
            model_path: 模型保存路径
        """
        logger.info("\n" + "="*60)
        logger.info("保存模型...")
        logger.info("="*60)

        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        # 保存模型
        joblib.dump(self.model, model_path)
        logger.info(f"✅ 模型已保存到: {model_path}")

        # 保存指标
        metrics_path = 'backend/model/trained/rf_metrics.json'
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ 指标已保存到: {metrics_path}")

        # 保存最优参数
        if self.best_params:
            params_path = 'backend/model/trained/rf_best_params.json'
            with open(params_path, 'w', encoding='utf-8') as f:
                json.dump(self.best_params, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ 最优参数已保存到: {params_path}")

    def generate_report(self):
        """生成训练报告"""
        report_path = 'backend/reports/模型训练报告-RandomForest.md'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# RandomForest模型训练报告\n\n")
            f.write(f"**训练时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**负责人**: 黄子权\n\n")

            f.write("## 1. 模型配置\n\n")
            if self.best_params:
                f.write("### 最优参数（网格搜索）\n\n")
                for key, value in self.best_params.items():
                    f.write(f"- {key}: {value}\n")
            else:
                f.write("### 默认参数\n\n")
                f.write("- n_estimators: 200\n")
                f.write("- max_depth: 30\n")
                f.write("- class_weight: balanced\n")

            f.write("\n## 2. 性能指标\n\n")
            f.write(f"- **准确率**: {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)\n")
            f.write(f"- **精确率**: {self.metrics['precision']:.4f} ({self.metrics['precision']*100:.2f}%)\n")
            f.write(f"- **召回率**: {self.metrics['recall']:.4f} ({self.metrics['recall']*100:.2f}%)\n")
            f.write(f"- **F1分数**: {self.metrics['f1_score']:.4f} ({self.metrics['f1_score']*100:.2f}%)\n")

            f.write("\n## 3. 可视化结果\n\n")
            f.write("### 混淆矩阵\n")
            f.write("![Confusion Matrix](figures/rf_confusion_matrix.png)\n\n")
            f.write("### 性能指标\n")
            f.write("![Metrics](figures/rf_metrics.png)\n\n")

            f.write("## 4. 结论\n\n")
            if self.metrics['recall'] >= 0.70:
                f.write("✅ **模型达标**：召回率达到70%以上的目标\n")
            else:
                f.write(f"⚠️ **模型未达标**：召回率{self.metrics['recall']*100:.2f}%，未达到70%目标\n")

        logger.info(f"✅ 训练报告已生成: {report_path}")


def main():
    """主函数"""
    start_time = datetime.now()

    logger.info("\n" + "="*60)
    logger.info("🚀 RandomForest基线模型训练")
    logger.info("="*60)

    try:
        # 创建训练器
        trainer = RandomForestTrainer()

        # 1. 加载数据
        X_train, X_test, y_train, y_test, feature_names = trainer.load_data()

        # 2. 训练模型（选择一种方式）
        # 方式1：快速训练（推荐，5-10分钟）
        # trainer.train_simple(X_train, y_train)

        # 方式2：网格搜索（耗时，10-30分钟）
        trainer.train_with_grid_search(X_train, y_train)

        # 3. 评估模型
        trainer.evaluate(X_test, y_test)

        # 4. 特征重要性
        trainer.get_feature_importance(feature_names, top_n=20)

        # 5. 绘制结果
        trainer.plot_results(X_test, y_test)

        # 6. 保存模型
        trainer.save_model()

        # 7. 生成报告
        trainer.generate_report()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "="*60)
        logger.info(f"✅ 训练流程完成！耗时: {duration:.2f} 秒")
        logger.info("="*60)

        logger.info("\n📦 交付物:")
        logger.info("   1. 模型文件: backend/model/trained/rf_model.pkl")
        logger.info("   2. 性能指标: backend/model/trained/rf_metrics.json")
        logger.info("   3. 训练报告: backend/reports/模型训练报告-RandomForest.md")
        logger.info("   4. 可视化图表: backend/reports/figures/")

    except Exception as e:
        logger.error(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
