const path = require("path");
const fs = require("fs");

const model = require("./example_eeg_cap_model.js");
const { MsgType, NoiseTypes } = require("../pkg/bc_ecap_sdk");
const EEGData = model.EEGData;
const IMUData = model.IMUData;
const printTimestamp = model.printTimestamp;

const lib = require("./ecap_node.js");
const { init_eeg_filters, apply_eeg_filters } = require("./ecap_sdk.js");
const deviceId = "ecap-mock";

// EEG数据
const sample_rate = 250; // 采样频率
const num_channels = 32; // 通道数
const eeg_buffer_length = 2000; // 默认缓冲区长度，注意采样率应该小于此数
let eegValues = Array.from({ length: num_channels }, () =>
  Array(eeg_buffer_length).fill(0)
);

// IMU数据
const imu_buffer_length = 1000; // 默认缓冲区长度, 1000个数据点

const imp_window_length = 250; // 阻抗检测默认窗口长度, 250个数据点

function updateEegChart() {
  // 获取EEG数据缓冲区中的数据
  const fetch_num = 1250; // 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
  const clean = true; // 是否清空缓冲区
  let eegBuff = lib.get_eeg_buffer_arr(fetch_num, clean);
  // console.log("eegBuff", eegBuff);
  console.log(`eegBuff, len=${eegBuff.length}`);
  let list = eegBuff.map((row) => EEGData.fromData(row));
  printTimestamp(list);

  for (const row of list) {
    const channelValues = row.channelValues;
    // 更新每个通道的数据
    for (let i = 0; i < channelValues.length; i++) {
      eegValues[i].shift(); // 移除第一个元素
      eegValues[i].push(channelValues[i]); // 添加最新的数据值
    }
  }

  // 绘制更新后的数据
  for (let channel = 0; channel < eegValues.length; channel++) {
    const rawData = eegValues[channel]; // 连续的时域数据
    const filterData = apply_eeg_filters(rawData, channel);
    if (channel == 0) {
      console.log(`data len=${rawData.length}`);
      console.log(`rawData=${rawData.slice(1550, 1555)}`);
      console.log(`filterData=${filterData.slice(1550, 1555)}`);
    }
    const n = rawData.length;
    // 频率轴
    const fftFreq = lib.get_filtered_freq(n, sample_rate);
    // 原始EEG数据fft
    const fftData = lib.get_filtered_fft(
      Float32Array.from(rawData),
      sample_rate
    );
    // 滤波后的EEG数据fft
    const fftData2 = lib.get_filtered_fft(
      Float32Array.from(filterData),
      sample_rate
    );
    if (channel == 0) {
      console.log(`fftFreq=${fftFreq.slice(0, 10)}`);
      console.log(`fftData=${fftData.slice(0, 10)}`);
      console.log(`fftData2=${fftData2.slice(0, 10)}`);
    }
    // TODO: 绘制图表
  }
}

function printImuData() {
  const fetch_num = 5000; // 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
  const clean = true; // 是否清空缓冲区
  let json = lib.get_imu_buffer_json(fetch_num, clean);
  let imuBuff = JSON.parse(json);
  if (imuBuff.length <= 0) {
    return;
  }
  console.log(`imuBuff, len=${imuBuff.length}`);
  let list = imuBuff.map((row) => IMUData.fromData(row));
  printTimestamp(list);
}

function mock_recv_data() {
  console.log("mock_recv_data");
  const msgs = [
    // empty response
    [
      0x42, 0x52, 0x4e, 0x43, 0x02, 0x0b, 0x02, 0x00, 0x00, 0x02, 0x00, 0x08,
      0x02, 0xac, 0x36,
    ],
    // Device info response
    [
      0x42, 0x52, 0x4e, 0x43, 0x02, 0x0b, 0x27, 0x00, 0x00, 0x02, 0x00, 0x08,
      0x02, 0x32, 0x23, 0x0a, 0x05, 0x45, 0x45, 0x47, 0x33, 0x32, 0x12, 0x0c,
      0x45, 0x45, 0x47, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
      0x22, 0x05, 0x31, 0x2e, 0x30, 0x2e, 0x30, 0x2a, 0x05, 0x30, 0x2e, 0x30,
      0x2e, 0x36, 0xb1, 0x8c,
    ],
    // IMU config response
    [
      0x42, 0x52, 0x4e, 0x43, 0x02, 0x0b, 0x08, 0x00, 0x00, 0x02, 0x00, 0x08,
      0x03, 0x22, 0x04, 0x0a, 0x02, 0x08, 0x01, 0x4b, 0xf8,
    ],
  ];
  for (const msg of msgs) {
    receiveTcpData(msg);
  }
  // return;

  // read from file, eeg_cap_sample_eeg.log
  console.log(path.resolve(__dirname, "eeg_cap_sample_eeg.log"));
  const f = fs.readFileSync(path.resolve(__dirname, "eeg_cap_sample_eeg.log"));
  const lines = f.toString().split("\n");
  console.log(`lines, len=${lines.length}`);
  for (const line of lines) {
    const data = line.split(", ");
    receiveTcpData(data);
  }

  // read from file, eeg_cap_sample_imu.log
  console.log(path.resolve(__dirname, "eeg_cap_sample_imu.log"));
  const f2 = fs.readFileSync(path.resolve(__dirname, "eeg_cap_sample_imu.log"));
  const lines2 = f2.toString().split("\n");
  console.log(`lines2, len=${lines2.length}`);
  for (const line of lines2) {
    const data = line.split(", ");
    receiveTcpData(data);
  }
}

function receiveTcpData(data) {
  lib.did_receive_data(deviceId, Uint8Array.from(data));
}

function initCfg() {
  let log_level = 3; // 0: error, 1: warn, 2: info, 3: debug, 4: trace
  log_level = 2;
  lib.init_logging(log_level);

  lib.set_env_noise_cfg(NoiseTypes.FIFTY, sample_rate); // 设置环境噪声滤波器，50Hz 电源干扰
  lib.set_cfg(eeg_buffer_length, imu_buffer_length, imp_window_length);
  lib.init_ble_parser(deviceId, MsgType.EEGCap);
  lib.set_msg_resp_callback((resp) => {
    console.log("ECAP msg response:", resp);
  });
  init_eeg_filters(sample_rate, num_channels); // 初始化EEG滤波器
}

async function main() {
  initCfg();
  mock_recv_data();
  await setTimeout(() => {
    updateEegChart();
    printImuData();
  }, 1000);
}
main();
