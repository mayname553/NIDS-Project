import http from '../utils/request.js';
import { ENDPOINTS } from './config.js';

class AuthService {
    // 用户登录
    async login(username, password) {
        try {
            const { data } = await http.post(ENDPOINTS.AUTH.LOGIN, {
                username,
                password
            });

            // 保存Token
            http.setToken(data.access_token, data.refresh_token);
            
            return {
                success: true,
                user: data.user
            };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.message || '登录失败'
            };
        }
    }

    // 刷新Token
    async refreshToken() {
        const refreshToken = localStorage.getItem('neurosec_refresh_token');
        if (!refreshToken) {
            throw new Error('没有可用的刷新令牌');
        }

        const { data } = await http.post(ENDPOINTS.AUTH.REFRESH, {
            refresh_token: refreshToken
        });

        http.setToken(data.access_token, data.refresh_token);
        return data.access_token;
    }

    // 用户登出
    async logout() {
        try {
            await http.post(ENDPOINTS.AUTH.LOGOUT);
        } catch (error) {
            console.error('登出失败:', error);
        } finally {
            http.clearToken();
            localStorage.removeItem('neurosec_user');
        }
    }

    // 检查登录状态
    isAuthenticated() {
        const token = localStorage.getItem('neurosec_token');
        if (!token) return false;

        try {
            // 解析JWT Token，检查是否过期
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 > Date.now();
        } catch (error) {
            return false;
        }
    }

    // 获取当前用户
    getCurrentUser() {
        const userStr = localStorage.getItem('neurosec_user');
        return userStr ? JSON.parse(userStr) : null;
    }
}

export default new AuthService();
// src/api/auth.js
import http from './config.js';

export const authApi = {
    login(data) {
        return http.post('/auth/login', data);
    },
    logout() {
        return http.post('/auth/logout');
    },
    refresh(data) {
        return http.post('/auth/refresh', data);
    },
};