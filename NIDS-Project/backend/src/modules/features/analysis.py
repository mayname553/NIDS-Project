import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import chi2
from sklearn.preprocessing import MinMaxScaler

def analyze_feature_importance(X, y):
    """
    特征重要性分析：RandomForest 重要性 + Chi-squared 卡方评分。
    
    参数:
    - X: 特征 DataFrame
    - y: 标签 Series
    
    返回:
    - 包含重要性评分的 DataFrame
    """
    feature_names = X.columns
    
    # 1. 随机森林重要性 (RF Importance)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    rf_importance = rf.feature_importances_
    
    # 2. 卡方检验 (Chi-squared Test)
    # 先归一化到非负值
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    chi2_scores, p_values = chi2(X_scaled, y)
    
    # 合并结果
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'RF_Importance': rf_importance,
        'Chi2_Score': chi2_scores,
        'Mean_Importance': (rf_importance + (chi2_scores / (chi2_scores.max() if chi2_scores.max() > 0 else 1))) / 2
    }).sort_values(by='Mean_Importance', ascending=False)
    
    return importance_df

def get_feature_analysis_node(X, y):
    """
    标准化入口函数：特征分析节点
    """
    try:
        importance_df = analyze_feature_importance(X, y)
        return importance_df
    except Exception as e:
        print(f"❌ 特征分析失败: {e}")
        return None
