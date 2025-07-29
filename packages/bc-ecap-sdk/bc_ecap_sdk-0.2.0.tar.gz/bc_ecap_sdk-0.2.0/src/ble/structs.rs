#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone)]
// #[repr(C)]
pub struct BLEDeviceInfo {
  pub manufacturer: String,
  pub model: String,
  pub serial: String,
  pub hardware: String,
  pub firmware: String,
}

#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone, Default)]
pub struct ScanResult {
  pub id: String,
  pub name: String,
  pub rssi: i16,
  pub is_in_pairing_mode: bool,
  pub battery_level: u8,
}

// use pyo3::prelude::*;
// use pyo3::types::*;
// impl IntoPy<PyObject> for ScanResult {
//   fn into_py(self, py: Python) -> PyObject {
//     let dict = PyDict::new(py);
//     dict.set_item("id", self.id).unwrap();
//     dict.set_item("name", self.name).unwrap();
//     dict.set_item("rssi", self.rssi).unwrap();
//     dict
//       .set_item("is_in_pairing_mode", self.is_in_pairing_mode)
//       .unwrap();
//     dict.set_item("battery_level", self.battery_level).unwrap();
//     dict.into()
//   }
// }
