# 后端开发指南

## 项目结构

```
backend/
├── api_server.py              # Flask API服务器
├── network_attack_detector.py # 检测引擎
├── requirements.txt           # Python依赖
├── test_system.py            # 系统测试
├── main.py                   # 主程序
├── preprocess/               # 数据预处理
└── uploads/                  # 上传文件目录（自动创建）
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install Flask flask-cors psutil pandas numpy requests scikit-learn
```

### 2. 启动API服务器
```bash
python api_server.py
```

服务器将运行在: http://localhost:5000

### 3. 测试系统
```bash
python test_system.py
```

## API接口文档

### 基础信息
- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **CORS**: 已启用，允许所有来源

### 接口列表

#### 1. 健康检查
```http
GET /api/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "message": "API服务器运行正常"
}
```

#### 2. 启动检测
```http
POST /api/detection/start
```

**响应示例**:
```json
{
  "status": "success",
  "message": "检测已启动"
}
```

#### 3. 停止检测
```http
POST /api/detection/stop
```

**响应示例**:
```json
{
  "status": "success",
  "message": "检测已停止"
}
```

#### 4. 获取检测状态
```http
GET /api/detection/status
```

**响应示例**:
```json
{
  "is_detecting": true,
  "scan_count": 42,
  "threat_count": 5,
  "last_scan_time": "2026-03-09 14:30:45"
}
```

#### 5. 获取日志
```http
GET /api/logs?limit=50&level=all
```

**查询参数**:
- `limit` (可选): 返回的日志数量，默认50
- `level` (可选): 日志级别过滤 (all/info/warning/error/success)

**响应示例**:
```json
{
  "logs": [
    {
      "timestamp": "2026-03-09 14:30:45",
      "level": "warning",
      "message": "[DDoS攻击] 检测到异常高的网络流量"
    }
  ],
  "total": 100
}
```

#### 6. 获取统计数据
```http
GET /api/stats
```

**响应示例**:
```json
{
  "total_scans": 42,
  "total_threats": 5,
  "attack_types": {
    "DDoS攻击": 2,
    "端口扫描": 2,
    "恶意软件活动": 1
  },
  "last_scan_time": "2026-03-09 14:30:45"
}
```

#### 7. 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data
```

**请求参数**:
- `file`: PCAP文件

**响应示例**:
```json
{
  "status": "success",
  "message": "文件上传成功",
  "filename": "traffic_20260309_143045.pcap"
}
```

#### 8. 生成报告
```http
GET /api/report
```

**响应示例**:
```json
{
  "report": {
    "generated_at": "2026-03-09 14:30:45",
    "summary": {
      "total_scans": 42,
      "total_threats": 5,
      "detection_rate": "11.9%"
    },
    "threats": [...]
  }
}
```

#### 9. 清空日志
```http
POST /api/clear-logs
```

**响应示例**:
```json
{
  "status": "success",
  "message": "日志已清空"
}
```

#### 10. 重置统计
```http
POST /api/reset-stats
```

**响应示例**:
```json
{
  "status": "success",
  "message": "统计数据已重置"
}
```

## 核心模块说明

### api_server.py

Flask API服务器，主要功能：

1. **路由处理**: 10个API端点
2. **后台检测**: 使用线程运行检测循环
3. **日志管理**: 自动限制日志数量（最多100条）
4. **统计收集**: 实时更新统计数据
5. **文件上传**: 处理PCAP文件上传

**关键变量**:
```python
detection_thread = None      # 检测线程
is_detecting = False         # 检测状态
logs = []                    # 日志列表
stats = {...}                # 统计数据
detector = NetworkAttackDetector()  # 检测器实例
```

**关键函数**:
```python
detection_loop()             # 后台检测循环
add_log(level, message)      # 添加日志
```

### network_attack_detector.py

检测引擎，包含5种检测方法：

1. **check_ddos()** - DDoS攻击检测
2. **check_port_scan()** - 端口扫描检测
3. **check_malware()** - 恶意软件活动检测
4. **check_brute_force()** - 暴力破解检测
5. **check_system_health()** - 系统健康检查

**使用示例**:
```python
from network_attack_detector import NetworkAttackDetector

