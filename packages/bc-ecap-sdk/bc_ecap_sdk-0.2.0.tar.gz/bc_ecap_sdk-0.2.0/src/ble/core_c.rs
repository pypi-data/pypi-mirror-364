use super::c_utils::*;
use super::enums::*;
use super::lib::*;
use super::structs::*;
use crate::utils::c_utils::CStringExt;
use crate::utils::runtime::get_runtime;
use btleplug::api::CentralState;
use btleplug::platform::PeripheralId;
use std::ffi::*;
use uuid::Uuid;

#[allow(unused_imports)]
use super::constants::*;
#[allow(unused_imports)]
use crate::utils::logging::LogLevel;
#[allow(unused_imports)]
use crate::utils::logging_desktop as logging;

crate::cfg_import_logging!();

/// Initializes the logging options.
#[no_mangle]
pub extern "C" fn initialize_logging(level: LogLevel) {
  logging::initialize_logging(level);
}

/// Initializes the BLE adapter.
#[no_mangle]
pub extern "C" fn ble_initialize() -> i32 {
  let rt = get_runtime();
  let result = rt.block_on(async {
    let initialize_result = initialize_central_adapter().await;
    initialize_result
  });

  match result {
    Ok(_) => 0,   // 成功返回 0
    Err(_) => -1, // 失败返回 -1
  }
}

/*
 * This module contains BLE scan-related functions that can be called from the C side.
 *
 * Functions:
 * - `is_ble_scanning`: Returns whether the BLE adapter is currently scanning.
 * - `start_ble_scan`: Starts a BLE scan with the specified service UUIDs.
 * - `stop_ble_scan`: Stops the current BLE scan.
 */
/// Returns whether the BLE adapter is currently scanning.
#[no_mangle]
pub extern "C" fn is_ble_scanning() -> bool {
  is_scanning()
}

/// Starts a BLE scan with the specified service UUIDs.
///
/// # Arguments
///
/// * `services` - A pointer to an array of service UUIDs to scan for.
///
#[no_mangle]
pub extern "C" fn start_ble_scan(services: *const *const c_char) -> i32 {
  let service_uuids: Vec<Uuid> = match convert_to_uuids(services) {
    Ok(uuids) => uuids,
    #[cfg(any(target_os = "macos", target_os = "ios", target_os = "linux"))]
    Err(_) => vec![OXYZ_SERVICE_UUID, CMSN_SERVICE_UUID],
    #[cfg(target_os = "windows")]
    Err(_) => vec![],
  };
  let result = start_scan_with_uuids(service_uuids);
  match result {
    Ok(_) => 0, // 成功返回 0
    Err(e) => {
      error!("Failed to start scan: {:?}", e);
      -1
    }
  }
}

/// Stops the current BLE scan.
#[no_mangle]
pub extern "C" fn stop_ble_scan() {
  let _ = stop_scan();
}

/// Request the MTU size for the BLE connection.
#[no_mangle]
pub extern "C" fn set_prefer_mtu(mtu: u16) {
  set_mtu(mtu as usize);
}

/*
 * This module contains BLE connection-related functions that can be called from the C side.
 *
 * Functions:
 * - `connect_ble`: Connects to a BLE peripheral with the specified ID.
 * - `disconnect_ble`: Disconnects from a BLE peripheral with the specified ID.
 * - `ble_write_value`: Writes a value to a BLE peripheral with the specified ID.
 */
/// Connects to a BLE peripheral with the specified ID.
#[no_mangle]
pub extern "C" fn connect_ble(id: *const c_char) {
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id_with_char(id);
    info!("connect_ble, peripheral_id: {:?}", peripheral_id);
    run_connection_state_callback(&peripheral_id, ConnectionState::Connecting);

    let rt = get_runtime();
    let _ = rt.block_on(async move {
      // Perform connection
      match perform_connect(&central, &peripheral_id).await {
        Ok(_) => {
          info!("Successfully connected to peripheral: {:?}", peripheral_id);
          run_connection_state_callback(&peripheral_id, ConnectionState::Connected);
          Ok(())
        }
        Err(e) => {
          error!("Failed to connect to peripheral: {:?}", e);
          run_connection_state_callback(&peripheral_id, ConnectionState::Disconnected);
          Err(e)
        }
      }
    });
  } else {
    error!("No central adapter available.");
  }
}

/// Disconnects from a BLE peripheral with the specified ID.
#[no_mangle]
pub extern "C" fn disconnect_ble(id: *const c_char) {
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id_with_char(id);
    info!("disconnect_ble, peripheral_id: {:?}", peripheral_id);
    run_connection_state_callback(&peripheral_id, ConnectionState::Disconnecting);

    let rt = get_runtime();
    rt.block_on(async move {
      // Execute the disconnection process
      if let Err(e) = perform_disconnect(&central, &peripheral_id).await {
        error!("Disconnection process failed: {:?}", e);
      }
    });
  } else {
    error!("No central adapter available.");
  }
}

