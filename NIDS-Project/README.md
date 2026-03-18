# NeuroSec-Aegis 🛡️

**基于智能模型与动态优化的轻量级网络入侵检测系统**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Development-yellow.svg)]()

一个集成了深度学习和强化学习的现代化网络入侵检测系统，提供实时流量分析、威胁检测和可视化监控。

## 🚀 项目特色

- **🧠 双核 AI 引擎**: CNN-LSTM 深度学习模型 + TD3 强化学习策略
- **⚡ 高性能优化**: INT8 量化加速，实时检测延迟 < 200ms
- **📊 可视化监控**: 赛博朋克风格的实时威胁态势感知界面
- **🔧 模块化设计**: 松耦合架构，支持独立开发和部署
- **📡 实时检测**: 基于 Scapy 的网络流量实时捕获与分析

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据采集层     │    │   AI 分析层      │    │   响应决策层     │
│                │    │                │    │                │
│ • 网络包捕获    │───▶│ • CNN-LSTM模型  │───▶│ • 威胁分类      │
│ • 流量预处理    │    │ • 强化学习策略  │    │ • 动态防御      │
│ • 特征提取      │    │ • 模型融合      │    │ • 告警响应      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 项目结构

```
NIDS-Project/
├── 📂 backend/                    # 后端服务
│   ├── 🐍 api_server.py          # Flask API 服务器
│   ├── 🔍 network_attack_detector.py  # 核心检测引擎
│   ├── 🤖 ai_detector.py         # AI 模型集成
│   ├── 📊 data_preprocessor.py   # 数据预处理
│   ├── 📂 src/                   # 源代码模块 (HuangBobo 任务)
│   │   ├── 📂 utils/             # 基础工具类
│   │   │   └── 🐍 feature_engineering/ # 特征工程工具
│   │   └── 📂 modules/           # 业务逻辑模块
│   │       └── 🐍 features/      # 特征工程业务逻辑
│   ├── 📂 config/                # 配置文件
│   │   └── 📂 features/          # 特征工程配置与数据库
│   ├── 🎯 train_model.py         # 模型训练脚本
│   ├── 📋 requirements.txt       # Python 依赖
│   ├── 📂 model/                 # 训练好的模型文件
│   ├── 📂 dataset/               # 数据集目录
│   └── 📖 BACKEND_GUIDE.md       # 后端开发指南
├── 📂 frontend/
│   └── 📂 neurosec-ai-ids/       # 前端应用
│       ├── 🌐 index.html         # 主页面
│       ├── ⚡ script.js          # 业务逻辑
│       ├── 🎨 style.css          # 样式文件
│       └── 📦 package.json       # 前端依赖
├── 🚀 start_neurosec.bat         # Windows 启动脚本
├── 🚀 start_neurosec.sh          # Linux/macOS 启动脚本
├── 📖 README.md                  # 项目说明
├── 📖 README_NEUROSEC.md         # 详细技术文档
├── 📖 体验指南.md                # 中文使用指南
└── 📖 项目完成指导手册.md        # 开发指导
```

## 🛠️ 技术栈

### 后端技术
- **🐍 Python 3.8+** - 核心开发语言
- **🌶️ Flask** - 轻量级 Web 框架
- **📡 Scapy** - 网络包捕获与分析
- **🧠 TensorFlow/PyTorch** - 深度学习框架
- **📊 NumPy, Pandas** - 数据处理与分析
- **🔄 scikit-learn** - 机器学习工具

### 前端技术
- **⚡ 原生 JavaScript (ES6+)** - 前端逻辑
- **📈 ECharts** - 数据可视化
- **🎨 Glassmorphism UI** - 现代化设计风格
- **🌐 RESTful API** - 前后端通信

### AI/ML 技术
- **🔗 CNN-LSTM** - 深度学习检测模型
- **🎯 TD3 (Twin Delayed DDPG)** - 强化学习策略
- **⚖️ SMOTE** - 样本平衡技术
- **🗜️ INT8 量化** - 模型压缩优化

## 🚀 快速开始

### 环境要求

- 🐍 Python 3.8 或更高版本
- 🟢 Node.js 16+ (用于前端开发)
- 💻 Windows/Linux/macOS
- 👑 管理员权限（用于网络包捕获）

### 安装步骤

1. **📥 克隆项目**
```bash
git clone https://github.com/your-username/NIDS-Project.git
cd NIDS-Project
```

2. **🔧 安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

3. **📦 安装前端依赖**
```bash
cd frontend/neurosec-ai-ids
npm install
```

### 🎯 启动系统

**一键启动 (推荐):**

**Windows:**
```bash
start_neurosec.bat
```

**Linux/macOS:**
```bash
chmod +x start_neurosec.sh
./start_neurosec.sh
```

**手动启动:**

