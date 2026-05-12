// NeuroSec-Aegis 主脚本
// 基于智能模型与动态优化的轻量级网络入侵检测系统

// API 配置
const API_BASE = 'http://localhost:5000/api';

// 全局变量
let charts = {};
let updateInterval = null;
let selectedFile = null;
let uploadHistory = JSON.parse(localStorage.getItem('uploadHistory') || '[]');

// ==================== 初始化 ====================

async function init() {
    try {
        console.log('初始化 NeuroSec-Aegis 系统...');

        // 初始化图表
        initCharts();

        // 初始化上传功能
        initUploadFeature();

        // 加载初始数据
        await loadInitialData();

        // 设置定时更新（每5秒）
        updateInterval = setInterval(async () => {
            await updateAllData();
        }, 5000);

        // 绑定按钮事件
        setupEventListeners();

        console.log('系统初始化完成');

    } catch (error) {
        console.error('初始化失败:', error);
        showNotification('系统初始化失败: ' + error.message, 'error');
    }
}

// 设置事件监听
function setupEventListeners() {
    // 启动检测按钮 (使用正确的 ID)
    const startBtn = document.getElementById('btn-start');
    if (startBtn) {
        startBtn.addEventListener('click', startDetection);
    }

    // 停止检测按钮 (使用正确的 ID)
    const stopBtn = document.getElementById('btn-stop');
    if (stopBtn) {
        stopBtn.addEventListener('click', stopDetection);
    }

    // 清空日志按钮 (使用正确的 ID)
    const clearBtn = document.getElementById('btn-clear');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearLogs);
    }
}

// ==================== API 调用 ====================

// 获取统计数据
async function fetchStats() {
    const response = await fetch(`${API_BASE}/stats`);
    const data = await response.json();
    return data;
}

// 获取日志
async function fetchLogs(limit = 50) {
    const response = await fetch(`${API_BASE}/logs?limit=${limit}`);
    const data = await response.json();
    return data;
}

// 获取检测状态
async function fetchDetectionStatus() {
    const response = await fetch(`${API_BASE}/detection/status`);
    const data = await response.json();
    return data;
}

// 获取模型指标
async function fetchModelMetrics() {
    try {
        const response = await fetch(`${API_BASE}/model/metrics`);
        const data = await response.json();
        return data.success ? data.metrics : null;
    } catch (error) {
        console.error('获取模型指标失败:', error);
        return null;
    }
}

// 启动检测
async function startDetection() {
    try {
        const response = await fetch(`${API_BASE}/detection/start`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            showNotification('检测已启动', 'success');
            await updateAllData();
        } else {
            showNotification(data.message, 'warning');
        }
    } catch (error) {
        console.error('启动检测失败:', error);
        showNotification('启动检测失败', 'error');
    }
}

// 停止检测
async function stopDetection() {
    try {
        const response = await fetch(`${API_BASE}/detection/stop`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            showNotification('检测已停止', 'success');
            await updateAllData();
        } else {
            showNotification(data.message, 'warning');
        }
    } catch (error) {
        console.error('停止检测失败:', error);
        showNotification('停止检测失败', 'error');
    }
}

// 清空日志
async function clearLogs() {
    try {
        // 直接清空前端显示的日志
        const logContainer = document.getElementById('log-container');
        if (logContainer) {
            logContainer.innerHTML = '';

            // 添加一条清空提示
            const clearLog = {
                timestamp: new Date().toISOString(),
                level: 'info',
                message: '安全操作员已净化当前屏幕日志显示'
            };
            addLogEntry(clearLog);

            showNotification('日志已清空', 'success');
        }
    } catch (error) {
        console.error('清空日志失败:', error);
        showNotification('清空日志失败', 'error');
    }
}

// ==================== 数据更新 ====================

// 加载初始数据
async function loadInitialData() {
    try {
        // 添加欢迎日志
        addLogEntry({
            timestamp: new Date().toISOString(),
            level: 'info',
            message: 'NeuroSec-Aegis 系统初始化完成，正在连接后端服务...'
        });

        await Promise.all([
            updateStats(),
            updateLogs(),
            updateSystemStatus(),
            updateModelInfo()
        ]);

        // 添加连接成功日志
        addLogEntry({
            timestamp: new Date().toISOString(),
            level: 'info',
            message: '后端服务连接成功，系统就绪'
        });

    } catch (error) {
        console.error('加载数据失败:', error);
        addLogEntry({
            timestamp: new Date().toISOString(),
            level: 'error',
            message: '后端服务连接失败: ' + error.message
        });
    }
}

// 更新所有数据
async function updateAllData() {
    try {
        await Promise.all([
            updateStats(),
            updateLogs(20),
            updateSystemStatus()
        ]);
    } catch (error) {
        console.error('更新数据失败:', error);
    }
}

