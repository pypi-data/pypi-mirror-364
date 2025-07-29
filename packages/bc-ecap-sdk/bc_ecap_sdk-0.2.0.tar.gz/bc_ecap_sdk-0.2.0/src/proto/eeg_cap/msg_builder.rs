#![allow(clippy::not_unsafe_ptr_arg_deref)]
crate::cfg_import_logging!();

use serde::{Deserialize, Serialize};

use crate::{
  generated::eeg_cap_proto::*,
  impl_enum_conversion,
  proto::{enums::*, msg_builder::Builder},
};

// use super::enums::EegSignalGain;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EEGCapMessage {
  App2Ble(Box<AppBle>),
  Ble2App(Box<BleApp>),
  App2Mcu(Box<AppMain>),
  Mcu2App(Box<MainApp>),
}
impl_enum_conversion!(EEGCapModuleId, MCU = 0, BLE = 1, APP = 2);

impl EegSignalGain {
  pub fn get_gain(self) -> f32 {
    match self {
      EegSignalGain::EegGain1 => 1.0,
      EegSignalGain::EegGain2 => 2.0,
      EegSignalGain::EegGain4 => 4.0,
      EegSignalGain::EegGain6 => 6.0,
      EegSignalGain::EegGain8 => 8.0,
      EegSignalGain::EegGain12 => 12.0,
      EegSignalGain::EegGain24 => 24.0,
      _ => 6.0,
    }
  }
}

impl Builder {
  pub fn build_eeg_cap_to_ble(&self, payload: &[u8]) -> Vec<u8> {
    if self.msg_type != MsgType::EEGCap {
      panic!("Invalid message type");
    }
    self.build_msg(
      payload,
      EEGCapModuleId::APP.into(),
      EEGCapModuleId::BLE.into(),
    )
  }

  pub fn build_eeg_cap_to_mcu(&self, payload: &[u8]) -> Vec<u8> {
    if self.msg_type != MsgType::EEGCap {
      panic!("Invalid message type");
    }
    self.build_msg(
      payload,
      EEGCapModuleId::APP.into(),
      EEGCapModuleId::MCU.into(),
    )
  }
}

impl EEGCapMessage {
  const PARSE_TYPE: MsgType = MsgType::EEGCap;
  pub fn parse_message(
    src_module: u8,
    dst_module: u8,
    payload: &[u8],
  ) -> Result<EEGCapMessage, ParseError> {
    trace!(
      "parse_message: {:?}, {:?}, {:?}",
      src_module,
      dst_module,
      payload
    );
    if EEGCapModuleId::APP == src_module.into() {
      Self::parse_req_message(dst_module, payload)
    } else if EEGCapModuleId::APP == dst_module.into() {
      Self::parse_resp_message(src_module, payload)
    } else {
      Err(ParseError::InvalidModule(
        Self::PARSE_TYPE,
        src_module,
        dst_module,
      ))
    }
  }

  fn parse_req_message(dst_module: u8, payload: &[u8]) -> Result<EEGCapMessage, ParseError> {
    // info!("parse_req_message: {:?}, {:?}", dst_module, payload);
    let module: EEGCapModuleId = dst_module.into();
    match module {
      EEGCapModuleId::BLE => {
        let req = decode::<AppBle>(payload)?;
        Ok(EEGCapMessage::App2Ble(Box::new(req)))
      }
      EEGCapModuleId::MCU => {
        let req = decode::<AppMain>(payload)?;
        Ok(EEGCapMessage::App2Mcu(Box::new(req)))
      }
      _ => Err(ParseError::InvalidModule(Self::PARSE_TYPE, 0, dst_module)),
    }
  }

  fn parse_resp_message(src_module: u8, payload: &[u8]) -> Result<EEGCapMessage, ParseError> {
    let module: EEGCapModuleId = src_module.into();
    match module {
      EEGCapModuleId::BLE => {
        let resp = decode::<BleApp>(payload)?;
        // info!("resp: {:}", serde_json::to_string(&resp).unwrap_or_else(|_| "".to_string()));
        Ok(EEGCapMessage::Ble2App(Box::new(resp)))
      }
      EEGCapModuleId::MCU => {
        let resp = decode::<MainApp>(payload)?;
        Ok(EEGCapMessage::Mcu2App(Box::new(resp)))
      }
      _ => Err(ParseError::InvalidModule(Self::PARSE_TYPE, src_module, 0)),
    }
  }
}

pub mod eeg_cap_msg_builder {
  use crate::proto::{enums::MsgType, msg_builder::Builder};
  use lazy_static::lazy_static;
  use prost::Message;
  use std::sync::atomic::{AtomicU32, Ordering};

