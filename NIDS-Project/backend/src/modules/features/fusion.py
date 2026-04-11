import pandas as pd
import numpy as np

def fuse_multimodal_features(df, window_size=5):
    """
    多模态特征融合：统计特征 + 时间窗口特征。
    
    参数:
    - df: 输入原始特征 DataFrame
    - window_size: 滑动窗口大小
    
    返回:
    - 融合后的特征 DataFrame
    """
    # 1. 基础统计特征 (Statistical Features)
    # 对每行数据，增加一些横向统计量
    df_stats = df.copy()
    df_stats['row_mean'] = df.mean(axis=1)
    df_stats['row_std'] = df.std(axis=1)
    df_stats['row_max'] = df.max(axis=1)
    df_stats['row_min'] = df.min(axis=1)
    
    # 2. 时间窗口特征 (Time Window Features)
    # 假设 df 是按时间顺序排列的流量数据
    # 计算滑动窗口内的均值和方差
    df_window = df.rolling(window=window_size, min_periods=1).mean()
    df_window.columns = [f'win_mean_{c}' for c in df_window.columns]
    
    df_window_std = df.rolling(window=window_size, min_periods=1).std().fillna(0)
    df_window_std.columns = [f'win_std_{c}' for c in df_window_std.columns]
    
    # 3. 融合 (Fusion)
    fused_df = pd.concat([df_stats, df_window, df_window_std], axis=1)
    
    return fused_df

def get_feature_fusion_node(df, window_size=5):
    """
    标准化入口函数：特征融合节点
    """
    try:
        fused_df = fuse_multimodal_features(df, window_size)
        return fused_df
    except Exception as e:
        print(f"❌ 特征融合失败: {e}")
        return df
