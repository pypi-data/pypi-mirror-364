use crate::data_handler::afe_handler::parse_32ch_eeg_data;
use crate::data_handler::filter;
use crate::data_handler::filter::perform_impendance_filter;
use crate::generated::eeg_cap_proto::{eeg_data::*, *};
use crate::proto::eeg_cap::enums::*;
use crate::proto::eeg_cap::msg_builder::*;
use parking_lot::Mutex;
use parking_lot::RwLock;
use std::f64::consts::SQRT_2;

crate::cfg_import_logging!();

lazy_static::lazy_static! {
  // 默认缓冲区长度, 2000个数据点，每个数据点有32个通道，每个通道的值类型为float32，即4字节，大约占用256KB内存
  // 2000 * 32 * 4 = 256000 bytes
  static ref EEG_BUFFER_LEN: RwLock<usize> = RwLock::new(2000);
  static ref EEG_CFG: RwLock<EegConfig> = RwLock::new(EegConfig::default());
  static ref EEG_DATA_BUFFER: Mutex<Vec<EegSample>> = Mutex::new(Vec::new());

  // EEG数据缓冲区，用于计算阻抗值
  static ref IMP_EEG_DATA_BUFFER_1: Mutex<Vec<EegSample>> = Mutex::new(Vec::new());
  static ref IMP_EEG_DATA_BUFFER_2: Mutex<Vec<EegSample>> = Mutex::new(Vec::new());
  static ref IMP_EEG_DATA_BUFFER_3: Mutex<Vec<EegSample>> = Mutex::new(Vec::new());
  static ref IMP_EEG_DATA_BUFFER_4: Mutex<Vec<EegSample>> = Mutex::new(Vec::new());

  // 阻抗值缓冲区，用于计算阻抗值, 32个通道, 默认值为0
  static ref IMPEDANCE_VALUES: Mutex<Vec<f32>> = Mutex::new(vec![0.0; 32]);
  // static ref IMPEDANCE_CFG: Mutex<EegLeadOffConfig> = Mutex::new(EegLeadOffConfig::default());
  static ref IMPEDANCE_LOOP_CHECK: RwLock<bool> = RwLock::new(false);
  static ref IMPEDANCE_SKIP_COUNT: RwLock<usize> = RwLock::new(1);
  static ref IMPEDANCE_CHIP: RwLock<LeadOffChip> = RwLock::new(LeadOffChip::Chip1);
  static ref IMPEDANCE_FREQ: RwLock<LeadOffFreq> = RwLock::new(LeadOffFreq::Ac31p2hz);
  static ref IMPEDANCE_CURRENT: RwLock<LeadOffCurrent> = RwLock::new(LeadOffCurrent::Cur6nA);
  static ref IMPEDANCE_WIN_LEN: RwLock<usize> = RwLock::new(250); // 阻抗计算窗口长度, 默认250组

  // 默认缓冲区长度, 2000个数据点, 每个数据点包含acc/gyro/mag/timestamp数据值，(3 * 3 + 1) = 10个数值，每个数据占4字节，大约占用80KB内存
  static ref IMU_BUFFER_LEN: RwLock<usize> = RwLock::new(2000);
  static ref IMU_DATA_BUFFER: Mutex<Vec<ImuData>> = Mutex::new(Vec::new());
}

#[allow(unused_variables)]
fn notify_eeg_cap_message(device_id: String, msg: &EEGCapMessage) {
  // trace!(
  //   "notify_eeg_cap_message, device_id: {:?}, msg: {:?}",
  //   device_id, msg
  // );
  cfg_if::cfg_if! {
    if #[cfg(any(feature = "examples", feature = "node_addons"))] {
      crate::callback::callback_rs::run_msg_resp_callback(device_id, serde_json::to_string(msg).unwrap_or_else(|_| "".to_string()));
    } else if #[cfg(feature = "python")] {
      if !crate::python::callback::is_registered_msg_resp() {
        return;
      }
      crate::python::callback::run_msg_resp_callback(
        device_id,
        serde_json::to_string(msg).unwrap_or_else(|_| "".to_string()),
      );
    }
    // else if #[cfg(target_family = "wasm")] {
    //  crate::callback::callback_wasm::run_resp_callback(device_id, msg);
    // }
  }
}