/// Writes a value to a BLE peripheral with the specified ID.
///
/// # Arguments
///
/// * `id` - The ID of the peripheral to write to.
/// * `data` - The data to write to the peripheral.
/// * `len` - The length of the data to write.
/// * `without_response` - Whether to write the data without a response.
///
#[no_mangle]
pub extern "C" fn ble_write_value(
  id: *const c_char,
  data: *const u8,
  len: u32,
  without_response: bool,
) {
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id_with_char(id);
    let data_slice = unsafe { std::slice::from_raw_parts(data, len as usize) };
    let data_vec: Vec<u8> = data_slice.to_vec();
    trace!(
      "ble_write_value, peripheral_id: {:?}, data: {:?}",
      peripheral_id,
      data_vec
    );
    let rt = get_runtime();
    rt.block_on(async move {
      trace!("Writing value to peripheral...");
      if let Err(e) =
        perform_write_value(&central, &peripheral_id, &data_vec, without_response).await
      {
        error!("Write value process failed: {:?}", e);
      }
    });
  } else {
    error!("No central adapter available.");
  }
}

// Rust 库中的回调类型定义
/*
 * This module contains several callback functions that can be set from the C side.
 *
 * Functions:
 * - `set_ble_adapter_state_callback`: Set the callback function for adapter state changes.
 * - `set_ble_scan_callback`: Set the callback function for scan results.
 * - `set_ble_connection_state_callback`: Set the callback function for connection state changes.
 * - `set_ble_read_data_callback`: Set the callback function for reading data from a device.
 * - `set_ble_battery_level_callback`: Set the callback function for reading the battery level of a device.
 * - `set_ble_device_info_callback`: Set the callback function for reading the device info of a device.
 */
pub type AdapterStateCallback = extern "C" fn(state: CentralAdapterState);
pub type ScanResultCallback = extern "C" fn(
  id: *const c_char,        // 设备地址, 以null结尾的字符串
  name: *const c_char,      // 设备名称, 以null结尾的字符串
  rssi: i16,                // 信号强度
  is_in_pairing_mode: bool, // 是否处于配对模式
  battery_level: u8,        // 电量
);
pub type ConnectionStateCallback = extern "C" fn(id: *const c_char, state: ConnectionState);
pub type ReceivedDataCallback = extern "C" fn(id: *const c_char, data: *const u8, len: u32);
pub type BatteryLevelCallback = extern "C" fn(id: *const c_char, battery_level: u8);
pub type DeviceInfoCallback = extern "C" fn(
  id: *const c_char,
  manufacturer: *const c_char,
  model: *const c_char,
  serial: *const c_char,
  hardware: *const c_char,
  firmware: *const c_char,
);

/// Sets the callback for BLE adapter state changes.
///
/// # Arguments
///
/// * `callback` - The function to call when the adapter state changes.
#[no_mangle]
pub extern "C" fn set_adapter_state_callback(callback: AdapterStateCallback) {
  let mut cb = ADAPTER_STATE_CALLBACK.lock();
  *cb = Some(callback);
}

pub fn run_adapter_state_callback(state: CentralState) {
  let cb = ADAPTER_STATE_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback((state as u8).into());
  }
}

/// Sets the callback for BLE scan results.
///
/// # Arguments
///
/// * `callback` - The function to call by ManufacturerDataAdvertisementData
#[no_mangle]
pub extern "C" fn set_scan_result_callback(callback: ScanResultCallback) {
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
    callback(
      result.id.to_cbytes(),
      result.name.to_cbytes(),
      result.rssi,
      result.is_in_pairing_mode,
      result.battery_level,
    );
  }
}

/// Sets the callback for BLE scan results.
///
/// # Arguments
///
/// * `callback` - The function to call by DeviceDiscovered
#[no_mangle]
pub extern "C" fn set_device_discovered_callback(callback: ScanResultCallback) {
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
    callback(
      result.id.to_cbytes(),
      result.name.to_cbytes(),
      result.rssi,
      result.is_in_pairing_mode,
      result.battery_level,
    );
  }
}

/// Sets the callback for BLE connection state changes.
///
/// # Arguments
///
/// * `callback` - The function to call when the connection state changes.
#[no_mangle]
pub extern "C" fn set_connection_state_callback(callback: ConnectionStateCallback) {
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
    callback(id.to_cbytes(), state.into());
  }
}