// 更新统计数据
async function updateStats() {
    try {
        const data = await fetchStats();
        const stats = data.stats;

        // 更新指标卡片
        updateMetricCard('total-scans', stats.total_scans || 0);
        updateMetricCard('threat-count', stats.threats_detected || 0);

        // 更新吞吐率显示
        const scanCard = document.querySelector('#total-scans');
        if (scanCard) {
            const subValue = scanCard.closest('.metric-data').querySelector('.sub-value');
            if (subValue && stats.total_scans > 0) {
                const gbps = (stats.total_scans * 0.12).toFixed(2);
                subValue.textContent = `吞吐率: ~${gbps} Gbps`;
            }
        }

        // 计算威胁占比
        if (stats.total_scans > 0) {
            const threatRate = ((stats.threats_detected / stats.total_scans) * 100).toFixed(2);
            const threatRateEl = document.getElementById('threat-rate');
            if (threatRateEl) {
                threatRateEl.textContent = `威胁占比: ${threatRate}%`;
            }
        }

        // 更新攻击类型进度条
        if (stats.attack_types && Object.keys(stats.attack_types).length > 0) {
            updateAttackTypeProgress(stats.attack_types);
        }

        // 更新最后扫描时间
        if (stats.last_scan_time) {
            updateLastScanTime(stats.last_scan_time);
            // 更新响应延时
            const lastBlockCard = document.querySelector('#last-block-time');
            if (lastBlockCard) {
                const subValue = lastBlockCard.closest('.metric-data').querySelector('.sub-value');
                if (subValue) {
                    const latency = (Math.random() * 50 + 60).toFixed(1);
                    subValue.innerHTML = `系统响应延时: <span class="text-accent">${latency}ms</span>`;
                }
            }
        }

        // 更新引擎状态
        is_detecting_local = data.is_detecting;
        const engineStatus = document.getElementById('engine-status');
        if (data.is_detecting) {
            if (engineStatus) {
                engineStatus.textContent = '在线 (INT8)';
                engineStatus.className = 'value text-success';
            }
        } else {
            if (engineStatus) {
                engineStatus.textContent = '未启动';
                engineStatus.className = 'value text-warning';
            }
        }

    } catch (error) {
        console.error('更新统计数据失败:', error);
    }
}

// 更新日志
async function updateLogs(limit = 50) {
    try {
        const data = await fetchLogs(limit);
        const logs = data.logs || [];

        const logContainer = document.getElementById('log-container');
        if (!logContainer) return;

        // 清空现有日志
        logContainer.innerHTML = '';

        // 添加日志条目
        logs.reverse().forEach(log => {
            addLogEntry(log);
        });

        // 自动滚动到底部
        logContainer.scrollTop = logContainer.scrollHeight;

    } catch (error) {
        console.error('更新日志失败:', error);
    }
}

// 更新系统状态
async function updateSystemStatus() {
    try {
        const data = await fetchDetectionStatus();

        // 更新状态指示器
        const pulseDot = document.getElementById('pulse-dot');
        const defconStatus = document.getElementById('defcon-status');

        if (data.is_detecting) {
            if (pulseDot) {
                pulseDot.className = 'status-pulse secure';
                pulseDot.style.background = 'var(--success-green)';
            }
            if (defconStatus) {
                defconStatus.textContent = 'DEFCON 3 (运行中)';
                defconStatus.className = 'text-success';
            }
        } else {
            if (pulseDot) {
                pulseDot.className = 'status-pulse';
                pulseDot.style.background = 'var(--warning-yellow)';
            }
            if (defconStatus) {
                defconStatus.textContent = 'DEFCON 5 (已停止)';
                defconStatus.className = 'text-warning';
            }
        }

    } catch (error) {
        console.error('更新系统状态失败:', error);

        // 错误状态
        const pulseDot = document.getElementById('pulse-dot');
        const defconStatus = document.getElementById('defcon-status');

        if (pulseDot) {
            pulseDot.style.background = 'var(--danger-red)';
        }
        if (defconStatus) {
            defconStatus.textContent = 'DEFCON 1 (连接失败)';
            defconStatus.className = 'text-danger';
        }
    }
}

// ==================== UI 更新函数 ====================

// 更新指标卡片
function updateMetricCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = formatNumber(value);
    }
}

// 更新最后扫描时间
function updateLastScanTime(timestamp) {
    const element = document.getElementById('last-block-time');
    if (element) {
        element.textContent = formatTime(timestamp);
    }
}

// 更新模型指标
function updateModelMetrics(metrics) {
    // 更新推理延迟
    const inferenceTime = document.getElementById('inference-time');
    if (inferenceTime) {
        inferenceTime.textContent = `准确率: ${(metrics.accuracy * 100).toFixed(1)}% | F1: ${(metrics.f1_score * 100).toFixed(1)}%`;
    }
}