```bash
# 启动后端 (端口 5000)
cd backend
python api_server.py

# 启动前端 (端口 5175)
cd frontend/neurosec-ai-ids
npm run dev
```

### 🌐 访问系统

打开浏览器访问: `http://localhost:5175`

**默认登录信息：**
- 👤 用户名: `Admin_SecOps`
- 🔑 密码: 任意（演示模式）

## 📊 核心功能

### 🔍 实时威胁检测
- **DDoS 攻击检测** - 基于流量模式分析
- **端口扫描识别** - 异常连接行为检测
- **SQL 注入检测** - 恶意查询语句识别
- **XSS 攻击识别** - 跨站脚本攻击防护

### 🧠 AI 智能分析
- **深度学习推理** - CNN-LSTM 混合模型
- **强化学习优化** - 自适应防御策略
- **特征工程** - 自动化特征提取与选择
- **模型融合** - 多模型集成决策

### 📈 可视化监控
- **实时仪表盘** - 系统状态总览
- **威胁态势图** - 攻击趋势可视化
- **网络拓扑图** - 流量路径分析
- **日志流展示** - 实时事件追踪

## 🔧 开发指南

### 后端开发

扩展检测规则:
```python
# backend/network_attack_detector.py
class NetworkAttackDetector:
    def analyze_packet(self, packet):
        # 添加自定义检测逻辑
        if self.detect_custom_attack(packet):
            return self.generate_alert(packet, "CUSTOM_ATTACK")
```

### 前端开发

自定义 UI 组件:
```javascript
// frontend/neurosec-ai-ids/script.js
function updateThreatMap(data) {
    // 威胁地图更新逻辑
    threatChart.setOption({
        series: [{
            data: data.threats
        }]
    });
}
```

## 🎯 模型训练

重新训练 AI 模型:

```bash
cd backend

# 下载数据集
python download_dataset.py

# 数据预处理
python data_preprocessor.py

# 训练模型
python train_model.py

# 测试集成
python test_ai_integration.py
```

## 📊 API 接口

### 🎮 检测控制
- `POST /api/v1/start_detection` - 启动实时检测
- `POST /api/v1/stop_detection` - 停止检测服务

### 📈 数据查询
- `GET /api/v1/stats` - 获取系统统计
- `GET /api/v1/detection_stats` - 实时检测数据
- `GET /api/v1/detection_logs` - 检测日志查询

详细 API 文档: [backend/BACKEND_GUIDE.md](backend/BACKEND_GUIDE.md)

## 🔧 故障排查

### 常见问题

**🐍 后端启动失败**
```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 重新安装依赖
pip install -r requirements.txt

# 检查端口占用
netstat -ano | findstr :5000
```

**🌐 前端连接失败**
```bash
# 确认后端服务状态
curl http://localhost:5000/api/v1/stats

# 检查 API 配置
# 编辑 frontend/neurosec-ai-ids/src/api/config.js
```

**📡 网络捕获权限**
- Windows: 以管理员身份运行
- Linux: 使用 `sudo` 或配置网络权限
- 安装 Npcap/WinPcap (Windows)

## 🚀 性能优化

- **⚡ 模型量化**: INT8 量化减少 60% 推理时间
- **🔄 批处理**: 批量数据处理提升吞吐量
- **💾 缓存策略**: Redis 缓存热点数据
- **⚖️ 负载均衡**: 多进程并行检测

## 👥 团队协作

### 开发分工
- **🎯 项目负责人**: 架构设计、集成测试
- **🎨 前端开发**: UI/UX、数据可视化
- **📊 数据工程**: 数据集管理、预处理
- **🧠 算法工程**: 模型训练、优化
- **🔧 后端开发**: API 服务、系统集成

### Git 工作流
```bash
# 功能分支开发
git checkout -b feature/your-feature
git add .
git commit -m "feat: add new detection rule"
git push origin feature/your-feature

# 提交 Pull Request 进行代码审查
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. 🍴 Fork 本项目
2. 🌿 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 💾 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送分支 (`git push origin feature/AmazingFeature`)
5. 🔄 创建 Pull Request

## 📞 联系我们

- 📧 邮箱: [your-email@example.com]
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-username/NIDS-Project/issues)
- 📖 详细文档: [README_NEUROSEC.md](README_NEUROSEC.md)

## 🙏 致谢

感谢以下开源项目和研究工作：
- [Scapy](https://scapy.net/) - 网络包处理
- [TensorFlow](https://tensorflow.org/) - 深度学习框架
- [ECharts](https://echarts.apache.org/) - 数据可视化
- NSL-KDD, CIC-IDS2017 数据集

---

<div align="center">

**🛡️ NeuroSec-Aegis - 智能守护网络安全 🛡️**

*Built with ❤️ by 大创团队*

</div>