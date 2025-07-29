use crate::data_handler::enums::*;
use crate::data_handler::filter;
use crate::data_handler::filter::*;
use crate::data_handler::filter_bc::*;
use crate::data_handler::filter_sos::SosFilter;
use crate::eeg_cap::data::*;
use crate::proto::eeg_cap::enums::*;
use crate::proto::eeg_cap::msg_builder::*;
use crate::wasm::wasm::build_message;
use wasm_bindgen::prelude::*;

crate::cfg_import_logging!();

#[wasm_bindgen]
pub fn get_device_info() -> JsValue {
  build_message(eeg_cap_msg_builder::get_device_info)
}

#[wasm_bindgen]
pub fn start_eeg_stream() -> JsValue {
  build_message(eeg_cap_msg_builder::start_eeg_stream)
}

#[wasm_bindgen]
pub fn stop_eeg_stream() -> JsValue {
  build_message(eeg_cap_msg_builder::stop_eeg_stream)
}

#[wasm_bindgen]
pub fn get_eeg_data_buffer(take: usize, clean: bool) -> JsValue {
  let data = get_eeg_buffer(take, clean);
  let message = serde_json::to_string(&data).unwrap();
  JsValue::from_str(&message)
}

#[wasm_bindgen]
pub fn get_imu_data_buffer(take: usize, clean: bool) -> JsValue {
  let data = get_imu_buffer(take, clean);
  let message = serde_json::to_string(&data).unwrap();
  JsValue::from_str(&message)
}

#[wasm_bindgen]
pub fn get_eeg_config() -> JsValue {
  build_message(eeg_cap_msg_builder::get_eeg_config)
}

#[wasm_bindgen]
pub fn set_eeg_config(sr: EegSampleRate, gain: EegSignalGain, signal: EegSignalSource) -> JsValue {
  let builder = || eeg_cap_msg_builder::set_eeg_config(sr as i32, gain as i32, signal as i32);
  build_message(builder)
}

#[wasm_bindgen]
pub fn get_leadoff_config() -> JsValue {
  build_message(eeg_cap_msg_builder::get_leadoff_config)
}

// #[wasm_bindgen]
// pub fn run_next_leadoff_chek(chip: LeadOffChip, freq: LeadOffFreq, current: LeadOffCurrent) -> JsValue {
//   let builder = || {
//     eeg_cap_msg_builder::switch_and_start_leadoff_check(chip as i32, freq as i32, current as i32)
//   };
//   build_message(builder)
// }

#[wasm_bindgen]
pub fn start_imu_stream() -> JsValue {
  build_message(eeg_cap_msg_builder::start_imu_stream)
}

#[wasm_bindgen]
pub fn stop_imu_stream() -> JsValue {
  build_message(eeg_cap_msg_builder::stop_imu_stream)
}

#[wasm_bindgen]
pub fn get_imu_config() -> JsValue {
  build_message(eeg_cap_msg_builder::get_imu_config)
}

#[wasm_bindgen]
pub fn set_imu_config(sr: ImuSampleRate) -> JsValue {
  let builder = || eeg_cap_msg_builder::set_imu_config(sr as i32);
  build_message(builder)
}

#[wasm_bindgen]
pub fn get_ble_device_info() -> JsValue {
  build_message(eeg_cap_msg_builder::get_ble_device_info)
}

