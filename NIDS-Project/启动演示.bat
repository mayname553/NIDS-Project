@echo off
chcp 65001 >nul
echo ================================================
echo   NeuroSec-Aegis 网络入侵检测系统 - 演示启动
echo ================================================
echo.

echo [1/2] 启动后端 API 服务器...
cd /d "%~dp0backend"
start "NIDS Backend" cmd /k "python api_server.py"

echo [2/2] 等待后端启动...
timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo   系统已启动！
echo ================================================
echo.
echo   后端 API: http://localhost:5000
echo   前端页面: 请用浏览器打开以下文件
echo   %~dp0frontend\neurosec-ai-ids\index.html
echo.
echo   操作说明:
echo   1. 在浏览器中打开 index.html
echo   2. 点击"建立安全连接"登录
echo   3. 点击"重置并启动全域引擎"开始检测
echo   4. 观察实时日志和威胁态势图
echo.
echo   按任意键打开前端页面...
pause >nul

start "" "%~dp0frontend\neurosec-ai-ids\index.html"
