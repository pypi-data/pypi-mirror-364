const lib = require("./ecap_node.js");
const { LeadOffCurrent, LeadOffFreq } = require("../pkg/bc_ecap_sdk");

class EcapDevice {
  constructor(addr, port) {
    this.addr = addr;
    this.port = port;
  }
  async connect() {
    await lib.tcp_connect(this.addr, this.port); // init tcp client and connect
  }
  async disconnect() {
    await lib.tcp_disconnect(this.addr, this.port);
  }
  async get_device_info() {
    return lib.get_device_info(this.addr, this.port);
  }
  async get_battery_level() {
    return lib.get_battery_level(this.addr, this.port);
  }
  // async set_device_info() {
  //   return lib.set_device_info(this.addr, this.port);
  // }
  async get_imu_config() {
    return lib.get_imu_config(this.addr, this.port);
  }
  async get_eeg_config() {
    return lib.get_eeg_config(this.addr, this.port);
  }
  async get_leadoff_config() {
    await lib.get_leadoff_config(this.addr, this.port);
  }
  async set_eeg_config(sample_rate, gain, signal_source) {
    return lib.set_eeg_config(this.addr, this.port, {
      sample_rate,
      gain,
      signal_source,
    });
  }
  async set_imu_config(sample_rate) {
    await lib.set_imu_config(this.addr, this.port, {
      sample_rate,
    });
  }
  async start_imu_stream(sample_rate) {
    await this.set_imu_config(sample_rate);
    await this.get_imu_config();
    await lib.start_imu_stream(this.addr, this.port);
  }
  async stop_imu_stream() {
    await lib.stop_imu_stream(this.addr, this.port);
  }
  // 开始正常EEG模式，注意：从阻抗检测模式切换到正常EEG模式, 需要先停止阻抗检测
  async start_eeg_stream(sample_rate, gain, signal_source) {
    await this.set_eeg_config(sample_rate, gain, signal_source); // 设置EEG参数
    await this.get_eeg_config(); // 读取EEG配置, 计算EEG电压值用到配置信息, gain
    await lib.start_eeg_stream(this.addr, this.port); // 订阅EEG数据流
  }
  // 停止EEG数据流
  async stop_eeg_stream() {
    await lib.stop_eeg_stream(this.addr, this.port);
  }
  // 开始阻抗检测，与正常EEG模式互斥
  async start_leadoff_check() {
    const current = LeadOffCurrent.Cur6nA; // 默认使用6nA
    const freq = LeadOffFreq.Ac31p2hz; // AC 31.2 Hz
    // 开始阻抗检测, 从芯片1~4轮询，每个芯片包含8个通道
    // 至少轮询过一轮chip 1~4，才能获取到完整的32个通道的阻抗值
    // const loop_check = false; // 是否循环检测
    const loop_check = true; // 是否循环检测
    await lib.start_leadoff_check(
      this.addr,
      this.port,
      { loop_check, freq, current },
      (obj) => {
        // chip 1~4
        // values, Unit: kΩ, 计算结果不正确时，为0或负数
        console.log("on_leadoff_check", JSON.stringify(obj));
      }
    );
  }
  // 停止阻抗检测，与正常EEG模式互斥，注意：从阻抗检测模式切换到正常EEG模式, 需要先停止阻抗检测
  async stop_leadoff_check() {
    await lib.stop_leadoff_check(this.addr, this.port);
  }
}

// 创建导出对象
function export_symbols() {
  return EcapDevice;
}

// CommonJS
if (typeof module !== "undefined" && module.exports) {
  module.exports = export_symbols();
}
