// 环境配置 - 基于智能模型与动态优化的轻量级网络入侵检测系统
const config = {
    // 开发环境
    development: {
        apiBaseUrl: 'http://localhost:5000/api',
        wsUrl: 'ws://localhost:5000/ws',
        debug: true
    },

    // 生产环境
    production: {
        apiBaseUrl: 'http://localhost:5000/api',
        wsUrl: 'ws://localhost:5000/ws',
        debug: false
    }
};

// 获取当前环境
const env = import.meta.env.MODE || 'development';

// 导出配置
export default config[env];