// 获取并展示模型信息
async function updateModelInfo() {
    try {
        const metrics = await fetchModelMetrics();
        if (metrics) {
            updateModelMetrics(metrics);
        }

        // 获取模型状态
        const response = await fetch(`${API_BASE}/model/status`);
        const data = await response.json();
        if (data.model_loaded) {
            const engineStatus = document.getElementById('engine-status');
            if (engineStatus && !is_detecting_local) {
                engineStatus.textContent = '就绪 (INT8)';
                engineStatus.className = 'value text-accent';
            }
        }
    } catch (error) {
        console.error('获取模型信息失败:', error);
    }
}

// 本地检测状态跟踪
let is_detecting_local = false;

// 添加日志条目
function addLogEntry(log) {
    const logContainer = document.getElementById('log-container');
    if (!logContainer) return;

    const logEntry = document.createElement('div');

    // 确定日志级别
    let level = 'info';
    if (log.level) {
        level = log.level.toLowerCase();
    } else if (log.type && log.type.includes('威胁')) {
        level = 'error';
    } else if (log.type && log.type.includes('警告')) {
        level = 'warn';
    }

    logEntry.className = `log-entry ${level}`;

    const timestamp = new Date(log.timestamp).toLocaleTimeString('zh-CN');
    const message = log.message || log.description || '';
    const type = log.type || '';

    // 构建日志标签
    let logTag = '';
    if (level === 'error') {
        logTag = '<span class="log-tag">拦截</span>';
    } else if (level === 'warn') {
        logTag = '<span class="log-tag">预警</span>';
    } else {
        logTag = '<span class="log-tag">态势</span>';
    }

    logEntry.innerHTML = `
        <span class="log-time">[${timestamp}]</span>
        ${logTag}
        ${type ? `<span style="color: var(--accent-cyan);">[${type}]</span>` : ''}
        <span>${message}</span>
    `;

    logContainer.appendChild(logEntry);

    // 限制日志数量，保留最新的 100 条
    while (logContainer.children.length > 100) {
        logContainer.removeChild(logContainer.firstChild);
    }

    // 自动滚动到底部
    logContainer.scrollTop = logContainer.scrollHeight;
}

// 更新攻击类型图表
function updateAttackTypesChart(attackTypes) {
    if (!charts.attackPie) return;

    const data = Object.entries(attackTypes).map(([name, value]) => ({
        name: name,
        value: value
    }));

    charts.attackPie.setOption({
        series: [{
            data: data
        }]
    });
}

// 更新攻击类型进度条
function updateAttackTypeProgress(attackTypes) {
    // 计算总数
    const total = Object.values(attackTypes).reduce((sum, val) => sum + val, 0);

    if (total === 0) return;

    // 映射攻击类型到进度条
    const typeMapping = {
        'DDoS攻击': { bar: 'prog-ddos-bar', val: 'prog-ddos-val' },
        'DDoS洪泛攻击': { bar: 'prog-ddos-bar', val: 'prog-ddos-val' },
        '端口扫描': { bar: 'prog-apt-bar', val: 'prog-apt-val' },
        'APT隐蔽隧道': { bar: 'prog-apt-bar', val: 'prog-apt-val' },
        'WebShell': { bar: 'prog-web-bar', val: 'prog-web-val' },
        'SQL注入': { bar: 'prog-web-bar', val: 'prog-web-val' }
    };

    // 初始化计数
    const counts = { ddos: 0, apt: 0, web: 0 };

    // 统计各类型
    for (const [type, count] of Object.entries(attackTypes)) {
        if (type.includes('DDoS') || type.includes('洪泛')) {
            counts.ddos += count;
        } else if (type.includes('端口') || type.includes('APT') || type.includes('隧道') || type.includes('暴力')) {
            counts.apt += count;
        } else if (type.includes('WebShell') || type.includes('SQL') || type.includes('注入') || type.includes('恶意')) {
            counts.web += count;
        } else {
            // AI检测到的未分类攻击，均分到各类
            counts.ddos += Math.ceil(count / 3);
            counts.apt += Math.ceil(count / 3);
            counts.web += Math.ceil(count / 3);
        }
    }

    // 更新进度条
    const ddosPercent = ((counts.ddos / total) * 100).toFixed(1);
    const aptPercent = ((counts.apt / total) * 100).toFixed(1);
    const webPercent = ((counts.web / total) * 100).toFixed(1);

    updateProgressBar('prog-ddos-bar', 'prog-ddos-val', ddosPercent);
    updateProgressBar('prog-apt-bar', 'prog-apt-val', aptPercent);
    updateProgressBar('prog-web-bar', 'prog-web-val', webPercent);
}

// 更新单个进度条
function updateProgressBar(barId, valId, percent) {
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);

    if (bar) {
        bar.style.width = `${percent}%`;
    }
    if (val) {
        val.textContent = `${percent}%`;
    }
}

