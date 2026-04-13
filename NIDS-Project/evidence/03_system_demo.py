"""
佐证材料 3：系统端到端演示脚本
运行方式：在项目根目录执行 python evidence/03_system_demo.py
功能：模拟真实检测场景，展示系统如何检测各类攻击，并生成演示报告
"""

import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

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

ATTACK_CATEGORIES = {
    'DoS':   ['neptune', 'smurf', 'back', 'pod', 'teardrop', 'land'],
    'Probe': ['ipsweep', 'portsweep', 'nmap', 'satan'],
    'R2L':   ['guess_passwd', 'ftp_write', 'imap', 'phf', 'multihop', 'warezmaster'],
    'U2R':   ['buffer_overflow', 'loadmodule', 'perl', 'rootkit'],
}


def get_category(attack_type):
    if attack_type == 'normal':
        return 'Normal'
    for cat, attacks in ATTACK_CATEGORIES.items():
        if attack_type in attacks:
            return cat
    return 'Other'


def load_model_and_preprocessor():
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    model_path = os.path.join(model_dir, 'rf_model.pkl')
    prep_path  = os.path.join(model_dir, 'preprocessor.pkl')

    if not os.path.exists(model_path):
        print("  [!] 未找到已训练模型，请先运行 02_model_evaluation.py")
        return None, None

    print(f"  加载模型：{model_path}")
    model = joblib.load(model_path)

    print(f"  加载预处理器：{prep_path}")
    prep_data = joblib.load(prep_path)

    return model, prep_data


def sample_test_records(n_normal=10, n_attack=10):
    test_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'KDDTest+.txt')
    df = pd.read_csv(test_path, names=COLUMN_NAMES, header=None)
    normal_df = df[df['attack_type'] == 'normal'].sample(n=n_normal, random_state=42)
    attack_df = df[df['attack_type'] != 'normal'].sample(n=n_attack, random_state=42)
    samples = pd.concat([normal_df, attack_df]).sample(frac=1, random_state=42).reset_index(drop=True)
    return samples


def preprocess_sample(row, prep_data):
    categorical = prep_data['categorical_features']
    numerical   = prep_data['numerical_features']
    scaler      = prep_data['scaler']
    encoders    = prep_data['label_encoders']
    data = row.copy()
    for col in categorical:
        le = encoders[col]
        val = str(data[col])
        data[col] = le.transform([val])[0] if val in le.classes_ else -1
    feature_cols = numerical + categorical
    X = pd.DataFrame([data[feature_cols]])
    X[numerical] = scaler.transform(X[numerical])
    return X


def run_demo_detection(model, prep_data, samples):
    results = []
    correct = 0
    print(f"\n  开始检测 {len(samples)} 条网络流量记录...\n")
    print(f"  {'序号':<5} {'真实标签':<12} {'预测结果':<12} {'置信度':>8} {'判断':>6} {'耗时':>8}")
    print("  " + "-" * 60)

    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        t_start = time.time()
        true_label = 'normal' if row['attack_type'] == 'normal' else 'attack'
        true_category = get_category(row['attack_type'])
        try:
            X = preprocess_sample(row, prep_data)
            pred = model.predict(X)[0]
            proba = model.predict_proba(X)[0]
            pred_label = 'normal' if pred == 0 else 'attack'
            confidence = max(proba) * 100
        except Exception:
            pred_label = 'error'
            confidence = 0.0
        elapsed = (time.time() - t_start) * 1000
        is_correct = (pred_label == true_label)
        if is_correct:
            correct += 1
        mark = 'OK' if is_correct else 'MISS'
        print(f"  {idx:<5} {true_label:<12} {pred_label:<12} {confidence:>7.1f}% {mark:>6} {elapsed:>6.1f}ms")
        results.append({
            'index': idx,
            'true_attack_type': row['attack_type'],
            'true_category': true_category,
            'true_label': true_label,
            'predicted_label': pred_label,
            'confidence': round(confidence, 2),
            'correct': is_correct,
            'elapsed_ms': round(elapsed, 2),
        })

    accuracy = correct / len(samples) * 100
    print(f"\n  演示准确率：{correct}/{len(samples)} = {accuracy:.1f}%")
    return results, accuracy