// DeviceInfo.model max_length:32
// DeviceInfo.sn max_length:32
#[wasm_bindgen]
pub fn set_ble_device_info(model: String, sn: String) -> JsValue {
  if model.len() > 32 {
    return JsValue::from_str("model length must be less than 32");
  }
  if sn.len() > 32 {
    return JsValue::from_str("sn length must be less than 32");
  }
  // if mac.len() != 6 {
  //   return JsValue::from_str("mac length must be 6");
  // }
  let builder = || {
    eeg_cap_msg_builder::set_ble_device_info(model, sn, vec![0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
  };
  build_message(builder)
}

#[wasm_bindgen]
pub fn get_wifi_status() -> JsValue {
  build_message(eeg_cap_msg_builder::get_wifi_status)
}

#[wasm_bindgen]
pub fn get_wifi_config() -> JsValue {
  build_message(eeg_cap_msg_builder::get_wifi_config)
}

// bandwidth_40mhz: 是否使用40Mhz带宽
// SSID， 最大长度为32
// 密码， 最小长度8，最大长度32。当security类型为NONE时，密码为空。
#[wasm_bindgen]
pub fn set_wifi_config(
  bandwidth_40mhz: bool,
  // security: i32,
  security: WiFiSecurity,
  ssid: String,
  password: String,
) -> JsValue {
  if ssid.len() > 32 {
    return JsValue::from_str("ssid length must be less than 32");
  }
  if security == WiFiSecurity::SECURITY_NONE || security == WiFiSecurity::SECURITY_OPEN {
    if !password.is_empty() {
      return JsValue::from_str("password must be empty when security is OPEN or NONE");
    }
  } else {
    if password.len() < 8 {
      return JsValue::from_str("password length must be greater than 8");
    }
    if password.len() > 32 {
      return JsValue::from_str("password length must be less than 32");
    }
  }
  // if let Ok(wifi_security) = WiFiSecurity::try_from(security) {
  //   if wifi_security == WiFiSecurity::SecurityNone || wifi_security == WiFiSecurity::SecurityOpen {
  //     if !password.is_empty() {
  //       return JsValue::from_str("password must be empty when security is OPEN or NONE");
  //     }
  //   } else {
  //     if password.len() < 8 {
  //       return JsValue::from_str("password length must be greater than 8");
  //     }
  //     if password.len() > 32 {
  //       return JsValue::from_str("password length must be less than 32");
  //     }
  //   }
  // } else {
  //   return JsValue::from_str("invalid security type");
  // }
  let builder =
    || eeg_cap_msg_builder::set_wifi_config(bandwidth_40mhz, security as i32, ssid, password);
  build_message(builder)
}

#[wasm_bindgen]
pub fn send_start_dfu(file_size: u32, file_md5: String, file_sha256: String) -> JsValue {
  let builder = || eeg_cap_msg_builder::start_dfu(file_size, file_md5, file_sha256);
  build_message(builder)
}

#[wasm_bindgen]
pub fn send_dfu_data(offset: u32, data: Vec<u8>, finished: bool) -> JsValue {
  let builder = || eeg_cap_msg_builder::send_dfu_data(offset, data, finished);
  build_message(builder)
}

#[wasm_bindgen]
pub fn send_dfu_reboot() -> JsValue {
  build_message(eeg_cap_msg_builder::send_dfu_reboot)
}

#[wasm_bindgen]
pub fn set_env_noise_cfg(noise_type: NoiseTypes, fs: f64) {
  filter::set_env_noise_cfg(noise_type, fs);
}

#[wasm_bindgen]
pub fn remove_env_noise(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::remove_env_noise(data, channel)
}

#[wasm_bindgen]
pub fn remove_env_noise_sosfiltfilt(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::remove_env_noise_sosfiltfilt(data, channel)
}

#[wasm_bindgen]
pub fn remove_env_noise_notch(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::remove_env_noise_notch(data, channel)
}

#[wasm_bindgen]
pub fn set_eeg_filter_cfg(
  high_pass_enabled: bool,
  high_cut: f64,
  low_pass_enabled: bool,
  low_cut: f64,
  band_pass_enabled: bool,
  band_pass_low: f64,
  band_pass_high: f64,
  band_stop_enabled: bool,
  band_stop_low: f64,
  band_stop_high: f64,
  fs: f64,
) {
  let config = EegFilterConfig {
    fs,
    high_pass_enabled,
    low_pass_enabled,
    band_pass_enabled,
    band_stop_enabled,
    high_cut,
    low_cut,
    band_pass_low,
    band_pass_high,
    band_stop_low,
    band_stop_high,
  };

  set_easy_eeg_filter(config);
}

#[wasm_bindgen]
pub fn apply_easy_mode_filters(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::apply_easy_mode_filters(data, channel)
}

#[wasm_bindgen]
pub fn apply_easy_mode_sosfiltfilt(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::apply_easy_mode_sosfiltfilt(data, channel)
}

#[wasm_bindgen]
pub fn sosfiltfilt_highpass(filter: &mut SosFilter, data: Vec<f64>) -> Vec<f64> {
  filter.perform(data)
}

#[wasm_bindgen]
pub fn sosfiltfilt_lowpass(filter: &mut SosFilter, data: Vec<f64>) -> Vec<f64> {
  filter.perform(data)
}

#[wasm_bindgen]
pub fn sosfiltfilt_bandpass(filter: &mut SosFilter, data: Vec<f64>) -> Vec<f64> {
  filter.perform(data)
}

#[wasm_bindgen]
pub fn sosfiltfilt_bandstop(filter: &mut SosFilter, data: Vec<f64>) -> Vec<f64> {
  filter.perform(data)
}

#[wasm_bindgen]
pub fn apply_highpass(filter: &mut HighPassFilter, data: Vec<f64>) -> Vec<f64> {
  filter.process_iter(data)
}

#[wasm_bindgen]
pub fn apply_lowpass(filter: &mut LowPassFilter, data: Vec<f64>) -> Vec<f64> {
  filter.process_iter(data)
}

#[wasm_bindgen]
pub fn apply_bandpass(filter: &mut BandPassFilter, data: Vec<f64>) -> Vec<f64> {
  filter.process_iter(data)
}

#[wasm_bindgen]
pub fn apply_bandstop(filter: &mut BandStopFilter, data: Vec<f64>) -> Vec<f64> {
  filter.process_iter(data)
}