detector = NetworkAttackDetector()
results = detector.detect()

for result in results:
    print(f"{result['type']}: {result['message']}")
```

## 开发建议

### 1. 添加新的检测类型

在 `network_attack_detector.py` 中添加新方法：

```python
def check_new_attack(self):
    """检测新类型的攻击"""
    # 检测逻辑
    if condition:
        return {
            'type': '新攻击类型',
            'severity': 'high',
            'message': '检测到新类型攻击',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    return None
```

在 `detect()` 方法中调用：

```python
def detect(self):
    results = []
    # ... 现有检测
    new_result = self.check_new_attack()
    if new_result:
        results.append(new_result)
    return results
```

### 2. 添加新的API接口

在 `api_server.py` 中添加路由：

```python
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    try:
        # 处理逻辑
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
```

### 3. 修改检测间隔

在 `api_server.py` 的 `detection_loop()` 中修改：

```python
def detection_loop():
    while is_detecting:
        # ... 检测逻辑
        time.sleep(10)  # 改为其他秒数
```

### 4. 自定义日志级别

添加新的日志级别：

```python
def add_log(level, message):
    # level: 'info', 'warning', 'error', 'success', 'critical'
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'message': message
    }
    logs.append(log_entry)
```

## 配置选项

### 修改端口

在 `api_server.py` 底部修改：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # 改为其他端口，如 port=8000
```

### 修改CORS设置

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],  # 限制特定来源
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 修改上传目录

```python
UPLOAD_FOLDER = 'uploads'  # 改为其他目录
```

## 测试

### 单元测试

创建 `test_api.py`:

```python
import unittest
from api_server import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_health(self):
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

### 使用curl测试

```bash
# 健康检查
curl http://localhost:5000/api/health

# 启动检测
curl -X POST http://localhost:5000/api/detection/start

# 获取日志
curl http://localhost:5000/api/logs?limit=10

# 上传文件
curl -X POST -F "file=@traffic.pcap" http://localhost:5000/api/upload
```

### 使用Postman测试

1. 导入API集合
2. 设置环境变量: `base_url = http://localhost:5000`
3. 测试各个接口

## 性能优化

### 1. 使用数据库

替换内存存储为数据库：

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nids.db'
db = SQLAlchemy(app)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    level = db.Column(db.String(20))
    message = db.Column(db.Text)
```

### 2. 使用缓存

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/stats')
@cache.cached(timeout=5)
def get_stats():
    return jsonify(stats)
```

### 3. 异步处理

使用 Celery 处理耗时任务：

```python
from celery import Celery

celery = Celery(app.name, broker='redis://localhost:6379/0')

@celery.task
def analyze_pcap(filename):
    # 分析PCAP文件
    pass
```

## 安全建议

### 1. 添加认证

```python
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not verify_token(token):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/detection/start', methods=['POST'])
@require_auth
def start_detection():
    # ...
```

### 2. 限流

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/upload', methods=['POST'])
@limiter.limit("5 per minute")
def upload_file():
    # ...
```

### 3. 输入验证

```python
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pcap', 'pcapng'}

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
```

## 日志记录

### 配置日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nids.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 使用日志

```python
logger.info("检测已启动")
logger.warning("检测到威胁")
logger.error("发生错误")
```

## 部署

### 使用Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### 使用Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "api_server.py"]
```

构建和运行：

```bash
docker build -t nids-backend .
docker run -p 5000:5000 nids-backend
```

## 故障排除

### 问题1: 端口被占用
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### 问题2: 导入错误
```bash
# 确保在正确的目录
cd backend
python api_server.py
```

### 问题3: 权限不足
```bash
# Windows: 以管理员身份运行
# Linux/Mac: 使用 sudo
sudo python api_server.py
```

## 更多资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [Flask-CORS 文档](https://flask-cors.readthedocs.io/)
- [psutil 文档](https://psutil.readthedocs.io/)

---

**提示**: 开发时建议使用虚拟环境隔离依赖。
