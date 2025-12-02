import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# 设置输出路径
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "balanced_subset.csv")
OUT_BAR = os.path.join(OUT_DIR, "balance_bar.png")
OUT_PIE = os.path.join(OUT_DIR, "balance_pie.png")

# 默认数据路径
DEFAULT_DATA_PATHS = [
    "data/NSL-KDDTrain+.txt",
    "data/KDDTrain+.txt",
    "NSL-KDDTrain+.txt",
    "KDDTrain+.txt"
]

COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent", "hot",
    "num_failed_logins", "logged_in", "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", "is_guest_login",
    "count", "srv_count", "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "label"
]

def find_data_path(given_path=None):
    """查找数据文件路径"""
    if given_path:
        if os.path.exists(given_path):
            return given_path
        else:
            raise FileNotFoundError(f"指定路径不存在: {given_path}")
    for p in DEFAULT_DATA_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("找不到数据文件。请把 NSL-KDDTrain+.txt 放入 data/ 或使用 --data 指定路径。")

def load_raw(path):
    """加载原始数据"""
    try:
        df = pd.read_csv(path, names=COLUMNS, header=None)
        return df
    except Exception:
        df = pd.read_csv(path, header=None)
        return df

def inspect_labels(df):
    """检查标签列"""
    last_col = df.columns[-1]
    labels = df[last_col]
    cnt = Counter(labels)
    print("\n=== 标签统计（示例） ===")
    for label, c in cnt.most_common():
        print(f"标签: {label}    数量: {c}")
    print("========================\n")
    top_labels = [l for l, _ in cnt.most_common()[:10]]
    print("每个标签的前3行示例：")
    for lab in top_labels:
        sample_rows = df[df[last_col] == lab].head(3)
        print(f"--- 标签: {lab} ---")
        print(sample_rows.head(3).to_string(index=False))
        print()
    return last_col, cnt

def parse_normal_labels(arg_str):
    """解析用户指定的normal标签"""
    if not arg_str:
        return None
    parts = [p.strip() for p in arg_str.split(",") if p.strip() != ""]
    parsed = set()
    for p in parts:
        try:
            parsed.add(int(p))
            continue
        except Exception:
            pass
        try:
            parsed.add(float(p))
            continue
        except Exception:
            pass
        parsed.add(p)
    return parsed

def balance_data(df, normal_labels_set):
    """进行数据平衡：SMOTE 或下采样"""
    df["binary_label"] = df["label"].apply(lambda x: "normal" if x in normal_labels_set else "attack")
    X = df.drop(columns=["label", "binary_label"])
    y = df["binary_label"].map({"normal": 0, "attack": 1}).values

    from collections import Counter as Cnt
    cls_count = Cnt(y)
    print("当前类别分布:", cls_count)

    from imblearn.over_sampling import SMOTE
    try:
        sm = SMOTE(random_state=42)
        X_bal, y_bal = sm.fit_resample(X, y)
        print("使用 SMOTE 进行过采样平衡...")
    except:
        print("SMOTE 不可用，使用下采样平衡...")
        min_c = min(cls_count.values())
        idx0 = np.where(y == 0)[0][:min_c]
        idx1 = np.where(y == 1)[0][:min_c]
        sel = np.concatenate([idx0, idx1])
        X_bal = X[sel]
        y_bal = y[sel]

    return X_bal, y_bal

def save_balanced_data(X_bal, y_bal, feature_names):
    """保存平衡后的数据"""
    balanced_df = pd.DataFrame(X_bal, columns=feature_names)
    balanced_df["binary_label"] = ["normal" if v == 0 else "attack" for v in y_bal]
    balanced_df.to_csv(OUT_CSV, index=False)
    print(f"✅ 已生成平衡数据: {OUT_CSV}")

    class_counts = balanced_df["binary_label"].value_counts()
    plt.figure()
    class_counts.plot(kind="bar")
    plt.title("Class Distribution After Balancing")
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.savefig(OUT_BAR)
    plt.close()

    plt.figure()
    class_counts.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Class Ratio After Balancing")
    plt.savefig(OUT_PIE)
    plt.close()

    print("✅ 已生成图表：outputs/balance_bar.png & outputs/balance_pie.png")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=None, help="数据文件路径")
    parser.add_argument("--normal-labels", type=str, default=None, help="指定 normal 标签")
    args = parser.parse_args()

    data_path = find_data_path(args.data)
    print(f"📘 正在加载数据: {data_path}")
    df = load_raw(data_path)

    last_col, cnt = inspect_labels(df)
    normal_labels_set = parse_normal_labels(args.normal_labels)

    if normal_labels_set is None:
        print("请手动输入 normal 标签集：")
        user_in = input("输入标签，例如 0 或 normal, 或 auto 自动识别：").strip()
        if user_in.lower() == "auto":
            found = [lab for lab in cnt.keys() if str(lab).lower() == "normal"]
            if found:
                normal_labels_set = set(found)
                print("自动识别到 normal 标签:", normal_labels_set)
            else:
                min_count = min(cnt.values())
                candidates = [lab for lab, c in cnt.items() if c == min_count]
                normal_labels_set = set(candidates)
                print("自动选择了最少出现的标签作为 normal:", candidates)
        else:
            normal_labels_set = parse_normal_labels(user_in)

    print("你选择的 normal 标签：", normal_labels_set)
    X_bal, y_bal = balance_data(df, normal_labels_set)
    save_balanced_data(X_bal, y_bal, df.columns[:-1])

if __name__ == "__main__":
    main()
