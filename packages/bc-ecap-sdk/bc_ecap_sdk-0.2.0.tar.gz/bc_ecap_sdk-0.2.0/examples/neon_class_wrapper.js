// JavaScript 类包装器 - 使用Neon 1.0 函数导出
// 文件: examples/neon_class_wrapper.js

/**
 * 这个文件展示了如何在JavaScript中包装Neon导出的函数，
 * 使其表现得像真正的JavaScript类。
 *
 * 假设 Rust 端导出了以下函数：
 * - eeg_device_new(id, name) -> handle
 * - eeg_device_get_id(handle) -> string
 * - eeg_device_get_name(handle) -> string
 * - eeg_device_is_connected(handle) -> boolean
 * - eeg_device_connect(handle) -> void
 * - eeg_device_disconnect(handle) -> void
 * - eeg_device_get_info(handle) -> object
 */

// 假设这是从编译的Neon模块导入的
const nativeModule = {
  // 这些函数实际上会从 .node 文件导入
  eeg_device_new: (id, name) => ({ _internal: "device_handle", id, name }),
  eeg_device_get_id: (handle) => handle.id,
  eeg_device_get_name: (handle) => handle.name,
  eeg_device_is_connected: (handle) => handle._connected || false,
  eeg_device_connect: (handle) => {
    handle._connected = true;
  },
  eeg_device_disconnect: (handle) => {
    handle._connected = false;
  },
  eeg_device_get_info: (handle) => ({
    id: handle.id,
    name: handle.name,
    isConnected: handle._connected || false,
    sampleRate: 250,
  }),
  create_default_device: () => ({
    _internal: "device_handle",
    id: "default",
    name: "Default Device",
  }),
};

/**
 * EEG设备类的JavaScript包装器
 */
class EEGDevice {
  /**
   * 创建新的EEG设备
   * @param {string} id - 设备ID
   * @param {string} name - 设备名称
   */
  constructor(id, name) {
    if (typeof id !== "string" || typeof name !== "string") {
      throw new TypeError("ID and name must be strings");
    }

    // 调用Rust函数创建底层对象
    this._handle = nativeModule.eeg_device_new(id, name);
  }

  /**
   * 获取设备ID
   * @returns {string} 设备ID
   */
  getId() {
    return nativeModule.eeg_device_get_id(this._handle);
  }

  /**
   * 获取设备名称
   * @returns {string} 设备名称
   */
  getName() {
    return nativeModule.eeg_device_get_name(this._handle);
  }

  /**
   * 检查设备是否已连接
   * @returns {boolean} 连接状态
   */
  isConnected() {
    return nativeModule.eeg_device_is_connected(this._handle);
  }

  /**
   * 连接设备
   * @returns {Promise<void>} 连接操作的Promise
   */
  async connect() {
    try {
      nativeModule.eeg_device_connect(this._handle);
    } catch (error) {
      throw new Error(`Failed to connect device: ${error.message}`);
    }
  }

  /**
   * 断开设备连接
   */
  disconnect() {
    nativeModule.eeg_device_disconnect(this._handle);
  }

  /**
   * 获取设备完整信息
   * @returns {Object} 设备信息对象
   */
  getInfo() {
    return nativeModule.eeg_device_get_info(this._handle);
  }

  /**
   * 创建默认设备实例（静态方法）
   * @returns {EEGDevice} 默认设备实例
   */
  static createDefault() {
    const handle = nativeModule.create_default_device();
    const device = Object.create(EEGDevice.prototype);
    device._handle = handle;
    return device;
  }

  /**
   * 转换为JSON字符串
   * @returns {string} JSON字符串
   */
  toJSON() {
    return this.getInfo();
  }

  /**
   * 转换为字符串
   * @returns {string} 字符串表示
   */
  toString() {
    const info = this.getInfo();
    return `EEGDevice(id: ${info.id}, name: ${info.name}, connected: ${info.isConnected})`;
  }

  /**
   * 符号转换为原始值
   * @returns {string} 字符串表示
   */
  [Symbol.toPrimitive](hint) {
    if (hint === "string") {
      return this.toString();
    }
    if (hint === "number") {
      return this.isConnected() ? 1 : 0;
    }
    return this.getInfo();
  }
}

/**
 * EEG配置类的JavaScript包装器
 */
