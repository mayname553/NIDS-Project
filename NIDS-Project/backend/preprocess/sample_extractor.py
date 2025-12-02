import pandas as pd
import os

SAMPLE_FILE = "outputs/sample_subset.csv"

def sample_extractor(per_class=300, max_total=1000):
    train_path, test_path = find_dataset_paths()
    _, test_df = load_dataset(train_path, test_path)
    test_df["label"] = test_df["label"].astype(str).str.strip()
    test_df["binary_label"] = test_df["label"].apply(lambda x: "normal" if x=="normal" else "attack")

    normals = test_df[test_df["binary_label"]=="normal"]
    attacks = test_df[test_df["binary_label"]=="attack"]

    sampled = []
    if len(normals)>0: sampled.append(normals.sample(min(per_class,len(normals)), random_state=42))
    if len(attacks)>0: sampled.append(attacks.sample(min(per_class,len(attacks)), random_state=42))

    subset_df = pd.concat(sampled).reset_index(drop=True)
    if len(subset_df)>max_total:
        subset_df = subset_df.sample(max_total, random_state=42)
    subset_df.to_csv(SAMPLE_FILE, index=False)
    print(f"✅ 样本抽取完成：{len(subset_df)} 条 → {SAMPLE_FILE}")
    return subset_df
