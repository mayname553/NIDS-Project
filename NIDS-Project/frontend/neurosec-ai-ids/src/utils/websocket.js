/**
 * WebSocket 服务 - 实时数据推送
 * 基于智能模型与动态优化的轻量级网络入侵检测系统
 */

import config from '../../config.js';

class WebSocketService {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.subscriptions = new Map();
        this.heartbeatInterval = null;
    }

    // 连接WebSocket
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                // 注意：当前后端没有WebSocket支持，这里使用轮询模拟
                console.warn('WebSocket未实现，使用HTTP轮询模拟实时更新');
                this.isConnected = true;
                this.startPolling();
                resolve();
            } catch (error) {
                console.error('WebSocket连接失败:', error);
                this.isConnected = false;
                reject(error);
            }
        });
    }

    // 使用HTTP轮询模拟WebSocket
    startPolling() {
        // 每5秒轮询一次状态
        this.heartbeatInterval = setInterval(async () => {
            try {
                const response = await fetch(`${config.apiBaseUrl}/detection/status`);
                const data = await response.json();

                // 触发状态更新事件
                this.emit('status_update', {
                    status: data.is_detecting ? 'normal' : 'warning',
                    is_detecting: data.is_detecting
                });

                // 触发连接数更新
                this.emit('connections_update', {
                    count: data.stats.total_scans || 0
                });

            } catch (error) {
                console.error('轮询失败:', error);
            }
        }, 5000);

        // 每3秒检查新日志
        setInterval(async () => {
            try {
                const response = await fetch(`${config.apiBaseUrl}/logs?limit=5`);
                const data = await response.json();

                if (data.logs && data.logs.length > 0) {
                    // 触发新告警事件
                    data.logs.forEach(log => {
                        if (log.level === 'warning' || log.level === 'error') {
                            this.emit('alert_new', {
                                timestamp: log.timestamp,
                                type: log.level === 'error' ? 'error' : 'warn',
                                title: log.type || '系统告警',
                                description: log.description || log.message || '',
                                source: '系统检测',
                                severity: log.severity || 'medium'
                            });
                        }
                    });
                }
            } catch (error) {
                console.error('日志轮询失败:', error);
            }
        }, 3000);
    }

    // 断开连接
    disconnect() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.isConnected = false;
        console.log('WebSocket已断开');
    }

    // 订阅事件
    subscribe(event, callback) {
        if (!this.subscriptions.has(event)) {
            this.subscriptions.set(event, []);
        }
        this.subscriptions.get(event).push(callback);

        return () => this.unsubscribe(event, callback);
    }

    // 取消订阅
    unsubscribe(event, callback) {
        if (this.subscriptions.has(event)) {
            const callbacks = this.subscriptions.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    // 触发事件
    emit(event, data) {
        if (this.subscriptions.has(event)) {
            this.subscriptions.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`WebSocket事件处理错误 (${event}):`, error);
                }
            });
        }
    }

    // 发送消息
    send(message) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket未连接，无法发送消息');
        }
    }

    // 获取连接状态
    getConnectionStatus() {
        return this.isConnected;
    }
}

// 创建单例实例
const wsService = new WebSocketService();
export default wsService;
