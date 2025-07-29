use super::py_msg_parser::MessageParser;
use crate::utils::tcp_client::TcpClient;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::*;
use pyo3_async_runtimes::tokio::future_into_py;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
crate::cfg_import_logging!();
use pyo3_stub_gen::derive::*;
#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod")]
pub struct PyTcpClient {
  pub inner: Arc<Mutex<TcpClient>>,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyTcpClient {
  #[new]
  pub fn new(addr: String, port: u16) -> Self {
    let client = TcpClient::new(addr.parse().unwrap(), port);
    PyTcpClient {
      inner: Arc::new(Mutex::new(client)),
    }
  }

  pub fn start_data_stream<'a>(
    &self,
    py: Python<'a>,
    py_parser: PyRefMut<MessageParser>,
  ) -> PyResult<Bound<'a, PyAny>> {
    let mut parser = py_parser.clone();
    let client_arc = self.inner.clone();
    future_into_py(py, async move {
      let mut client = client_arc.lock().await;
      client.start_listen(Box::new(move |data: Vec<u8>| {
        parser.receive_data(data);
      }));

      match client.connect().await {
        Ok(_) => Ok(()),
        Err(e) => Err(PyRuntimeError::new_err(format!(
          "Failed to connect to TCP server: {}",
          e
        ))),
      }
    })
  }

  pub fn send_command<'a>(
    &self,
    py: Python<'a>,
    msg_id: u32,
    data: Vec<u8>,
  ) -> PyResult<Bound<'a, PyAny>> {
    let client_arc = self.inner.clone();
    future_into_py(py, async move {
      let client = client_arc.lock().await;
      match client.send_command_data(msg_id, &data).await {
        Ok(_) => Ok(msg_id),
        Err(e) => Err(PyRuntimeError::new_err(format!(
          "Failed to send command to TCP server: {}",
          e
        ))),
      }
    })
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