pub fn handle_eeg_cap_message(device_id: String, msg: &EEGCapMessage) {
  match msg {
    EEGCapMessage::Mcu2App(ref mcu_msg) => {
      if let Some(hw_info) = &mcu_msg.hw_info {
        // info!("Received hardware info: {:?}", hw_info);
        crate::callback::callback_rs::run_battery_level_callback(
          device_id.clone(),
          hw_info.bat_level as u8,
        );
      }
      if let Some(eeg) = &mcu_msg.eeg {
        if let Some(eeg_cfg) = &eeg.config {
          set_eeg_cfg(eeg_cfg);
        }
        if let Some(eeg_data) = &eeg.data {
          // info!("eeg data lead_off_chip: {:?}", eeg_data.lead_off_chip);
          if eeg_data.lead_off_chip != EegLeadOffChip::ChipNone as i32 {
            // 用于计算阻抗值
            add_imp_eeg_data_to_buffer(eeg_data);
          } else {
            add_eeg_data_to_buffer(eeg_data);
          }
          // return;
        }
      } else if let Some(imu) = &mcu_msg.imu {
        // if let Some(imu_cfg) = &imu.config {
        //   set_imu_cfg(imu_cfg);
        // }
        if let Some(imu_data) = &imu.data {
          // info!("imu data: {:?}", imu_data);
          add_imu_data_to_buffer(imu_data);
          return;
        }
      }
      notify_eeg_cap_message(device_id, msg);
    }
    EEGCapMessage::Ble2App(ref ble_msg) => {
      trace!("Ble2App message: {:?}", ble_msg);
      notify_eeg_cap_message(device_id, msg);
    }
    _ => {
      info!("Received message: {:?}", msg);
      notify_eeg_cap_message(device_id, msg);
    }
  }
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn set_cfg(eeg_buffer_len: usize, imu_buffer_len: usize, imp_win_len: usize) {
  *EEG_BUFFER_LEN.write() = eeg_buffer_len;
  *IMU_BUFFER_LEN.write() = imu_buffer_len;
  *IMPEDANCE_WIN_LEN.write() = imp_win_len;
}

pub fn set_eeg_cfg(cfg: &EegConfig) {
  let mut eeg_cfg = EEG_CFG.write();
  if eeg_cfg.freq != cfg.freq || eeg_cfg.gain != cfg.gain || eeg_cfg.source != cfg.source {
    eeg_cfg.freq = cfg.freq;
    eeg_cfg.gain = cfg.gain;
    eeg_cfg.source = cfg.source;
    info!(
      "Updated eeg config: {:?}",
      serde_json::to_string(cfg).unwrap_or_else(|_| "".to_string())
    );
    clear_eeg_buffer();
  }
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn clear_eeg_buffer() {
  let mut eeg_samples = EEG_DATA_BUFFER.lock();
  eeg_samples.clear();
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn clear_imu_buffer() {
  let mut imu_data_buffer = IMU_DATA_BUFFER.lock();
  imu_data_buffer.clear();
}

pub fn get_eeg_sample_buffer(take: usize, clean: bool) -> Vec<EegSample> {
  let mut eeg_samples = EEG_DATA_BUFFER.lock();
  let len = eeg_samples.len();
  // info!("eeg_samples.len(): {}", len);
  let take = take.min(len); // 确保 take 不超过缓冲区长度

  // 获取最后 n 个元素
  let eeg_data = eeg_samples[len - take..].to_vec();

  if clean {
    eeg_samples.clear();
  } else {
    eeg_samples.drain(len - take..);
  }
  eeg_data
}

pub fn get_imu_sample_buffer(take: usize, clean: bool) -> Vec<ImuData> {
  let mut imu_data_buffer = IMU_DATA_BUFFER.lock();
  let len = imu_data_buffer.len();
  // info!("imu_data_buffer.len(): {}", len);
  let take = take.min(len); // 确保 take 不超过缓冲区长度

  // 获取最后 n 个元素
  let imu_data = imu_data_buffer[len - take..].to_vec();

  if clean {
    imu_data_buffer.clear();
  } else {
    imu_data_buffer.drain(len - take..);
  }
  imu_data
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn get_eeg_buffer(take: usize, clean: bool) -> Vec<Vec<f64>> {
  let gain = {
    let eeg_cfg = EEG_CFG.read();
    eeg_cfg.gain
  };
  let arr: Vec<Vec<f64>> = get_eeg_sample_buffer(take, clean)
    .into_iter()
    .map(|sample| {
      let mut result = vec![sample.timestamp as f64];
      result.extend(parse_32ch_eeg_data(&sample.data, gain));
      result
    })
    .collect();

  arr
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn get_imu_buffer(take: usize, clean: bool) -> Vec<Vec<f32>> {
  let arr: Vec<Vec<f32>> = get_imu_sample_buffer(take, clean)
    .into_iter()
    .map(|sample| {
      let mut result = vec![sample.timestamp as f32];
      if let Some(accel) = &sample.accel {
        result.extend([accel.cord_x, accel.cord_y, accel.cord_z]);
      }
      if let Some(gyro) = &sample.gyro {
        result.extend([gyro.cord_x, gyro.cord_y, gyro.cord_z]);
      }
      if let Some(mag) = &sample.mag {
        result.extend([mag.cord_x, mag.cord_y, mag.cord_z]);
      }
      result
    })
    .collect();

  arr
}

pub fn add_imp_eeg_data_to_buffer(data: &EegData) {
  let chip = IMPEDANCE_CHIP.read();
  let lead_off_chip = (data.lead_off_chip as u8).into();
  if lead_off_chip != *chip {
    // warn!(
    //   "Lead off chip mismatch, expected: {:?}, received: {:?}",
    //   chip, lead_off_chip
    // );
    return;
  }

  let mut imp_eeg_samples = match lead_off_chip {
    LeadOffChip::Chip1 => IMP_EEG_DATA_BUFFER_1.lock(),
    LeadOffChip::Chip2 => IMP_EEG_DATA_BUFFER_2.lock(),
    LeadOffChip::Chip3 => IMP_EEG_DATA_BUFFER_3.lock(),
    LeadOffChip::Chip4 => IMP_EEG_DATA_BUFFER_4.lock(),
    _ => panic!("Invalid lead off chip"),
  };
  let skip_counter = *IMPEDANCE_SKIP_COUNT.read();
  if let Some(sample) = &data.sample_1 {
    // 每次收到阻抗EEG数据中包含2个Sample
    if imp_eeg_samples.len() == 2 && skip_counter > 0 {
      // skip first invalid sample to stabilize
      if imp_eeg_samples[0].timestamp > sample.timestamp {
        *IMPEDANCE_SKIP_COUNT.write() = skip_counter - 1;
        // if lead_off_chip == LeadOffChip::Chip1 {
        //   info!(
        //     "remove first invalid sample: {:?}, current: {}",
        //     serde_json::to_string(&imp_eeg_samples[0]).unwrap(),
        //     serde_json::to_string(sample).unwrap()
        //   );
        // }
        imp_eeg_samples.clear();
      } else {
        // if lead_off_chip == LeadOffChip::Chip1 {
        //   info!(
        //     "first sample: {:?}, second sample: {:?}",
        //     serde_json::to_string(&imp_eeg_samples[0]).unwrap(),
        //     serde_json::to_string(sample).unwrap()
        //   );
        //   let eeg_values_0 = parse_eeg(&imp_eeg_samples[0].data, 1);
        //   let eeg_values_1 = parse_eeg(&sample.data, 1);
        //   info!(
        //     "\n\teeg_values_0: {:?}, \n\teeg_values_1: {:?}",
        //     &eeg_values_0[..3],
        //     &eeg_values_1[..3]
        //   );
        // }
      }
    }
    imp_eeg_samples.push(sample.clone());
  }
  if let Some(sample) = &data.sample_2 {
    imp_eeg_samples.push(sample.clone());
  }
  if let Some(sample) = &data.sample_3 {
    imp_eeg_samples.push(sample.clone());
  }
  if let Some(sample) = &data.sample_4 {
    imp_eeg_samples.push(sample.clone());
  }
  let max_imp_len: usize = *IMPEDANCE_WIN_LEN.read();
  let len = imp_eeg_samples.len();
  if len < max_imp_len {
    if len % 50 == 0 {
      info!("{:?}, len: {}", lead_off_chip, imp_eeg_samples.len());
    }
    return;
  }
  if len > max_imp_len {
    let excess = imp_eeg_samples.len() - max_imp_len;
    imp_eeg_samples.drain(0..excess);
  }

  let freq = *IMPEDANCE_FREQ.read();
  let current = *IMPEDANCE_CURRENT.read();
  let offset = lead_off_chip.get_imp_offset();

  let sorted_eeg_samples: Vec<EegSample> = imp_eeg_samples.iter().cloned().collect();
  // sorted_eeg_samples.sort_by_key(|sample| sample.timestamp); // 按时间戳排序

  debug!(
    "{:?}, offset:{}, len: {}, seqNum from {} to {}",
    lead_off_chip,
    offset,
    imp_eeg_samples.len(),
    imp_eeg_samples.first().unwrap().timestamp,
    imp_eeg_samples.last().unwrap().timestamp
  );

  // 每次检测8个通道, 每个通道的值为一个Vec
  let mut chip_channel_values = vec![vec![]; 8];
  for eeg_sample in sorted_eeg_samples.iter() {
    #[allow(clippy::needless_range_loop)]
    for i in 0..8 {
      let eeg_values = parse_32ch_eeg_data(&eeg_sample.data, 1);
      let channel = i + offset;
      chip_channel_values[i].push(eeg_values[channel]);
    }
  }

  let mut imp_values = IMPEDANCE_VALUES.lock();
  #[allow(clippy::needless_range_loop)]
  for i in 0..8 {
    let channel = i + offset;
    // let channel_values = if loop_check {
    //   // &chip_channel_values[i][..MAX_IMP_LEN - 1]
    // } else {
    //   &chip_channel_values[i]
    // };
    let channel_values = &chip_channel_values[i];

    let data = filter::remove_env_noise(channel_values.iter().copied(), channel);
    let data = perform_impendance_filter(data.into_iter(), channel);
    let rms = compute_rms(&data);
    let impedance = compute_impedance_value(rms, current.get_current_uA());
    // if lead_off_chip == LeadOffChip::Chip1 {
    // info!(
    //   "Channel[{}], rms:{}, impedance: {}",
    //   channel, rms, impedance
    // );
    // }
    imp_values[channel] = impedance as f32;
  }

  imp_eeg_samples.clear(); // 计算完RMS后清空缓冲区

  // 通知下一个芯片检测阻抗值
  let loop_check = *IMPEDANCE_LOOP_CHECK.read();
  let next_chip = lead_off_chip.get_next_chip();
  if loop_check {
    *IMPEDANCE_CHIP.write() = next_chip;
    *IMPEDANCE_SKIP_COUNT.write() = 1;
    clear_chip_imp_buffer(next_chip);
  }

  cfg_if::cfg_if! {
    if #[cfg(target_family = "wasm")] {
    } else if #[cfg(feature = "python")] {
      use crate::python::callback::*;
      if is_registered_imp_data() {
        run_impedance_callback(lead_off_chip.into(), imp_values.clone());
        if loop_check {
          info!("run_next_leadoff_chek, lead_off_chip: {:?}", next_chip);
          crate::eeg_cap::callback::run_next_leadoff_chek(next_chip, freq, current);
        }
      }
    } else {
      use crate::callback::callback_rs::*;
      // let formatted_imp_values: Vec<String> = imp_values[..8].iter().map(|v| format!("{:.2}", v)).collect();
      // info!("run_impedance_callback, {:?}", formatted_imp_values);
      run_impedance_callback(lead_off_chip.into(), imp_values.clone());
      if loop_check {
        super::callback::run_next_leadoff_chek(next_chip, freq, current);
      }
    }
  }
}

pub fn clear_impedance_cache() {
  // clear impedance values and buffers
  let mut imp_values = IMPEDANCE_VALUES.lock();
  *imp_values = vec![0.0; 32];
  clear_imp_eeg_buffers();
  // debug!("Cleared impedance values and buffers");
}

fn clear_chip_imp_buffer(lead_off_chip: LeadOffChip) {
  let mut imp_eeg_samples = match lead_off_chip {
    LeadOffChip::Chip1 => IMP_EEG_DATA_BUFFER_1.lock(),
    LeadOffChip::Chip2 => IMP_EEG_DATA_BUFFER_2.lock(),
    LeadOffChip::Chip3 => IMP_EEG_DATA_BUFFER_3.lock(),
    LeadOffChip::Chip4 => IMP_EEG_DATA_BUFFER_4.lock(),
    _ => panic!("Invalid lead off chip"),
  };
  imp_eeg_samples.clear();
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn clear_imp_eeg_buffers() {
  // info!("Clearing impedance eeg data buffers");
  let mut imp_eeg_data_buffer_1 = IMP_EEG_DATA_BUFFER_1.lock();
  let mut imp_eeg_data_buffer_2 = IMP_EEG_DATA_BUFFER_2.lock();
  let mut imp_eeg_data_buffer_3 = IMP_EEG_DATA_BUFFER_3.lock();
  let mut imp_eeg_data_buffer_4 = IMP_EEG_DATA_BUFFER_4.lock();
  imp_eeg_data_buffer_1.clear();
  imp_eeg_data_buffer_2.clear();
  imp_eeg_data_buffer_3.clear();
  imp_eeg_data_buffer_4.clear();
  // debug!("Cleared impedance eeg data buffers");
}

pub fn save_lead_off_cfg(loop_check: bool, freq: LeadOffFreq, current: LeadOffCurrent) {
  let mut imp_loop_check = IMPEDANCE_LOOP_CHECK.write();
  *imp_loop_check = loop_check;
  let mut imp_skip_count = IMPEDANCE_SKIP_COUNT.write();
  *imp_skip_count = 1;
  let mut imp_chip = IMPEDANCE_CHIP.write();
  *imp_chip = LeadOffChip::Chip1;
  let mut imp_freq = IMPEDANCE_FREQ.write();
  *imp_freq = freq;
  let mut imp_current = IMPEDANCE_CURRENT.write();
  *imp_current = current;
  clear_impedance_cache();
}

pub fn get_impedance_values() -> Vec<f32> {
  IMPEDANCE_VALUES.lock().clone()
}

// RMS: Root Mean Square
pub fn compute_rms(data: &[f64]) -> f64 {
  // 去掉一个最大值和一个最小值
  // let mut data = data.to_vec();
  // data.sort_by(|a, b| a.partial_cmp(b).unwrap());
  // data.pop();
  // data.remove(0);
  let sum: f64 = data.iter().map(|x| x.powi(2)).sum();
  let mean: f64 = sum / data.len() as f64;
  let rms = mean.sqrt();
  #[allow(clippy::let_and_return)]
  rms
}

#[allow(non_snake_case)]
pub fn compute_impedance_value(uv_rms: f64, current_uA: f64) -> f64 {
  let mut impedance = uv_rms * SQRT_2 / current_uA; //  uV / uA = Ω
  const INPUT_IMPEDANCE: f64 = 10.0; // 10kΩ
  impedance = (impedance / 1000.0) - INPUT_IMPEDANCE;
  // if impedance < 0.0 {
  //   impedance = 0.0;
  // }
  impedance
}

pub fn add_eeg_data_to_buffer(data: &EegData) {
  let mut eeg_samples = EEG_DATA_BUFFER.lock();
  if let Some(sample) = &data.sample_1 {
    if !eeg_samples.is_empty() {
      if eeg_samples.last().unwrap().timestamp + 1 != sample.timestamp {
        warn!(
          "EEG SeqNum not continuous: {} -> {}",
          eeg_samples.last().unwrap().timestamp,
          sample.timestamp
        );
      } else {
        let sr: crate::proto::eeg_cap::enums::EegSampleRate = (data.freq as u8).into();
        let count = match sr {
          crate::proto::eeg_cap::enums::EegSampleRate::SR_250Hz => 250,
          crate::proto::eeg_cap::enums::EegSampleRate::SR_500Hz => 500,
          crate::proto::eeg_cap::enums::EegSampleRate::SR_1000Hz => 1000,
          crate::proto::eeg_cap::enums::EegSampleRate::SR_2000Hz => 2000,
          _ => 250, // 默认值
        };
        // info!("EEG SeqNum: {}, count: {}", sample.timestamp, count);
        if sample.timestamp % (count * 2) < 4 {
          info!("EEG SeqNum: {}", sample.timestamp);
        }
      }
    }
    eeg_samples.push(sample.clone());
  }
  if let Some(sample) = &data.sample_2 {
    eeg_samples.push(sample.clone());
  }
  if let Some(sample) = &data.sample_3 {
    eeg_samples.push(sample.clone());
  }
  if let Some(sample) = &data.sample_4 {
    eeg_samples.push(sample.clone());
  }

  let max_len = *EEG_BUFFER_LEN.read();
  if eeg_samples.len() > max_len {
    let excess = eeg_samples.len() - max_len;
    eeg_samples.drain(0..excess);
  }
}

pub fn add_imu_data_to_buffer(data: &ImuData) {
  let mut imu_data_buffer = IMU_DATA_BUFFER.lock();
  imu_data_buffer.push(*data);

  let max_len = *IMU_BUFFER_LEN.read();
  if imu_data_buffer.len() > max_len {
    let excess = imu_data_buffer.len() - max_len;
    imu_data_buffer.drain(0..excess);
  }
}
