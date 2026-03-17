@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo   NeuroSec-Aegis 系统启动
echo   异常流量精准识别系统
echo ==========================================
echo.

REM 检查 Python 环境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查 Node.js 环境
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

REM 进入后端目录
cd /d "%~dp0backend"

echo [1/4] 检查后端依赖...
if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
if exist "requirements.txt" (
    echo 安装 Python 依赖...
    pip install -r requirements.txt -q
)

echo [2/4] 启动后端 API 服务器...
start "NeuroSec Backend" cmd /k "python api_server.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 进入前端目录
cd /d "%~dp0frontend\neurosec-ai-ids"

echo [3/4] 检查前端依赖...
if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)

echo [4/4] 启动前端开发服务器...
start "NeuroSec Frontend" cmd /k "npm run dev"

echo.
echo ==========================================
echo   系统启动完成！
echo ==========================================
echo.
echo 后端 API: http://localhost:5000
echo 前端界面: http://localhost:5173
echo.
echo 请在浏览器中访问前端界面
echo.
pause
