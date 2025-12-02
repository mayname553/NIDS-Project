import csv
import json
import pandas as pd
import os

RUNTIME_CSV = "outputs/runtime_features.csv"
RUNTIME_JSON = "outputs/runtime_features.json"
FEATURES_DIR = "features"
FEATURE_MAP_FILE = "feature_mapping.csv"

def realtime_feature_collector():
    mapping_path = os.path.join(FEATURES_DIR, FEATURE_MAP_FILE)
    if not os.path.exists(mapping_path):
        print("⚠️ 特征映射文件缺失")
        return
    with open(mapping_path,"r",encoding="utf-8") as f:
        reader = csv.reader(f)
        mapped_cols = [row[0] for row in reader if row]

    row_data = None
    if os.path.exists(SAMPLE_FILE):
        df = pd.read_csv(SAMPLE_FILE)
        if not df.empty:
            row = df.sample(1, random_state=42).iloc[0].to_dict()
            row_data = {c: row.get(c,0) for c in mapped_cols}
    if row_data is None:
        row_data = {c:0 for c in mapped_cols}

    file_exists = os.path.exists(RUNTIME_CSV)
    with open(RUNTIME_CSV,"a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=mapped_cols)
        if not file_exists: writer.writeheader()
        writer.writerow(row_data)

    with open(RUNTIME_JSON,"w",encoding="utf-8") as jf:
        json.dump(row_data,jf,ensure_ascii=False,indent=2)
    print(f"✅ 实时特征采集完成 → {RUNTIME_CSV}, {RUNTIME_JSON}")
