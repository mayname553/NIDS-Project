import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt

# === 1. 读取真实数据 ===
data = pd.read_csv("network_data.csv")  # 改成你自己的文件名
target_column = "label"  # ⚠️ 改成你的目标列名

print("✅ 成功读取数据，前5行如下：")
print(data.head())

# === 2. 分离特征和标签 ===
X = data.drop(columns=[target_column])
y = data[target_column]

# === 3. 对非数值列编码 ===
for col in X.columns:
    if X[col].dtype == 'object':
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])

# === 4. 标准化数据（用于PCA） ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === 5. 特征选择方法 1：随机森林 ===
rf = RandomForestClassifier(random_state=42)
rf.fit(X, y)
rf_importances = pd.Series(rf.feature_importances_, index=X.columns)
rf_top20 = rf_importances.sort_values(ascending=False).head(20)

# === 6. 特征选择方法 2：卡方检验 ===
chi2_selector = SelectKBest(chi2, k=min(20, X.shape[1]))
X_positive = X.copy()
X_positive[X_positive < 0] = 0  # chi2要求非负
chi2_selector.fit(X_positive, y)
chi2_scores = pd.Series(chi2_selector.scores_, index=X.columns)
chi2_top20 = chi2_scores.sort_values(ascending=False).head(20)

# === 7. 特征选择方法 3：PCA ===
pca = PCA(n_components=min(20, X.shape[1]))
pca.fit(X_scaled)
pca_importances = pd.Series(pca.explained_variance_ratio_,
                            index=X.columns[:pca.n_components_])
pca_top20 = pca_importances.head(20)

# === 8. 对比分析 ===
common_features = set(rf_top20.index) & set(chi2_top20.index) & set(pca_top20.index)
print("\n✅ 三种方法共同选中的特征：")
print(common_features)
print(f"\n共有 {len(common_features)} 个特征在三种方法中都表现突出。")

# === 9. 绘图 ===
plt.figure(figsize=(10, 6))
plt.bar(rf_top20.index, rf_top20.values, label='RandomForest')
plt.bar(chi2_top20.index, chi2_top20.values, label='Chi²', alpha=0.6)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig("feature_comparison_chart.png", dpi=300)
print("✅ 特征重要性图已保存为 feature_comparison_chart.png")