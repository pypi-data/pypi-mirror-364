use crate::ble::core as ble;
use crate::ble::enums::*;
use crate::ble::lib;
use crate::ble::structs::*;
use parking_lot::Mutex;
use pyo3::prelude::*;
use pyo3::types::*;
use pyo3_async_runtimes::tokio::future_into_py;
use uuid::Uuid;

crate::cfg_import_logging!();

lazy_static::lazy_static! {
  static ref ADAPTER_STATE_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref DEVICE_DISCOVERED_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref SCAN_RESULT_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref CONNECTION_STATE_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref RECEIVED_DATA_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref BATTERY_LEVEL_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
  static ref DEVICE_INFO_CALLBACK: Mutex<Option<PyObject>> = Mutex::new(None);
}

#[pymodule]
pub fn mod_ble(parent: &Bound<'_, PyModule>) -> PyResult<()> {
  let py = parent.py();
  let sub = PyModule::new(py, "ble")?;
  parent.add_submodule(&sub)?;

  // enums
  sub.add_class::<CentralAdapterState>()?;
  sub.add_class::<ConnectionState>()?;

  // functions
  sub.add_function(wrap_pyfunction!(init_adapter, &sub)?)?;
  sub.add_function(wrap_pyfunction!(start_scan, &sub)?)?;
  sub.add_function(wrap_pyfunction!(stop_scan, &sub)?)?;
  sub.add_function(wrap_pyfunction!(connect, &sub)?)?;
  sub.add_function(wrap_pyfunction!(disconnect, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_adapter_state_callback, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_device_discovered_callback, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_scan_result_callback, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_connection_state_callback, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_received_data_callback, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_battery_level_callback, &sub)?)?;
  sub.add_function(wrap_pyfunction!(set_device_info_callback, &sub)?)?;
  Ok(())
}

use pyo3_stub_gen::derive::*;
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
pub fn init_adapter(py: Python) -> PyResult<Bound<PyAny>> {
  future_into_py(py, async move {
    let _ = lib::initialize_central_adapter().await;
    Ok(())
  })
}

#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
#[pyo3(signature = (with_uuids=None))]
fn start_scan(with_uuids: Option<Vec<String>>) {
  let uuids = with_uuids
    .map(|vec| {
      vec
        .into_iter()
        .map(|e| Uuid::parse_str(&e).unwrap())
        .collect()
    })
    .unwrap_or_else(Vec::new);

  let _ = lib::start_scan_with_uuids(uuids);
}

#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
pub fn stop_scan() {
  let _ = lib::stop_scan();
}

#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
pub fn connect(_py: Python, id: String) -> PyResult<Bound<PyAny>> {
  future_into_py(_py, async move {
    let _ = lib::connect_ble(&id).await;
    Ok(())
  })
}

#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
pub fn disconnect(_py: Python, id: String) -> PyResult<Bound<PyAny>> {
  future_into_py(_py, async move {
    let _ = lib::disconnect_ble(&id).await;
    Ok(())
  })
}

#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_adapter_state_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = ADAPTER_STATE_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_adapter_state_callback(Box::new(|state| {
    let state = (state as u8).into();
    let _ = run_central_state_callback(state);
  }));
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_device_discovered_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = DEVICE_DISCOVERED_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_device_discovered_callback(Box::new(|device| {
    let _ = run_device_discovered_callback(device);
  }));
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_scan_result_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = SCAN_RESULT_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_scan_result_callback(Box::new(|device| {
    let _ = run_scan_result_callback(device);
  }));
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_connection_state_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = CONNECTION_STATE_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_connection_state_callback(Box::new(|id, state| {
    let _ = run_connection_state_callback(id, state);
  }));
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_received_data_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = RECEIVED_DATA_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_received_data_callback(Box::new(|id, data| {
    let _ = run_received_data_callback(id, data);
  }));
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_battery_level_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = BATTERY_LEVEL_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_battery_level_callback(Box::new(|id, level| {
    let _ = run_battery_level_callback(id, level);
  }));
}
#[gen_stub_pyfunction(module = "bc_ecap_sdk.main_mod.ble")]
#[pyfunction]
fn set_device_info_callback(_py: Python, func: Py<PyAny>) {
  let mut cb = DEVICE_INFO_CALLBACK.lock();
  *cb = Some(func.into());
  ble::set_device_info_callback(Box::new(|id, info| {
    let _ = run_device_info_callback(id, info);
  }));
}

fn run_central_state_callback(state: CentralAdapterState) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = ADAPTER_STATE_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      let args = PyTuple::new(py, &[state as u8]).unwrap();
      match cb.call1(py, args) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}

fn run_device_discovered_callback(device: ScanResult) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = DEVICE_DISCOVERED_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      match cb.call1(py, (device.id.clone(), device)) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}

fn run_scan_result_callback(device: ScanResult) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = SCAN_RESULT_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      match cb.call1(py, (device.id.clone(), device)) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}

fn run_connection_state_callback(id: String, state: ConnectionState) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = CONNECTION_STATE_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      match cb.call1(py, (id, state as u8)) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}

fn run_received_data_callback(id: String, data: Vec<u8>) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = RECEIVED_DATA_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      match cb.call1(py, (id, data)) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}

fn run_battery_level_callback(id: String, level: u8) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = BATTERY_LEVEL_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      match cb.call1(py, (id, level)) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}

fn run_device_info_callback(id: String, info: BLEDeviceInfo) -> PyResult<()> {
  Python::with_gil(|py| {
    let cb = DEVICE_INFO_CALLBACK.lock();
    if let Some(ref cb) = *cb {
      match cb.call1(py, (id, info)) {
        Err(e) => {
          error!("Error calling callback: {:?}", e);
        }
        _ => {}
      }
    } else {
      warn!("No callback set");
    }
    Ok(())
  })
}
