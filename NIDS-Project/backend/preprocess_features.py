import argparse
import os
import json
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


def detect_column_types(df, label_col=None):
    """自动检测数值列与分类列（非常基础的启发式方法）。"""
    num_cols = []
    cat_cols = []
    for c in df.columns:
        if c == label_col:
            continue
        # 如果列的数据类型是数字或能被成功转为float且非缺失比例高，则视为数值型
        sample = df[c].dropna().astype(str).head(2000)
        # 判断是否都是数字（含小数）
        is_numeric = True
        for v in sample:
            try:
                float(v)
            except:
                is_numeric = False
                break
        if is_numeric:
            num_cols.append(c)
        else:
            # 否则作为分类，后续可能需要hash或embedding处理
            cat_cols.append(c)
    return num_cols, cat_cols

def custom_preprocess(df):
    """在这里加入项目特定的字段转换规则（IP->子网、timestamp->hour 等）。
    你可以根据数据集增加/调整规则。
    返回修改后的 DataFrame。
    """
    # 示例：如果有时间戳字段 named 'timestamp' 或 'time'，解析小时
    for cand in ['timestamp', 'time', 'ts']:
        if cand in df.columns:
            try:
                df[cand] = pd.to_datetime(df[cand], errors='coerce')
                df[cand + '_hour'] = df[cand].dt.hour
                df[cand + '_weekday'] = df[cand].dt.weekday
            except Exception:
                pass
    # 示例：对IP地址只提取前三段作为子网（如果存在 ip_src / ip_dst）
    for ipcol in ['src_ip', 'dst_ip', 'ip_src', 'ip_dst', 'sip', 'dip']:
        if ipcol in df.columns:
            df[ipcol + '_subnet'] = df[ipcol].astype(str).fillna('') .apply(lambda x: '.'.join(x.split('.')[:3]) if '.' in x else x)
    return df


def build_and_run_pipeline(raw_csv, label_col, topk, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(raw_csv, dtype=str)

    # 基本清洗：去除全空列
    df = df.dropna(axis=1, how='all')

    # 自定义预处理位点
    df = custom_preprocess(df)

    # 保留原始列名副本
    original_columns = list(df.columns)

    # 检查label列
    if label_col and label_col not in df.columns:
        raise ValueError(f"找不到label列: {label_col} 在输入文件中")
# 检测列类型
    num_cols, cat_cols = detect_column_types(df, label_col)

    # 确保label列数值化（如果是分类label则做编码）
    if label_col:
        # 尝试转为数字，否则做Label编码（OrdinalEncoder）
        try:
            df[label_col] = pd.to_numeric(df[label_col])
        except:
            le = OrdinalEncoder()
            df[label_col] = le.fit_transform(df[[label_col]]).astype(int)
            # 保存label编码映射
            label_map = {int(v): k for v, k in enumerate(le.categories_[0])}
            with open(os.path.join(output_dir, 'label_mapping.json'), 'w') as f:
                json.dump(label_map, f, ensure_ascii=False, indent=2)

    # 将数值列转为float
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # 简单缺失值处理策略：数值列用中位数，分类列用常量 'missing'
    num_imputer = SimpleImputer(strategy='median')
    cat_imputer = SimpleImputer(strategy='constant', fill_value='missing')

# 分类编码：如果分类基数很大（>20），使用 OrdinalEncoder（hash/embedding 可后续替换）；否则 OneHot
    small_cardinality = [c for c in cat_cols if df[c].nunique(dropna=True) <= 20]
    large_cardinality = [c for c in cat_cols if df[c].nunique(dropna=True) > 20]

    transformers = []
    if num_cols:
        transformers.append(('num', Pipeline([('imputer', num_imputer), ('scaler', StandardScaler())]), num_cols))
    if small_cardinality:
        transformers.append(('ohe', Pipeline([('imputer', cat_imputer), ('ohe', OneHotEncoder(sparse_output=False, handle_unknown='ignore'))]), small_cardinality))
    if large_cardinality:
        transformers.append(('ord', Pipeline([('imputer', cat_imputer), ('ord', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))]), large_cardinality))

    col_transformer = ColumnTransformer(transformers, remainder='drop')

    # 构造X, y
    if label_col:
        y = df[label_col]
        X = df.drop(columns=[label_col])
    else:
        y = None
        X = df

    # 为了保留列名，我们需要从 ColumnTransformer 转换后重建列名
    col_transformer.fit(X)

    # 生成训练特征名函数
    def get_feature_names(ct, input_cols):
        names = []
        for name, trans, cols in ct.transformers_:
            if name == 'remainder':
                continue
            if hasattr(trans, 'named_steps') and 'ohe' in trans.named_steps:
                ohe = trans.named_steps['ohe']
                # categories_ 里每一列对应的类别
                for i, col in enumerate(cols):
                    cats = ohe.categories_[i]
                    for cat in cats:
                        names.append(f"{col}__ohe__{cat}")
            elif hasattr(trans, 'named_steps') and 'ord' in trans.named_steps:
                for col in cols:
                    names.append(f"{col}__ord")
            else:
                for col in cols:
                    names.append(col)
        return names

    feature_names = get_feature_names(col_transformer, X.columns)

