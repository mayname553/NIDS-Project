# 特征工程模块使用说明

本模块由黄博波开发，集成了多模态特征融合、降维、重要性分析及特征数据库管理功能。

## 1. 环境依赖
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn

## 2. 目录结构
- `backend/src/utils/feature_engineering/`: 基础变换工具 (PCA, t-SNE, Scaling, Encoding)。
- `backend/src/modules/features/`: 核心特征逻辑 (融合、分析、选择)。
- `backend/config/features/`: 特征配置与数据库持久化。

## 3. 核心功能调用示例

### 3.1 完整流水线调用
```python
from src.modules.features.pipeline import run_feature_engineering_pipeline

# 加载数据
df = pd.read_csv("your_data.csv")

# 运行流水线
X_processed, selected_features = run_feature_engineering_pipeline(df, target_col='label', top_k=20)
```

### 3.2 独立模块调用

#### 特征融合 (融合统计特征与时间窗口特征)
```python
from src.modules.features.fusion import fuse_multimodal_features
fused_df = fuse_multimodal_features(df, window_size=5)
```

#### 特征重要性分析 (RF + Chi-squared)
```python
from src.modules.features.analysis import analyze_feature_importance
importance_df = analyze_feature_importance(X, y)
```

## 4. 参数说明
- `window_size`: 滑动时间窗口的大小，默认 5。
- `top_k`: 最终选择保留的重要特征数量，默认 20。
- `n_components`: PCA 降维保留的方差比例或主成分个数。

## 5. 性能基准
- 处理 10 万条样本 (41 个原始特征) 耗时: < 5s (取决于机器性能)。
- 内存峰值: 约 500MB。
