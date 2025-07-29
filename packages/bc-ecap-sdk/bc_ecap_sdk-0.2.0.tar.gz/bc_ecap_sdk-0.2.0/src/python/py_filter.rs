// use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
// use pyo3::types::*;
// use pyo3_async_runtimes::tokio::future_into_py;
use crate::data_handler::filter_sos::*;

use crate::data_handler::filter_sos::design_notch_filter;
use pyo3_stub_gen::derive::*;
use sci_rs::signal::filter::design::Sos;
use sci_rs::signal::filter::sosfiltfilt_dyn;

crate::cfg_import_logging!();

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod")]
#[derive(Debug)]
pub struct NotchFilter {
  pub sos_filter: Vec<Sos<f64>>,
}

#[gen_stub_pymethods]
#[pymethods]
impl NotchFilter {
  #[new]
  pub fn py_new(f0: f64, fs: f64, quality: f64) -> Self {
    let sos_filter = design_notch_filter(f0, fs, quality);
    NotchFilter { sos_filter }
  }

  pub fn apply(&self, signal: Vec<f64>) -> PyResult<Vec<f64>> {
    Ok(sosfiltfilt_dyn(signal.iter().copied(), &self.sos_filter))
  }
}

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod")]
#[derive(Debug)]
pub struct SosFilter {
  pub sos_filter: Vec<Sos<f64>>,
}

#[gen_stub_pymethods]
#[pymethods]
impl SosFilter {
  #[staticmethod]
  pub fn create_low_pass(order: u32, fs: f64, lowcut: f64) -> Self {
    let sos_filter = sos_butter_lowpass(order as usize, fs, lowcut);
    SosFilter { sos_filter }
  }

  #[staticmethod]
  pub fn create_high_pass(order: u32, fs: f64, highcut: f64) -> Self {
    let sos_filter = sos_butter_highpass(order as usize, fs, highcut);
    SosFilter { sos_filter }
  }

  #[staticmethod]
  pub fn create_band_pass(order: u32, fs: f64, lowcut: f64, highcut: f64) -> Self {
    let sos_filter = sos_butter_bandpass(order as usize, fs, lowcut, highcut);
    SosFilter { sos_filter }
  }

  #[staticmethod]
  pub fn create_band_stop(order: u32, fs: f64, lowcut: f64, highcut: f64) -> Self {
    let sos_filter = sos_butter_bandstop(order as usize, fs, lowcut, highcut);
    SosFilter { sos_filter }
  }

  pub fn apply(&self, signal: Vec<f64>) -> PyResult<Vec<f64>> {
    Ok(sosfiltfilt_dyn(signal.iter().copied(), &self.sos_filter))
  }
}
