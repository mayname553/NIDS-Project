"""
网络入侵检测系统 - Flask API服务器
提供RESTful API接口用于前后端交互
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import os
import json
from datetime import datetime
from network_attack_detector import NetworkAttackDetector
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 脚本所在目录（确保路径正确，无论从哪里启动）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量
detector = NetworkAttackDetector()
detection_thread = None
is_detecting = False
detection_logs = []
detection_stats = {
    'total_scans': 0,
    'threats_detected': 0,
    'last_scan_time': None,
    'attack_types': {}
}

def background_detection():
    """后台检测线程"""
    global is_detecting, detection_logs, detection_stats

    while is_detecting:
        try:
            # 运行检测
            report = detector.run_detection()

            # 更新统计数据
            detection_stats['total_scans'] += 1
            detection_stats['last_scan_time'] = datetime.now().isoformat()

            if report['detected_attacks']:
                detection_stats['threats_detected'] += len(report['detected_attacks'])

                # 统计攻击类型
                for attack in report['detected_attacks']:
                    attack_type = attack['type']
                    detection_stats['attack_types'][attack_type] = \
                        detection_stats['attack_types'].get(attack_type, 0) + 1

                    # 添加日志
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'level': 'warning',
                        'type': attack_type,
                        'severity': attack['severity'],
                        'description': attack['description']
                    }
                    detection_logs.append(log_entry)
            else:
                # 正常日志
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': 'info',
                    'message': '系统正常，未检测到威胁'
                }
                detection_logs.append(log_entry)

            # 限制日志数量
            if len(detection_logs) > 100:
                detection_logs = detection_logs[-100:]

            # 等待一段时间再进行下次检测
            time.sleep(10)

        except Exception as e:
            logger.error(f"检测线程错误: {e}")
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'level': 'error',
                'message': f'检测错误: {str(e)}'
            }
            detection_logs.append(log_entry)
            time.sleep(5)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'NIDS API Server'
    })

@app.route('/api/detection/start', methods=['POST'])
def start_detection():
    """启动实时检测"""
    global is_detecting, detection_thread

    if is_detecting:
        return jsonify({
            'success': False,
            'message': '检测已在运行中'
        }), 400

    try:
        is_detecting = True
        detection_thread = threading.Thread(target=background_detection, daemon=True)
        detection_thread.start()

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'info',
            'message': '实时检测已启动'
        }
        detection_logs.append(log_entry)

        return jsonify({
            'success': True,
            'message': '实时检测已启动',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"启动检测失败: {e}")
        return jsonify({
            'success': False,
            'message': f'启动失败: {str(e)}'
        }), 500

@app.route('/api/detection/stop', methods=['POST'])
def stop_detection():
    """停止实时检测"""
    global is_detecting

    if not is_detecting:
        return jsonify({
            'success': False,
            'message': '检测未在运行'
        }), 400

    try:
        is_detecting = False

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'info',
            'message': '实时检测已停止'
        }
        detection_logs.append(log_entry)

        return jsonify({
            'success': True,
            'message': '实时检测已停止',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"停止检测失败: {e}")
        return jsonify({
            'success': False,
            'message': f'停止失败: {str(e)}'
        }), 500

@app.route('/api/detection/status', methods=['GET'])
def get_detection_status():
    """获取检测状态"""
    return jsonify({
        'is_detecting': is_detecting,
        'stats': detection_stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取检测日志"""
    limit = request.args.get('limit', 50, type=int)
    level = request.args.get('level', None)

    # 过滤日志
    filtered_logs = detection_logs
    if level:
        filtered_logs = [log for log in detection_logs if log.get('level') == level]

    # 返回最新的N条日志
    return jsonify({
        'logs': filtered_logs[-limit:],
        'total': len(filtered_logs),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    return jsonify({
        'stats': detection_stats,
        'is_detecting': is_detecting,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_pcap():
    """上传PCAP文件进行分析"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': '未找到文件'
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'message': '未选择文件'
        }), 400

    if not file.filename.endswith('.pcap'):
        return jsonify({
            'success': False,
            'message': '仅支持.pcap文件'
        }), 400

    try:
        # 保存文件
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)

        file.save(filepath)

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': 'info',
            'message': f'文件上传成功: {filename}'
        }
        detection_logs.append(log_entry)

        # TODO: 实现PCAP文件分析逻辑
        # 这里可以调用Scapy或其他工具进行流量分析

        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'filename': filename,
            'filepath': filepath,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return jsonify({
            'success': False,
            'message': f'上传失败: {str(e)}'
        }), 500

@app.route('/api/report', methods=['GET'])
def generate_report():
    """生成检测报告"""
    try:
        report = detector.generate_report()
        report['stats'] = detection_stats

        return jsonify({
            'success': True,
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return jsonify({
            'success': False,
            'message': f'生成报告失败: {str(e)}'
        }), 500

@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """清空日志"""
    global detection_logs
    detection_logs = []

    return jsonify({
        'success': True,
        'message': '日志已清空',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/reset-stats', methods=['POST'])
def reset_stats():
    """重置统计数据"""
    global detection_stats
    detection_stats = {
        'total_scans': 0,
        'threats_detected': 0,
        'last_scan_time': None,
        'attack_types': {}
    }

    return jsonify({
        'success': True,
        'message': '统计数据已重置',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/model/status', methods=['GET'])
def get_model_status():
    """获取AI模型状态"""
    return jsonify({
        'model_loaded': detector.use_ai,
        'model_path': 'model/nids_model.pkl',
        'model_type': 'Random Forest',
        'preprocessor_path': 'model/preprocessor.pkl',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/model/metrics', methods=['GET'])
def get_model_metrics():
    """获取模型性能指标"""
    try:
        metrics_path = os.path.join(BASE_DIR, 'model', 'model_metrics.json')
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            return jsonify({
                'success': True,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': '模型指标文件不存在',
                'timestamp': datetime.now().isoformat()
            }), 404
    except Exception as e:
        logger.error(f"读取模型指标失败: {e}")
        return jsonify({
            'success': False,
            'message': f'读取失败: {str(e)}'
        }), 500

@app.route('/api/model/train', methods=['POST'])
def train_model():
    """触发模型训练（后台任务）"""
    training_flag = os.path.join(BASE_DIR, 'model', '.training')
    try:
        # 检查是否已在训练
        if os.path.exists(training_flag):
            return jsonify({
                'success': False,
                'message': '模型正在训练中，请稍后再试'
            }), 400

        # 创建训练标记文件
        os.makedirs(os.path.join(BASE_DIR, 'model'), exist_ok=True)
        with open(training_flag, 'w') as f:
            f.write(datetime.now().isoformat())

        # 在后台线程中训练
        def train_in_background():
            try:
                import subprocess
                result = subprocess.run(
                    ['python', 'train_and_save.py'],
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True
                )
                logger.info(f"模型训练完成: {result.returncode}")
            except Exception as e:
                logger.error(f"模型训练失败: {e}")
            finally:
                # 删除训练标记
                if os.path.exists(training_flag):
                    os.remove(training_flag)

        training_thread = threading.Thread(target=train_in_background, daemon=True)
        training_thread.start()

        return jsonify({
            'success': True,
            'message': '模型训练已启动（后台运行）',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"启动训练失败: {e}")
        return jsonify({
            'success': False,
            'message': f'启动失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    import sys
    import io

    # 设置UTF-8编码输出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("="*50)
    print("[NIDS] 网络入侵检测系统 API 服务器")
    print("="*50)
    print("服务地址: http://localhost:5000")
    print("API文档:")
    print("  GET  /api/health           - 健康检查")
    print("  POST /api/detection/start  - 启动检测")
    print("  POST /api/detection/stop   - 停止检测")
    print("  GET  /api/detection/status - 检测状态")
    print("  GET  /api/logs             - 获取日志")
    print("  GET  /api/stats            - 获取统计")
    print("  POST /api/upload           - 上传PCAP")
    print("  GET  /api/report           - 生成报告")
    print("  GET  /api/model/status     - 模型状态")
    print("  GET  /api/model/metrics    - 模型指标")
    print("  POST /api/model/train      - 训练模型")
    print("="*50)
    print("")
    print("正在启动服务器...")
    print("")

    app.run(host='0.0.0.0', port=5000, debug=True)