  use super::*;
  crate::cfg_import_logging!();
  lazy_static! {
    static ref BUILDER: Builder = Builder::new(MsgType::EEGCap);
  }

  static MSG_ID: AtomicU32 = AtomicU32::new(1);
  fn gen_msg_id() -> u32 {
    MSG_ID.fetch_add(1, Ordering::SeqCst)
  }

  fn _encode_app_to_ble(msg: AppBle) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_ble: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    (
      msg.msg_id,
      BUILDER.build_eeg_cap_to_ble(&msg.encode_to_vec()),
    )
  }

  fn encode_app_to_mcu(msg: AppMain) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_mcu: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    (
      msg.msg_id,
      BUILDER.build_eeg_cap_to_mcu(&msg.encode_to_vec()),
    )
  }

  fn encode_app_to_ble(msg: AppBle) -> (u32, Vec<u8>) {
    info!(
      "encode_app_to_ble: {:?}",
      serde_json::to_string(&msg).unwrap_or_else(|_| "".to_string())
    );
    (
      msg.msg_id,
      BUILDER.build_eeg_cap_to_ble(&msg.encode_to_vec()),
    )
  }

  fn _get_seconds() -> u64 {
    // let now = std::time::SystemTime::now();
    // now.duration_since(std::time::UNIX_EPOCH)
    //   .unwrap()
    //   .as_millis() as u64
    chrono::Utc::now().timestamp() as u64
  }

  // 1 disable数据流
  // 2 切换到阻抗模式
  // 3 设置leadoff配置
  // 4 启动数据流
  pub fn switch_and_start_leadoff_check(chip: i32, freq: i32, current: i32) -> (u32, Vec<u8>) {
    let (_, cmd1) = stop_eeg_stream();
    let (_msg_id, cmd2) = set_and_start_leadoff_check(chip, freq, current);
    // let (_, cmd3) = enable_eeg_stream();
    let mut buf = vec![];
    buf.extend_from_slice(&cmd1);
    buf.extend_from_slice(&cmd2);
    // buf.extend_from_slice(&cmd3);
    (_msg_id, buf)
  }

  pub fn stop_leadoff_check() -> (u32, Vec<u8>) {
    let eeg_acq_request = EegAcqRequest {
      enable: Some(BoolValue { value: false }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  // 1 切换到阻抗模式
  // 2 设置leadoff配置
  // 3 启动数据流
  pub(crate) fn set_and_start_leadoff_check(
    chip: i32,
    ac_freq: i32,
    current: i32,
  ) -> (u32, Vec<u8>) {
    let leadoff_config = EegLeadOffConfig {
      chip,
      ac_freq,
      current,
      gain: EegSignalGain::EegGain1 as i32,
      ..Default::default()
    };
    let eeg_req = EegAcqRequest {
      lead_off: Some(leadoff_config),
      mode: EegMode::LeadOff as i32,
      enable: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_req),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn enable_leadoff_check() -> (u32, Vec<u8>) {
    let eeg_req = EegAcqRequest {
      enable: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_req),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn get_leadoff_config() -> (u32, Vec<u8>) {
    let eeg_req = EegAcqRequest {
      mode_req: Some(BoolValue { value: true }),
      config_req: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_req),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  // pub fn run_next_leadoff_chek(chip: i32, ac_freq: i32, current: i32) -> (u32, Vec<u8>) {
  //   let leadoff_config = EegLeadOffConfig {
  //     chip,
  //     ac_freq,
  //     current,
  //     ..Default::default()
  //   };
  //   let eeg_req = EegAcqRequest {
  //     lead_off: Some(leadoff_config),
  //     // enable: Some(BoolValue { value: true }),
  //     ..Default::default()
  //   };

  //   let msg = AppMain {
  //     msg_id: gen_msg_id(),
  //     eeg: Some(eeg_req),
  //     ..Default::default()
  //   };
  //   encode_app_to_mcu(msg)
  // }

  pub fn get_eeg_mode() -> (u32, Vec<u8>) {
    let eeg_req = EegAcqRequest {
      mode_req: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_req),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn get_eeg_config() -> (u32, Vec<u8>) {
    let eeg_acq_request = EegAcqRequest {
      mode_req: Some(BoolValue { value: true }),
      config_req: Some(BoolValue { value: true }),
      lead_off_req: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  // 1 disable数据流
  // 2 设置EEG配置
  pub fn set_eeg_config(sr: i32, gain: i32, signal: i32) -> (u32, Vec<u8>) {
    let eeg_config = EegConfig {
      freq: sr,
      gain,
      source: signal,
    };
    let eeg_req = EegAcqRequest {
      config: Some(eeg_config),
      enable: Some(BoolValue { value: false }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_req),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }
  pub fn enable_eeg_stream() -> (u32, Vec<u8>) {
    let eeg_acq_request = EegAcqRequest {
      enable: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  // 1 切换到正常工作模式
  // 2 启动数据流
  pub fn start_eeg_stream() -> (u32, Vec<u8>) {
    let eeg_acq_request = EegAcqRequest {
      mode: EegMode::Normal as i32,
      enable: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn stop_eeg_stream() -> (u32, Vec<u8>) {
    let eeg_acq_request = EegAcqRequest {
      enable: Some(BoolValue { value: false }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      eeg: Some(eeg_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn get_imu_config() -> (u32, Vec<u8>) {
    let imu_acq_request = ImuAcqRequest {
      config_req: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      imu: Some(imu_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn set_imu_config(sample_rate: i32) -> (u32, Vec<u8>) {
    let imu_config = ImuConfig {
      freq: sample_rate,
      ..Default::default()
    };

    let imu_acq_request = ImuAcqRequest {
      config: Some(imu_config),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      imu: Some(imu_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn start_imu_stream() -> (u32, Vec<u8>) {
    let imu_acq_request = ImuAcqRequest {
      enable: Some(BoolValue { value: true }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      imu: Some(imu_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn stop_imu_stream() -> (u32, Vec<u8>) {
    let imu_acq_request = ImuAcqRequest {
      enable: Some(BoolValue { value: false }),
      ..Default::default()
    };

    let msg = AppMain {
      msg_id: gen_msg_id(),
      imu: Some(imu_acq_request),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn get_device_info() -> (u32, Vec<u8>) {
    let msg = AppMain {
      msg_id: gen_msg_id(),
      device_info_req: Some(BoolValue { value: true }),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn get_battery_level() -> (u32, Vec<u8>) {
    let msg = AppMain {
      msg_id: gen_msg_id(),
      hw_info_req: Some(BoolValue { value: true }),
      ..Default::default()
    };
    encode_app_to_mcu(msg)
  }

  pub fn get_ble_device_info() -> (u32, Vec<u8>) {
    let msg = AppBle {
      msg_id: gen_msg_id(),
      device_info_req: Some(BoolValue { value: true }),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  pub fn set_ble_device_info(model: String, sn: String, _mac: Vec<u8>) -> (u32, Vec<u8>) {
    // mac 暂未使用
    let config = DeviceInfoConfig {
      model,
      sn,
      ..Default::default()
    };
    let msg = AppBle {
      msg_id: gen_msg_id(),
      device_info: Some(config),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  pub fn get_wifi_status() -> (u32, Vec<u8>) {
    let msg = AppBle {
      msg_id: gen_msg_id(),
      wifi_status_req: Some(BoolValue { value: true }),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  pub fn get_wifi_config() -> (u32, Vec<u8>) {
    let msg = AppBle {
      msg_id: gen_msg_id(),
      wifi_config_req: Some(BoolValue { value: true }),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  /// SSID， 最大长度为32
  /// 密码， 最小长度8，最大长度32。当security类型为NONE时，密码为空。
  pub fn set_wifi_config(
    bandwidth_40mhz: bool,
    security: i32,
    ssid: String,
    password: String,
  ) -> (u32, Vec<u8>) {
    let config = WiFiConfig {
      band_40mhz: Some(UInt32Value {
        value: if bandwidth_40mhz { 1 } else { 0 },
      }),
      wpa_config: Some(WpaConfig {
        security,
        ssid,
        password,
      }),
    };
    let msg = AppBle {
      msg_id: gen_msg_id(),
      wifi_config: Some(config),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  pub fn start_dfu(file_size: u32, file_md5: String, file_sha256: String) -> (u32, Vec<u8>) {
    let ota_cfg = OtaConfig {
      cmd: ota_config::Cmd::OtaStart as i32,
      file_size,
      file_md5,
      file_sha256,
      ..Default::default()
    };
    let msg = AppBle {
      msg_id: gen_msg_id(),
      ota_cfg: Some(ota_cfg),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  pub fn send_dfu_data(offset: u32, data: Vec<u8>, finished: bool) -> (u32, Vec<u8>) {
    let ota_cfg = OtaConfig {
      ota_data: Some(OtaData {
        offset,
        data,
        finished,
      }),
      ..Default::default()
    };
    let msg = AppBle {
      msg_id: gen_msg_id(),
      ota_cfg: Some(ota_cfg),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }

  pub fn send_dfu_reboot() -> (u32, Vec<u8>) {
    let ota_cfg = OtaConfig {
      cmd: ota_config::Cmd::OtaReboot as i32,
      ..Default::default()
    };
    let msg = AppBle {
      msg_id: gen_msg_id(),
      ota_cfg: Some(ota_cfg),
      ..Default::default()
    };
    encode_app_to_ble(msg)
  }
}
