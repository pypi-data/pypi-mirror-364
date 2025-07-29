use super::callback as cb;
use crate::data_handler::enums::*;
use crate::data_handler::filter_bc::*;
use crate::proto::enums::MsgType;
use crate::python::py_filter::*;
use crate::python::py_msg_parser::*;
use crate::python::py_tcp_client::*;
use crate::utils::logging::LogLevel;
use pyo3::prelude::*;
crate::cfg_import_logging!();

#[pymodule]
fn main_mod(m: &Bound<'_, PyModule>) -> PyResult<()> {
  pyo3_log::init();
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );

  // enums
  m.add_class::<LogLevel>()?;
  m.add_class::<MsgType>()?;
  m.add_class::<NoiseTypes>()?;
  m.add_class::<DownsamplingOperations>()?;

  // structs
  m.add_class::<MessageParser>()?;
  m.add_class::<MessageStream>()?;
  m.add_class::<NotchFilter>()?;
  m.add_class::<SosFilter>()?;
  m.add_class::<PyTcpClient>()?;
  m.add_class::<PyTcpStream>()?;
  // m.add_class::<PySerialStream>()?;

  // filters
  m.add_class::<LowPassFilter>()?;
  m.add_class::<HighPassFilter>()?;
  m.add_class::<BandPassFilter>()?;
  m.add_class::<BandStopFilter>()?;

  // functions
  // m.add_function(wrap_pyfunction!(get_bytes, m)?)?;
  // m.add_function(wrap_pyfunction!(get_sdk_version, m)?)?;

  use super::eeg_cap::py_mod_eeg_cap::*;
  m.add_function(wrap_pyfunction!(apply_downsampling, m)?)?;
  m.add_function(wrap_pyfunction!(set_env_noise_cfg, m)?)?;
  m.add_function(wrap_pyfunction!(remove_env_noise, m)?)?;
  m.add_function(wrap_pyfunction!(remove_env_noise_notch, m)?)?;
  m.add_function(wrap_pyfunction!(remove_env_noise_sosfiltfilt, m)?)?;
  // m.add_function(wrap_pyfunction!(available_usb_ports, m)?)?;
  m.add_function(wrap_pyfunction!(cb::set_msg_resp_callback, m)?)?;
  m.add_function(wrap_pyfunction!(cb::set_eeg_data_callback, m)?)?;
  m.add_function(wrap_pyfunction!(cb::set_imu_data_callback, m)?)?;
  m.add_function(wrap_pyfunction!(cb::set_imp_data_callback, m)?)?;

  // Register child module
  #[cfg(feature = "eeg-cap")]
  super::eeg_cap::py_mod_eeg_cap::mod_ecap(m)?;

  #[cfg(feature = "ble")]
  super::ble::py_mod_ble::mod_ble(m)?;

  Ok(())
}

// use pyo3_stub_gen::derive::*;
// #[gen_stub_pyfunction]
// #[pyfunction]
// pub fn get_sdk_version() -> PyResult<String> {
//   Ok(StarkSDK::get_sdk_version())
// }

// Define a function to gather stub information.
pyo3_stub_gen::define_stub_info_gatherer!(stub_info);
