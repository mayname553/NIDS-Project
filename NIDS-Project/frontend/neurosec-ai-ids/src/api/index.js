import authService from './auth.js';
import monitorService from './monitor.js';
import statsService from './stats.js';

// 统一导出所有API服务
const api = {
    auth: authService,
    monitor: monitorService,
    stats: statsService
};

export default api;
// src/api/index.js
export { authApi } from './auth.js';
export { monitorApi } from './monitor.js';
export { statsApi } from './stats.js';