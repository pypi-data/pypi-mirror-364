use parking_lot::RwLock;

use crate::utils::tcp_client::TcpExitReason;

pub type BatteryLevelCallback = Box<dyn Fn(u8) + Send + Sync>;
pub type TcpStreamExitCallback = Box<dyn Fn(usize) + Send + Sync>;
pub type MsgRespCallback = Box<dyn Fn(String, String) + Send + Sync>;
pub type ImpedanceCallback = Box<dyn Fn(ImpedanceResult) + Send + Sync>;

#[derive(Debug)]
pub struct ImpedanceResult {
  pub chip: u8,
  pub values: Vec<f32>,
}

lazy_static::lazy_static! {
  // 默认AFE缓冲区长度, 2000个数据点
  static ref AFE_BUFFER_LEN: RwLock<usize> = RwLock::new(2000);
  // 默认IMU缓冲区长度, 2000个数据点
  static ref IMU_BUFFER_LEN: RwLock<usize> = RwLock::new(2000);
  // 默认MAG缓冲区长度, 2000个数据点
  static ref MAG_BUFFER_LEN: RwLock<usize> = RwLock::new(2000);
  // 电池电量回调
  static ref BATTERY_LEVEL_CB: RwLock<Option<BatteryLevelCallback>> = RwLock::new(None);
  // TCP连接断开回调
  static ref TCP_STREAM_EXIT_CB: RwLock<Option<TcpStreamExitCallback>> = RwLock::new(None);
  // 消息响应回调
  static ref MSG_RESP_CB: RwLock<Option<MsgRespCallback>> = RwLock::new(None);
  // 阻抗回调
  static ref IMP_CB: RwLock<Option<ImpedanceCallback>> = RwLock::new(None);
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn edu_set_afe_buffer_cfg(buff_len: usize) {
  let mut buff_len_guard = AFE_BUFFER_LEN.write();
  *buff_len_guard = buff_len;
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn edu_set_imu_buffer_cfg(imu_buffer_len: usize) {
  let mut imu_buffer_len_guard = IMU_BUFFER_LEN.write();
  *imu_buffer_len_guard = imu_buffer_len;
}

#[cfg_attr(feature = "python", pyo3::pyfunction)]
pub fn edu_set_mag_buffer_cfg(mag_buffer_len: usize) {
  let mut mag_buffer_len_guard = MAG_BUFFER_LEN.write();
  *mag_buffer_len_guard = mag_buffer_len;
}

pub fn set_battery_level_callback(callback: BatteryLevelCallback) {
  let mut cb = BATTERY_LEVEL_CB.write();
  *cb = Some(callback);
}

pub fn clear_battery_level_callback() {
  let mut cb = BATTERY_LEVEL_CB.write();
  *cb = None;
}

pub fn run_battery_level_callback(_device_id: String, level: u8) {
  let cb = BATTERY_LEVEL_CB.read();
  if let Some(ref callback) = *cb {
    callback(level);
  }
}

pub fn set_tcp_stream_exit_callback(callback: TcpStreamExitCallback) {
  let mut cb = TCP_STREAM_EXIT_CB.write();
  *cb = Some(callback);
}

pub fn clear_tcp_stream_exit_callback() {
  let mut cb = TCP_STREAM_EXIT_CB.write();
  *cb = None;
}

pub fn run_tcp_stream_exit_callback(exit_code: TcpExitReason) {
  let cb = TCP_STREAM_EXIT_CB.read();
  if let Some(ref callback) = *cb {
    callback(exit_code as usize);
  }
}

pub fn set_msg_resp_callback(callback: MsgRespCallback) {
  let mut cb = MSG_RESP_CB.write();
  *cb = Some(callback);
}

pub fn clear_msg_resp_callback() {
  let mut cb = MSG_RESP_CB.write();
  *cb = None;
}

pub fn run_msg_resp_callback(device_id: String, msg: String) {
  let cb = MSG_RESP_CB.read();
  if let Some(ref callback) = *cb {
    callback(device_id, msg);
  }
}

pub fn set_impedance_callback(callback: ImpedanceCallback) {
  let mut imp_cb = IMP_CB.write();
  *imp_cb = Some(callback);
}

pub fn clear_impedance_callback() {
  let mut imp_cb = IMP_CB.write();
  *imp_cb = None;
}

pub fn run_impedance_callback(chip: u8, values: Vec<f32>) {
  let imp_cb = IMP_CB.read();
  if let Some(ref callback) = *imp_cb {
    let result = ImpedanceResult { chip, values };
    callback(result);
  }
}

pub fn get_afe_buffer_len() -> usize {
  let buff_len = AFE_BUFFER_LEN.read();
  *buff_len
}

pub fn get_imu_buffer_len() -> usize {
  let imu_buffer_len = IMU_BUFFER_LEN.read();
  *imu_buffer_len
}

pub fn get_mag_buffer_len() -> usize {
  let mag_buffer_len = MAG_BUFFER_LEN.read();
  *mag_buffer_len
}
