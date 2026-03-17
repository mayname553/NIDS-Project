import api from './api/index.js';

class LoginManager {
    constructor() {
        this.form = document.getElementById('login-form');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.togglePasswordBtn = document.getElementById('toggle-password');
        this.loginButton = document.getElementById('login-button');
        this.buttonLoader = document.getElementById('button-loader');
        this.errorElement = document.getElementById('login-error');
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkRememberedUser();
    }

    bindEvents() {
        // 表单提交
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // 显示/隐藏密码
        this.togglePasswordBtn.addEventListener('click', () => this.togglePassword());
        
        // 输入时清除错误
        this.usernameInput.addEventListener('input', () => this.clearError());
        this.passwordInput.addEventListener('input', () => this.clearError());
        
        // 回车键提交
        this.form.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.loginButton.disabled) {
                this.handleSubmit(e);
            }
        });
    }

    checkRememberedUser() {
        const rememberedUser = localStorage.getItem('neurosec_remembered_user');
        if (rememberedUser) {
            this.usernameInput.value = rememberedUser;
            document.getElementById('remember-me').checked = true;
            this.passwordInput.focus();
        } else {
            this.usernameInput.focus();
        }
    }

    togglePassword() {
        const type = this.passwordInput.type === 'password' ? 'text' : 'password';
        this.passwordInput.type = type;
        this.togglePasswordBtn.innerHTML = type === 'password' 
            ? '<i class="fas fa-eye"></i>' 
            : '<i class="fas fa-eye-slash"></i>';
    }

    clearError() {
        this.errorElement.classList.remove('show');
        this.errorElement.textContent = '';
    }

    showError(message) {
        this.errorElement.textContent = message;
        this.errorElement.classList.add('show');
    }

    setLoading(loading) {
        this.loginButton.disabled = loading;
        this.loginButton.classList.toggle('loading', loading);
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        const username = this.usernameInput.value.trim();
        const password = this.passwordInput.value;
        const rememberMe = document.getElementById('remember-me').checked;
        
        // 验证输入
        if (!username || !password) {
            this.showError('请输入用户名和密码');
            return;
        }
        
        this.setLoading(true);
        this.clearError();
        
        try {
            const result = await api.auth.login(username, password);
            
            if (result.success) {
                // 保存记住的用户名
                if (rememberMe) {
                    localStorage.setItem('neurosec_remembered_user', username);
                } else {
                    localStorage.removeItem('neurosec_remembered_user');
                }
                
                // 保存用户信息
                localStorage.setItem('neurosec_user', JSON.stringify(result.user));
                
                // 显示成功消息
                this.showSuccess('登录成功，正在跳转...');
                
                // 延迟跳转
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
                
            } else {
                this.showError(result.error || '登录失败，请检查用户名和密码');
            }
            
        } catch (error) {
            console.error('登录错误:', error);
            this.showError('网络错误，请检查网络连接后重试');
            
        } finally {
            this.setLoading(false);
        }
    }

    showSuccess(message) {
        this.errorElement.style.color = '#00ff00';
        this.errorElement.textContent = message;
        this.errorElement.classList.add('show');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new LoginManager();
    
    // 检查URL参数
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('session_expired')) {
        const errorElement = document.getElementById('login-error');
        errorElement.style.color = '#ffaa00';
        errorElement.textContent = '会话已过期，请重新登录';
        errorElement.classList.add('show');
    }
});