# NeuroSec-Aegis 系统使用指南

## 基于智能模型与动态优化的轻量级网络入侵检测系统

---

## 🚀 快速启动

### Windows 系统

双击运行 `start_neurosec.bat` 文件，系统会自动：
1. 检查并安装依赖
2. 启动后端 API 服务器（端口 5000）
3. 启动前端界面（端口 5173）

### Linux/Mac 系统

```bash
chmod +x start_neurosec.sh
./start_neurosec.sh
```

---

## 🌐 访问系统

启动完成后，在浏览器中访问：

**前端界面**: http://localhost:5173

**后端 API**: http://localhost:5000/api/health

---

## 📊 系统功能

### 1. 实时监控
- 网络流量实时分析
- 异常行为检测
- 攻击类型识别

### 2. 智能检测
- CNN-LSTM 双核检测引擎
- TD3 强化学习策略优化
- INT8 量化加速推理

### 3. 威胁态势
- DDoS 洪泛攻击检测
- APT 隐蔽隧道识别
- WebShell/SQL 注入防护

### 4. 可视化展示
- 实时流量图表
- 攻击类型分布
- 风险等级评估
- AI 性能指标

---

## 🎮 操作说明

### 登录界面
- 默认用户名: `Admin_SecOps`
- 默认密码: 任意（演示模式）
- 点击"建立安全连接"进入系统

### 主控制台

#### 核心指标卡片
- **累积解析包数**: 显示系统处理的总数据包数
- **捕获威胁实体**: 检测到的威胁数量
- **AI 引擎状态**: 模型运行状态和推理延迟
- **最后阻断指令**: 最近一次防御操作时间

#### 威胁态势图谱
- 实时显示各类攻击的占比
- 基于 MITRE ATT&CK 框架分类
- 动态更新攻击趋势

#### 智能决策终端流
- 实时日志输出
- 颜色标识不同级别：
  - 🔵 蓝色：系统信息
  - 🟡 黄色：预警信息
  - 🔴 红色：拦截操作

#### 控制按钮
- **重置并启动全域引擎**: 启动检测服务
- **物理隔离/挂起引擎**: 停止检测服务
- **净化终端日志**: 清空日志显示

---

## 🔧 技术架构

### 后端技术栈
- **框架**: Flask + Python 3.8+
- **检测引擎**: 基于规则的网络流量分析
- **AI 模型**: Random Forest（可扩展为深度学习模型）
- **数据处理**: Pandas + NumPy

### 前端技术栈
- **构建工具**: Vite
- **可视化**: ECharts 5.4.3
- **样式**: 赛博朋克深空主题
- **字体**: Orbitron + Exo 2

### API 接口

#### 检测控制
- `POST /api/detection/start` - 启动检测
- `POST /api/detection/stop` - 停止检测
- `GET /api/detection/status` - 获取状态

#### 数据查询
- `GET /api/stats` - 获取统计数据
- `GET /api/logs?limit=50` - 获取日志
- `GET /api/model/metrics` - 获取模型指标

#### 系统管理
- `POST /api/clear-logs` - 清空日志
- `POST /api/reset-stats` - 重置统计
- `GET /api/report` - 生成报告

---

## 📁 项目结构

```
NIDS-Project/
├── backend/                    # 后端服务
│   ├── api_server.py          # Flask API 服务器
│   ├── network_attack_detector.py  # 检测引擎
│   ├── ai_detector.py         # AI 模型接口
│   └── requirements.txt       # Python 依赖
│
├── frontend/neurosec-ai-ids/  # 前端界面
│   ├── index.html             # 主页面
│   ├── src/
│   │   ├── api/              # API 接口层
│   │   └── utils/            # 工具函数
│   ├── config.js             # 配置文件
│   └── package.json          # 前端依赖
│
├── start_neurosec.bat        # Windows 启动脚本
├── start_neurosec.sh         # Linux/Mac 启动脚本
└── README_NEUROSEC.md        # 本文档
```

---

## 🛠️ 开发说明

### 修改后端 API 端口

编辑 `backend/api_server.py` 最后一行：
```python
app.run(host='0.0.0.0', port=5000, debug=True)  # 修改 port 参数
```

同时修改前端配置 `frontend/neurosec-ai-ids/config.js`：
```javascript
apiBaseUrl: 'http://localhost:5000/api'  // 修改端口号
```

### 修改前端端口

编辑 `frontend/neurosec-ai-ids/vite.config.js`：
```javascript
server: {
    port: 5173,  // 修改此处
    ...
}
```

### 自定义检测规则

编辑 `backend/network_attack_detector.py` 中的检测逻辑：
```python
def detect_ddos(self, packet_rate):
    # 自定义 DDoS 检测阈值
    if packet_rate > 5000:
        return True
```

---

## 🎯 项目特色

1. **轻量级设计**: 资源占用低，适合边缘设备部署
2. **智能检测**: 结合规则和 AI 模型的混合检测
3. **实时响应**: 毫秒级检测延迟
4. **可视化**: 专业的赛博朋克风格界面
5. **易扩展**: 模块化设计，便于功能扩展

---

## 📝 注意事项

1. 首次启动需要安装依赖，可能需要几分钟
2. 确保端口 5000 和 5173 未被占用
3. 建议使用 Chrome、Edge 或 Firefox 浏览器
4. 系统默认使用模拟数据，实际部署需配置网络接口

---

## 🤝 技术支持

如遇问题，请检查：
1. Python 版本是否 >= 3.8
2. Node.js 版本是否 >= 14
3. 防火墙是否阻止了端口访问
4. 依赖是否完整安装

---

## 📄 许可证

本项目为教育研究项目，仅供学习使用。

---

**NeuroSec-Aegis** - 基于智能模型与动态优化的轻量级网络入侵检测系统
