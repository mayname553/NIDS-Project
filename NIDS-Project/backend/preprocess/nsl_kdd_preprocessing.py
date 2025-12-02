import pandas as pd
from sklearn.preprocessing import LabelEncoder

# 定义 NSL-KDD 的列名（41个特征 + 1个标签）
columns = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
    "hot", "num_failed_logins", "logged_in", "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login", "count", "srv_count",
    "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate", "dst_host_diff_srv_rate",
    "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label"
]

# 读取数据集
train_path = "data/KDDTrain+.txt"
test_path = "data/KDDTest+.txt"

train_df = pd.read_csv(train_path, names=columns)
test_df = pd.read_csv(test_path, names=columns)

print("训练集大小:", train_df.shape)
print("测试集大小:", test_df.shape)

# 类别型特征
categorical_cols = ["protocol_type", "service", "flag"]

# 针对每个类别列单独处理
for col in categorical_cols:
    # 找出训练集和测试集的所有取值
    all_values = pd.concat([train_df[col], test_df[col]], axis=0).unique()

    # 在所有值的基础上创建 LabelEncoder
    encoder = LabelEncoder()
    encoder.fit(all_values)

    # 分别编码训练集和测试集
    train_df[col] = encoder.transform(train_df[col])
    test_df[col] = encoder.transform(test_df[col])

print("\n数据示例（前5行）：")
print(train_df.head())