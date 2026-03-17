#!/bin/bash

# NeuroSec-Aegis 启动脚本
# 基于智能模型与动态优化的轻量级网络入侵检测系统

echo "=========================================="
echo "  NeuroSec-Aegis 系统启动"
echo "  异常流量精准识别系统"
echo "=========================================="
echo ""

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")/backend"

echo "[1/4] 检查后端依赖..."
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
if [ -f "requirements.txt" ]; then
    echo "安装 Python 依赖..."
    pip install -r requirements.txt -q
fi

echo "[2/4] 启动后端 API 服务器..."
python api_server.py &
BACKEND_PID=$!
echo "后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 进入前端目录
cd ../frontend/neurosec-ai-ids

echo "[3/4] 检查前端依赖..."
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

echo "[4/4] 启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "  系统启动完成！"
echo "=========================================="
echo ""
echo "后端 API: http://localhost:5000"
echo "前端界面: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait
