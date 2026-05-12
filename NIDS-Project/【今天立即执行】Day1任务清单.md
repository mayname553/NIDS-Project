# 📋 Day 1 任务清单（今天立即执行）

**日期**：2026年4月16日  
**截止时间**：今晚9点提交日报

---

## 🎯 张子城（数据处理专员）- 4小时

### 任务1：下载CICIDS2017数据集（2小时）

**步骤**：
```bash
# 方式1：官网下载（推荐）
访问：https://www.unb.ca/cic/datasets/ids-2017.html
下载5个CSV文件到：D:\大学\大创\执行文件\NIDS-Project\backend\dataset\cicids2017\

# 方式2：百度网盘（备用）
搜索关键词："CICIDS2017 百度网盘"
找到资源后下载

# 需要下载的文件：
1. Monday-WorkingHours.pcap_ISCX.csv
2. Tuesday-WorkingHours.pcap_ISCX.csv
3. Wednesday-workingHours.pcap_ISCX.csv
4. Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
5. Friday-WorkingHours-Morning.pcap_ISCX.csv
```

**验证**：
```bash
# 检查文件是否下载完整
cd D:\大学\大创\执行文件\NIDS-Project\backend\dataset\cicids2017
dir
# 应该看到5个CSV文件，总大小约8GB
```

### 任务2：运行数据加载测试（1小时）

**步骤**：
```bash
cd D:\大学\大创\执行文件\NIDS-Project\backend\preprocess
python cicids_preprocessing.py
```

**预期输出**：
- 显示每个CSV文件的加载进度
- 显示数据集基本信息（行数、列数、标签分布）

### 任务3：查看数据集结构（1小时）

**步骤**：
```python
# 在Python中运行
import pandas as pd

# 加载第一个文件
df = pd.read_csv('backend/dataset/cicids2017/Monday-WorkingHours.pcap_ISCX.csv')

# 查看基本信息
print(f"行数: {len(df)}")
print(f"列数: {df.shape[1]}")
print(f"\n列名:\n{df.columns.tolist()}")
print(f"\n标签分布:\n{df['Label'].value_counts()}")

# 保存到Excel
df.describe().to_excel('backend/reports/数据集统计信息.xlsx')
```

### 交付物（今晚9点前）

- ✅ 5个CSV文件下载完成截图
- ✅ 数据集基本信息文档（Excel或Markdown）
- ✅ 日报（格式见下方）

---

## 🎯 黄博波（特征工程专员）- 4小时

### 任务1：创建特征工程模块结构（1小时）

**步骤**：
```bash
cd D:\大学\大创\执行文件\NIDS-Project

# 创建目录
mkdir backend\src\modules\features
mkdir backend\config\features
mkdir backend\reports\figures

# 创建__init__.py文件
type nul > backend\src\__init__.py
type nul > backend\src\modules\__init__.py
type nul > backend\src\modules\features\__init__.py
```

### 任务2：实现统计特征提取（3小时）

**步骤**：
```bash
# 已提供完整代码模板
# 文件位置：backend/src/modules/features/statistical.py

# 运行测试
cd backend\src\modules\features
python statistical.py
```

**预期输出**：
- 显示提取的统计特征
- 显示窗口特征数量
- 无报错

### 任务3：编写单元测试（可选）

**步骤**：
```python
# 测试statistical.py的功能
import numpy as np
import pandas as pd
from statistical import StatisticalFeatureExtractor

# 生成测试数据
test_data = pd.DataFrame({
    'timestamp': np.arange(0, 100, 0.1),
    'packet_length': np.random.randint(64, 1500, 1000),
    'protocol': np.random.choice([6, 17, 1], 1000)
})

# 提取特征
extractor = StatisticalFeatureExtractor(window_size=5)
features = extractor.extract_all_features(test_data)

print("✅ 测试通过！")
```

### 交付物（今晚9点前）

- ✅ statistical.py（150行代码）
- ✅ 单元测试通过截图
- ✅ 日报

