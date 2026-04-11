import authService from './auth.js';
import monitorService from './monitor.js';
import statsService from './stats.js';

const api = {
    auth: authService,
    monitor: monitorService,
    stats: statsService
};

export default api;