def generate_demo_report(results, accuracy):
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
    sep  = "=" * 60
    sep2 = "-" * 60
    normal_results = [r for r in results if r['true_label'] == 'normal']
    attack_results = [r for r in results if r['true_label'] == 'attack']
    tp = sum(1 for r in attack_results if r['predicted_label'] == 'attack')
    tn = sum(1 for r in normal_results if r['predicted_label'] == 'normal')
    fp = sum(1 for r in normal_results if r['predicted_label'] == 'attack')
    fn = sum(1 for r in attack_results if r['predicted_label'] == 'normal')
    avg_time = sum(r['elapsed_ms'] for r in results) / len(results)

    lines = [
        sep,
        "  系统端到端检测演示报告",
        f"  生成时间：{now}",
        sep, "",
        "一、演示说明",
        sep2,
        "  本演示从 NSL-KDD 测试集中随机抽取 20 条流量记录（10条正常 + 10条攻击），",
        "  通过已训练的随机森林模型逐条进行检测，验证系统的端到端检测能力。",
        "",
        "二、检测结果汇总",
        sep2,
        f"  总检测条数：{len(results)} 条",
        f"  正确检测数：{tp + tn} 条",
        f"  演示准确率：{accuracy:.1f}%",
        f"  平均检测耗时：{avg_time:.2f} ms/条",
        "",
        "三、混淆矩阵（演示集）",
        sep2,
        "                  预测：正常    预测：攻击",
        f"  实际：正常      {tn:>8}    {fp:>8}",
        f"  实际：攻击      {fn:>8}    {tp:>8}",
        "",
        "四、逐条检测明细",
        sep2,
        f"  {'序号':<5} {'真实类型':<18} {'真实标签':<10} {'预测结果':<10} {'置信度':>8} {'判断':>5}",
        "  " + "-" * 62,
    ]
    for r in results:
        mark = '正确' if r['correct'] else '错误'
        lines.append(
            f"  {r['index']:<5} {r['true_attack_type']:<18} {r['true_label']:<10} "
            f"{r['predicted_label']:<10} {r['confidence']:>7.1f}% {mark:>5}"
        )
    lines += [
        "",
        "五、结论",
        sep2,
        f"  在本次 {len(results)} 条样本的演示检测中，系统准确率达到 {accuracy:.1f}%，",
        f"  平均每条记录检测耗时仅 {avg_time:.2f} 毫秒，",
        "  验证了系统具备实时检测能力，能够有效区分正常流量与攻击流量。",
        "",
        sep, "  报告结束", sep,
    ]

    out_path = os.path.join(OUTPUT_DIR, 'system_demo_report.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\n  -> 演示报告已保存：{out_path}")

    json_path = os.path.join(OUTPUT_DIR, 'system_demo_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'summary': {'total': len(results), 'accuracy': accuracy,
                               'avg_time_ms': avg_time, 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn},
                   'details': results}, f, ensure_ascii=False, indent=2)
    print(f"  -> JSON 结果已保存：{json_path}")


def main():
    print("=" * 60)
    print("  系统端到端检测演示")
    print("=" * 60)
    print("\n[步骤 1/3] 加载模型...")
    model, prep_data = load_model_and_preprocessor()
    if model is None:
        sys.exit(1)
    print("\n[步骤 2/3] 抽取测试样本...")
    samples = sample_test_records(n_normal=10, n_attack=10)
    print(f"  已抽取 {len(samples)} 条样本")
    print("\n[步骤 3/3] 执行检测演示...")
    results, accuracy = run_demo_detection(model, prep_data, samples)
    generate_demo_report(results, accuracy)
    print("\n完成！")


if __name__ == '__main__':
    main()
