use crate::proto::{enums::MsgType, msg_parser::*};
use futures::StreamExt;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::*;
use pyo3_async_runtimes::tokio::future_into_py;
use pyo3_stub_gen::derive::*;
use std::pin::Pin;
use std::sync::Arc;
use tokio::sync::Mutex;

crate::cfg_import_logging!();

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod")]
#[derive(Clone)]
pub struct MessageParser {
  pub inner: Parser,
  pub stream: MessageStream,
}

#[gen_stub_pymethods]
#[pymethods]
impl MessageParser {
  #[new]
  pub fn py_new(device_id: String, msg_type: MsgType) -> Self {
    let parser = Parser::new(device_id, msg_type);
    let stream = parser.message_stream();
    MessageParser {
      inner: parser,
      stream: MessageStream {
        inner: Arc::new(Mutex::new(stream)),
      },
    }
  }

  pub fn receive_data(&mut self, data: Vec<u8>) {
    // trace!("Received data: {:?}", data);
    self.inner.receive_data(&data);
  }
}

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod.ecap")]
#[derive(Clone)]
pub struct MessageStream {
  inner: ArcMutexStream,
}

#[gen_stub_pymethods]
#[pymethods]
impl MessageStream {
  fn __aiter__(slf: PyRef<Self>) -> PyRef<Self> {
    slf
  }

  fn __anext__(slf: PyRefMut<Self>) -> PyResult<PyObject> {
    let stream = Arc::clone(&slf.inner);
    let future = async move {
      let mut stream = stream.lock().await;
      let mut pin_stream = Pin::new(&mut *stream);
      match pin_stream.next().await {
        Some(Ok((_device_id, message))) => {
          let json = serde_json::to_vec(&message).unwrap();
          Python::with_gil(|py| Ok::<Py<PyAny>, PyErr>(PyBytes::new(py, &json).into()))
        }
        // Err(RecvError::Lagged(n)) => println!("Channel lagged by {}", n),
        Some(Err(e)) => Python::with_gil(|_| {
          let py_err = PyErr::new::<PyRuntimeError, _>(format!("{:?}", e));
          Err(py_err)
        }),
        None => Python::with_gil(|_| {
          let py_err = PyErr::new::<PyRuntimeError, _>("Stream ended unexpectedly");
          Err(py_err)
        }),
      }
    };
    future_into_py(slf.py(), future).map(|bound| bound.into())
  }
}
