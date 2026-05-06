"""
CNN-LSTM 混合模型定义
用于网络入侵检测
"""

import tensorflow as tf
from tensorflow.keras import layers, models

def create_hybrid_model(input_shape):
    """
    创建 CNN-LSTM 混合模型
    
    Args:
        input_shape: 输入特征维度 (feature_dim,)
    
    Returns:
        编译好的 Keras 模型
    """
    model = models.Sequential([
        layers.Input(shape=input_shape),
        
        layers.Reshape((input_shape[0], 1)),
        
        layers.Conv1D(64, 3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(2),
        
        layers.Conv1D(128, 3, activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling1D(2),
        
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.3),
        
        layers.LSTM(32),
        layers.Dropout(0.3),
        
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.3),
        
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model
