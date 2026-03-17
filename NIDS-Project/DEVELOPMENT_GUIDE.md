# 开发指南 📋

## 团队分工与协作

### 👥 团队成员职责

#### 🎯 项目负责人
- **主要职责**: 整体架构设计、模块集成、项目协调
- **负责文件**:
  - `README.md` - 项目文档维护
  - `docs/` - 技术文档编写
  - 集成测试和部署脚本
- **工作流程**:
  1. 制定开发规范和接口标准
  2. 协调各模块开发进度
  3. 代码审查和合并管理
  4. 系统集成测试

#### 🎨 前端开发
- **负责模块**: `frontend/neurosec-ai-ids/`
- **主要任务**:
  - 实时监控仪表盘开发
  - 威胁可视化界面设计
  - 用户交互逻辑实现
  - API 调用集成
- **技术栈**: JavaScript ES6+, ECharts, CSS3
- **交付物**:
  - 响应式 Web 界面
  - 实时数据可视化组件
  - 用户操作界面

#### 📊 数据集管理
- **负责模块**: `backend/dataset/`, `backend/download_dataset.py`
- **主要任务**:
  - NSL-KDD、CIC-IDS2017 等数据集整理
  - 数据清洗和标注
  - 数据集版本管理
  - 提供标准化数据接口
- **技术要求**: 熟悉网络安全数据集格式
- **交付物**:
  - 清洗后的训练数据
  - 数据集文档说明
  - 数据加载脚本

#### 🔧 数据预处理
- **负责模块**: `backend/data_preprocessor.py`
- **主要任务**:
  - 特征工程 pipeline 设计
  - 数据标准化和归一化
  - SMOTE 过采样实现
  - 实时数据流处理
- **技术栈**: Python, Pandas, NumPy, scikit-learn
- **交付物**:
  - 特征提取模块
  - 数据预处理管道
  - 实时处理接口

#### 🧠 模型训练
- **负责模块**: `backend/train_model.py`, `backend/ai_detector.py`
- **主要任务**:
  - CNN-LSTM 模型实现
  - TD3 强化学习算法
  - 模型量化和优化
  - 模型评估和调优
- **技术栈**: TensorFlow/PyTorch, scikit-learn
- **交付物**:
  - 训练好的模型文件
  - 模型推理接口
  - 性能评估报告

## 🔄 开发工作流

### Git 分支管理

```bash
# 主分支
main/master          # 生产环境代码
develop             # 开发环境代码

# 功能分支
feature/frontend    # 前端开发
feature/dataset     # 数据集管理
feature/preprocessing # 数据预处理
feature/model-training # 模型训练
feature/backend-api # 后端API

# 修复分支
hotfix/bug-name     # 紧急修复
```

### 开发流程

1. **创建功能分支**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-module
```

2. **开发和提交**
```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-module
```

3. **创建 Pull Request**
- 目标分支: `develop`
- 请求代码审查
- 通过测试后合并

4. **发布流程**
```bash
git checkout main
git merge develop
git tag v1.0.0
git push origin main --tags
```

## 📋 接口规范

### 数据格式标准

#### 网络流量数据格式
```python
{
    "timestamp": "2024-03-17T10:30:00Z",
    "src_ip": "192.168.1.100",
    "dst_ip": "10.0.0.1",
    "src_port": 12345,
    "dst_port": 80,
    "protocol": "TCP",
    "packet_size": 1024,
    "features": [0.1, 0.2, 0.3, ...],  # 提取的特征向量
    "label": "normal"  # 标签: normal, ddos, portscan, etc.
}
```

#### 模型预测结果格式
```python
{
    "prediction": {
        "class": "ddos",
        "confidence": 0.95,
        "probabilities": {
            "normal": 0.05,
            "ddos": 0.95,
            "portscan": 0.00
        }
    },
    "timestamp": "2024-03-17T10:30:00Z",
    "processing_time": 0.003  # 秒
}
```

### API 接口规范

#### 后端 API 端点
```python
# 检测控制
POST /api/v1/start_detection
POST /api/v1/stop_detection
GET  /api/v1/detection_status

# 数据查询
GET  /api/v1/stats
GET  /api/v1/detection_logs?limit=100&offset=0
GET  /api/v1/threat_summary