class EEGConfig {
  /**
   * 创建EEG配置
   * @param {number[]} channels - 通道数组
   * @param {number} sampleRate - 采样率
   * @param {number} gain - 增益
   */
  constructor(channels, sampleRate, gain) {
    if (!Array.isArray(channels)) {
      throw new TypeError("Channels must be an array");
    }
    if (typeof sampleRate !== "number" || typeof gain !== "number") {
      throw new TypeError("Sample rate and gain must be numbers");
    }

    // 这里会调用Rust函数：nativeModule.eeg_config_new(channels, sampleRate, gain)
    this._handle = { channels, sampleRate, gain }; // 模拟
  }

  /**
   * 获取通道配置
   * @returns {number[]} 通道数组
   */
  getChannels() {
    // 实际调用：return nativeModule.eeg_config_get_channels(this._handle);
    return this._handle.channels;
  }

  /**
   * 获取采样率
   * @returns {number} 采样率
   */
  getSampleRate() {
    return this._handle.sampleRate;
  }

  /**
   * 获取增益
   * @returns {number} 增益值
   */
  getGain() {
    return this._handle.gain;
  }

  /**
   * 转换为JSON对象
   * @returns {Object} 配置对象
   */
  toJson() {
    // 实际调用：return nativeModule.eeg_config_to_json(this._handle);
    return {
      channels: this.getChannels(),
      sampleRate: this.getSampleRate(),
      gain: this.getGain(),
    };
  }
}

// 使用示例
console.log("=== Neon 类包装器使用示例 ===\n");

try {
  // 1. 创建设备
  console.log("1. 创建设备：");
  const device = new EEGDevice("device123", "我的脑电设备");
  console.log(`设备: ${device}`);
  console.log(`ID: ${device.getId()}`);
  console.log(`名称: ${device.getName()}`);
  console.log(`连接状态: ${device.isConnected()}`);

  // 2. 连接设备
  console.log("\n2. 连接设备：");
  await device.connect();
  console.log(`连接后状态: ${device.isConnected()}`);

  // 3. 获取设备信息
  console.log("\n3. 设备信息：");
  const info = device.getInfo();
  console.log(JSON.stringify(info, null, 2));

  // 4. 断开连接
  console.log("\n4. 断开连接：");
  device.disconnect();
  console.log(`断开后状态: ${device.isConnected()}`);

  // 5. 使用静态方法
  console.log("\n5. 创建默认设备：");
  const defaultDevice = EEGDevice.createDefault();
  console.log(`默认设备: ${defaultDevice}`);

  // 6. 创建配置
  console.log("\n6. 创建配置：");
  const config = new EEGConfig([1, 2, 3, 4], 250, 1.5);
  console.log("配置JSON:", JSON.stringify(config.toJson(), null, 2));
} catch (error) {
  console.error("错误:", error.message);
}

// 导出类以供其他模块使用
module.exports = {
  EEGDevice,
  EEGConfig,
};

/**
 * TypeScript 类型定义（可以放在单独的 .d.ts 文件中）
 */
/*
declare class EEGDevice {
  constructor(id: string, name: string);
  getId(): string;
  getName(): string;
  isConnected(): boolean;
  connect(): Promise<void>;
  disconnect(): void;
  getInfo(): {
    id: string;
    name: string;
    isConnected: boolean;
    sampleRate: number;
  };
  static createDefault(): EEGDevice;
  toJSON(): object;
  toString(): string;
}

declare class EEGConfig {
  constructor(channels: number[], sampleRate: number, gain: number);
  getChannels(): number[];
  getSampleRate(): number;
  getGain(): number;
  toJson(): {
    channels: number[];
    sampleRate: number;
    gain: number;
  };
}

export { EEGDevice, EEGConfig };
*/

/**
 * 使用模式总结：
 *
 * 1. Rust端导出函数而不是类
 * 2. JavaScript端创建类包装器
 * 3. 使用私有_handle属性存储Rust对象
 * 4. 所有方法都是对Rust函数的包装调用
 * 5. 添加JavaScript特有的便利方法
 * 6. 提供完整的错误处理
 * 7. 支持异步操作
 * 8. 提供TypeScript类型定义
 *
 * 优势：
 * - 更好的错误处理
 * - 支持JavaScript原生特性
 * - 更灵活的API设计
 * - 更容易调试和测试
 * - 完整的TypeScript支持
 */
