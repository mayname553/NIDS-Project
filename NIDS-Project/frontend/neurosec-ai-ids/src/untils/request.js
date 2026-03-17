import { API_CONFIG } from '../api/config.js';

class HttpRequest {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.timeout = API_CONFIG.TIMEOUT;
        this.retryConfig = API_CONFIG.RETRY;
        this.token = localStorage.getItem('neurosec_token') || null;
        this.refreshToken = localStorage.getItem('neurosec_refresh_token') || null;
    }

    // 设置Token
    setToken(token, refreshToken) {
        this.token = token;
        this.refreshToken = refreshToken;
        localStorage.setItem('neurosec_token', token);
        if (refreshToken) {
            localStorage.setItem('neurosec_refresh_token', refreshToken);
        }
    }

    // 清除Token
    clearToken() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('neurosec_token');
        localStorage.removeItem('neurosec_refresh_token');
    }

    // 获取请求头
    getHeaders(hasBody = true) {
        const headers = {
            'Accept': 'application/json',
        };

        if (hasBody) {
            headers['Content-Type'] = 'application/json';
        }

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // 请求拦截器
    async requestInterceptor(config) {
        // 可以在这里添加全局请求逻辑
        return config;
    }

    // 响应拦截器
    async responseInterceptor(response) {
        // 检查Token是否即将过期
        if (response.headers.has('token-expiring-soon')) {
            await this.refreshAccessToken();
        }
        return response;
    }

    // 错误处理
    async errorHandler(error, config, retryCount = 0) {
        const { retryCondition, MAX_RETRIES, RETRY_DELAY } = this.retryConfig;
        
        // 如果是401错误，尝试刷新Token
        if (error.response && error.response.status === 401 && this.refreshToken) {
            try {
                await this.refreshAccessToken();
                // 重试原始请求
                return this.request(config.url, config.options, retryCount);
            } catch (refreshError) {
                // 刷新Token失败，跳转到登录页
                this.redirectToLogin();
                throw refreshError;
            }
        }

        // 检查是否需要重试
        if (retryCondition(error) && retryCount < MAX_RETRIES) {
            console.log(`请求失败，正在重试 (${retryCount + 1}/${MAX_RETRIES})...`);
            
            // 指数退避延迟
            const delay = RETRY_DELAY * Math.pow(2, retryCount);
            await this.sleep(delay);
            
            return this.request(config.url, config.options, retryCount + 1);
        }

        // 处理其他错误
        this.handleError(error);
        throw error;
    }

    // 刷新访问令牌
    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.baseURL}${ENDPOINTS.AUTH.REFRESH}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.refreshToken}`
                },
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });

            if (!response.ok) {
                throw new Error('刷新Token失败');
            }

            const data = await response.json();
            this.setToken(data.access_token, data.refresh_token);
            return data.access_token;
        } catch (error) {
            this.clearToken();
            this.redirectToLogin();
            throw error;
        }
    }

    // 跳转到登录页
    redirectToLogin() {
        window.location.href = '/login.html?session_expired=true';
    }

    // 错误处理
    handleError(error) {
        if (error.response) {
            console.error('API错误:', {
                status: error.response.status,
                statusText: error.response.statusText,
                data: error.response.data
            });
        } else if (error.request) {
            console.error('网络错误:', error.message);
        } else {
            console.error('请求错误:', error.message);
        }
    }

    // 延迟函数
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 主请求方法
    async request(url, options = {}, retryCount = 0) {
        const config = {
            url: url.startsWith('http') ? url : `${this.baseURL}${url}`,
            options: {
                ...options,
                headers: this.getHeaders(options.body !== undefined),
                timeout: this.timeout
            }
        };

        try {
            // 请求拦截
            await this.requestInterceptor(config);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const fetchOptions = {
                ...config.options,
                signal: controller.signal
            };

            if (fetchOptions.body && typeof fetchOptions.body === 'object') {
                fetchOptions.body = JSON.stringify(fetchOptions.body);
            }

            const response = await fetch(config.url, fetchOptions);
            clearTimeout(timeoutId);

            if (!response.ok) {
                const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                error.response = response;
                throw error;
            }

            const data = await response.json();
            
            // 响应拦截
            await this.responseInterceptor(response);
            
            return { data, response };

        } catch (error) {
            return this.errorHandler(error, config, retryCount);
        }
    }

    // HTTP方法封装
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        return this.request(fullUrl, { method: 'GET' });
    }

    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: data
        });
    }

    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data
        });
    }

    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }

    async patch(url, data = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: data
        });
    }
}

// 创建单例实例
const http = new HttpRequest();
export default http;