import { API_CONFIG } from '../api/config.js';

class WebSocketService {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.heartbeatTimer = null;
        this.subscribers = new Map();
        this.isConnected = false;
        this.url = API_CONFIG.WS_URL;
    }

    // 连接WebSocket
    connect() {
        return new Promise((resolve, reject) => {
            try {
                const token = localStorage.getItem('neurosec_token');
                const wsUrl = `${this.url}?token=${encodeURIComponent(token || '')}`;
                
                this.ws = new WebSocket(wsUrl);
                
                this.ws.onopen = () => {
                    console.log('WebSocket连接成功');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.startHeartbeat();
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (error) {
                        console.error('WebSocket消息解析错误:', error);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('WebSocket错误:', error);
                    reject(error);
                };

                this.ws.onclose = (event) => {
                    console.log('WebSocket连接关闭:', event.code, event.reason);
                    this.isConnected = false;
                    this.stopHeartbeat();
                    this.handleDisconnect();
                };

            } catch (error) {
                reject(error);
            }
        });
    }

    // 处理消息
    handleMessage(data) {
        const { type, payload, timestamp } = data;
        
        // 心跳响应
        if (type === 'pong') {
            return;
        }

        // 通知所有订阅者
        if (this.subscribers.has(type)) {
            const callbacks = this.subscribers.get(type);
            callbacks.forEach(callback => {
                try {
                    callback(payload, timestamp);
                } catch (error) {
                    console.error(`WebSocket回调错误 (${type}):`, error);
                }
            });
        }
    }

    // 订阅消息
    subscribe(type, callback) {
        if (!this.subscribers.has(type)) {
            this.subscribers.set(type, []);
        }
        this.subscribers.get(type).push(callback);
        
        // 返回取消订阅的函数
        return () => this.unsubscribe(type, callback);
    }

    // 取消订阅
    unsubscribe(type, callback) {
        if (this.subscribers.has(type)) {
            const callbacks = this.subscribers.get(type);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
            if (callbacks.length === 0) {
                this.subscribers.delete(type);
            }
        }
    }

    // 发送消息
    send(type, data) {
        if (this.isConnected && this.ws) {
            const message = JSON.stringify({
                type,
                data,
                timestamp: Date.now()
            });
            this.ws.send(message);
        } else {
            console.error('WebSocket未连接，无法发送消息');
        }
    }

    // 开始心跳
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected && this.ws) {
                this.send('ping', {});
            }
        }, API_CONFIG.HEARTBEAT_INTERVAL * 1000);
    }

    // 停止心跳
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    // 处理断开连接
    handleDisconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }

        if (this.reconnectAttempts < API_CONFIG.RECONNECT.MAX_ATTEMPTS) {
            const delay = Math.min(
                API_CONFIG.RECONNECT.INITIAL_DELAY * Math.pow(2, this.reconnectAttempts),
                API_CONFIG.RECONNECT.MAX_DELAY
            );

            this.reconnectTimer = setTimeout(() => {
                console.log(`尝试重新连接 (${this.reconnectAttempts + 1}/${API_CONFIG.RECONNECT.MAX_ATTEMPTS})...`);
                this.reconnectAttempts++;
                this.connect().catch(error => {
                    console.error('重新连接失败:', error);
                });
            }, delay);
        } else {
            console.error('达到最大重连次数，连接失败');
            this.notifyDisconnected();
        }
    }

    // 通知所有订阅者连接断开
    notifyDisconnected() {
        this.subscribers.forEach((callbacks, type) => {
            callbacks.forEach(callback => {
                try {
                    callback(null, { error: '连接已断开' });
                } catch (error) {
                    console.error('断开通知回调错误:', error);
                }
            });
        });
    }

    // 断开连接
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        this.stopHeartbeat();
        this.subscribers.clear();
        
        if (this.ws) {
            this.ws.close(1000, '正常关闭');
            this.ws = null;
        }
        
        this.isConnected = false;
    }
}

// 创建单例实例
const wsService = new WebSocketService();
export default wsService;