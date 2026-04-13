import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Dropout, Flatten, Reshape
import numpy as np

def create_hybrid_model(input_shape):
    """
    创建 CNN-LSTM 混合模型
    input_shape: (features,)
    """
    model = Sequential([
        # 输入层：将 1D 特征 Reshape 为 3D (batch, steps, features) 供 Conv1D 使用
        Reshape((input_shape[0], 1), input_shape=input_shape),
        
        # CNN 层：提取空间特征
        Conv1D(filters=64, kernel_size=3, activation='relu', padding='same'),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=128, kernel_size=3, activation='relu', padding='same'),
        MaxPooling1D(pool_size=2),
        
        # LSTM 层：提取时序特征
        LSTM(64, return_sequences=True),
        LSTM(64),
        
        # 全连接层
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid') # 二分类：正常 vs 攻击
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    # 测试模型构建
    input_dim = 41 # NSL-KDD 特征数
    model = create_hybrid_model((input_dim,))
    model.summary()
