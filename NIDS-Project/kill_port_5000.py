import subprocess
import time

# 查找占用5000端口的进程（包括TCP和UDP）
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
lines = result.stdout.split('\n')

pids = set()
for line in lines:
    if ':5000' in line:  # 移除LISTENING限制，包括UDP
        parts = line.split()
        if parts:
            pid = parts[-1]
            if pid.isdigit():  # 确保是有效的PID
                pids.add(pid)

print(f"找到 {len(pids)} 个占用5000端口的进程: {pids}")

# 终止这些进程
for pid in pids:
    try:
        result = subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, text=True)
        print(f"已终止进程 PID: {pid}")
    except Exception as e:
        print(f"终止进程 {pid} 失败: {e}")

time.sleep(3)

# 验证端口是否已释放
result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
if ':5000' in result.stdout:
    print("警告: 5000端口仍被占用")
    print(result.stdout)
else:
    print("✓ 5000端口已释放")
