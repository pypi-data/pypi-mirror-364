const model = require("./example_eeg_cap_model.js");
const EEGData = model.EEGData;
const IMUData = model.IMUData;
const printTimestamp = model.printTimestamp;

const {
  NoiseTypes,
  EegSampleRate,
  EegSignalGain,
  EegSignalSource,
  ImuSampleRate,
} = require("../pkg/bc_ecap_sdk");

const lib = require("./ecap_node.js");
const { init_eeg_filters, apply_eeg_filters } = require("./ecap_sdk.js");
const EcapDevice = require("./ecap_device.js");

// EEG数据
const fs = 250; // 采样频率
const num_channels = 32; // 通道数
const eeg_buffer_length = 2000; // EEG缓冲区长度, 默认2000个数据点，注意采样率应该小于此数
let eegValues = Array.from({ length: num_channels }, () =>
  Array(eeg_buffer_length).fill(0)
);

// IMU数据
const imu_buffer_length = 2000; // IMU缓冲区长度, 默认2000个数据点

const imp_window_length = 250; // 阻抗检测窗口长度, 默认250组

function initCfg() {
  let log_level = 3; // 0: error, 1: warn, 2: info, 3: debug, 4: trace
  log_level = 2;
  lib.init_logging(log_level);

  lib.set_env_noise_cfg(NoiseTypes.FIFTY, fs); // 设置环境噪声滤波器，50Hz 电源干扰
  lib.set_cfg(eeg_buffer_length, imu_buffer_length, imp_window_length);
  lib.set_msg_resp_callback((resp) => {
    console.log("ECAP msg response:", resp);
  });
  lib.set_battery_level_callback((battery_level) => {
    console.log("Battery level:", battery_level);
  });
  lib.set_tcp_stream_exit_callback((code) => {
    console.log("ECAP TCP stream exit:", code);
    // Normal = 0,
    // Disconnected = 1,
    // Timeout = 2,
    // ConnectionError = 3,
  });
  init_eeg_filters(fs, num_channels); // 初始化EEG滤波器
}

async function main() {
  initCfg();
  initChart();
  await scan_mdns();
}
main();

// 如果已知IP地址和端口，可以直接指定
// scan_service();
// let addr = "192.168.3.7"; // hailong-dev
// let addr = "192.168.3.12"; // xiangao-dev
// let addr = "192.168.3.23"; // yongle-dev
// let addr = "192.168.3.6"; // yongle-dev
// let addr = "192.168.2.19"; // yongle-dev
// let port = 53129;
async function scan_mdns() {
  lib.set_mdns_scan_result_callback(async (result) => {
    console.log("mdns scan result:", result);
    if (result.sn === "SN-Yongle-dev") {
      await lib.mdns_stop_scan();
      await connect_device(result);
    }
  });
  await lib.mdns_start_scan();
}

let target_device = null;
async function connect_device(result) {
  target_device = new EcapDevice(result.addr, result.port); // 创建设备对象
  await target_device.connect(); // 连接设备
  await target_device.get_device_info(); // 读取设备信息
  await target_device.get_battery_level(); // 读取电池电量
  return;
  await target_device.start_leadoff_check(); // 开启阻抗检测模式，与正常EEG模式互斥
  return;

  // 开启正常工作模式
  // 配置EEG为正常佩戴信号
  // await target_device.start_eeg_stream(
  //   EegSampleRate.SR_250Hz,
  //   EegSignalGain.GAIN_1,
  //   EegSignalSource.NORMAL
  // );
  // 500Hz, 增益为1倍，正常信号
  await target_device.start_eeg_stream(
    EegSampleRate.SR_500Hz,
    EegSignalGain.GAIN_1,
    EegSignalSource.NORMAL
  );
  // 1000Hz，增益为1倍，测试信号，循环 1Hz 方波
  // FIXME: 1000Hz 采样率下，有丢包，待优化解决
  // await target_device.start_eeg_stream(
  //   EegSampleRate.SR_1000Hz,
  //   EegSignalGain.GAIN_1,
  //   EegSignalSource.TEST_SIGNAL
  // );
  // await target_device.start_imu_stream(ImuSampleRate.SR_50Hz);
  await target_device.start_imu_stream(ImuSampleRate.SR_100Hz);
}

function initChart() {
  // TODO:初始化绘图
  setInterval(updateChart, 1000); // 每 1000ms 更新绘图
}

function updateChart() {
  // 更新绘图
  updateEegChart();
  updateImuChart();
}

let startTime = Date.now(); // 记录开始时间

function updateEegChart() {
  // 获取EEG数据缓冲区中的数据
  const fetch_num = 2000; // 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
  const clean = true; // 是否清空缓冲区
  let eegBuff = lib.get_eeg_buffer_arr(fetch_num, clean);
  // console.log("eegBuff", eegBuff);
  if (eegBuff.length <= 0) {
    return;
  }
  let elapsedTime = (Date.now() - startTime) / 1000;
  // console.log(`elapsedTime=${elapsedTime}, eegBuff, len=${eegBuff.length}`);
  let list = eegBuff.map((row) => EEGData.fromData(row));
  // printTimestamp(list);

  for (const row of list) {
    const channelValues = row.channelValues;

    // 更新每个通道的数据
    for (let i = 0; i < channelValues.length; i++) {
      eegValues[i].shift(); // 移除第一个元素
      eegValues[i].push(channelValues[i]); // 添加最新的数据值
    }
  }

  // TODO: 根据需要绘制EEG时域信号图表和FFT图表
  for (let channel = 0; channel < eegValues.length; channel++) {
    // TODO: 绘制EEG时域信号图表
    const rawData = eegValues[channel]; // 连续的时域数据
    // if (channel == 0)
    //   console.log(`rawData, len=${rawData.length}, ${rawData.slice(rawData.length - 5)}`);
    const filterData = apply_eeg_filters(rawData, channel);
    // if (channel == 0)
    //   console.log(`filterData, ${filterData.slice(filterData.length - 5)}`);

    // TODO: 绘制FFT图表
    const n = rawData.length;
    // 频率轴
    const fftFreq = lib.get_filtered_freq(n, fs);
    // 原始EEG数据fft
    const fftData = lib.get_filtered_fft(Float32Array.from(rawData), fs);
    // 滤波后的EEG数据fft
    const fftData2 = lib.get_filtered_fft(Float32Array.from(filterData), fs);
  }
}

function updateImuChart() {
  // 获取IMU数据缓冲区中的数据
  const fetch_num = 5000; // 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
  const clean = true; // 是否清空缓冲区
  let json = lib.get_imu_buffer_json(fetch_num, clean);
  let imuBuff = JSON.parse(json);
  // console.log("imuBuff", imuBuff.length, typeof imuBuff);
  if (imuBuff.length <= 0) {
    return;
  }
  let elapsedTime = (Date.now() - startTime) / 1000;
  console.log(`elapsedTime=${elapsedTime}, imuBuff, len=${imuBuff.length}`);
  let list = imuBuff.map((row) => IMUData.fromData(row));
  printTimestamp(list);
  // TODO: updateImuPlotlyChart(list);
}
