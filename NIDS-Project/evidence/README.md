# 佐证材料说明

本目录包含大创项目中期汇报所需的全部佐证材料脚本及说明。

## 目录结构

```
evidence/
├── 01_dataset_analysis.py    # 数据集统计分析脚本
├── 02_model_evaluation.py    # 模型训练与评估脚本
├── 03_system_demo.py         # 系统端到端演示脚本
├── 04_run_all.py             # 一键运行所有脚本
├── README.md                 # 本说明文件
└── output/                   # 运行后自动生成的报告目录
    ├── dataset_statistics_report.txt    ← 可打印提交
    ├── dataset_statistics.json
    ├── model_evaluation_report.txt      ← 可打印提交
    ├── model_metrics.json
    ├── system_demo_report.txt           ← 可打印提交
    ├── system_demo_results.json
    └── validation_summary_report.txt    ← 可打印提交
```

## 运行方式

在项目根目录（NIDS-Project/）下执行：

```bash
# 一键运行全部（推荐）
python evidence/04_run_all.py

# 或单独运行某一步
python evidence/01_dataset_analysis.py   # 仅数据集分析
python evidence/02_model_evaluation.py   # 仅模型训练（耗时较长）
python evidence/03_system_demo.py        # 仅系统演示（需先运行02）
```

> 注意：`02_model_evaluation.py` 会重新训练模型，耗时约 2-5 分钟。

## 各脚本说明

### 01_dataset_analysis.py — 数据集统计分析
- 加载 `dataset/KDDTrain+.txt` 和 `dataset/KDDTest+.txt`
- 统计样本数量、类别分布、特征分组、数据质量
- 输出：`dataset_statistics_report.txt`（可直接打印）

### 02_model_evaluation.py — 模型训练与评估
- 完整执行：数据预处理 → 随机森林训练 → 测试集评估 → 特征重要性分析
- 保存模型到 `models/rf_model.pkl`
- 输出：`model_evaluation_report.txt`（含混淆矩阵、性能指标）

### 03_system_demo.py — 系统端到端演示
- 从测试集抽取 20 条样本（10正常 + 10攻击）
- 逐条调用已训练模型进行检测，记录耗时和准确率
- 输出：`system_demo_report.txt`（含逐条检测明细）

### 04_run_all.py — 一键验证
- 依次调用以上三个脚本
- 生成汇总报告 `validation_summary_report.txt`

## 提交给老师的材料清单

| 材料 | 文件 | 说明 |
|------|------|------|
| 数据集佐证 | `dataset_statistics_report.txt` | 证明已获取并分析 NSL-KDD 数据集 |
| 模型训练佐证 | `model_evaluation_report.txt` | 证明模型已训练，准确率 77.65% |
| 系统验证佐证 | `system_demo_report.txt` | 证明系统可端到端运行 |
| 汇总报告 | `validation_summary_report.txt` | 所有验证步骤的汇总 |
| 代码佐证 | `evidence/*.py` | 验证程序源代码 |
| 数据集文件 | `dataset/KDDTrain+.txt` 等 | 原始数据集文件 |
