import * as net from "net";
// import * as ping from "ping"; // ping.promise.probe
import { exec } from "child_process";

// 创建一个 TCP 客户端
const client = new net.Socket();

// ICMP 探测配置
const PING_INTERVAL = 2000; // 每 2 秒探测一次
let isNetworkAlive = true; // 网络是否可达

let HOST = "127.0.0.1"; // localhost
let port = 8080;
// let HOST = "192.168.3.23"; // yongle-dev
// let port = 53129;
client.connect(
  { host: HOST, port, keepAlive: true, keepAliveInitialDelay: 1000 },
  () => {
    console.log("已连接到服务器");
  }
);

// 数据接收事件
client.on("data", (data) => {
  console.log("收到数据:", data.toString());
});

// 连接关闭事件
client.on("close", (hadError) => {
  console.log("连接已关闭", hadError ? "（由于错误）" : "");
});

// 错误事件（例如连接断开或服务器不可用）
client.on("error", (err) => {
  console.error("连接错误:", err.message);
});

// ICMP 网络层检测
function startNetworkCheck() {
  setInterval(() => {
    // Windows 用 "ping -n 1"，Linux/Mac 用 "ping -c 1"
    const cmd =
      process.platform === "win32" ? `ping -n 1 ${HOST}` : `ping -c 1 ${HOST}`;
    exec(cmd, (err, stdout, stderr) => {
      const newAlive =
        (!err && stdout.includes("1 received")) ||
        stdout.includes("bytes from");
      if (newAlive !== isNetworkAlive) {
        isNetworkAlive = newAlive;
        console.log(`网络状态更新: ${newAlive ? "可达" : "不可达"}`);
        checkConnectionStatus();
      }
    });
  }, PING_INTERVAL);
}

// 综合判断连接状态
function checkConnectionStatus() {
  if (client.destroyed && !isNetworkAlive) {
    console.log("结论: 服务器完全不可用（TCP 已断开且网络不可达）");
  } else if (client.destroyed) {
    console.log("结论: TCP 连接断开，但网络仍然可达，可能是服务器关闭");
  } else if (!isNetworkAlive) {
    console.log("结论: 网络不可达，但 TCP 连接尚未关闭，可能是临时中断");
  } else {
    console.log("结论: 连接正常");
  }
}

// 启动网络层检测
startNetworkCheck();
