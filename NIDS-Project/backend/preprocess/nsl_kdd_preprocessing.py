import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import os

# 获取项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))

print(f"项目根目录: {project_root}")

# 定义列名
columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
           'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
           'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
           'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
           'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
           'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
           'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
           'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
           'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
           'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty']

# 读取数据（使用绝对路径）
train_path = os.path.join(project_root, 'dataset', 'KDDTrain+.txt')
test_path = os.path.join(project_root, 'dataset', 'KDDTest+.txt')

print(f"读取训练数据: {train_path}")
train_data = pd.read_csv(train_path, names=columns, header=None)

print(f"读取测试数据: {test_path}")
test_data = pd.read_csv(test_path, names=columns, header=None)

print(f"训练集大小: {train_data.shape}")
print(f"测试集大小: {test_data.shape}")

# 合并数据以便统一处理
all_data = pd.concat([train_data, test_data], ignore_index=True)

# 将标签转换为二分类（normal vs attack）
all_data['label'] = all_data['label'].apply(lambda x: 0 if x == 'normal' else 1)

# 删除difficulty列
all_data = all_data.drop('difficulty', axis=1)

# 对分类特征进行编码
categorical_columns = ['protocol_type', 'service', 'flag']
label_encoders = {}

for col in categorical_columns:
    le = LabelEncoder()
    all_data[col] = le.fit_transform(all_data[col])
    label_encoders[col] = le

print("分类特征编码完成")

# 分离特征和标签
X = all_data.drop('label', axis=1)
y = all_data['label']

# 标准化特征
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("特征标准化完成")

# 分割回训练集和测试集
train_size = len(train_data)
X_train = X_scaled[:train_size]
y_train = y[:train_size]
X_test = X_scaled[train_size:]
y_test = y[train_size:]

print(f"最终训练集大小: {X_train.shape}")
print(f"最终测试集大小: {X_test.shape}")
print(f"训练集攻击样本比例: {y_train.sum() / len(y_train):.2%}")
print(f"测试集攻击样本比例: {y_test.sum() / len(y_test):.2%}")

# 保存处理后的数据
output_dir = os.path.join(project_root, 'backend', 'data', 'processed')
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, 'nsl_kdd_processed.npz')
print(f"保存处理后的数据到: {output_path}")

np.savez(output_path,
         X_train=X_train,
         y_train=y_train,
         X_test=X_test,
         y_test=y_test,
         feature_names=X.columns.tolist())

print("数据预处理完成！")
