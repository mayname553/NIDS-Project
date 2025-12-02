import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table } from "@/components/ui/table";
import { Search } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Lightweight Network Intrusion Detection System - Single-file React dashboard
// Tailwind CSS assumed. Uses shadcn/ui, lucide-react, recharts (all available per canvas instructions).

const sampleTraffic = [
  { time: '10:00', flows: 120 },
  { time: '10:05', flows: 220 },
  { time: '10:10', flows: 180 },
  { time: '10:15', flows: 260 },
  { time: '10:20', flows: 210 },
  { time: '10:25', flows: 300 },
];

const sampleAlerts = [
  { id: 'A-1001', time: '2025-10-11 09:13', src: '192.168.1.11', dst: '10.0.0.2', type: 'Port Scan', score: 0.78 },
  { id: 'A-1002', time: '2025-10-11 09:26', src: '203.0.113.5', dst: '10.0.0.15', type: 'Brute Force', score: 0.92 },
  { id: 'A-1003', time: '2025-10-11 09:40', src: '192.168.1.20', dst: '10.0.0.3', type: 'Suspicious Payload', score: 0.64 },
];

export default function NIDSDashboard() {
  const [running, setRunning] = useState(false);
  const [alerts, setAlerts] = useState(sampleAlerts);
  const [query, setQuery] = useState('');
  const [pcapName, setPcapName] = useState(null);

  function toggleDetection() {
    setRunning(r => !r);
    // placeholder: in real app call backend start/stop endpoints
  }

  function handleUpload(e) {
    const f = e.target.files?.[0];
    if (f) setPcapName(f.name);
    // placeholder: upload file to backend for offline analysis
  }

  function clearAlerts() {
    setAlerts([]);
  }

  const filteredAlerts = alerts.filter(a => {
    if (!query) return true;
    return [a.id, a.src, a.dst, a.type].some(v => v.toLowerCase().includes(query.toLowerCase()));
  });

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold text-slate-800">轻量级网络入侵检测系统 (NIDS)</h1>
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 bg-white rounded-md px-3 py-1 shadow-sm">
            <Search className="w-4 h-4 text-slate-400" />
            <input
              className="outline-none text-sm"
              placeholder="搜索告警 / IP / 类型"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={toggleDetection} className="px-3 py-1">
              {running ? '停止检测' : '开始检测'}
            </Button>
            <Button onClick={clearAlerts} className="px-3 py-1" variant="ghost">
              清空告警
            </Button>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left column: controls and quick actions */}
        <section className="lg:col-span-1 space-y-4">
          <Card>
            <CardContent>
              <h2 className="font-medium text-lg mb-2">检测控制</h2>
              <p className="text-sm text-slate-600 mb-3">本控件用于快速启动/停止实时检测与上传抓包进行离线分析。</p>
              <div className="flex flex-col gap-2">
                <label className="block text-sm">上传PCAP（用于离线回放）</label>
                <input type="file" accept=".pcap,.pcapng" onChange={handleUpload} />
                {pcapName && <div className="text-sm text-slate-700">已选择: {pcapName}</div>}

                <label className="block text-sm mt-3">模型阈值 (简单演示)</label>
                <input type="range" min="0" max="1" step="0.01" defaultValue="0.7" />
                <div className="text-xs text-slate-500">阈值越低，越敏感（误报增多）</div>

                <div className="flex gap-2 mt-3">
                  <Button onClick={() => alert('触发手动扫描（前端模拟）')}>手动扫描</Button>
                  <Button variant="ghost" onClick={() => alert('导出当前告警为CSV')}>
                    导出CSV
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <h3 className="font-medium">系统概要</h3>
              <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <div className="bg-white p-3 rounded-md shadow-sm">
                  <div className="text-xs text-slate-500">检测状态</div>
                  <div className="font-semibold mt-1">{running ? '运行中' : '已停止'}</div>
                </div>
                <div className="bg-white p-3 rounded-md shadow-sm">
                  <div className="text-xs text-slate-500">活跃连接</div>
                  <div className="font-semibold mt-1">48</div>
                </div>
                <div className="bg-white p-3 rounded-md shadow-sm">
                  <div className="text-xs text-slate-500">今日告警</div>
                  <div className="font-semibold mt-1">{alerts.length}</div>
                </div>
                <div className="bg-white p-3 rounded-md shadow-sm">
                  <div className="text-xs text-slate-500">平均响应(ms)</div>
                  <div className="font-semibold mt-1">120</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Right column: main dashboard area */}
        <section className="lg:col-span-3 space-y-4">
          <Card>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-medium text-lg">流量趋势</h2>
                <div className="text-sm text-slate-500">示例：近 30 分钟</div>
              </div>

              <div className="w-full h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sampleTraffic}>
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="flows" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-medium text-lg">告警列表</h2>
                <div className="text-sm text-slate-500">按置信度排序（示例）</div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full bg-white divide-y divide-slate-200">
                  <thead className="bg-slate-50 text-xs text-slate-600">
                    <tr>
                      <th className="px-4 py-2 text-left">告警 ID</th>
                      <th className="px-4 py-2 text-left">时间</th>
                      <th className="px-4 py-2 text-left">源 IP</th>
                      <th className="px-4 py-2 text-left">目标 IP</th>
                      <th className="px-4 py-2 text-left">类型</th>
                      <th className="px-4 py-2 text-left">置信度</th>
                      <th className="px-4 py-2 text-left">操作</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {filteredAlerts.map(a => (
                      <tr key={a.id} className="border-b">
                        <td className="px-4 py-2">{a.id}</td>
                        <td className="px-4 py-2">{a.time}</td>
                        <td className="px-4 py-2">{a.src}</td>
                        <td className="px-4 py-2">{a.dst}</td>
                        <td className="px-4 py-2">{a.type}</td>
                        <td className="px-4 py-2">{Math.round(a.score * 100)}%</td>
                        <td className="px-4 py-2">
                          <div className="flex gap-2">
                            <Button size="sm" variant="ghost" onClick={() => alert('查看详情: ' + a.id)}>详情</Button>
                            <Button size="sm" variant="destructive" onClick={() => setAlerts(prev => prev.filter(x => x.id !== a.id))}>忽略</Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredAlerts.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-4 py-6 text-center text-slate-500">无告警</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <h3 className="font-medium mb-2">事件日志（实时）</h3>
              <div className="bg-black text-green-200 p-3 rounded-md h-40 overflow-auto text-xs font-mono">
                <div>[09:13:22] 已加载特征提取模块</div>
                <div>[09:13:23] 模型 1 预测：0.12（正常）</div>
                <div>[09:26:11] 检测到告警 A-1002：Brute Force，置信度 0.92</div>
                <div>[09:40:02] 检测到告警 A-1003：Suspicious Payload，置信度 0.64</div>
                <div>[实时输出] ...</div>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>

      <footer className="mt-6 text-sm text-slate-500">小提示：此界面为前端演示，后台 API（开始/停止/上传/导出）需连接你的后端实现。</footer>
    </div>
  );
}
