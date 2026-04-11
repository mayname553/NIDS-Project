import psutil
import socket
import subprocess
import time
import platform
from datetime import datetime
import logging
import requests
from collections import defaultdict
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class NetworkAttackDetector:
    def __init__(self):
        self.suspicious_activities = []
        self.attack_thresholds = {
            'high_cpu_usage': 90,  # CPU使用率阈值
            'high_memory_usage': 85,  # 内存使用率阈值
            'high_network_connections': 100,  # 网络连接数阈值
            'port_scan_threshold': 10,  # 端口扫描阈值
        }

        # 尝试加载AI模型
        self.ai_detector = None
        self.use_ai = False
        self._load_ai_model()

    def _load_ai_model(self):
        """加载AI模型"""
        try:
            model_path = os.path.join(BASE_DIR, 'model', 'nids_model.pkl')
            preprocessor_path = os.path.join(BASE_DIR, 'model', 'preprocessor.pkl')

            # 检查模型文件是否存在
            if os.path.exists(model_path) and os.path.exists(preprocessor_path):
                from ai_detector import AIDetector
                self.ai_detector = AIDetector(model_path, preprocessor_path)
                self.use_ai = True
                logger.info("✅ AI模型已加载，启用智能检测模式")
            else:
                logger.warning("⚠️ AI模型文件不存在，使用规则检测模式")
                logger.info(f"   请运行 'python train_and_save.py' 训练模型")
        except Exception as e:
            logger.warning(f"⚠️ AI模型加载失败: {e}")
            logger.info("   使用规则检测模式")
            self.use_ai = False

    def detect_ddos_attack(self):
        """检测DDoS攻击"""
        try:
            # 检查网络连接数
            connections = psutil.net_connections()
            connection_count = len(connections)

            if connection_count > self.attack_thresholds['high_network_connections']:
                self.suspicious_activities.append({
                    'type': 'DDoS攻击',
                    'severity': '高危',
                    'description': f'检测到异常高的网络连接数: {connection_count}',
                    'solution': self.get_ddos_solution()
                })
                return True
            return False
        except Exception as e:
            logger.error(f"DDoS检测错误: {e}")
            return False

    def detect_port_scan(self):
        """检测端口扫描"""
        try:
            # 模拟检测端口扫描 - 实际中需要更复杂的逻辑
            net_stats = psutil.net_io_counters()
            packet_count = net_stats.packets_sent + net_stats.packets_recv

            # 这里简化检测逻辑，实际应该分析端口访问模式
            if packet_count > 1000:  # 简单的包数量阈值
                self.suspicious_activities.append({
                    'type': '端口扫描',
                    'severity': '中危',
                    'description': '检测到可能的端口扫描活动',
                    'solution': self.get_port_scan_solution()
                })
                return True
            return False
        except Exception as e:
            logger.error(f"端口扫描检测错误: {e}")
            return False

    def detect_malware_activity(self):
        """检测恶意软件活动"""
        try:
            # 检查异常进程
            suspicious_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    # 检查高资源占用的未知进程
                    if (proc.info['cpu_percent'] > 50 or
                        proc.info['memory_percent'] > 50):
                        if self.is_suspicious_process(proc.info['name']):
                            suspicious_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if suspicious_processes:
                self.suspicious_activities.append({
                    'type': '恶意软件活动',
                    'severity': '高危',
                    'description': f'检测到可疑进程: {suspicious_processes}',
                    'solution': self.get_malware_solution()
                })
                return True
            return False
        except Exception as e:
            logger.error(f"恶意软件检测错误: {e}")
            return False

    def detect_brute_force(self):
        """检测暴力破解攻击"""
        try:
            # 检查失败的登录尝试（简化版）
            # 实际中应该分析系统日志
            if platform.system() == "Windows":
                # Windows系统检查
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                if "FAILED" in result.stdout or "REFUSED" in result.stdout:
                    self.suspicious_activities.append({
                        'type': '暴力破解攻击',
                        'severity': '中危',
                        'description': '检测到可能的暴力破解活动',
                        'solution': self.get_brute_force_solution()
                    })
                    return True
            return False
        except Exception as e:
            logger.error(f"暴力破解检测错误: {e}")
            return False

    def is_suspicious_process(self, process_name):
        """判断进程是否可疑"""
        suspicious_keywords = [
            'miner', 'crypto', 'bitcoin', 'monero', 'backdoor',
            'trojan', 'virus', 'malware', 'hack', 'exploit'
        ]
        process_lower = process_name.lower()
        return any(keyword in process_lower for keyword in suspicious_keywords)

    def get_ddos_solution(self):
        """DDoS攻击解决方案"""
        return """
        DDoS攻击应对措施:
        1. 立即联系网络服务提供商
        2. 启用云防护服务（如Cloudflare）
        3. 配置防火墙规则限制连接频率
        4. 使用负载均衡分散流量
        5. 临时关闭非必要服务
        """

    def get_port_scan_solution(self):
        """端口扫描解决方案"""
        return """
        端口扫描应对措施:
        1. 检查并关闭不必要的开放端口
        2. 配置防火墙规则限制IP访问
        3. 使用入侵检测系统(IDS)
        4. 定期进行安全审计
        5. 启用端口隐藏技术
        """

    def get_malware_solution(self):
        """恶意软件解决方案"""
        return """
        恶意软件清除步骤:
        1. 立即断开网络连接
        2. 使用杀毒软件进行全盘扫描
        3. 结束可疑进程
        4. 删除可疑文件
        5. 更新系统和软件补丁
        6. 修改所有密码
        """

    def get_brute_force_solution(self):
        """暴力破解解决方案"""
        return """
        暴力破解防护措施:
        1. 启用账户锁定策略
        2. 使用强密码策略
        3. 启用双因素认证
        4. 限制登录尝试次数
        5. 监控登录日志
        6. 使用VPN或白名单IP访问
        """

    def system_health_check(self):
        """系统健康检查"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.attack_thresholds['high_cpu_usage']:
                logger.warning(f"CPU使用率过高: {cpu_percent}%")

            # 内存使用率
            memory = psutil.virtual_memory()
            if memory.percent > self.attack_thresholds['high_memory_usage']:
                logger.warning(f"内存使用率过高: {memory.percent}%")

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                logger.warning(f"磁盘使用率过高: {disk.percent}%")

        except Exception as e:
            logger.error(f"系统健康检查错误: {e}")

    def generate_report(self):
        """生成检测报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'platform': platform.platform(),
                'hostname': socket.gethostname()
            },
            'detected_attacks': self.suspicious_activities,
            'recommendations': [],
            'ai_enabled': self.use_ai
        }

        if self.suspicious_activities:
            report['status'] = '发现安全威胁'
            report['recommendations'] = [
                "立即采取防护措施",
                "联系网络安全专家",
                "备份重要数据",
                "更新安全补丁"
            ]
        else:
            report['status'] = '系统正常'
            report['recommendations'] = [
                "保持系统更新",
                "定期进行安全扫描",
                "启用防火墙",
                "使用强密码策略"
            ]

        return report

    def run_detection(self):
        """运行所有检测（混合模式：规则检测 + AI检测）"""
        detection_mode = "AI智能检测" if self.use_ai else "规则检测"
        logger.info(f"开始网络安全检测... (模式: {detection_mode})")

        # 清空之前的检测结果
        self.suspicious_activities = []

        # 1. 规则检测（快速筛选）
        rule_detectors = [
            self.detect_ddos_attack,
            self.detect_port_scan,
            self.detect_malware_activity,
            self.detect_brute_force,
            self.system_health_check
        ]

        for detector in rule_detectors:
            try:
                detector()
            except Exception as e:
                logger.error(f"规则检测器执行错误: {e}")

        # 2. AI检测（精确判断）
        if self.use_ai and self.ai_detector:
            try:
                ai_threats = self.ai_detector.detect_threats()
                if ai_threats:
                    logger.info(f"🤖 AI检测到 {len(ai_threats)} 个威胁")
                    self.suspicious_activities.extend(ai_threats)
                else:
                    logger.info("🤖 AI检测: 未发现威胁")
            except Exception as e:
                logger.error(f"AI检测错误: {e}")

        # 生成报告
        report = self.generate_report()
        self.display_report(report)

        return report

    def display_report(self, report):
        """显示检测报告"""
        print("\n" + "="*50)
        print("网络安全检测报告")
        print("="*50)
        print(f"检测时间: {report['timestamp']}")
        print(f"系统状态: {report['status']}")
        print(f"主机名: {report['system_info']['hostname']}")
        print(f"检测模式: {'AI智能检测' if report.get('ai_enabled') else '规则检测'}")

        if report['detected_attacks']:
            print("\n发现的威胁:")
            for i, attack in enumerate(report['detected_attacks'], 1):
                print(f"{i}. {attack['type']} - 严重程度: {attack['severity']}")
                print(f"   描述: {attack['description']}")
                if 'confidence' in attack:
                    print(f"   置信度: {attack['confidence']*100:.1f}%")
                print(f"   解决方案: {attack['solution']}")
        else:
            print("\n未发现明显安全威胁")

        print("\n建议措施:")
        for rec in report['recommendations']:
            print(f"• {rec}")

def main():
    """主函数"""
    detector = NetworkAttackDetector()

    try:
        # 运行检测
        report = detector.run_detection()

        # 可选：将报告保存到文件
        with open('security_report.txt', 'w') as f:
            import json
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("检测完成，报告已保存到 security_report.txt")

    except KeyboardInterrupt:
        logger.info("检测被用户中断")
    except Exception as e:
        logger.error(f"检测过程中发生错误: {e}")

if __name__ == "__main__":
    # 安装所需库: pip install psutil
    main()
