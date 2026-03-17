// src/utils/storage.js
const STORAGE_KEYS = {
    TOKEN: 'neurosec_token',
    REFRESH_TOKEN: 'neurosec_refresh_token',
    USER_INFO: 'neurosec_user',
};

export const storage = {
    setToken(token, refreshToken) {
        localStorage.setItem(STORAGE_KEYS.TOKEN, token);
        if (refreshToken) {
            localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
        }
    },
    getToken() {
        return localStorage.getItem(STORAGE_KEYS.TOKEN);
    },
    getRefreshToken() {
        return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    },
    clearAll() {
        Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
    },
};