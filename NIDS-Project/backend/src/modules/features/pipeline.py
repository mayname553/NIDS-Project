import pandas as pd
from .fusion import get_feature_fusion_node
from .analysis import get_feature_analysis_node
from .selector import get_feature_selection_node
from src.utils.feature_engineering.transform import encode_features, scale_features

def run_feature_engineering_pipeline(df, target_col=None, top_k=20):
    """
    完整的特征工程流水线：
    1. 编码 (Encoding)
    2. 融合 (Fusion: Statistical + Time Window)
    3. 标准化 (Scaling)
    4. 分析 (Analysis: RF Importance)
    5. 选择与保存 (Selection & DB)
    
    参数:
    - df: 原始数据 DataFrame
    - target_col: 目标列名
    - top_k: 选择特征数量
    
    返回:
    - 处理后的 DataFrame, 选中特征列表
    """
    print("🚀 启动特征工程流水线...")
    
    # 1. 数据清洗与编码
    df_clean, encoders = encode_features(df)
    
    # 分离 X 和 y
    if target_col and target_col in df_clean.columns:
        X = df_clean.drop(columns=[target_col])
        y = df_clean[target_col]
    else:
        X = df_clean
        y = None
        
    # 2. 特征融合 (Multimodal Fusion)
    print("  - 正在执行多模态特征融合...")
    X_fused = get_feature_fusion_node(X)
    
    # 3. 特征标准化
    print("  - 正在执行特征标准化...")
    X_scaled, scaler = scale_features(X_fused)
    
    # 4. 特征重要性分析与选择 (如果 y 存在)
    selected_features = []
    if y is not None:
        print("  - 正在执行特征重要性分析...")
        importance_df = get_feature_analysis_node(X_scaled, y)
        if importance_df is not None:
            print("  - 正在选择特征并更新数据库...")
            selected_features = get_feature_selection_node(importance_df, top_k=top_k)
            X_final = X_scaled[selected_features]
        else:
            X_final = X_scaled
    else:
        X_final = X_scaled
        
    print(f"✅ 流水线执行完毕。最终特征数: {X_final.shape[1]}")
    return X_final, selected_features

if __name__ == "__main__":
    # 测试代码
    import numpy as np
    mock_data = pd.DataFrame(np.random.rand(100, 10), columns=[f'feat_{i}' for i in range(10)])
    mock_data['label'] = np.random.randint(0, 2, 100)
    
    X_res, feats = run_feature_engineering_pipeline(mock_data, target_col='label')
    print("选中特征:", feats)
