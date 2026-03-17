// src/config/constants.js
export const API_CONFIG = {
    BASE_URL: 'http://localhost:8080/api/v1', // 本地开发时用这个
    TIMEOUT: 30000,
    RETRY: {
        MAX_RETRIES: 3,
        RETRY_DELAY: 1000,
    },
};