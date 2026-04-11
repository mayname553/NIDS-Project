import pandas as pd
import os
import json

CONFIG_DIR = "backend/config/features/"
DATABASE_FILE = os.path.join(CONFIG_DIR, "feature_selection_database.json")

def select_and_save_features(importance_df, top_k=20):
    """
    特征选择并保存到特征数据库。
    
    参数:
    - importance_df: 包含特征重要性评分的 DataFrame
    - top_k: 选择前 k 个特征
    
    返回:
    - 选中特征列表
    """
    # 1. 特征选择 (Selection)
    selected_features = importance_df['Feature'].head(top_k).tolist()
    
    # 2. 建立特征数据库 (Database)
    # 实际上是持久化保存特征选择结果和权重
    feature_db = {
        'top_k': top_k,
        'selected_features': selected_features,
        'feature_details': importance_df.head(top_k).to_dict(orient='records')
    }
    
    # 确保配置目录存在
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # 3. 持久化 (Persistence)
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(feature_db, f, ensure_ascii=False, indent=2)
    
    return selected_features

def get_feature_selection_node(importance_df, top_k=20):
    """
    标准化入口函数：特征选择节点
    """
    try:
        selected_features = select_and_save_features(importance_df, top_k)
        return selected_features
    except Exception as e:
        print(f"❌ 特征选择失败: {e}")
        return []
