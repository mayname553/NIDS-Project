@echo off
echo 正在强制终止占用5000端口的进程...
taskkill /F /PID 13596
taskkill /F /PID 25320
taskkill /F /PID 7164
timeout /T 2 /NOBREAK > nul
echo.
echo 检查端口状态:
netstat -ano | findstr :5000
pause
