// src/services/auth.service.js
import http from '../utils/request.js';
import { storage } from '../utils/storage.js';

export const authService = {
    async login(username, password) {
        const res = await http.post('/auth/login', { username, password });
        if (res.token) {
            storage.setToken(res.token, res.refreshToken);
            return res;
        }
        throw new Error('登录失败');
    },

    async logout() {
        await http.post('/auth/logout');
        storage.clearAll();
    },

    async refreshToken() {
        const refreshToken = storage.getRefreshToken();
        if (!refreshToken) throw new Error('无刷新令牌');
        const res = await http.post('/auth/refresh', { refreshToken });
        storage.setToken(res.token, res.refreshToken);
        return res.token;
    },
};