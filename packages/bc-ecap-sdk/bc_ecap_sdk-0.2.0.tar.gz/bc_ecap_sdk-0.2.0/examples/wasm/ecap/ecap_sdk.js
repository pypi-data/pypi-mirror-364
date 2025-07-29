const lib = require("./ecap_node.js");
const { BandStopFilter, BandPassFilter, NotchFilter, SosBandPassFilter } = require("./filter.js");

// EEG数据参数
const fs = 250; // 采样频率
const order = 4; // 滤波器阶数

// SOS滤波器
const Q = 30; // 品质因子
const notch_50_filters = [];
const notch_60_filters = [];
const eeg_freq_filters = [];
const use_sos_filters = false; // 是否使用SOS滤波器

function init_eeg_filters(fs, num_channels) {
  notch_50_filters.length = 0;
  notch_60_filters.length = 0;
  eeg_freq_filters.length = 0;
  // 创建每个通道的滤波器
  console.log("init_eeg_filters, num_channels:", num_channels);
  for (let i = 0; i < num_channels; i++) {
    // 新滤波方式
    if (use_sos_filters === true) {
      // 使用SOS滤波器
      const notchFilter50 = new NotchFilter(50, fs, Q); // 50Hz notch filter
      const notchFilter60 = new NotchFilter(60, fs, Q); // 60Hz notch filter
      const eegFilter = new SosBandPassFilter(order, fs, 2, 45);
      notch_50_filters.push(notchFilter50);
      notch_60_filters.push(notchFilter60);
      eeg_freq_filters.push(eegFilter);
      continue;
    }
    // 旧滤波方式
    const notchFilter50 = new BandStopFilter(order, fs, 49, 51); // remove 50Hz noise
    const notchFilter60 = new BandStopFilter(order, fs, 59, 61); // remove 60Hz noise
    const eegFilter = new BandPassFilter(order, fs, 2, 45);
    notch_50_filters.push(notchFilter50);
    notch_60_filters.push(notchFilter60);
    eeg_freq_filters.push(eegFilter);
  }
}

// EEG数据滤波处理, channel_data为某个通道的数据
function apply_eeg_filters(channel_data, channel) {
  if (channel < 0 || channel >= 32) {
    throw new RangeError("Channel must be between 0 and 31");
  }
  if (
    notch_50_filters.length === 0 ||
    notch_60_filters.length === 0 ||
    eeg_freq_filters.length === 0
  ) {
    init_eeg_filters(fs, 32); // 32个通道
  }

  let f32_data = Float32Array.from(channel_data);
  const notchFilter50 = notch_50_filters[channel];
  const notchFilter60 = notch_60_filters[channel];
  const eegFilter = eeg_freq_filters[channel];
  f32_data = notchFilter50.apply(f32_data);
  f32_data = notchFilter60.apply(f32_data);
  f32_data = eegFilter.apply(f32_data);
  return f32_data;
}

module.exports = {
  init_eeg_filters,
  apply_eeg_filters,
};