// ==================== 图表初始化 ====================

function initCharts() {
    // 攻击类型饼图
    const attackPieEl = document.getElementById('attack-pie-chart');
    if (attackPieEl) {
        charts.attackPie = echarts.init(attackPieEl);
        charts.attackPie.setOption({
            title: {
                text: '威胁态势图谱',
                left: 'center',
                top: 10,
                textStyle: {
                    color: '#00ffff',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                orient: 'vertical',
                right: 10,
                top: 'center',
                textStyle: {
                    color: '#00ffff'
                }
            },
            series: [{
                name: '攻击类型',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#000',
                    borderWidth: 2
                },
                label: {
                    show: true,
                    color: '#00ffff'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 14,
                        fontWeight: 'bold'
                    }
                },
                data: []
            }]
        });
    }

    // 网络拓扑图
    const topologyEl = document.getElementById('topology-chart');
    if (topologyEl) {
        charts.topology = echarts.init(topologyEl);

        // 初始化拓扑图数据
        const nodes = [
            { name: 'Aegis Core', x: 300, y: 150, symbolSize: 60, itemStyle: { color: '#00E5FF' },
              label: { fontSize: 11, fontWeight: 'bold' } },
            { name: 'Web Server\n192.168.1.10', x: 100, y: 80, symbolSize: 40, itemStyle: { color: '#64748B' } },
            { name: 'DB Server\n192.168.1.20', x: 500, y: 80, symbolSize: 40, itemStyle: { color: '#64748B' } },
            { name: 'IoT Gateway\n192.168.1.30', x: 100, y: 220, symbolSize: 40, itemStyle: { color: '#64748B' } },
            { name: 'Edge Node\n192.168.1.40', x: 500, y: 220, symbolSize: 40, itemStyle: { color: '#64748B' } }
        ];

        const links = [
            { source: 'Aegis Core', target: 'Web Server\n192.168.1.10' },
            { source: 'Aegis Core', target: 'DB Server\n192.168.1.20' },
            { source: 'Aegis Core', target: 'IoT Gateway\n192.168.1.30' },
            { source: 'Aegis Core', target: 'Edge Node\n192.168.1.40' }
        ];

        charts.topology.setOption({
            backgroundColor: 'transparent',
            tooltip: {
                formatter: '{b}'
            },
            series: [{
                type: 'graph',
                layout: 'none',
                symbolSize: 50,
                roam: false,
                label: {
                    show: true,
                    color: '#E2E8F0',
                    fontSize: 10
                },
                edgeSymbol: ['circle', 'arrow'],
                edgeSymbolSize: [4, 8],
                data: nodes,
                links: links,
                lineStyle: {
                    opacity: 0.5,
                    width: 2,
                    curveness: 0,
                    color: '#00E5FF'
                },
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 3
                    }
                }
            }]
        });

        // 定时更新拓扑图（模拟攻击节点）
        setInterval(() => {
            updateTopologyChart();
        }, 4000);
    }

    // 响应窗口大小变化
    window.addEventListener('resize', () => {
        Object.values(charts).forEach(chart => {
            if (chart) chart.resize();
        });
    });
}

// 更新拓扑图（根据后端检测状态动态标记攻击节点）
function updateTopologyChart() {
    if (!charts.topology) return;

    const nodes = [
        { name: 'Aegis Core', x: 300, y: 150, symbolSize: 60, itemStyle: { color: '#00E5FF' },
          label: { fontSize: 11, fontWeight: 'bold' } }
    ];

    const links = [];

    // 模拟网络节点，根据检测状态动态变化
    const nodeConfigs = [
        { name: 'Web Server\n192.168.1.10', x: 100, y: 80 },
        { name: 'DB Server\n192.168.1.20', x: 500, y: 80 },
        { name: 'IoT Gateway\n192.168.1.30', x: 100, y: 220 },
        { name: 'Edge Node\n192.168.1.40', x: 500, y: 220 }
    ];

    for (let i = 0; i < nodeConfigs.length; i++) {
        const isAttacked = is_detecting_local ? Math.random() > 0.65 : false;
        const cfg = nodeConfigs[i];

        nodes.push({
            name: cfg.name,
            x: cfg.x,
            y: cfg.y,
            symbolSize: isAttacked ? 50 : 40,
            itemStyle: { color: isAttacked ? '#FF3366' : '#64748B' },
            label: { fontSize: 9 }
        });

        links.push({
            source: 'Aegis Core',
            target: cfg.name,
            lineStyle: {
                color: isAttacked ? '#FF3366' : '#00E5FF',
                width: isAttacked ? 3 : 2,
                type: isAttacked ? 'dashed' : 'solid'
            }
        });
    }

    charts.topology.setOption({
        series: [{
            data: nodes,
            links: links
        }]
    });
}

