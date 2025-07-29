use crate::eeg_cap::msg_parser::EegData;
use crate::generated::eeg_cap_proto::*;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use serde::{Deserialize, Serialize};

crate::cfg_import_logging!();
use pyo3_stub_gen::derive::*;
#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod.ecap")]
#[derive(Debug, Serialize, Deserialize)]
struct EEGData {
  timestamp: u64,
  sample1: Vec<u8>,
}

#[gen_stub_pymethods]
#[pymethods]
impl EEGData {
  fn new(data: &EegData) -> Self {
    EEGData {
      timestamp,
      gain,
      sample1,
    }
  }

  #[staticmethod]
  fn from_json(py: Python, json_str: &str, gain: i32) -> PyResult<Self> {
    let json_obj: Py<PyDict> = PyDict::from_json(py, json_str)?;
    let sample1 = json_obj
      .get_item("EEGCap")
      .unwrap()
      .get_item("Mcu2App")
      .unwrap()
      .get_item("eeg")
      .unwrap()
      .get_item("data")
      .unwrap()
      .get_item("sample1")
      .unwrap();
    let timestamp = sample1.get_item("timestamp").unwrap().extract::<u64>()?;
    let data = sample1.get_item("data").unwrap().extract::<String>()?;
    let sample1 = base64::decode(data).unwrap();
    Ok(EEGData {
      timestamp,
      gain,
      sample1,
    })
  }

  fn __repr__(&self) -> String {
    format!(
      "EEGData(timestamp={}, sample1={:?})",
      self.timestamp, self.sample1
    )
  }
}

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod.ecap")]
#[derive(Debug, Serialize, Deserialize)]
struct IMUCord {
  cord_x: f32,
  cord_y: f32,
  cord_z: f32,
}

#[gen_stub_pymethods]
#[pymethods]
impl IMUCord {
  #[new]
  fn new(cord_x: f32, cord_y: f32, cord_z: f32) -> Self {
    IMUCord {
      cord_x,
      cord_y,
      cord_z,
    }
  }

  #[staticmethod]
  fn from_json(json_obj: &PyDict) -> PyResult<Self> {
    Ok(IMUCord {
      cord_x: json_obj.get_item("cordX").unwrap().extract::<f32>()?,
      cord_y: json_obj.get_item("cordY").unwrap().extract::<f32>()?,
      cord_z: json_obj.get_item("cordZ").unwrap().extract::<f32>()?,
    })
  }

  fn __repr__(&self) -> String {
    format!(
      "IMUCord(cordX={}, cordY={}, cordZ={})",
      self.cord_x, self.cord_y, self.cord_z
    )
  }
}

#[gen_stub_pyclass]
#[pyclass(module = "bc_ecap_sdk.main_mod.ecap")]
#[derive(Debug, Serialize, Deserialize)]
struct IMUData {
  timestamp: u64,
  acc: IMUCord,
  gyro: IMUCord,
  mag: IMUCord,
}

#[gen_stub_pymethods]
#[pymethods]
impl IMUData {
  #[new]
  fn new(timestamp: u64, acc: IMUCord, gyro: IMUCord, mag: IMUCord) -> Self {
    IMUData {
      timestamp,
      acc,
      gyro,
      mag,
    }
  }

  #[staticmethod]
  fn from_json(py: Python, json_str: &str) -> PyResult<Self> {
    let json_obj: Py<PyDict> = PyDict::from_json(py, json_str)?;
    let imu_data = json_obj
      .get_item("EEGCap")
      .unwrap()
      .get_item("Mcu2App")
      .unwrap()
      .get_item("imu")
      .unwrap()
      .get_item("data")
      .unwrap();
    let timestamp = imu_data
      .get_item("timestamp")
      .unwrap_or(py.None())
      .extract::<u64>()
      .unwrap_or(0);
    let acc = IMUCord::from_json(
      imu_data
        .get_item("accel")
        .unwrap()
        .downcast::<PyDict>()
        .unwrap(),
    )?;
    let gyro = IMUCord::from_json(
      imu_data
        .get_item("gyro")
        .unwrap()
        .downcast::<PyDict>()
        .unwrap(),
    )?;
    let mag = IMUCord::from_json(
      imu_data
        .get_item("mag")
        .unwrap()
        .downcast::<PyDict>()
        .unwrap(),
    )?;
    Ok(IMUData {
      timestamp,
      acc,
      gyro,
      mag,
    })
  }

  fn __repr__(&self) -> String {
    format!(
      "IMUData(timestamp={}, acc={}, gyro={}, mag={})",
      self.timestamp, self.acc, self.gyro, self.mag
    )
  }
}
