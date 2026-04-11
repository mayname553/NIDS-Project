import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, LabelEncoder

def encode_features(df):
    """对非数值列进行 Label Encoding"""
    df_encoded = df.copy()
    label_encoders = {}
    for col in df_encoded.columns:
        if df_encoded[col].dtype == 'object':
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            label_encoders[col] = le
    return df_encoded, label_encoders

def scale_features(df):
    """特征标准化"""
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    return pd.DataFrame(scaled_data, columns=df.columns), scaler

def apply_pca(df, n_components=0.95):
    """应用 PCA 降维"""
    pca = PCA(n_components=n_components)
    pca_data = pca.fit_transform(df)
    columns = [f'PC{i+1}' for i in range(pca_data.shape[1])]
    return pd.DataFrame(pca_data, columns=columns), pca

def apply_tsne(df, n_components=2, perplexity=30, n_iter=1000):
    """应用 t-SNE 降维（主要用于可视化）"""
    tsne = TSNE(n_components=n_components, perplexity=perplexity, n_iter=n_iter, random_state=42)
    tsne_data = tsne.fit_transform(df)
    columns = [f'TSNE{i+1}' for i in range(n_components)]
    return pd.DataFrame(tsne_data, columns=columns), tsne
