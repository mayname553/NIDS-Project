import http from '../untils/request.js';
import { ENDPOINTS } from './config.js';

class MonitorService {
    // 获取网络流量数据
    async getTrafficData(timeRange = '10m', interval = '1m') {
        try {
            const { data } = await http.get(ENDPOINTS.MONITOR.TRAFFIC);

            // 生成模拟流量数据
            return this.generateTrafficData();
        } catch (error) {
            console.error('获取流量数据失败:', error);
            return this.generateTrafficData();
        }
    }

    // 生成流量数据
    generateTrafficData() {
        const now = Date.now();
        const timestamps = [];
        const total = [];

        for (let i = 9; i >= 0; i--) {
            timestamps.push(now - i * 60000);
            total.push(Math.floor(Math.random() * 5000) + 2000);
        }

        return {
            timestamps,
            total,
            inbound: total.map(v => Math.floor(v * 0.6)),
            outbound: total.map(v => Math.floor(v * 0.4))
        };
    }

    // 获取活跃连接数
    async getActiveConnections() {
        try {
            const { data } = await http.get(ENDPOINTS.MONITOR.CONNECTIONS);
            return {
                count: data.stats.total_scans || 0,
                active: data.is_detecting
            };
        } catch (error) {
            console.error('获取连接数失败:', error);
            return { count: 0, active: false };
        }
    }

    // 获取实时告警
    async getAlerts(limit = 20, severity = null) {
        try {
            const params = { limit };
            if (severity) {
                params.level = severity;
            }

            const { data } = await http.get(ENDPOINTS.MONITOR.ALERTS, params);
            return this.formatAlerts(data.logs || []);
        } catch (error) {
            console.error('获取告警失败:', error);
            return [];
        }
    }

    // 格式化告警数据
    formatAlerts(logs) {
        return logs.map(log => ({
            id: log.timestamp,
            type: this.mapLevelToType(log.level),
            title: log.type || '系统消息',
            description: log.description || log.message || '',
            source: log.source || '系统检测',
            timestamp: new Date(log.timestamp),
            severity: log.severity || 'medium',
            status: 'active'
        }));
    }

    // 将日志级别映射到前端类型
    mapLevelToType(level) {
        const map = {
            'error': 'error',
            'warning': 'warn',
            'info': 'info'
        };
        return map[level] || 'info';
    }

    // 获取系统状态
    async getSystemStatus() {
        try {
            const { data } = await http.get(ENDPOINTS.MONITOR.STATUS);

            let status = 'normal';
            if (!data.is_detecting) {
                status = 'warning';
            } else if (data.stats.threats_detected > 10) {
                status = 'critical';
            }

            return {
                status,
                is_detecting: data.is_detecting,
                message: data.is_detecting ? '系统运行正常' : '检测已停止',
                stats: data.stats
            };
        } catch (error) {
            console.error('获取系统状态失败:', error);
            return {
                status: 'error',
                is_detecting: false,
                message: '无法连接到服务器'
            };
        }
    }
}
}

export default new MonitorService();
// src/api/monitor.js
import http from './config.js';

export const monitorApi = {
    getTrafficData(params) {
        return http.get('/monitor/traffic', params);
    },
    getAlerts(params) {
        return http.get('/monitor/alerts', params);
    },
    getSystemStatus() {
        return http.get('/monitor/status');
    },
};