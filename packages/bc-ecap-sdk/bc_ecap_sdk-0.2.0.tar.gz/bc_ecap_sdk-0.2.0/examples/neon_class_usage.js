// JavaScript 使用 Neon 导出类的示例
// 文件: examples/neon_class_usage.js

const { EEGDevice, EEGConfig, createDefaultDevice } = require("../index.node"); // 假设编译后的模块路径

console.log("=== Neon 类导出使用示例 ===\n");

// 1. 使用 EEGDevice 类
console.log("1. EEGDevice 类使用示例：");
try {
  // 创建设备实例
  const device = new EEGDevice("device123", "我的脑电设备");

  console.log(`设备ID: ${device.getId()}`);
  console.log(`设备名称: ${device.getName()}`);
  console.log(`连接状态: ${device.isConnected()}`);
  console.log(`采样率: ${device.getSampleRate()}`);

  // 连接设备
  device.connect();
  console.log(`连接后状态: ${device.isConnected()}`);

  // 设置采样率
  device.setSampleRate(500);
  console.log(`新采样率: ${device.getSampleRate()}`);

  // 获取设备信息
  const info = device.getInfo();
  console.log("设备信息:", JSON.stringify(info, null, 2));

  // 断开连接
  device.disconnect();
  console.log(`断开后状态: ${device.isConnected()}`);
} catch (error) {
  console.error("EEGDevice 使用出错:", error.message);
}

console.log("\n---\n");

// 2. 使用 EEGConfig 类
console.log("2. EEGConfig 类使用示例：");
try {
  // 创建配置实例
  const config = new EEGConfig([1, 2, 3, 4, 5, 6, 7, 8], 250, 1.5);

  console.log(`通道配置: ${config.getChannels()}`);
  console.log(`采样率: ${config.getSampleRate()}`);
  console.log(`增益: ${config.getGain()}`);

  // 转换为JSON
  const configJson = config.toJson();
  console.log("配置JSON:", JSON.stringify(configJson, null, 2));
} catch (error) {
  console.error("EEGConfig 使用出错:", error.message);
}

console.log("\n---\n");

// 3. 使用工厂函数
console.log("3. 工厂函数使用示例：");
try {
  const defaultDevice = createDefaultDevice();
  console.log(`默认设备ID: ${defaultDevice.getId()}`);
  console.log(`默认设备名称: ${defaultDevice.getName()}`);
} catch (error) {
  console.error("工厂函数使用出错:", error.message);
}

console.log("\n---\n");

// 4. 类型检查示例
console.log("4. 类型检查示例：");
try {
  const device = new EEGDevice("test", "测试设备");

  console.log(`device instanceof EEGDevice: ${device instanceof EEGDevice}`);
  console.log(`device.constructor.name: ${device.constructor.name}`);

  // 检查方法是否存在
  console.log(`device.getId 是函数: ${typeof device.getId === "function"}`);
  console.log(`device.connect 是函数: ${typeof device.connect === "function"}`);
} catch (error) {
  console.error("类型检查出错:", error.message);
}

console.log("\n---\n");

// 5. 错误处理示例
console.log("5. 错误处理示例：");
try {
  // 尝试用错误的参数创建设备
  const device = new EEGDevice(); // 缺少必需参数
} catch (error) {
  console.log(`捕获到预期错误: ${error.message}`);
}

try {
  // 尝试用错误的参数创建配置
  const config = new EEGConfig("invalid", 250, 1.0); // 第一个参数应该是数组
} catch (error) {
  console.log(`捕获到预期错误: ${error.message}`);
}

console.log("\n=== 示例结束 ===");

// 6. 性能测试示例
console.log("\n6. 性能测试示例：");
const startTime = Date.now();
const devices = [];

// 创建大量设备实例
for (let i = 0; i < 1000; i++) {
  const device = new EEGDevice(`device${i}`, `设备${i}`);
  device.setSampleRate(250 + (i % 100));
  devices.push(device);
}

const endTime = Date.now();
console.log(`创建1000个设备实例耗时: ${endTime - startTime}ms`);

// 清理测试
devices.length = 0;
console.log("性能测试完成，已清理资源");
