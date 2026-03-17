export class Dashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.charts = {};
    }

    render() {
        this.container.innerHTML = `
            <header class="top-navbar">
                <div class="logo-container">
                    <div class="logo-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h1 class="system-title">NeuroSec-AI <span class="subtitle">智能网络入侵检测平台</span></h1>
                </div>
                <div class="nav-info">
                    <div class="time-display">
                        <i class="far fa-clock"></i>
                        <span id="current-time">${new Date().toLocaleString()}</span>
                    </div>
                    <div class="status-indicator">
                        <div class="status-dot" id="status-dot"></div>
                        <span id="system-status">系统状态: <span class="status-text" id="status-text">加载中...</span></span>
                    </div>
                </div>
            </header>

            <main class="dashboard">
                <section class="left-panel">
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3><i class="fas fa-chart-line"></i> 实时网络流量监控</h3>
                        </div>
                        <div class="card-content">
                            <div id="traffic-chart" class="chart-container"></div>
                        </div>
                    </div>
                    
                    <div class="stats-row">
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-network-wired"></i>
                            </div>
                            <div class="stat-info">
                                <h4>活跃连接数</h4>
                                <p class="stat-value" id="active-connections">0</p>
                                <p class="stat-change positive" id="connections-change">+0</p>
                            </div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon">
                                <i class="fas fa-biohazard"></i>
                            </div>
                            <div class="stat-info">
                                <h4>今日攻击次数</h4>
                                <p class="stat-value" id="attack-count">0</p>
                                <p class="stat-change negative" id="attacks-change">+0</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section class="center-panel">
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3><i class="fas fa-chart-pie"></i> 攻击类型统计</h3>
                        </div>
                        <div class="card-content">
                            <div id="attack-pie" class="chart-container"></div>
                        </div>
                    </div>
                    
                    <div class="dashboard-row">
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3><i class="fas fa-tachometer-alt"></i> 整体风险等级</h3>
                            </div>
                            <div class="card-content">
                                <div id="risk-gauge" class="chart-container"></div>
                            </div>
                        </div>
                        
                        <div class="dashboard-card">
                            <div class="card-header">
                                <h3><i class="fas fa-chart-bar"></i> 攻击趋势分析</h3>
                            </div>
                            <div class="card-content">
                                <div id="attack-trend" class="chart-container"></div>
                            </div>
                        </div>
                    </div>
                </section>

                <section class="right-panel">
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3><i class="fas fa-exclamation-triangle"></i> 实时告警日志</h3>
                        </div>
                        <div class="card-content">
                            <div class="alert-log">
                                <div id="alert-list" class="alert-list">
                                    <!-- 告警日志将通过JS动态生成 -->
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="dashboard-card">
                        <div class="card-header">
                            <h3><i class="fas fa-brain"></i> AI模型性能评估</h3>
                        </div>
                        <div class="card-content">
                            <div id="ai-radar" class="chart-container"></div>
                        </div>
                    </div>
                </section>
            </main>

            <footer class="footer">
                <div class="footer-info">
                    <p><i class="fas fa-server"></i> 总监测节点: 12 | 
                       <i class="fas fa-shield-alt"></i> 防护设备: 36 | 
                       <i class="fas fa-user-shield"></i> 在线管理员: 3</p>
                    <p>系统版本: NeuroSec-AI v2.6.3 | 最后更新: ${new Date().toLocaleString()}</p>
                </div>
            </footer>
        `;

        this.initCharts();
        this.loadData();
        this.startTimers();
    }

    initCharts() {
        // 初始化 ECharts 图表
        this.charts.traffic = echarts.init(document.getElementById('traffic-chart'));
        this.charts.attackPie = echarts.init(document.getElementById('attack-pie'));
        this.charts.riskGauge = echarts.init(document.getElementById('risk-gauge'));
        this.charts.attackTrend = echarts.init(document.getElementById('attack-trend'));
        this.charts.aiRadar = echarts.init(document.getElementById('ai-radar'));
    }

    async loadData() {
        try {
            const [
                trafficData,
                attackTypes,
                alerts,
                systemStatus
            ] = await Promise.all([
                window.dataService.getTrafficData(),
                window.dataService.getAttackTypes(),
                window.dataService.getAlerts(20),
                window.dataService.getSystemStatus()
            ]);

            this.updateTrafficChart(trafficData);
            this.updateAttackPie(attackTypes);
            this.updateAlerts(alerts);
            this.updateSystemStatus(systemStatus);

        } catch (error) {
            console.error('加载数据失败:', error);
        }
    }

    updateTrafficChart(data) {
        if (!this.charts.traffic) return;
        
        const option = {
            xAxis: {
                type: 'category',
                data: data.timestamps
            },
            yAxis: {
                type: 'value',
                name: 'Mbps'
            },
            series: [{
                data: data.total,
                type: 'line',
                smooth: true
            }]
        };
        
        this.charts.traffic.setOption(option);
    }

    updateAttackPie(data) {
        if (!this.charts.attackPie) return;
        
        const option = {
            tooltip: {
                trigger: 'item'
            },
            series: [{
                type: 'pie',
                data: data.map(item => ({
                    name: item.name,
                    value: item.value
                }))
            }]
        };
        
        this.charts.attackPie.setOption(option);
    }

    updateAlerts(alerts) {
        const alertList = document.getElementById('alert-list');
        if (!alertList) return;
        
        alertList.innerHTML = '';
        
        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item ${alert.type}`;
            alertItem.innerHTML = `
                <div class="alert-header">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-time">${this.formatRelativeTime(alert.timestamp)}</div>
                </div>
                <div class="alert-desc">${alert.description}</div>
                <div class="alert-source">
                    <i class="fas fa-map-marker-alt"></i> 来源: ${alert.source}
                </div>
            `;
            alertList.appendChild(alertItem);
        });
    }

    updateSystemStatus(status) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.getElementById('status-dot');
        
        if (statusText && statusDot) {
            const statusMap = {
                'normal': { text: '安全', class: 'secure', color: '#00ff00' },
                'warning': { text: '风险', class: 'warning', color: '#ffaa00' },
                'critical': { text: '高危', class: 'danger', color: '#ff3300' }
            };
            
            const statusInfo = statusMap[status.status] || statusMap.normal;
            
            statusText.textContent = statusInfo.text;
            statusText.className = `status-text ${statusInfo.class}`;
            statusDot.style.backgroundColor = statusInfo.color;
        }
    }

    startTimers() {
        // 更新时间
        setInterval(() => {
            const timeElement = document.getElementById('current-time');
            if (timeElement) {
                timeElement.textContent = new Date().toLocaleString();
            }
        }, 1000);

        // 定时刷新数据
        setInterval(() => {
            this.loadData();
        }, 30000);
    }

    formatRelativeTime(timestamp) {
        const now = new Date();
        const date = new Date(timestamp);
        const diffMs = now - date;
        const diffMin = Math.floor(diffMs / 60000);
        
        if (diffMin < 1) return '刚刚';
        if (diffMin < 60) return `${diffMin}分钟前`;
        if (diffMin < 1440) return `${Math.floor(diffMin / 60)}小时前`;
        return `${Math.floor(diffMin / 1440)}天前`;
    }
}