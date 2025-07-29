use parking_lot::RwLock;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use pyo3_stub_gen::derive::*;
crate::cfg_import_logging!();

lazy_static::lazy_static! {
  static ref ON_MSG_RESP: RwLock<Option<PyObject>> = RwLock::new(None);
  static ref ON_EEG_DATA: RwLock<Option<PyObject>> = RwLock::new(None);
  static ref ON_IMU_DATA: RwLock<Option<PyObject>> = RwLock::new(None);
  static ref ON_IMP_DATA: RwLock<Option<PyObject>> = RwLock::new(None);
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn set_msg_resp_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_MSG_RESP.write();
  *cb = Some(func.into());
  Ok(())
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn set_imp_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_IMP_DATA.write();
  *cb = Some(func.into());
  Ok(())
}

pub fn unresister_imp_data_callback() {
  let mut cb = ON_IMP_DATA.write();
  *cb = None;
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn set_eeg_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_EEG_DATA.write();
  *cb = Some(func.into());
  Ok(())
}

#[gen_stub_pyfunction]
#[pyfunction]
pub fn set_imu_data_callback(_py: Python, func: Py<PyAny>) -> PyResult<()> {
  let mut cb = ON_IMU_DATA.write();
  *cb = Some(func.into());
  Ok(())
}

pub fn is_registered_imp_data() -> bool {
  ON_IMP_DATA.read().is_some()
}

pub fn is_registered_eeg_data() -> bool {
  ON_EEG_DATA.read().is_some()
}

pub fn is_registered_imu_data() -> bool {
  ON_IMU_DATA.read().is_some()
}

pub fn is_registered_msg_resp() -> bool {
  ON_MSG_RESP.read().is_some()
}

pub fn run_msg_resp_callback(device_id: String, resp: String) {
  let cb = ON_MSG_RESP.read();
  if let Some(ref cb) = *cb {
    Python::with_gil(|py| {
      let _ = cb.call1(py, (device_id, resp));
    });
  }
}

pub fn run_eeg_data_callback(data: Vec<u8>) {
  Python::with_gil(|py| {
    let cb = ON_EEG_DATA.read();
    if let Some(ref cb) = *cb {
      let args = PyTuple::new(py, &[data]).unwrap();
      match cb.call1(py, args) {
        Ok(_) => {}
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
      }
    }
  });
}

pub fn run_impedance_callback(chip: u8, impedance_values: Vec<f32>) {
  let cb = ON_IMP_DATA.read();
  if let Some(ref cb) = *cb {
    Python::with_gil(|py| {
      let _ = cb.call1(py, (chip, impedance_values));
    });
  }
}
