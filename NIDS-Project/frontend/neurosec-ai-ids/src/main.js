import './style.css';
import { authService } from './services/auth.service.js';
import { LoginPage } from './components/LoginPage.js';
import { Dashboard } from './components/Dashboard.js';

// 将服务挂载到全局，方便组件访问
window.authService = authService;
window.dataService = dataService; // 假设 dataService 在 data.service.js 中

class NeuroSecApp {
    constructor() {
        this.currentPage = null;
        this.init();
    }

    async init() {
        console.log('NeuroSec-AI 系统启动中...');
        
        // 检查登录状态
        if (this.checkAuth()) {
            this.showDashboard();
        } else {
            this.showLoginPage();
        }
    }

    checkAuth() {
        return authService.isAuthenticated();
    }

    showLoginPage() {
        this.currentPage = new LoginPage('app', () => {
            this.showDashboard();
        });
        this.currentPage.render();
    }

    showDashboard() {
        this.currentPage = new Dashboard('app');
        this.currentPage.render();
    }
}

// 启动应用
document.addEventListener('DOMContentLoaded', () => {
    new NeuroSecApp();
});