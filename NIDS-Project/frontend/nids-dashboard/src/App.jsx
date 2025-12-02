import React, { useState } from "react";

export default function App() {
  const [isDetecting, setIsDetecting] = useState(false);
  const [logs, setLogs] = useState([]);

  const toggleDetection = () => {
    if (!isDetecting) {
      setIsDetecting(true);
      addLog("实时检测已启动...");
    } else {
      setIsDetecting(false);
      addLog("实时检测已停止。");
    }
  };

  const uploadFile = (event) => {
    const file = event.target.files[0];
    if (file) {
      addLog(`上传文件：${file.name}`);
    }
  };

  const addLog = (msg) => {
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full bg-white shadow-xl rounded-2xl p-6">
        <h1 className="text-2xl font-bold text-slate-800 mb-4 text-center">
          🛡️ 轻量级网络入侵检测系统
        </h1>

        <p className="text-sm text-slate-600 mb-4 text-center">
          本界面用于启动实时检测与上传离线流量包进行分析。
        </p>

        <div className="flex justify-center mb-4">
          <button
            onClick={toggleDetection}
            className={`px-6 py-2 rounded-xl text-white font-semibold transition ${
              isDetecting ? "bg-red-500 hover:bg-red-600" : "bg-green-500 hover:bg-green-600"
            }`}
          >
            {isDetecting ? "停止检测" : "启动检测"}
          </button>
        </div>

        <div className="mb-6 text-center">
          <label
            htmlFor="upload"
            className="cursor-pointer text-blue-600 hover:underline"
          >
            上传流量文件（.pcap）
          </label>
          <input
            id="upload"
            type="file"
            accept=".pcap"
            className="hidden"
            onChange={uploadFile}
          />
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 h-48 overflow-y-auto">
          <h2 className="font-semibold text-slate-700 mb-2">📜 日志输出：</h2>
          {logs.length === 0 ? (
            <p className="text-slate-400 text-sm">暂无日志...</p>
          ) : (
            logs.map((log, index) => (
              <p key={index} className="text-xs text-slate-600">
                {log}
              </p>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
