"""
佐证材料 1：NSL-KDD 数据集统计分析脚本
运行方式：在项目根目录执行 python evidence/01_dataset_analysis.py
输出：evidence/output/ 目录下的统计报告和图表
"""

import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime

# 确保能找到 backend 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLUMN_NAMES = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
    'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
    'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
    'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
    'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
    'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
    'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'attack_type', 'difficulty'
]

FEATURE_GROUPS = {
    '基础连接特征': ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
                     'land', 'wrong_fragment', 'urgent'],
    '内容特征':     ['hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
                     'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
                     'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login'],
    '流量统计特征': ['count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
                     'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate'],
    '主机统计特征': ['dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
                     'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
                     'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
                     'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
                     'dst_host_srv_rerror_rate'],
}

ATTACK_CATEGORIES = {
    'DoS':   ['back', 'land', 'neptune', 'pod', 'smurf', 'teardrop', 'apache2',
              'udpstorm', 'processtable', 'worm'],
    'Probe': ['ipsweep', 'nmap', 'portsweep', 'satan', 'mscan', 'saint'],
    'R2L':   ['ftp_write', 'guess_passwd', 'imap', 'multihop', 'phf', 'spy',
              'warezclient', 'warezmaster', 'sendmail', 'named', 'snmpgetattack',
              'snmpguess', 'xlock', 'xsnoop', 'httptunnel'],
    'U2R':   ['buffer_overflow', 'loadmodule', 'perl', 'rootkit', 'ps',
              'sqlattack', 'xterm'],
}


def get_attack_category(attack_type):
    if attack_type == 'normal':
        return 'Normal'
    for cat, attacks in ATTACK_CATEGORIES.items():
        if attack_type in attacks:
            return cat
    return 'Other'


def load_datasets():
    base = os.path.join(os.path.dirname(__file__), '..', 'dataset')
    train_path = os.path.join(base, 'KDDTrain+.txt')
    test_path  = os.path.join(base, 'KDDTest+.txt')

    print("正在加载数据集...")
    train_df = pd.read_csv(train_path, names=COLUMN_NAMES, header=None)
    test_df  = pd.read_csv(test_path,  names=COLUMN_NAMES, header=None)
    print(f"  训练集：{len(train_df):,} 条记录")
    print(f"  测试集：{len(test_df):,} 条记录")
    return train_df, test_df


def analyze_basic_info(train_df, test_df):
    print("\n[1/5] 基本信息统计...")
    total = len(train_df) + len(test_df)

    train_normal = (train_df['attack_type'] == 'normal').sum()
    train_attack = len(train_df) - train_normal
    test_normal  = (test_df['attack_type']  == 'normal').sum()
    test_attack  = len(test_df) - test_normal

    info = {
        'dataset_name': 'NSL-KDD',
        'description': '网络入侵检测领域广泛使用的基准数据集，由加拿大网络安全研究所提供',
        'total_records': total,
        'train_set': {
            'total': len(train_df),
            'normal': int(train_normal),
            'attack': int(train_attack),
            'normal_ratio': f"{train_normal/len(train_df)*100:.2f}%",
            'attack_ratio': f"{train_attack/len(train_df)*100:.2f}%",
        },
        'test_set': {
            'total': len(test_df),
            'normal': int(test_normal),
            'attack': int(test_attack),
            'normal_ratio': f"{test_normal/len(test_df)*100:.2f}%",
            'attack_ratio': f"{test_attack/len(test_df)*100:.2f}%",
        },
        'total_features': 41,
        'feature_groups': {k: len(v) for k, v in FEATURE_GROUPS.items()},
        'categorical_features': ['protocol_type', 'service', 'flag'],
        'numerical_features_count': 38,
    }
    return info


def analyze_attack_distribution(train_df, test_df):
    print("[2/5] 攻击类型分布统计...")

    train_df = train_df.copy()
    test_df  = test_df.copy()
    train_df['category'] = train_df['attack_type'].apply(get_attack_category)
    test_df['category']  = test_df['attack_type'].apply(get_attack_category)

    train_cat = train_df['category'].value_counts().to_dict()
    test_cat  = test_df['category'].value_counts().to_dict()

    train_types = train_df['attack_type'].value_counts().head(20).to_dict()
    test_types  = test_df['attack_type'].value_counts().head(20).to_dict()

    return {
        'train_category_distribution': {k: int(v) for k, v in train_cat.items()},
        'test_category_distribution':  {k: int(v) for k, v in test_cat.items()},
        'train_top20_attack_types':    {k: int(v) for k, v in train_types.items()},
        'test_top20_attack_types':     {k: int(v) for k, v in test_types.items()},
    }


def analyze_features(train_df):
    print("[3/5] 特征统计分析...")
    categorical = ['protocol_type', 'service', 'flag']
    result = {}
    for col in categorical:
        vc = train_df[col].value_counts()
        result[col] = {
            'unique_values': int(vc.shape[0]),
            'top5': {k: int(v) for k, v in vc.head(5).items()},
        }

    numerical = [c for c in COLUMN_NAMES
                 if c not in categorical + ['attack_type', 'difficulty']]
    num_stats = train_df[numerical].describe().round(4)
    result['numerical_summary'] = {
        col: {
            'mean':  float(num_stats.loc['mean', col]),
            'std':   float(num_stats.loc['std',  col]),
            'min':   float(num_stats.loc['min',  col]),
            'max':   float(num_stats.loc['max',  col]),
        }
        for col in numerical
    }
    return result