# 模型管理
POST /api/v1/model/retrain
GET  /api/v1/model/metrics
POST /api/v1/model/update
```

#### 前端调用示例
```javascript
// 启动检测
const startDetection = async () => {
    const response = await fetch('/api/v1/start_detection', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    });
    return response.json();
};

// 获取实时数据
const getStats = async () => {
    const response = await fetch('/api/v1/stats');
    return response.json();
};
```

## 🧪 测试规范

### 单元测试
```python
# backend/tests/test_preprocessor.py
import unittest
from data_preprocessor import DataPreprocessor

class TestDataPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DataPreprocessor()

    def test_feature_extraction(self):
        # 测试特征提取功能
        pass

    def test_data_normalization(self):
        # 测试数据标准化
        pass
```

### 集成测试
```python
# backend/test_system.py
def test_end_to_end_detection():
    # 端到端检测流程测试
    pass

def test_api_endpoints():
    # API 接口测试
    pass
```

### 性能测试
```python
# 测试指标
- 检测延迟 < 200ms
- 吞吐量 > 1000 packets/sec
- 内存使用 < 2GB
- CPU 使用率 < 80%
```

## 📁 文件组织规范

### 代码结构
```
backend/
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── detector.py        # 检测引擎
│   └── models.py          # 数据模型
├── api/                   # API 接口
│   ├── __init__.py
│   ├── routes.py          # 路由定义
│   └── schemas.py         # 数据模式
├── data/                  # 数据处理
│   ├── __init__.py
│   ├── preprocessor.py    # 预处理
│   └── loader.py          # 数据加载
├── ml/                    # 机器学习
│   ├── __init__.py
│   ├── models/            # 模型定义
│   └── training/          # 训练脚本
├── tests/                 # 测试代码
├── config/                # 配置文件
└── utils/                 # 工具函数
```

### 命名规范
- **文件名**: 小写字母 + 下划线 (`data_preprocessor.py`)
- **类名**: 大驼峰命名 (`NetworkAttackDetector`)
- **函数名**: 小写字母 + 下划线 (`analyze_packet()`)
- **常量**: 大写字母 + 下划线 (`MAX_PACKET_SIZE`)

## 🔧 环境配置

### 开发环境设置
```bash
# Python 虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 前端环境
cd frontend/neurosec-ai-ids
npm install
npm run dev
```

### 配置文件
```python
# backend/config/settings.py
class Config:
    DEBUG = True
    API_HOST = "localhost"
    API_PORT = 5000
    MODEL_PATH = "model/"
    DATASET_PATH = "dataset/"

class ProductionConfig(Config):
    DEBUG = False
    # 生产环境配置
```

## 📊 进度跟踪

### 里程碑计划
- **Week 1-2**: 环境搭建、基础框架
- **Week 3-4**: 核心模块开发
- **Week 5-6**: 模块集成测试
- **Week 7-8**: 性能优化、文档完善

### 任务分配
| 模块 | 负责人 | 预计完成时间 | 状态 |
|------|--------|-------------|------|
| 前端界面 | 前端同学 | Week 4 | 🟡 进行中 |
| 数据集整理 | 数据同学 | Week 2 | ✅ 完成 |
| 数据预处理 | 预处理同学 | Week 3 | 🟡 进行中 |
| 模型训练 | 算法同学 | Week 5 | 🔴 待开始 |
| 系统集成 | 项目负责人 | Week 6 | 🔴 待开始 |

## 🚀 部署指南

### 本地部署
```bash
# 启动后端
cd backend
python api_server.py

# 启动前端
cd frontend/neurosec-ai-ids
npm run dev
```

### Docker 部署
```dockerfile
# Dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api_server.py"]
```

### 生产环境
```bash
# 使用 gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app

# 使用 nginx 反向代理
# 配置 SSL 证书
# 设置防火墙规则
```

## 📞 联系方式

- **项目负责人**: [你的联系方式]
- **技术讨论**: 微信群/QQ群
- **代码审查**: GitHub Pull Request
- **问题反馈**: GitHub Issues

---

**记住**: 代码质量比速度更重要，及时沟通比独自解决更高效！ 🚀