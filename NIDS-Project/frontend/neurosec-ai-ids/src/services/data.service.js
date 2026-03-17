import { monitorApi, statsApi } from '../api/index.js';

class DataService {
    constructor() {
        this.cache = new Map();
        this.cacheTTL = 10000; // 10秒缓存
    }

    // 获取实时网络流量
    async getTrafficData(forceRefresh = false) {
        const cacheKey = 'traffic_data';
        if (!forceRefresh && this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            const response = await monitorApi.getTrafficData({
                time_range: '10m',
                interval: '1m'
            });
            
            const data = this.formatTrafficData(response.data);
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
            return this.cache.get(cacheKey);
        }

        try {
            const response = await statsApi.getAttackTypes({
                time_range: '24h'
            });
            
            this.updateCache(cacheKey, response.data);
            return response.data;
        } catch (error) {
            console.error('获取攻击类型失败:', error);
            return this.getFallbackData('attack_types');
        }
    }

    // 获取实时告警
    async getAlerts(limit = 20) {
        try {
            const response = await monitorApi.getAlerts({ limit });
            return this.formatAlerts(response.data);
        } catch (error) {
            console.error('获取告警失败:', error);
            return this.getFallbackData('alerts');
        }
    }

    // 获取系统状态
    async getSystemStatus() {
        try {
            const response = await monitorApi.getSystemStatus();
            return response.data;
        } catch (error) {
            console.error('获取系统状态失败:', error);
            return { status: 'error', message: '无法连接到服务器' };
        }
    }

    // 格式化流量数据
    formatTrafficData(data) {
        return {
            timestamps: data.timestamps || [],
            inbound: data.inbound || [],
            outbound: data.outbound || [],
            total: data.total || []
        };
    }

    // 格式化告警数据
    formatAlerts(alerts) {
        return alerts.map(alert => ({
            id: alert.id,
            type: this.mapSeverityToType(alert.severity),
            title: alert.title,
            description: alert.description,
            source: alert.source_ip || alert.source,
            timestamp: new Date(alert.timestamp),
            severity: alert.severity
        }));
    }

    // 映射严重级别
    mapSeverityToType(severity) {
        const map = {
            'critical': 'critical',
            'high': 'critical',
            'medium': 'warning',
            'low': 'info',
            'info': 'info'
        };
        return map[severity] || 'info';
    }

    // 缓存管理
    updateCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    isCacheValid(key) {
        if (!this.cache.has(key)) return false;
        const cacheItem = this.cache.get(key);
        return (Date.now() - cacheItem.timestamp) < this.cacheTTL;
    }

    // 后备数据
    getFallbackData(type) {
        console.warn(`使用后备数据: ${type}`);
        // 这里可以返回一些默认数据
        return null;
    }
}

export default new DataService();