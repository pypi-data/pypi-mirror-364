use super::py_tcp_client::ECapClient;
use crate::ble::lib::ble_write_value;
use crate::data_handler::afe_handler::parse_32ch_eeg_data;
use crate::data_handler::enums::*;
use crate::data_handler::fft::*;
use crate::data_handler::filter;
use crate::data_handler::filter::*;
use crate::eeg_cap::data::*;
use crate::proto::eeg_cap::enums::*;
use crate::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use crate::utils::mdns::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3_async_runtimes::tokio::future_into_py;

crate::cfg_import_logging!();

#[pymodule]
pub fn mod_ecap(parent: &Bound<'_, PyModule>) -> PyResult<()> {
  let py = parent.py();
  let sub = PyModule::new(py, "ecap")?;
  parent.add_submodule(&sub)?;

  sub.add_class::<ECapClient>()?;

  // enums
  sub.add_class::<EegSampleRate>()?;
  sub.add_class::<EegSignalGain>()?;
  sub.add_class::<EegSignalSource>()?;
  sub.add_class::<ImuSampleRate>()?;
  sub.add_class::<WiFiSecurity>()?;
  sub.add_class::<LeadOffChip>()?;
  sub.add_class::<LeadOffFreq>()?;
  sub.add_class::<LeadOffCurrent>()?;

  // functions
  sub.add_function(wrap_pyfunction!(start_scan, &sub)?)?;
  sub.add_function(wrap_pyfunction!(stop_scan, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_cfg, &sub)?)?;
  sub.add_function(wrap_pyfunction!(clear_eeg_buffer, &sub)?)?;
  sub.add_function(wrap_pyfunction!(clear_imu_buffer, &sub)?)?;
  sub.add_function(wrap_pyfunction!(clear_imp_eeg_buffers, &sub)?)?;
  sub.add_function(wrap_pyfunction!(get_eeg_buffer, &sub)?)?;
  // sub.add_function(wrap_pyfunction!(get_imp_buffer, &sub)?)?;
  sub.add_function(wrap_pyfunction!(get_imu_buffer, &sub)?)?;
  sub.add_function(wrap_pyfunction!(parse_eeg_data, &sub)?)?;
  sub.add_function(wrap_pyfunction!(calculate_fft_data, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_impendance_filter, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_impendance_sosfiltfilt, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_eeg_filter, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_eeg_sosfiltfilt, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_lowpass_filter, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_highpass_filter, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_bandpass_filter, &sub)?)?;
  sub.add_function(wrap_pyfunction!(apply_bandstop_filter, &sub)?)?;

  // BLE commands
  sub.add_function(wrap_pyfunction!(get_ble_device_info, &sub)?)?;
  sub.add_function(wrap_pyfunction!(get_wifi_config, &sub)?)?;
  sub.add_function(wrap_pyfunction!(get_wifi_status, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_ble_device_info, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_wifi_config, &sub)?)?;

  Ok(())
}

use pyo3_stub_gen::derive::*;
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
#[pyo3(signature = (with_sn=None))]
pub fn start_scan(py: Python, with_sn: Option<String>) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async {
    match mdns_start_scan(with_sn) {
      Ok((addr, port)) => Ok((addr.to_string(), port)),
      Err(e) => Err(PyRuntimeError::new_err(format!(
        "Failed to scan for mDNS service: {}",
        e
      ))),
    }
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn stop_scan(py: Python) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let _ = mdns_stop_scan();
    Ok(())
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn get_ble_device_info(py: Python, id: String) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let (msg_id, cmd) = eeg_cap_msg_builder::get_ble_device_info();
    ble_write_value(&id, &cmd, true).await;
    Ok(msg_id)
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn get_wifi_config(py: Python, id: String) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let (msg_id, cmd) = eeg_cap_msg_builder::get_wifi_config();
    ble_write_value(&id, &cmd, true).await;
    Ok(msg_id)
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn get_wifi_status(py: Python, id: String) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let (msg_id, cmd) = eeg_cap_msg_builder::get_wifi_status();
    ble_write_value(&id, &cmd, true).await;
    Ok(msg_id)
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn set_ble_device_info(
  py: Python,
  id: String,
  model: String,
  sn: String,
) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let (msg_id, cmd) =
      eeg_cap_msg_builder::set_ble_device_info(model, sn, vec![0x00, 0x00, 0x00, 0x00, 0x00, 0x00]);
    ble_write_value(&id, &cmd, true).await;
    Ok(msg_id)
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn set_wifi_config(
  py: Python,
  id: String,
  enable: bool, // bandwidth_40mhz
  security: WiFiSecurity,
  ssid: String,
  password: String,
) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let (msg_id, cmd) =
      eeg_cap_msg_builder::set_wifi_config(enable, security as i32, ssid, password);
    ble_write_value(&id, &cmd, true).await;
    Ok(msg_id)
  })
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn parse_eeg_data(data: Vec<u8>, gain: EegSignalGain) -> PyResult<Vec<f64>> {
  Ok(parse_32ch_eeg_data(&data, gain as i32))
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn calculate_fft_data(data: Vec<f64>, fs: f64) -> PyResult<(Vec<f64>, Vec<f64>)> {
  Ok(calculate_fft(&data, fs))
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn set_env_noise_cfg(noise_type: NoiseTypes, fs: f64) {
  filter::set_env_noise_cfg(noise_type, fs);
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn remove_env_noise(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::remove_env_noise(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn remove_env_noise_sosfiltfilt(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::remove_env_noise_sosfiltfilt(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn remove_env_noise_notch(data: Vec<f64>, channel: usize) -> Vec<f64> {
  filter::remove_env_noise_notch(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_impendance_filter(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_impendance_filter(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_impendance_sosfiltfilt(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_impendance_sosfiltfilt(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_eeg_filter(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_eeg_filter(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_eeg_sosfiltfilt(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_eeg_sosfiltfilt(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_lowpass_filter(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_lowpass_sosfiltfilt(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_highpass_filter(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_highpass_sosfiltfilt(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_bandpass_filter(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_bandpass_sosfiltfilt(data, channel)
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_bandstop_filter(data: Vec<f64>, channel: usize) -> Vec<f64> {
  perform_bandstop_sosfiltfilt(data, channel)
}
// #[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
// #[pyfunction]
// pub fn apply_highpass_filter(data: Vec<f32>, order: usize, high_cut: f32, fs: f32) -> Vec<f32> {
//   apply_highpass(data, order, high_cut, fs)
// }
// #[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
// #[pyfunction]
// pub fn apply_lowpass_filter(data: Vec<f32>, order: usize, low_cut: f32, fs: f32) -> Vec<f32> {
//   apply_lowpass(data, order, low_cut, fs)
// }
// #[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
// #[pyfunction]
// pub fn apply_bandpass_filter(
//   data: Vec<f32>,
//   order: usize,
//   low_cut: f32,
//   high_cut: f32,
//   fs: f32,
// ) -> Vec<f32> {
//   apply_bandpass(data, order, low_cut, high_cut, fs)
// }
// #[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
// #[pyfunction]
// pub fn apply_bandstop_filter(
//   data: Vec<f32>,
//   order: usize,
//   low_cut: f32,
//   high_cut: f32,
//   fs: f32,
// ) -> Vec<f32> {
//   apply_bandstop(data, order, low_cut, high_cut, fs)
// }
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ecap")]
#[pyfunction]
pub fn apply_downsampling(
  data: Vec<f64>,
  window_size: usize,
  operation: DownsamplingOperations,
) -> Vec<f64> {
  perform_downsampling(data, window_size, operation)
}
