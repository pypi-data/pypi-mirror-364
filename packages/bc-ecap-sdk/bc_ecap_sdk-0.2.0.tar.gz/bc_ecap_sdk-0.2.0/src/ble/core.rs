use crate::ble::enums::*;
use crate::ble::lib::*;
use crate::ble::structs::*;
use btleplug::api::CentralState;
use btleplug::platform::PeripheralId;

crate::cfg_import_logging!();

// 回调类型定义
pub type AdapterStateCallback = Box<dyn Fn(CentralState) + Send + Sync>;
pub type ScanResultCallback = Box<dyn Fn(ScanResult) + Send + Sync>;
pub type ConnectionStateCallback = Box<dyn Fn(String, ConnectionState) + Send + Sync>; // id, state
pub type DeviceInfoCallback = Box<dyn Fn(String, BLEDeviceInfo) + Send + Sync>; // id, device_info
pub type BatteryLevelCallback = Box<dyn Fn(String, u8) + Send + Sync>; // id, battery_level
pub type ReceivedDataCallback = Box<dyn Fn(String, Vec<u8>) + Send + Sync>; // id, data

/// Sets the callback for BLE adapter state changes.
///
/// # Arguments
///
/// * `callback` - The function to call when the adapter state changes.
pub fn set_adapter_state_callback(callback: AdapterStateCallback) {
  let mut cb = ADAPTER_STATE_CALLBACK.lock();
  *cb = Some(callback);
}

pub fn run_adapter_state_callback(state: CentralState) {
  info!("run_adapter_state_callback: {:?}", state);
  let cb = ADAPTER_STATE_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(state);
  } else {
    error!("Adapter state callback is not set")
  }
}

/// Sets the callback for BLE scan results.
///
/// # Arguments
///
/// * `callback` - The function to call by ManufacturerDataAdvertisementData
pub fn set_scan_result_callback(callback: ScanResultCallback) {
  let mut cb = SCAN_RESULT_CALLBACK.lock();
  *cb = Some(callback);
}

pub fn clear_scan_result_callback() {
  let mut cb = SCAN_RESULT_CALLBACK.lock();
  *cb = None;
}

pub(crate) fn run_scan_result_callback(result: ScanResult) {
  let cb = SCAN_RESULT_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(result);
  }
}

/// Sets the callback for BLE scan results.
///
/// # Arguments
///
/// * `callback` - The function to call by DeviceDiscovered
pub fn set_device_discovered_callback(callback: ScanResultCallback) {
  let mut cb = DEVICE_DISCOVERED_CALLBACK.lock();
  *cb = Some(callback);
}

pub fn clear_device_discovered_callback() {
  let mut cb = DEVICE_DISCOVERED_CALLBACK.lock();
  *cb = None;
}

pub(crate) fn run_device_discovered_callback(result: ScanResult) {
  let cb = DEVICE_DISCOVERED_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(result);
  }
}

/// Sets the callback for BLE connection state changes.
///
/// # Arguments
///
/// * `callback` - The function to call when the connection state changes.
pub fn set_connection_state_callback(callback: ConnectionStateCallback) {
  let mut cb = CONNECTION_STATE_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_connection_state_callback(id: &PeripheralId, state: ConnectionState) {
  debug!(
    "run_connection_state_callback: {}, {:?}",
    id.to_string(),
    state
  );
  let cb = CONNECTION_STATE_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(id.to_string(), state);
  }
}

/// Sets the callback for reading data from a device.
///
/// # Arguments
///
/// * `callback` - The function to call when data is read from a device.
pub fn set_received_data_callback(callback: ReceivedDataCallback) {
  let mut cb = RECEIVED_DATA_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_received_data_callback(id: &PeripheralId, data: Vec<u8>) {
  let cb = RECEIVED_DATA_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(id.to_string(), data);
  }
}

/// Sets the callback for reading the battery level of a device.
///
/// # Arguments
///
/// * `callback` - The function to call when the battery level of a device is read.
pub fn set_battery_level_callback(callback: BatteryLevelCallback) {
  let mut cb = BATTERY_LEVEL_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_battery_level_callback(id: &PeripheralId, battery_level: u8) {
  let cb = BATTERY_LEVEL_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(id.to_string(), battery_level);
  }
}

/// Sets the callback for reading the device info of a device.
///
/// # Arguments
///
/// * `callback` - The function to call when the device info of a device is read.
pub fn set_device_info_callback(callback: DeviceInfoCallback) {
  let mut cb = DEVICE_INFO_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_device_info_callback(id: &PeripheralId, device_info: BLEDeviceInfo) {
  let cb = DEVICE_INFO_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(id.to_string(), device_info);
  }
}
