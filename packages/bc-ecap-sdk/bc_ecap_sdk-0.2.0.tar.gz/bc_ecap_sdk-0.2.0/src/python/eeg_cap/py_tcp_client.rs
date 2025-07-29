use crate::eeg_cap::callback::*;
use crate::eeg_cap::data::*;
use crate::proto::eeg_cap::enums::*;
use crate::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use crate::python::callback::*;
use crate::python::py_msg_parser::MessageParser;
use crate::python::py_tcp_client::PyTcpClient;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::*;
use pyo3_async_runtimes::tokio::future_into_py;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
crate::cfg_import_logging!();

use pyo3_stub_gen::derive::*;
#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod.ecap")]
pub struct ECapClient {
  tcp: PyTcpClient,
}

#[gen_stub_pymethods]
#[pymethods]
impl ECapClient {
  #[new]
  pub fn new(addr: String, port: u16) -> Self {
    ECapClient {
      tcp: PyTcpClient::new(addr, port),
    }
  }

  pub fn start_data_stream<'a>(
    &self,
    py: Python<'a>,
    py_parser: PyRefMut<MessageParser>,
  ) -> PyResult<Bound<'a, PyAny>> {
    self.tcp.start_data_stream(py, py_parser)
  }

  pub fn send_command<'a>(
    &self,
    py: Python<'a>,
    msg_id: u32,
    data: Vec<u8>,
  ) -> PyResult<Bound<'a, PyAny>> {
    self.tcp.send_command(py, msg_id, data)
  }

  pub fn get_device_info<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::get_device_info();
    self.send_command(py, msg_id, data)
  }

  pub fn start_leadoff_check<'a>(
    &self,
    py: Python<'a>,
    loop_check: bool,
    freq: LeadOffFreq,
    current: LeadOffCurrent,
  ) -> PyResult<Bound<'a, PyAny>> {
    save_lead_off_cfg(loop_check, freq, current);

    let client_arc = self.tcp.inner.clone();
    set_next_leadoff_cb(Box::new(move |chip, freq, current| {
      let client_arc = client_arc.clone();
      Python::with_gil(move |_| {
        tokio::spawn(async move {
          let client = client_arc.lock().await;
          let (msg_id, data) = eeg_cap_msg_builder::switch_and_start_leadoff_check(
            chip as i32,
            freq as i32,
            current as i32,
          );
          match client.send_command_data(msg_id, &data).await {
            Ok(_) => Ok(msg_id),
            Err(e) => Err(PyRuntimeError::new_err(format!(
              "Failed to send command to TCP server: {}",
              e
            ))),
          }
        });
      });
    }));
    let (msg_id, data) = eeg_cap_msg_builder::switch_and_start_leadoff_check(
      LeadOffChip::Chip1 as i32,
      freq as i32,
      current as i32,
    );
    self.send_command(py, msg_id, data)
  }

  pub fn stop_leadoff_check<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    unresister_imp_data_callback();
    let (msg_id, data) = eeg_cap_msg_builder::stop_leadoff_check();
    self.send_command(py, msg_id, data)
  }

  pub fn start_eeg_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::start_eeg_stream();
    self.send_command(py, msg_id, data)
  }

  pub fn stop_eeg_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::stop_eeg_stream();
    self.send_command(py, msg_id, data)
  }

  pub fn start_imu_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::start_imu_stream();
    self.send_command(py, msg_id, data)
  }

  pub fn stop_imu_stream<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::stop_imu_stream();
    self.send_command(py, msg_id, data)
  }

  pub fn get_eeg_config<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::get_eeg_config();
    self.send_command(py, msg_id, data)
  }

  pub fn get_imu_config<'a>(&self, py: Python<'a>) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::get_imu_config();
    self.send_command(py, msg_id, data)
  }

  pub fn set_eeg_config<'a>(
    &self,
    py: Python<'a>,
    fs: EegSampleRate,
    gain: EegSignalGain,
    signal: EegSignalSource,
  ) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::set_eeg_config(fs as i32, gain as i32, signal as i32);
    self.send_command(py, msg_id, data)
  }

  pub fn set_imu_config<'a>(
    &self,
    py: Python<'a>,
    fs: ImuSampleRate,
  ) -> PyResult<Bound<'a, PyAny>> {
    let (msg_id, data) = eeg_cap_msg_builder::set_imu_config(fs as i32);
    self.send_command(py, msg_id, data)
  }
}

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod")]
pub struct PyTcpStream {
  rx: Arc<Mutex<broadcast::Receiver<Vec<u8>>>>,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyTcpStream {
  fn __aiter__(slf: PyRef<Self>) -> PyRef<Self> {
    slf
  }

  fn __anext__(slf: PyRefMut<Self>) -> PyResult<PyObject> {
    let rx_arc = Arc::clone(&slf.rx);
    let future = async move {
      let mut rx = rx_arc.lock().await;
      if let Ok(data) = rx.recv().await {
        debug!("Received data: {:?}", data);
        Python::with_gil(|py| Ok::<Py<PyAny>, PyErr>(PyBytes::new(py, &data).into()))
      } else {
        Python::with_gil(|_| {
          let py_err = PyErr::new::<PyRuntimeError, _>("Stream ended unexpectedly");
          Err(py_err)
        })
      }
    };
    future_into_py(slf.py(), future).map(|bound| bound.into())
  }
}
