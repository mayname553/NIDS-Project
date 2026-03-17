export class LoginPage {
    constructor(containerId, onLoginSuccess) {
        this.container = document.getElementById(containerId);
        this.onLoginSuccess = onLoginSuccess;
    }

    render() {
        this.container.innerHTML = `
            <div class="login-container">
                <div class="login-card">
                    <div class="login-header">
                        <div class="login-logo">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <h1>NeuroSec-AI</h1>
                        <p class="login-subtitle">智能网络入侵检测平台</p>
                    </div>
                    
                    <form id="login-form" class="login-form">
                        <div class="form-group">
                            <label for="username">
                                <i class="fas fa-user"></i> 用户名
                            </label>
                            <input 
                                type="text" 
                                id="username" 
                                name="username" 
                                placeholder="请输入用户名" 
                                required
                                autocomplete="username"
                            >
                        </div>
                        
                        <div class="form-group">
                            <label for="password">
                                <i class="fas fa-lock"></i> 密码
                            </label>
                            <div class="password-input">
                                <input 
                                    type="password" 
                                    id="password" 
                                    name="password" 
                                    placeholder="请输入密码" 
                                    required
                                    autocomplete="current-password"
                                >
                                <button type="button" class="toggle-password" id="toggle-password">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                        </div>
                        
                        <button type="submit" class="login-button" id="login-button">
                            <span class="button-text">登录</span>
                            <span class="button-loader" id="button-loader">
                                <i class="fas fa-spinner fa-spin"></i>
                            </span>
                        </button>
                        
                        <div class="login-error" id="login-error"></div>
                    </form>
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        const form = document.getElementById('login-form');
        const togglePasswordBtn = document.getElementById('toggle-password');
        const loginButton = document.getElementById('login-button');
        const errorElement = document.getElementById('login-error');

        // 显示/隐藏密码
        togglePasswordBtn.addEventListener('click', () => {
            const passwordInput = document.getElementById('password');
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            togglePasswordBtn.innerHTML = type === 'password' 
                ? '<i class="fas fa-eye"></i>' 
                : '<i class="fas fa-eye-slash"></i>';
        });

        // 表单提交
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                this.showError('请输入用户名和密码');
                return;
            }
            
            this.setLoading(true);
            
            try {
                const result = await window.authService.login(username, password);
                
                if (result.success) {
                    this.showSuccess('登录成功，正在跳转...');
                    
                    setTimeout(() => {
                        this.onLoginSuccess();
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
        });
    }

    setLoading(loading) {
        const loginButton = document.getElementById('login-button');
        loginButton.disabled = loading;
        loginButton.classList.toggle('loading', loading);
    }

    showError(message) {
        const errorElement = document.getElementById('login-error');
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }

    showSuccess(message) {
        const errorElement = document.getElementById('login-error');
        errorElement.style.color = '#00ff00';
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}