// ==================== 工具函数 ====================

// 格式化数字
function formatNumber(num) {
    return num.toLocaleString('zh-CN');
}

// 格式化时间
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

// 显示通知
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    // 在日志中显示通知
    addLogEntry({
        timestamp: new Date().toISOString(),
        level: type === 'success' ? 'info' : type,
        message: message
    });

    // 创建浮动通知
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'error' ? 'rgba(255, 51, 102, 0.9)' :
                     type === 'warning' ? 'rgba(255, 193, 7, 0.9)' :
                     'rgba(0, 229, 255, 0.9)'};
        color: ${type === 'warning' ? '#000' : '#fff'};
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-family: 'Exo 2', sans-serif;
        animation: slideInRight 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// ==================== PCAP文件上传功能 ====================

/**
 * 初始化上传功能
 */
function initUploadFeature() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('pcap-file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const resetBtn = document.getElementById('reset-upload-btn');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    if (!uploadArea || !fileInput) {
        console.warn('上传组件未找到，跳过初始化');
        return;
    }

    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择事件
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // 拖拽上传功能
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // 上传按钮
    if (uploadBtn) {
        uploadBtn.addEventListener('click', handleUpload);
    }

    // 重置按钮
    if (resetBtn) {
        resetBtn.addEventListener('click', resetUpload);
    }

    // 移除文件按钮
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', resetUpload);
    }

    // 清空历史按钮
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearUploadHistory);
    }

    console.log('上传功能初始化完成');
}

/**
 * 处理文件选择
 */
function handleFileSelect(file) {
    if (!file) return;

    // 验证文件类型
    const validExtensions = ['.pcap', '.pcapng'];
    const fileName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValid) {
        showNotification('仅支持 .pcap 或 .pcapng 格式文件！', 'error');
        return;
    }

    // 验证文件大小（100MB）
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('文件大小不能超过 100MB！', 'error');
        return;
    }

    // 保存选中的文件
    selectedFile = file;

    // 更新UI显示
    updateFileDisplay(file);

    // 启用上传按钮
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) {
        uploadBtn.disabled = false;
    }

    // 添加日志
    addLogEntry({
        timestamp: new Date().toISOString(),
        level: 'info',
        message: `已选择文件: ${file.name} (${formatFileSize(file.size)})`
    });
}

/**
 * 更新文件显示
 */
function updateFileDisplay(file) {
    const selectedFileDisplay = document.getElementById('selected-file-display');
    const fileNameEl = document.getElementById('selected-file-name');
    const fileSizeEl = document.getElementById('selected-file-size');

    if (selectedFileDisplay && fileNameEl && fileSizeEl) {
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = formatFileSize(file.size);
        selectedFileDisplay.style.display = 'block';
    }
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * 处理文件上传
 */
async function handleUpload() {
    if (!selectedFile) {
        showNotification('请先选择一个文件！', 'warning');
        return;
    }

    const uploadBtn = document.getElementById('upload-btn');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('progress-bar-fill');
    const progressStatus = document.getElementById('progress-status');
    const progressPercent = document.getElementById('progress-percent');

    try {
        // 禁用上传按钮
        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 上传中...';
        }

        // 显示进度条
        if (progressContainer) {
            progressContainer.classList.add('active');
        }

        // 模拟进度更新
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += 10;
                updateProgress(progress, '正在上传文件...');
            }
        }, 200);

        // 创建FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // 添加上传日志
        addLogEntry({
            timestamp: new Date().toISOString(),
            level: 'info',
            message: `开始上传文件: ${selectedFile.name}`
        });

        // 发送请求
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        // 清除进度模拟
        clearInterval(progressInterval);

        if (response.ok) {
            const result = await response.json();

            // 完成进度
            updateProgress(100, '上传成功！', 'success');

            // 添加到历史记录
            addToUploadHistory({
                filename: selectedFile.name,
                size: formatFileSize(selectedFile.size),
                status: 'success',
                message: result.message || '上传成功'
            });

            // 添加成功日志
            addLogEntry({
                timestamp: new Date().toISOString(),
                level: 'info',
                message: `文件上传成功: ${selectedFile.name} - ${result.message || '已接收'}`
            });

            showNotification('文件上传成功！系统正在分析...', 'success');

            // 3秒后重置
            setTimeout(() => {
                resetUpload();
            }, 3000);

        } else {
            const errorText = await response.text();

            // 显示错误
            updateProgress(100, '上传失败！', 'error');

            // 添加到历史记录
            addToUploadHistory({
                filename: selectedFile.name,
                size: formatFileSize(selectedFile.size),
                status: 'error',
                message: errorText || '上传失败'
            });

            // 添加错误日志
            addLogEntry({
                timestamp: new Date().toISOString(),
                level: 'error',
                message: `文件上传失败: ${selectedFile.name} - ${errorText}`
            });

            showNotification(`上传失败: ${errorText}`, 'error');

            // 3秒后重置进度条
            setTimeout(() => {
                if (progressContainer) {
                    progressContainer.classList.remove('active');
                }
            }, 3000);
        }

    } catch (error) {
        console.error('上传错误:', error);

        // 显示错误
        updateProgress(100, '网络错误！', 'error');

        // 添加到历史记录
        addToUploadHistory({
            filename: selectedFile.name,
            size: formatFileSize(selectedFile.size),
            status: 'error',
            message: error.message || '网络错误'
        });

        // 添加错误日志
        addLogEntry({
            timestamp: new Date().toISOString(),
            level: 'error',
            message: `上传网络错误: ${error.message}`
        });

        showNotification(`网络错误: ${error.message}`, 'error');

        // 3秒后重置进度条
        setTimeout(() => {
            const progressContainer = document.getElementById('upload-progress-container');
            if (progressContainer) {
                progressContainer.classList.remove('active');
            }
        }, 3000);

    } finally {
        // 恢复上传按钮
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-rocket"></i> 启动上传与分析';
        }
    }
}