def analyze_missing_values(train_df, test_df):
    print("[4/5] 数据质量检查...")
    train_missing = train_df.isnull().sum().sum()
    test_missing  = test_df.isnull().sum().sum()
    train_dup     = train_df.duplicated().sum()
    test_dup      = test_df.duplicated().sum()
    return {
        'train_missing_values': int(train_missing),
        'test_missing_values':  int(test_missing),
        'train_duplicates':     int(train_dup),
        'test_duplicates':      int(test_dup),
        'data_quality': '优良' if train_missing == 0 and test_missing == 0 else '存在缺失值',
    }


def generate_text_report(basic, attack_dist, quality, output_path):
    print("[5/5] 生成文本报告...")
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
    lines = []
    sep  = "=" * 60
    sep2 = "-" * 60

    lines += [
        sep,
        "  NSL-KDD 数据集统计分析报告",
        f"  生成时间：{now}",
        sep, "",
        "一、数据集概述",
        sep2,
        f"数据集名称：{basic['dataset_name']}",
        f"数据集描述：{basic['description']}",
        f"总记录数  ：{basic['total_records']:,} 条",
        f"特征总数  ：{basic['total_features']} 个（含标签列）",
        "",
        "二、数据集规模",
        sep2,
        f"{'集合':<10} {'总数':>10} {'正常流量':>10} {'攻击流量':>10} {'正常占比':>10} {'攻击占比':>10}",
        "-" * 60,
        f"{'训练集':<10} {basic['train_set']['total']:>10,} "
        f"{basic['train_set']['normal']:>10,} {basic['train_set']['attack']:>10,} "
        f"{basic['train_set']['normal_ratio']:>10} {basic['train_set']['attack_ratio']:>10}",
        f"{'测试集':<10} {basic['test_set']['total']:>10,} "
        f"{basic['test_set']['normal']:>10,} {basic['test_set']['attack']:>10,} "
        f"{basic['test_set']['normal_ratio']:>10} {basic['test_set']['attack_ratio']:>10}",
        "",
        "三、特征分组说明",
        sep2,
    ]
    for group, count in basic['feature_groups'].items():
        lines.append(f"  {group}：{count} 个特征")
    lines += [
        f"  类别特征（需编码）：{', '.join(basic['categorical_features'])}",
        f"  数值特征（需标准化）：{basic['numerical_features_count']} 个",
        "",
        "四、攻击类型分布（训练集）",
        sep2,
        f"{'攻击类别':<12} {'样本数':>10} {'占比':>10}",
        "-" * 35,
    ]
    train_total = basic['train_set']['total']
    for cat, cnt in sorted(attack_dist['train_category_distribution'].items(),
                           key=lambda x: -x[1]):
        lines.append(f"  {cat:<10} {cnt:>10,} {cnt/train_total*100:>9.2f}%")

    lines += [
        "",
        "五、攻击类型分布（测试集）",
        sep2,
        f"{'攻击类别':<12} {'样本数':>10} {'占比':>10}",
        "-" * 35,
    ]
    test_total = basic['test_set']['total']
    for cat, cnt in sorted(attack_dist['test_category_distribution'].items(),
                           key=lambda x: -x[1]):
        lines.append(f"  {cat:<10} {cnt:>10,} {cnt/test_total*100:>9.2f}%")

    lines += [
        "",
        "六、数据质量报告",
        sep2,
        f"训练集缺失值：{quality['train_missing_values']} 个",
        f"测试集缺失值：{quality['test_missing_values']} 个",
        f"训练集重复行：{quality['train_duplicates']} 条",
        f"测试集重复行：{quality['test_duplicates']} 条",
        f"数据质量评级：{quality['data_quality']}",
        "",
        "七、协议类型分布（训练集 Top 5）",
        sep2,
    ]
    for proto, cnt in attack_dist['train_top20_attack_types'].items():
        lines.append(f"  {proto:<20} {cnt:>8,} 条")

    lines += ["", sep, "  报告结束", sep]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"  → 已保存：{output_path}")


def main():
    print("=" * 60)
    print("  NSL-KDD 数据集统计分析")
    print("=" * 60)

    train_df, test_df = load_datasets()

    basic       = analyze_basic_info(train_df, test_df)
    attack_dist = analyze_attack_distribution(train_df, test_df)
    features    = analyze_features(train_df)
    quality     = analyze_missing_values(train_df, test_df)

    # 保存 JSON
    json_path = os.path.join(OUTPUT_DIR, 'dataset_statistics.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'basic': basic, 'attack_distribution': attack_dist,
                   'feature_analysis': features, 'data_quality': quality},
                  f, ensure_ascii=False, indent=2)
    print(f"\n  → JSON 已保存：{json_path}")

    # 保存文本报告
    txt_path = os.path.join(OUTPUT_DIR, 'dataset_statistics_report.txt')
    generate_text_report(basic, attack_dist, quality, txt_path)

    print("\n[完成] 数据集分析完成！")
    print(f"   输出目录：{OUTPUT_DIR}")


if __name__ == '__main__':
    main()
