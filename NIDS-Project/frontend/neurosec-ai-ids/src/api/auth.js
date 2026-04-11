import http from '../untils/request.js';
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
        return !!localStorage.getItem('neurosec_token');
    }

    // 获取当前用户
    getCurrentUser() {
        const userStr = localStorage.getItem('neurosec_user');
        return userStr ? JSON.parse(userStr) : null;
    }
}

export default new AuthService();