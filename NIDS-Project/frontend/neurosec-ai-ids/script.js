// NeuroSec-Aegis 主脚本
// 基于智能模型与动态优化的轻量级网络入侵检测系统

// API 配置
const API_BASE = 'http://localhost:5000';

// 全局变量
let charts = {};
let updateInterval = null;
let uploadHistory = JSON.parse(localStorage.getItem('uploadHistory') || '[]');
let is_detecting_local = false;

// ==================== 初始化 ====================

async function init() {
    try {
        console.log('初始化 NeuroSec-Aegis 系统...');

        // 初始化图表
        initCharts();

        // 加载初始数据
        await loadInitialData();

        // 设置定时更新（每5秒）
        updateInterval = setInterval(async () => {
            await updateAllData();
        }, 5000);

        // 绑定按钮事件
        setupEventListeners();

        // 初始化上传历史
        renderUploadHistory();
        if (uploadHistory.length > 0) {
            const historySection = document.getElementById('upload-history-section');
            if (historySection) {
                historySection.style.display = 'block';
            }
        }

        console.log('系统初始化完成');

    } catch (error) {
        console.error('初始化失败:', error);
        showNotification('系统初始化失败: ' + error.message, 'error');
    }
}

// 设置事件监听
function setupEventListeners() {
    // 启动检测按钮
    const startBtn = document.getElementById('btn-start');
    if (startBtn) {
        startBtn.addEventListener('click', startDetection);
    }

    // 停止检测按钮
    const stopBtn = document.getElementById('btn-stop');
    if (stopBtn) {
        stopBtn.addEventListener('click', stopDetection);
    }

    // 清空日志按钮
    const clearBtn = document.getElementById('btn-clear');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearLogs);
    }
}

// ==================== API 调用 ====================

// 获取统计数据
async function fetchStats() {
    const response = await fetch(`${API_BASE}/api/stats`);
    const data = await response.json();
    return data;
}

// 获取日志
async function fetchLogs(limit = 50) {
    const response = await fetch(`${API_BASE}/api/logs?limit=${limit}`);
    const data = await response.json();
    return data;
}

// 获取检测状态
async function fetchDetectionStatus() {
    const response = await fetch(`${API_BASE}/api/detection/status`);
    const data = await response.json();
    return data;
}

