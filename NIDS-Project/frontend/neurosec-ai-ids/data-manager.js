import api from './api/index.js';
import wsService from './utils/websocket.js';

class DataManager {
    constructor() {
        this.isInitialized = false;
        this.dataCache = new Map();
        this.cacheTTL = 10000; // 10秒缓存
        this.subscriptions = new Map();
    }

    // 初始化
    async initialize() {
        if (this.isInitialized) return;

        try {
            // 连接WebSocket
            await wsService.connect();
            
            // 订阅实时数据
            this.setupWebSocketSubscriptions();
            
            this.isInitialized = true;
            console.log('数据管理器初始化成功');
        } catch (error) {
            console.error('数据管理器初始化失败:', error);
            throw error;
        }
    }

    // 设置WebSocket订阅
    setupWebSocketSubscriptions() {
        // 订阅实时流量
        wsService.subscribe('traffic_update', (data) => {
            this.handleTrafficUpdate(data);
        });

        // 订阅实时告警
        wsService.subscribe('alert_new', (data) => {
            this.handleNewAlert(data);
        });

        // 订阅连接数更新
        wsService.subscribe('connections_update', (data) => {
            this.handleConnectionsUpdate(data);
        });

        // 订阅系统状态
        wsService.subscribe('status_update', (data) => {
            this.handleStatusUpdate(data);
        });
    }

    // 获取流量数据
    async getTrafficData(forceRefresh = false) {
        const cacheKey = 'traffic_data';
        
        if (!forceRefresh && this.isCacheValid(cacheKey)) {
            return this.dataCache.get(cacheKey);
        }

        try {
            const data = await api.monitor.getTrafficData('10m', '1m');
            this.updateCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('获取流量数据失败:', error);
            return this.getFallbackData('traffic');
        }
    }

    // 获取攻击类型统计
    async getAttackTypes(forceRefresh = false) {
        const cacheKey = 'attack_types';
        
        if (!forceRefresh && this.isCacheValid(cacheKey)) {
            return this.dataCache.get(cacheKey);
        }

        try {
            const data = await api.stats.getAttackTypes('24h');
            this.updateCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('获取攻击类型失败:', error);
            return this.getFallbackData('attack_types');
        }
    }

    // 获取风险等级
    async getRiskLevel(forceRefresh = false) {
        const cacheKey = 'risk_level';
        
        if (!forceRefresh && this.isCacheValid(cacheKey)) {
            return this.dataCache.get(cacheKey);
        }

        try {
            const data = await api.stats.getRiskLevel();
            this.updateCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('获取风险等级失败:', error);
            return this.getFallbackData('risk_level');
        }
    }

    // 获取AI性能
    async getAIPerformance(forceRefresh = false) {
        const cacheKey = 'ai_performance';
        
        if (!forceRefresh && this.isCacheValid(cacheKey)) {
            return this.dataCache.get(cacheKey);
        }

        try {
            const data = await api.stats.getAIPerformance();
            this.updateCache(cacheKey, data);
            return data;
        } catch (error) {
            console.error('获取AI性能失败:', error);
            return this.getFallbackData('ai_performance');
        }
    }

    // 获取告警
    async getAlerts(limit = 20) {
        try {
            return await api.monitor.getAlerts(limit);
        } catch (error) {
            console.error('获取告警失败:', error);
            return this.getFallbackData('alerts');
        }
    }

    // 获取系统状态
    async getSystemStatus() {
        try {
            return await api.monitor.getSystemStatus();
        } catch (error) {
            console.error('获取系统状态失败:', error);
            return this.getFallbackData('system_status');
        }
    }

    // WebSocket数据更新处理
    handleTrafficUpdate(data) {
        this.updateCache('traffic_data', data, true);
        this.notifySubscribers('traffic_update', data);
    }

    handleNewAlert(data) {
        this.notifySubscribers('alert_new', data);
    }

    handleConnectionsUpdate(data) {
        this.notifySubscribers('connections_update', data);
    }

    handleStatusUpdate(data) {
        this.updateCache('system_status', data, true);
        this.notifySubscribers('status_update', data);
    }

    // 缓存管理
    updateCache(key, data, isWebSocket = false) {
        const cacheItem = {
            data,
            timestamp: Date.now(),
            isWebSocket
        };
        this.dataCache.set(key, cacheItem);
    }

    isCacheValid(key) {
        if (!this.dataCache.has(key)) return false;
        
        const cacheItem = this.dataCache.get(key);
        const age = Date.now() - cacheItem.timestamp;
        
        return age < this.cacheTTL || cacheItem.isWebSocket;
    }

    // 后备数据
    getFallbackData(type) {
        // 这里可以返回模拟数据或缓存数据
        console.warn(`使用后备数据: ${type}`);
        
        const fallbackData = {
            traffic: {
                timestamps: [],
                inbound: [],
                outbound: [],
                total: []
            },
            attack_types: [],
            risk_level: { value: 25, level: 'low' },
            ai_performance: {
                accuracy: 95.5,
                recall: 94.2,
                f1_score: 94.8,
                precision: 93.7,
                response_time: 97.5
            },
            alerts: [],
            system_status: { status: 'unknown', message: '无法连接到服务器' }
        };

        return fallbackData[type] || null;
    }

    // 订阅数据更新
    subscribe(event, callback) {
        if (!this.subscriptions.has(event)) {
            this.subscriptions.set(event, []);
        }
        this.subscriptions.get(event).push(callback);
        
        // 返回取消订阅函数
        return () => this.unsubscribe(event, callback);
    }

    unsubscribe(event, callback) {
        if (this.subscriptions.has(event)) {
            const callbacks = this.subscriptions.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    notifySubscribers(event, data) {
        if (this.subscriptions.has(event)) {
            this.subscriptions.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`订阅回调错误 (${event}):`, error);
                }
            });
        }
    }

    // 清理
    cleanup() {
        this.subscriptions.clear();
        this.dataCache.clear();
        wsService.disconnect();
        this.isInitialized = false;
    }
}

// 创建单例实例
const dataManager = new DataManager();
export default dataManager;