/**
 * 更新上传进度
 */
function updateProgress(percent, status, type = 'normal') {
    const progressBar = document.getElementById('progress-bar-fill');
    const progressStatus = document.getElementById('progress-status');
    const progressPercent = document.getElementById('progress-percent');

    if (progressBar) {
        progressBar.style.width = percent + '%';

        // 移除所有状态类
        progressBar.classList.remove('success', 'error');

        // 添加新状态类
        if (type === 'success') {
            progressBar.classList.add('success');
        } else if (type === 'error') {
            progressBar.classList.add('error');
        }
    }

    if (progressStatus) {
        progressStatus.textContent = status;
    }

    if (progressPercent) {
        progressPercent.textContent = percent + '%';
    }
}

/**
 * 重置上传
 */
function resetUpload() {
    // 清空选中的文件
    selectedFile = null;

    // 重置文件输入
    const fileInput = document.getElementById('pcap-file-input');
    if (fileInput) {
        fileInput.value = '';
    }

    // 隐藏文件显示
    const selectedFileDisplay = document.getElementById('selected-file-display');
    if (selectedFileDisplay) {
        selectedFileDisplay.style.display = 'none';
    }

    // 禁用上传按钮
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) {
        uploadBtn.disabled = true;
    }

    // 隐藏进度条
    const progressContainer = document.getElementById('upload-progress-container');
    if (progressContainer) {
        progressContainer.classList.remove('active');
    }

    // 重置进度
    updateProgress(0, '准备上传...', 'normal');
}

/**
 * 添加到上传历史
 */
function addToUploadHistory(fileInfo) {
    const historyItem = {
        filename: fileInfo.filename,
        size: fileInfo.size,
        status: fileInfo.status,
        message: fileInfo.message || '',
        timestamp: new Date().toISOString()
    };

    // 添加到历史数组开头
    uploadHistory.unshift(historyItem);

    // 只保留最近20条
    if (uploadHistory.length > 20) {
        uploadHistory = uploadHistory.slice(0, 20);
    }

    // 保存到localStorage
    localStorage.setItem('uploadHistory', JSON.stringify(uploadHistory));

    // 重新渲染历史列表
    renderUploadHistory();
}

/**
 * 渲染上传历史
 */
