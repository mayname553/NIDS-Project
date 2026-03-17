// API 配置 - 基于智能模型与动态优化的轻量级网络入侵检测系统
const API_CONFIG = {
    // 基础URL - 连接到 Flask 后端
    BASE_URL: 'http://localhost:5000/api',

    // 超时设置
    TIMEOUT: 30000,

    // 重试配置
    RETRY: {
        MAX_RETRIES: 3,
        RETRY_DELAY: 1000,
        retryCondition: (error) => {
            // 只在网络错误或5xx状态码时重试
            return !error.response ||
                   error.response.status >= 500 ||
                   error.response.status === 408;
        }
    },

    // WebSocket配置（暂未实现，使用轮询）
    WS_URL: 'ws://localhost:5000/ws',

    // 心跳间隔（秒）
    HEARTBEAT_INTERVAL: 30,

    // 重连配置
    RECONNECT: {
        MAX_ATTEMPTS: 5,
        INITIAL_DELAY: 1000,
        MAX_DELAY: 10000
    }
};

// 接口端点 - 映射到 Flask API
const ENDPOINTS = {
    // 认证（简化版，无需真实认证）
    AUTH: {
        LOGIN: '/health',  // 使用健康检查代替登录
        REFRESH: '/health',
        LOGOUT: '/health'
    },

    // 监控
    MONITOR: {
        TRAFFIC: '/stats',  // 使用统计接口获取流量
        CONNECTIONS: '/stats',
        ALERTS: '/logs',
        STATUS: '/detection/status'
    },

    // 统计
    STATS: {
        ATTACK_TYPES: '/stats',
        TRENDS: '/stats',
        RISK_LEVEL: '/stats',
        AI_PERFORMANCE: '/model/metrics'
    },

    // 检测控制
    DETECTION: {
        START: '/detection/start',
        STOP: '/detection/stop',
        STATUS: '/detection/status'
    },

    // 模型
    MODEL: {
        STATUS: '/model/status',
        METRICS: '/model/metrics',
        TRAIN: '/model/train'
    },

    // 系统
    SYSTEM: {
        HEALTH: '/health',
        CLEAR_LOGS: '/clear-logs',
        RESET_STATS: '/reset-stats',
        REPORT: '/report'
    }
};

export { API_CONFIG, ENDPOINTS };