/// Sets the callback for reading data from a device.
///
/// # Arguments
///
/// * `callback` - The function to call when data is read from a device.
#[no_mangle]
pub extern "C" fn set_received_data_callback(callback: ReceivedDataCallback) {
  let mut cb = RECEIVED_DATA_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_received_data_callback(id: &PeripheralId, data: Vec<u8>) {
  let cb = RECEIVED_DATA_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(id.to_cbytes(), data.as_ptr(), data.len() as u32);
  }
}

/// Sets the callback for reading the battery level of a device.
///
/// # Arguments
///
/// * `callback` - The function to call when the battery level of a device is read.
#[no_mangle]
pub extern "C" fn set_battery_level_callback(callback: BatteryLevelCallback) {
  let mut cb = BATTERY_LEVEL_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_battery_level_callback(id: &PeripheralId, battery_level: u8) {
  let cb = BATTERY_LEVEL_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(id.to_cbytes(), battery_level);
  }
}

/// Sets the callback for reading the device info of a device.
///
/// # Arguments
///
/// * `callback` - The function to call when the device info of a device is read.
#[no_mangle]
pub extern "C" fn set_device_info_callback(callback: DeviceInfoCallback) {
  let mut cb = DEVICE_INFO_CALLBACK.lock();
  *cb = Some(callback);
}

pub(crate) fn run_device_info_callback(id: &PeripheralId, device_info: BLEDeviceInfo) {
  let cb = DEVICE_INFO_CALLBACK.lock();
  if let Some(callback) = &*cb {
    callback(
      id.to_cbytes(),
      device_info.manufacturer.to_cbytes(),
      device_info.model.to_cbytes(),
      device_info.serial.to_cbytes(),
      device_info.hardware.to_cbytes(),
      device_info.firmware.to_cbytes(),
    );
  }
}

/// Writes a value to a BLE peripheral with the specified ID.
#[allow(dead_code)]
fn ble_write<F>(id: *const c_char, msg_builder: F)
where
  F: FnOnce() -> (u32, Vec<u8>) + Send + 'static,
{
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id_with_char(id);
    let rt = get_runtime();
    rt.block_on(async move {
      info!("Writing value to peripheral...");
      let (_, data) = msg_builder();
      if let Err(e) = perform_write_value(&central, &peripheral_id, &data, true).await {
        error!("Write value process failed: {:?}", e);
      }
    });
  } else {
    error!("No central adapter available.");
  }
}

#[cfg(feature = "oxyzen-cbindgen")]
use crate::proto::oxyzen::msg_builder::oxyz_msg_builder;

/// 配对/检验配对信息
/// # Arguments
/// * `id` - 设备地址
/// * `in_pairing_mode` - 是否处于配对模式，true: 配对，false: 检验配对信息
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn send_pair(id: *const c_char, in_pairing_mode: bool) {
  ble_write(id, move || oxyz_msg_builder::pair(in_pairing_mode));
}

/// 开启接收数据，EEG/IMU/PPG
/// 默认采样率，EEG: 256Hz, IMU: 50Hz, PPG: 1Hz
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn start_data_stream(id: *const c_char) {
  ble_write(id, || oxyz_msg_builder::start_data_stream());
}

/// 停止接收数据, 关闭所有数据流
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn stop_data_stream(id: *const c_char) {
  ble_write(id, || oxyz_msg_builder::stop_data_stream());
}

/// 设置EEG采样率
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn set_eeg_config(id: *const c_char, afe_sr: AfeSr) {
  ble_write(id, move || oxyz_msg_builder::set_eeg_config(afe_sr as i32));
}

/// 设置IMU采样率
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn set_imu_config(id: *const c_char, imu_sr: ImuSr) {
  ble_write(id, move || oxyz_msg_builder::set_imu_config(imu_sr as i32));
}

/// 设置PPG参数
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn set_ppg_config(id: *const c_char, ppg_mode: PpgMode, ppg_ur: PpgUr) {
  ble_write(id, move || {
    oxyz_msg_builder::set_ppg_config(ppg_mode as i32, ppg_ur as i32)
  });
}

/// 设置自动休眠时间
/// # Arguments
/// * `id` - 设备地址
/// * `seconds` - 不使用多久后设备进入休眠，单位秒
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn set_sleep_idle_time(id: *const c_char, seconds: u32) {
  ble_write(id, move || oxyz_msg_builder::set_sleep_idle_time(seconds));
}

/// 设置设备名称
/// # Arguments
/// * `id` - 设备地址
/// * `name` - 设备名称
#[cfg(feature = "oxyzen-cbindgen")]
#[no_mangle]
pub extern "C" fn set_device_name(id: *const c_char, name: *const c_char) {
  let device_name = unsafe { CStr::from_ptr(name).to_str().unwrap() };
  ble_write(id, move || oxyz_msg_builder::set_device_name(device_name));
}