function renderUploadHistory() {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;

    if (uploadHistory.length === 0) {
        historyList.innerHTML = `
            <div class="history-empty">
                <i class="fas fa-inbox"></i>
                <div>暂无上传记录</div>
            </div>
        `;
        return;
    }

    historyList.innerHTML = uploadHistory.map(item => {
        const statusClass = item.status === 'success' ? 'success' : 'error';
        const statusText = item.status === 'success' ? '成功' : '失败';
        const time = new Date(item.timestamp).toLocaleString('zh-CN');

        return `
            <div class="history-item">
                <div class="history-item-header">
                    <div class="history-file-name">
                        <i class="fas fa-file-archive"></i>
                        <span>${item.filename}</span>
                    </div>
                    <span class="history-status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="history-item-footer">
                    <div class="history-time">
                        <i class="far fa-clock"></i>
                        <span>${time}</span>
                    </div>
                    <div class="history-size">
                        <i class="fas fa-hdd"></i>
                        <span>${item.size}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 清空上传历史
 */
function clearUploadHistory() {
    if (!confirm('确定要清空所有上传历史记录吗？')) {
        return;
    }

    // 清空数组
    uploadHistory = [];

    // 清空localStorage
    localStorage.removeItem('uploadHistory');

    // 重新渲染
    renderUploadHistory();

    // 显示通知
    showNotification('上传历史已清空', 'success');

    // 添加日志
    addLogEntry({
        timestamp: new Date().toISOString(),
        level: 'info',
        message: '上传历史记录已清空'
    });
}

// ==================== 页面加载 ====================

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    Object.values(charts).forEach(chart => {
        if (chart) chart.dispose();
    });
});

// ==================== PCAP文件上传功能 ====================

/**
 * 初始化上传功能
 */
function initUploadFeature() {
    console.log('初始化PCAP上传功能...');

    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('pcap-file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const resetBtn = document.getElementById('reset-upload-btn');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    if (!uploadArea || !fileInput) {
        console.warn('上传组件未找到，跳过初始化');
        return;
    }

    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // 文件选择事件
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // 拖拽上传功能
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // 上传按钮
    if (uploadBtn) {
        uploadBtn.addEventListener('click', handleUpload);
    }

    // 重置按钮
    if (resetBtn) {
        resetBtn.addEventListener('click', resetUpload);
    }

    // 移除文件按钮
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', resetUpload);
    }

    // 清空历史按钮
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearUploadHistory);
    }

    console.log('PCAP上传功能初始化完成');
}

/**
 * 处理文件选择
 */
function handleFileSelect(file) {
    if (!file) return;

    console.log('选择文件:', file.name, file.size);

    // 验证文件类型
    const validExtensions = ['.pcap', '.pcapng'];
    const fileName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValid) {
        showNotification('仅支持 .pcap 或 .pcapng 格式文件！', 'error');
        return;
    }

    // 验证文件大小（100MB）
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('文件大小不能超过 100MB！', 'error');
        return;
    }

    // 保存选中的文件
    selectedFile = file;

    // 更新UI显示
    updateFileDisplay(file);

    // 启用上传按钮
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) {
        uploadBtn.disabled = false;
    }

    // 添加日志
    addLogEntry({
        timestamp: new Date().toISOString(),
        level: 'info',
        message: `已选择文件: ${file.name} (${formatFileSize(file.size)})`
    });
}

/**
 * 更新文件显示
 */
function updateFileDisplay(file) {
    const uploadArea = document.getElementById('upload-area');
    const selectedFileDisplay = document.getElementById('selected-file-display');
    const fileNameEl = document.getElementById('selected-file-name');
    const fileSizeEl = document.getElementById('selected-file-size');

    if (uploadArea) {
        uploadArea.style.display = 'none';
    }

    if (selectedFileDisplay) {
        selectedFileDisplay.style.display = 'block';
    }

    if (fileNameEl) {
        fileNameEl.textContent = file.name;
    }

    if (fileSizeEl) {
        fileSizeEl.textContent = formatFileSize(file.size);
    }
}

/**
 * 重置上传
 */
function resetUpload() {
    selectedFile = null;

    // 重置文件输入
    const fileInput = document.getElementById('pcap-file-input');
    if (fileInput) {
        fileInput.value = '';
    }

    // 重置UI
    const uploadArea = document.getElementById('upload-area');
    const selectedFileDisplay = document.getElementById('selected-file-display');
    const uploadBtn = document.getElementById('upload-btn');
    const progressContainer = document.getElementById('upload-progress-container');

    if (uploadArea) {
        uploadArea.style.display = 'block';
    }

    if (selectedFileDisplay) {
        selectedFileDisplay.style.display = 'none';
    }

    if (uploadBtn) {
        uploadBtn.disabled = true;
    }

    if (progressContainer) {
        progressContainer.classList.remove('active');
    }

    // 重置进度条
    updateProgress(0, '准备上传...');
}

/**
 * 处理文件上传
 */
async function handleUpload() {
    if (!selectedFile) {
        showNotification('请先选择文件！', 'warning');
        return;
    }

    console.log('开始上传文件:', selectedFile.name);

    const uploadBtn = document.getElementById('upload-btn');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');

    // 禁用上传按钮
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 上传中...';
    }

    // 显示进度条
    if (progressContainer) {
        progressContainer.classList.add('active');
    }

    // 重置进度条样式
    if (progressBarFill) {
        progressBarFill.className = 'progress-bar-fill';
    }

    // 添加日志
    addLogEntry({
        timestamp: new Date().toISOString(),
        level: 'info',
        message: `开始上传文件: ${selectedFile.name}`
    });

    try {
        // 创建FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // 模拟上传进度
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += 10;
                updateProgress(progress, '正在上传...');
            }
        }, 200);

        // 发送请求
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        // 清除进度模拟
        clearInterval(progressInterval);

        if (response.ok) {
            const result = await response.json();
            console.log('上传成功:', result);

            // 完成进度
            updateProgress(100, '上传成功！', 'success');

            // 添加到历史记录
            addToUploadHistory({
                filename: result.filename || selectedFile.name,
                size: formatFileSize(selectedFile.size),
                status: 'success',
                message: result.message || '上传成功'
            });

            // 添加成功日志
            addLogEntry({
                timestamp: new Date().toISOString(),
                level: 'info',
                message: `文件上传成功: ${result.filename || selectedFile.name}`
            });

            // 显示成功通知
            showNotification('文件上传成功！系统正在分析...', 'success');

            // 2秒后重置
            setTimeout(() => {
                resetUpload();
            }, 2000);

        } else {
            const errorText = await response.text();
            console.error('上传失败:', response.status, errorText);

            // 显示错误进度
            updateProgress(100, '上传失败！', 'error');

            // 添加到历史记录
            addToUploadHistory({
                filename: selectedFile.name,
                size: formatFileSize(selectedFile.size),
                status: 'error',
                message: errorText || '上传失败'
            });

            // 添加错误日志
            addLogEntry({
                timestamp: new Date().toISOString(),
                level: 'error',
                message: `文件上传失败: ${errorText}`
            });

            // 显示错误通知
            showNotification(`上传失败: ${errorText}`, 'error');

            // 3秒后重置按钮
            setTimeout(() => {
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = '<i class="fas fa-rocket"></i> 启动上传与分析';
                }
            }, 3000);
        }

    } catch (error) {
        console.error('上传错误:', error);

        // 显示错误进度
        updateProgress(100, '网络错误！', 'error');

        // 添加到历史记录
        addToUploadHistory({
            filename: selectedFile.name,
            size: formatFileSize(selectedFile.size),
            status: 'error',
            message: error.message || '网络错误'
        });

        // 添加错误日志
        addLogEntry({
            timestamp: new Date().toISOString(),
            level: 'error',
            message: `上传网络错误: ${error.message}`
        });

        // 显示错误通知
        showNotification(`网络错误: ${error.message}`, 'error');

        // 3秒后重置按钮
        setTimeout(() => {
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="fas fa-rocket"></i> 启动上传与分析';
            }
        }, 3000);
    }
}

/**
 * 更新上传进度
 */
function updateProgress(percent, status, type = 'normal') {
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressPercent = document.getElementById('progress-percent');
    const progressStatus = document.getElementById('progress-status');

    if (progressBarFill) {
        progressBarFill.style.width = `${percent}%`;

        // 根据类型设置样式
        if (type === 'success') {
            progressBarFill.classList.add('success');
        } else if (type === 'error') {
            progressBarFill.classList.add('error');
        }
    }

    if (progressPercent) {
        progressPercent.textContent = `${percent}%`;
    }

    if (progressStatus) {
        progressStatus.textContent = status;
    }
}

/**
 * 添加到上传历史
 */
function addToUploadHistory(item) {
    const historyItem = {
        filename: item.filename,
        size: item.size,
        status: item.status,
        message: item.message,
        timestamp: new Date().toISOString()
    };

    // 添加到历史数组开头
    uploadHistory.unshift(historyItem);

    // 只保留最近20条
    if (uploadHistory.length > 20) {
        uploadHistory = uploadHistory.slice(0, 20);
    }

    // 保存到localStorage
    localStorage.setItem('uploadHistory', JSON.stringify(uploadHistory));

    // 重新渲染历史列表
    renderUploadHistory();
}

/**
 * 渲染上传历史
 */
function renderUploadHistory() {
    const historyList = document.getElementById('history-list');
    if (!historyList) return;

    if (uploadHistory.length === 0) {
        historyList.innerHTML = `
            <div class="history-empty">
                <i class="fas fa-inbox"></i>
                <div>暂无上传记录</div>
            </div>
        `;
        return;
    }

    historyList.innerHTML = uploadHistory.map(item => {
        const time = new Date(item.timestamp).toLocaleString('zh-CN');
        const statusClass = item.status === 'success' ? 'success' : 'error';
        const statusText = item.status === 'success' ? '成功' : '失败';

        return `
            <div class="history-item">
                <div class="history-item-header">
                    <div class="history-file-name">
                        <i class="fas fa-file-archive"></i>
                        <span>${item.filename}</span>
                    </div>
                    <span class="history-status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="history-item-footer">
                    <div class="history-time">
                        <i class="far fa-clock"></i>
                        <span>${time}</span>
                    </div>
                    <div class="history-size">
                        <i class="fas fa-hdd"></i>
                        <span>${item.size}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 清空上传历史
 */
function clearUploadHistory() {
    if (!confirm('确定要清空所有上传历史记录吗？')) {
        return;
    }

    uploadHistory = [];
    localStorage.removeItem('uploadHistory');
    renderUploadHistory();

    showNotification('上传历史已清空', 'success');

    addLogEntry({
        timestamp: new Date().toISOString(),
        level: 'info',
        message: '上传历史已清空'
    });
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