---

## 🎯 黄子权（模型训练专员）- 4小时

### 任务1：安装TensorFlow环境（1小时）

**步骤**：
```bash
# 打开命令行
cd D:\大学\大创\执行文件\NIDS-Project\backend

# 安装TensorFlow
pip install tensorflow==2.15.0 keras==3.0.0

# 验证安装
python -c "import tensorflow as tf; print('TensorFlow版本:', tf.__version__)"
python -c "import keras; print('Keras版本:', keras.__version__)"

# 检查GPU（如果有）
python -c "import tensorflow as tf; print('GPU可用:', len(tf.config.list_physical_devices('GPU')) > 0)"
```

**预期输出**：
```
TensorFlow版本: 2.15.0
Keras版本: 3.0.0
GPU可用: True/False
```

### 任务2：学习TensorFlow基础（2小时）

**学习资源**：
1. 官方快速入门：https://www.tensorflow.org/tutorials/quickstart/beginner
2. Keras Sequential模型：https://keras.io/guides/sequential_model/
3. 二分类示例：https://www.tensorflow.org/tutorials/keras/classification

**学习任务**：
- 运行官方示例代码
- 理解Sequential模型构建
- 理解compile和fit方法
- 截图保存学习笔记

### 任务3：编写RandomForest基线模型框架（1小时）

**步骤**：
```bash
# 已提供完整代码模板
# 文件位置：backend/train_baseline.py

# 查看代码结构
cd backend
type train_baseline.py

# 暂时不运行（等数据预处理完成）
```

**任务**：
- 阅读train_baseline.py代码
- 理解RandomForest训练流程
- 标注不理解的地方

### 交付物（今晚9点前）

- ✅ TensorFlow安装成功截图
- ✅ 学习笔记（截图或文档）
- ✅ train_baseline.py代码阅读笔记
- ✅ 日报

---

## 🎯 龚斯哲（前端优化专员）- 3小时

### 任务1：修复前端API错误处理（2小时）

**步骤**：
```bash
# 打开文件
cd D:\大学\大创\执行文件\NIDS-Project\frontend\neurosec-ai-ids
notepad script.js
```

**修改内容**：
在script.js开头添加以下代码：

```javascript
// 添加错误处理和重试机制
async function fetchWithRetry(url, options = {}, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`请求失败 (尝试 ${i + 1}/${retries}):`, error);
            if (i === retries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}

// 测试后端连接
async function testBackendConnection() {
    try {
        const response = await fetchWithRetry('http://localhost:5000/api/health');
        console.log('✅ 后端连接成功:', response);
        return true;
    } catch (error) {
        console.error('❌ 后端连接失败:', error);
        alert('无法连接到后端服务器，请确保后端已启动');
        return false;
    }
}

// 页面加载时测试连接
window.addEventListener('DOMContentLoaded', () => {
    testBackendConnection();
});
```

### 任务2：测试所有API接口（1小时）

**步骤**：
```bash
# 1. 启动后端（如果还没启动）
cd D:\大学\大创\执行文件\NIDS-Project\backend
python api_server.py

# 2. 打开前端
cd ..\frontend\neurosec-ai-ids
start index.html

# 3. 打开浏览器控制台（F12）
# 4. 测试每个API接口
```

**测试清单**：
- [ ] /api/health - 健康检查
- [ ] /api/stats - 统计信息
- [ ] /api/detect - 检测接口
- [ ] /api/model/info - 模型信息
- [ ] 其他接口...

**记录格式**：
```
接口名称 | 状态 | 响应时间 | 备注
/api/health | ✅ | 50ms | 正常
/api/stats | ❌ | - | 404错误
...
```

### 交付物（今晚9点前）

- ✅ 修复后的script.js
- ✅ API测试报告（Excel或Markdown）
- ✅ 测试截图（浏览器控制台）
- ✅ 日报

---

## 🎯 你（项目负责人）- 3小时

### 任务1：修复TensorFlow环境（1小时）

