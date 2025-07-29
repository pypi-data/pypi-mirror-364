// TypeScript 类型定义文件
// 文件: types/neon_classes.d.ts

/**
 * EEG设备类 - 通过Neon从Rust导出
 */
export declare class EEGDevice {
  /**
   * 创建新的EEG设备实例
   * @param id 设备唯一标识符
   * @param name 设备名称
   */
  constructor(id: string, name: string);

  /**
   * 获取设备ID
   * @returns 设备唯一标识符
   */
  getId(): string;

  /**
   * 获取设备名称
   * @returns 设备名称
   */
  getName(): string;

  /**
   * 检查设备是否已连接
   * @returns 连接状态
   */
  isConnected(): boolean;

  /**
   * 获取当前采样率
   * @returns 采样率 (Hz)
   */
  getSampleRate(): number;

  /**
   * 设置采样率
   * @param rate 新的采样率 (Hz)
   */
  setSampleRate(rate: number): void;

  /**
   * 连接设备
   */
  connect(): void;

  /**
   * 断开设备连接
   */
  disconnect(): void;

  /**
   * 获取设备完整信息
   * @returns 包含所有设备信息的对象
   */
  getInfo(): {
    id: string;
    name: string;
    isConnected: boolean;
    sampleRate: number;
  };
}

/**
 * EEG配置类 - 通过Neon从Rust导出
 */
export declare class EEGConfig {
  /**
   * 创建新的EEG配置实例
   * @param channels 通道数组
   * @param sampleRate 采样率
   * @param gain 增益值
   */
  constructor(channels: number[], sampleRate: number, gain: number);

  /**
   * 获取通道配置
   * @returns 通道数组
   */
  getChannels(): number[];

  /**
   * 获取采样率
   * @returns 采样率 (Hz)
   */
  getSampleRate(): number;

  /**
   * 获取增益值
   * @returns 增益值
   */
  getGain(): number;

  /**
   * 将配置转换为JSON对象
   * @returns 包含所有配置信息的JSON对象
   */
  toJson(): {
    channels: number[];
    sampleRate: number;
    gain: number;
  };
}

/**
 * 工厂函数 - 创建默认EEG设备
 * @returns 预配置的默认EEG设备实例
 */
export declare function createDefaultDevice(): EEGDevice;

/**
 * 模块导出接口
 */
export interface NeonEEGModule {
  EEGDevice: typeof EEGDevice;
  EEGConfig: typeof EEGConfig;
  createDefaultDevice: typeof createDefaultDevice;
}

/**
 * 使用示例：
 *
 * ```typescript
 * import { EEGDevice, EEGConfig, createDefaultDevice } from './your-neon-module';
 *
 * // 创建设备
 * const device = new EEGDevice("dev123", "我的设备");
 * device.connect();
 * console.log(device.isConnected()); // true
 *
 * // 创建配置
 * const config = new EEGConfig([1, 2, 3, 4], 250, 1.0);
 * console.log(config.getChannels()); // [1, 2, 3, 4]
 *
 * // 使用工厂函数
 * const defaultDevice = createDefaultDevice();
 * console.log(defaultDevice.getName()); // "Default EEG Device"
 * ```
 */

/**
 * 错误类型定义
 */
export interface NeonError extends Error {
  name: 'NeonError';
  message: string;
}

/**
 * 设备状态枚举
 */
export enum DeviceStatus {
  Disconnected = 0,
  Connecting = 1,
  Connected = 2,
  Error = 3
}

/**
 * 高级类型定义
 */
export type DeviceInfo = ReturnType<EEGDevice['getInfo']>;
export type ConfigJson = ReturnType<EEGConfig['toJson']>;

/**
 * 事件回调类型
 */
export type DeviceEventCallback = (device: EEGDevice) => void;
export type DataCallback = (data: number[]) => void;
export type ErrorCallback = (error: NeonError) => void;
