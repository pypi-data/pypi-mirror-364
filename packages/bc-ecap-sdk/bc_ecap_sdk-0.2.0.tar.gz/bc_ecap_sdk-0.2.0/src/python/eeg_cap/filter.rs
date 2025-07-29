use crate::data_handler::filter_bc::*;
use pyo3::prelude::*;
use pyo3_stub_gen::derive::*;

#[gen_stub_pymethods]
#[pymethods]
impl LowPassFilter {
  #[new]
  pub fn create(fs: f64, fl: f64) -> Self {
    LowPassFilter::new(4, fs, fl)
  }

  pub fn filter(&mut self, iter: Vec<f64>) -> Vec<f64> {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }
}

#[gen_stub_pymethods]
#[pymethods]
impl HighPassFilter {
  #[new]
  pub fn create(fs: f64, fu: f64) -> Self {
    HighPassFilter::new(4, fs, fu)
  }

  pub fn filter(&mut self, iter: Vec<f64>) -> Vec<f64> {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }
}

#[gen_stub_pymethods]
#[pymethods]
impl BandPassFilter {
  #[new]
  pub fn create(fs: f64, fl: f64, fu: f64) -> Self {
    BandPassFilter::new(4, fs, fl, fu)
  }

  pub fn filter(&mut self, iter: Vec<f64>) -> Vec<f64> {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }
}

#[gen_stub_pymethods]
#[pymethods]
impl BandStopFilter {
  #[new]
  pub fn create(fs: f64, fl: f64, fu: f64) -> Self {
    BandStopFilter::new(4, fs, fl, fu)
  }

  pub fn filter(&mut self, iter: Vec<f64>) -> Vec<f64> {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }
}

//   pub fn get_device_info<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
//     let (msg_id, data) = eeg_cap_msg_builder::get_device_info();
//     self.send_command(py, msg_id, &data)
//   }