**步骤**：
```bash
cd D:\大学\大创\执行文件\NIDS-Project\backend

# 安装所有依赖
pip install tensorflow==2.15.0
pip install keras==3.0.0
pip install imbalanced-learn
pip install scikit-learn
pip install pandas numpy matplotlib seaborn
pip install flask flask-cors

# 验证安装
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
python -c "from imblearn.over_sampling import SMOTE; print('SMOTE已安装')"
python -c "import sklearn; print('scikit-learn:', sklearn.__version__)"
```

### 任务2：创建工作目录（30分钟）

**步骤**：
```bash
cd D:\大学\大创\执行文件\NIDS-Project

# 创建所有必要的目录
mkdir backend\dataset\cicids2017
mkdir backend\dataset\processed
mkdir backend\model\trained
mkdir backend\reports\figures
mkdir backend\logs
mkdir backend\tests

# 验证目录结构
tree /F
```

### 任务3：下发任务给组员（1.5小时）

**步骤**：
1. 将以下文件发送给所有组员：
   - 14天冲刺任务详细分配.md
   - 【今天立即执行】Day1任务清单.md

2. 在群里@每个人：
```
@张子城 @黄博波 @黄子权 @龚斯哲

【紧急通知】14天冲刺计划正式启动！

请立即查收以下文件：
1. 14天冲刺任务详细分配.md（总体计划）
2. 【今天立即执行】Day1任务清单.md（今天的具体任务）

要求：
- 今天必须完成Day1的所有任务
- 今晚9点前在群里提交日报
- 遇到问题立即在群里提出

日报格式见文档末尾，请严格按照格式提交！

现在开始执行！💪
```

3. 建立每日9点日报制度

### 交付物（今晚9点前）

- ✅ TensorFlow安装成功截图
- ✅ 目录结构截图
- ✅ 任务分配确认表（每人回复"收到"）
- ✅ 日报

---

## 📝 日报格式（所有人必须遵守）

**提交时间**：每天晚上9点  
**提交方式**：在微信群里发送

**格式模板**：
```
【Day 1 日报 - 姓名】

✅ 完成任务：
1. xxx（具体描述，不要只写"完成了"）
2. xxx（具体描述）

❌ 遇到的问题：
1. xxx（问题描述 + 尝试的解决方法）
2. xxx（如果没有问题，写"无"）

📅 明日计划：
1. xxx（明天要做什么）
2. xxx（明天要做什么）

🔗 代码提交：
- Git commit: https://github.com/xxx/commit/abc123
- 或截图证明

📊 今日工作时长：X小时

💬 其他说明：
（可选，有什么想说的）
```

**示例**：
```
【Day 1 日报 - 张子城】

✅ 完成任务：
1. CICIDS2017数据集下载完成，5个CSV文件共8.2GB
2. 运行cicids_preprocessing.py，成功加载Monday数据，共445,909条记录
3. 生成数据集统计信息Excel文件，包含78个特征的描述性统计

❌ 遇到的问题：
1. 下载速度较慢，使用了百度网盘加速
2. 第一次运行时出现内存不足，调整了pandas的chunksize参数解决

📅 明日计划：
1. 完成数据预处理脚本（cicids_preprocessing.py）
2. 处理缺失值和无穷值
3. 应用SMOTE过采样

🔗 代码提交：
- 截图：[附上数据加载成功的截图]

📊 今日工作时长：4小时

💬 其他说明：
数据集比预期大，明天预处理可能需要更多时间
```

---

## ⚠️ 重要提醒

1. **今天必须完成Day1的所有任务**
2. **今晚9点前必须提交日报**
3. **遇到问题立即在群里提出，不要拖到明天**
4. **如果任务无法完成，必须提前说明原因**
5. **代码必须有注释，方便其他人理解**

---

## 🆘 紧急联系

- **技术问题**：@项目负责人
- **环境问题**：@项目负责人
- **进度延误**：提前1天预警

---

**现在开始执行！14天后见证成果！💪🚀**