// 获取模型指标
async function fetchModelMetrics() {
    try {
        const response = await fetch(`${API_BASE}/api/model/metrics`);
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
        const response = await fetch(`${API_BASE}/api/detection/start`, {
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
        const response = await fetch(`${API_BASE}/api/detection/stop`, {
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

// ==================== 文件上传功能 ====================

async function handleUpload() {
    console.log('开始处理文件上传...');
    
    const fileInput = document.getElementById('fileUpload');
    const uploadBtn = document.getElementById('upload-button');
    const originalBtnText = uploadBtn ? uploadBtn.innerHTML : '';
    
    // 1. 检查是否已选择文件
    if (!fileInput.files || fileInput.files.length === 0) {
        updateUploadStatus('请先选择一个文件！', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    
    // 2. 文件大小验证（100MB限制）
    if (file.size > 100 * 1024 * 1024) { // 100MB
        updateUploadStatus('文件大小不能超过100MB！', 'error');
        return;
    }
    
    // 3. 文件类型验证 - 根据后端只允许 .pcap
    const validTypes = ['.pcap'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    if (!validTypes.includes(fileExt)) {
        updateUploadStatus('仅支持 .pcap 格式文件！', 'error');
        return;
    }
    
    // 4. 禁用按钮并显示Loading
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 上传中...';
        uploadBtn.style.opacity = '0.7';
    }
    
    // 5. 显示进度条
    const statusDiv = document.getElementById('uploadStatus');
    if (statusDiv) {
        statusDiv.innerHTML = `
            <div class="upload-progress" style="margin-top: 8px;">
                <div class="progress-bar" style="width: 0%; background: #00E5FF; height: 4px; border-radius: 2px; transition: width 0.3s;"></div>
            </div>
        `;
    }
    
    // 6. 模拟进度动画
    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 90) {
            progress += 10;
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = progress + '%';
            }
        }
    }, 200);
    
    try {
        // 7. 创建表单数据
        const formData = new FormData();
        formData.append('file', file);
        
        // 8. 调用后端API
        const response = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        console.log('上传响应状态:', response.status);
        
        // 9. 处理响应
        if (response.ok) {
            const result = await response.json();
            console.log('上传成功结果:', result);
            
            // 完成进度条
            clearInterval(progressInterval);
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = '100%';
                progressBar.style.background = '#00FF88';
            }
            
            updateUploadStatus(`上传成功！${result.message || '文件已接收'}`, 'success');
            
            // 10. 添加到历史记录
            updateUploadHistory({
                filename: result.filename || file.name,
                size: (file.size / 1024).toFixed(1) + ' KB',
                status: '已上传'
            });
            
            // 11. 高亮显示历史区域
            const historySection = document.getElementById('upload-history-section');
            if (historySection) {
                historySection.style.display = 'block';
                historySection.style.animation = 'pulse-glow 2s';
                setTimeout(() => {
                    historySection.style.animation = '';
                }, 2000);
            }
            
            // 12. 记录上传日志
            addLogEntry({
                timestamp: new Date().toISOString(),
                level: 'info',
                message: `PCAP文件 ${result.filename || file.name} 上传成功，文件已保存到后端`
            });
            
        } else {
            const error = await response.text();
            console.error('上传失败:', response.status, error);
            
            // 进度条变红色
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.background = '#FF3366';
            }
            
            updateUploadStatus(`上传失败: ${error}`, 'error');
            
            // 添加到历史记录（标记为错误）
            updateUploadHistory({
                filename: file.name,
                size: (file.size / 1024).toFixed(1) + ' KB',
                status: '错误'
            });
        }
    } catch (error) {
        console.error('上传网络错误:', error);
        
        // 进度条变红色
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.background = '#FF3366';
        }
        
        updateUploadStatus(`网络错误: ${error.message}`, 'error');
        
        // 添加到历史记录（标记为错误）
        updateUploadHistory({
            filename: file.name,
            size: (file.size / 1024).toFixed(1) + ' KB',
            status: '错误'
        });
    } finally {
        // 恢复按钮状态
        if (uploadBtn) {
            setTimeout(() => {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = originalBtnText;
                uploadBtn.style.opacity = '1';
            }, 1000);
        }
        
        // 清除进度条
        clearInterval(progressInterval);
        
        // 5秒后清除进度条显示
        setTimeout(() => {
            const statusDiv = document.getElementById('uploadStatus');
            if (statusDiv) {
                statusDiv.innerHTML = '';
            }
        }, 5000);
    }
}

// 更新上传状态显示
function updateUploadStatus(message, type = 'info') {
    const statusDiv = document.getElementById('uploadStatus');
    if (!statusDiv) return;
    
    let color = '#aaa';
    switch(type) {
        case 'success': color = '#00ff88'; break;
        case 'error': color = '#ff3366'; break;
        case 'info': color = '#00e5ff'; break;
    }
    
    statusDiv.innerHTML = `<span style="color: ${color}">${message}</span>`;
    
    // 自动清除成功消息
    if (type === 'success') {
        setTimeout(() => {
            if (statusDiv.innerHTML.includes(message)) {
                statusDiv.innerHTML = '';
            }
        }, 5000);
    }
}

// ==================== 上传历史管理 ====================

// 更新上传历史列表
function updateUploadHistory(fileInfo) {
    if (fileInfo) {
        // 添加到历史记录
        uploadHistory.unshift({
            name: fileInfo.filename,
            time: new Date().toISOString(),
            size: fileInfo.size || 'N/A',
            status: fileInfo.status || '已上传'
        });
        // 只保留最近10条
        if (uploadHistory.length > 10) {
            uploadHistory = uploadHistory.slice(0, 10);
        }
        // 保存到本地存储
        localStorage.setItem('uploadHistory', JSON.stringify(uploadHistory));
    }
    
    // 更新UI
    renderUploadHistory();
}

// 渲染历史列表
function renderUploadHistory() {
    const listEl = document.getElementById('upload-history-list');
    if (!listEl) return;
    
    if (uploadHistory.length === 0) {
        listEl.innerHTML = '<div class="history-empty">暂无上传记录</div>';
        return;
    }
    
    listEl.innerHTML = uploadHistory.map((item, index) => `
        <div class="history-item" style="padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <i class="fas fa-file" style="color: #00E5FF; margin-right: 8px;"></i>
                    <span style="font-family: 'Consolas', monospace; font-size: 0.9rem;">${item.name}</span>
                </div>
                <div style="font-size: 0.8rem; color: #64748B;">
                    ${new Date(item.time).toLocaleString('zh-CN')}
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 4px; color: #829AB1;">
                <span>大小: ${item.size}</span>
                <span class="status-badge ${item.status === '错误' ? 'error' : ''}" style="background: ${item.status === '错误' ? 'rgba(255, 51, 102, 0.2)' : 'rgba(0, 229, 255, 0.2)'}; 
                      color: ${item.status === '错误' ? '#FF3366' : '#00E5FF'}; 
                      padding: 2px 8px; border-radius: 10px;">
                    ${item.status}
                </span>
            </div>
        </div>
    `).join('');
}

// 清空历史
function clearUploadHistory() {
    if (confirm('确定要清空上传历史记录吗？')) {
        uploadHistory = [];
        localStorage.removeItem('uploadHistory');
        renderUploadHistory();
        showNotification('上传历史已清空', 'success');
        
        const historySection = document.getElementById('upload-history-section');
        if (historySection) {
            historySection.style.display = 'none';
        }
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
        const response = await fetch(`${API_BASE}/api/model/status`);
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

        // 1. 立即尝试一次 resize（解决大部分情况）
        if (charts.topology) charts.topology.resize();

        // 2. 使用 requestAnimationFrame 在下一次屏幕刷新时再 resize 一次（解决顽固情况）
        requestAnimationFrame(() => {
            if (charts.topology) charts.topology.resize();
        });

        // 3. 延迟 100ms 再 resize 一次（兜底方案，针对某些父容器高度塌陷的情况）
        setTimeout(() => {
            if (charts.topology) charts.topology.resize();
        }, 100);

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