# transform X
    X_trans = col_transformer.transform(X)
    X_trans = np.asarray(X_trans)

    # 建立临时 DataFrame（训练用）
    df_train = pd.DataFrame(X_trans, columns=feature_names)

    # 将 label 移到首列
    if label_col:
        df_train.insert(0, label_col, y.values)

    # 输出 reprocessed_features.csv
    reprocessed_path = os.path.join(output_dir, 'reprocessed_features.csv')
    df_train.to_csv(reprocessed_path, index=False)

    # 输出清洗样本（前100行）
    cleaned_sample = df_train.head(100)
    cleaned_sample.to_csv(os.path.join(output_dir, 'cleaned_sample.csv'), index=False)

    # 输出特征列表
    features_list = pd.DataFrame({'training_feature': feature_names})
    features_list.to_csv(os.path.join(output_dir, 'features_list.csv'), index=False)

    # 生成训练 mapping（原始列 -> 训练特征）
    mapping_rows = []
    for name, trans, cols in col_transformer.transformers_:
        if name == 'remainder':
            continue
        if hasattr(trans, 'named_steps') and 'ohe' in trans.named_steps:
            ohe = trans.named_steps['ohe']
            for i, col in enumerate(cols):
                cats = ohe.categories_[i]
                for cat in cats:
                    mapping_rows.append({'original_column': col, 'train_feature': f"{col}__ohe__{cat}"})
        elif hasattr(trans, 'named_steps') and 'ord' in trans.named_steps:
            for col in cols:
                mapping_rows.append({'original_column': col, 'train_feature': f"{col}__ord"})
        else:
            for col in cols:
                mapping_rows.append({'original_column': col, 'train_feature': col})

    mapping_df = pd.DataFrame(mapping_rows)
    mapping_df.to_csv(os.path.join(output_dir, 'train_mapping.csv'), index=False)

    # 生成 runtime mapping 模板（假设runtime提供原始列名）
    # 在此模板中，用户需要填写如何在runtime阶段计算训练特征（例如: timestamp -> timestamp_hour）
    runtime_map = []
    for orig in mapping_df['original_column'].unique():
        runtime_map.append({'runtime_field': orig, 'how_to_compute_train_feature': 'SAME_AS_RUNTIME_OR_CUSTOM'})
    runtime_map_df = pd.DataFrame(runtime_map)
    runtime_map_df.to_csv(os.path.join(output_dir, 'runtime_mapping.csv'), index=False)

# 如果有label并且需要做特征重要性分析
    if label_col:
        # 训练一个简单的 RandomForest 来估算特征重要性
        rf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
        rf.fit(X_trans, y)
        importances = rf.feature_importances_
        feat_imp = pd.DataFrame({'feature': feature_names, 'importance': importances})
        feat_imp = feat_imp.sort_values('importance', ascending=False)
        feat_imp.to_csv(os.path.join(output_dir, 'feature_importances.csv'), index=False)

        # 选择 top-k
        topk = int(topk)
        top_features = feat_imp.head(topk)['feature'].tolist()

        # 生成一个训练用的 CSV 仅包含 label + topk 特征
        selected_cols = [label_col] + top_features
        # 从 df_train 选择（注意 df_train 列可能包含重复列）
        exist_cols = [c for c in selected_cols if c in df_train.columns]
        df_topk = df_train[exist_cols]
        df_topk.to_csv(os.path.join(output_dir, f'top{topk}_features_train.csv'), index=False)

# 保存关键特征列表
        pd.DataFrame({'top_features': top_features}).to_csv(os.path.join(output_dir, f'top{topk}_features_list.csv'), index=False)

    print('\nOutputs written to', output_dir)
    print(' - reprocessed_features.csv (所有数值化后、label在首列)')
    print(' - cleaned_sample.csv (示例样本)')
    print(' - features_list.csv (训练特征清单)')
    print(' - train_mapping.csv (原始列 -> 训练特征)')
    print(' - runtime_mapping.csv (runtime -> 训练 特征 对应模板)')
    if label_col:
        print(f' - feature_importances.csv and top{topk}_features_train.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='原始CSV文件路径')
    parser.add_argument('--label', required=False, help='标签列名（如果有）')
    parser.add_argument('--topk', default=20, help='选择多少个关键特征')
    parser.add_argument('--output_dir', default='out', help='输出目录')
    args = parser.parse_args()

    build_and_run_pipeline(args.input, args.label, args.topk, args.output_dir)
