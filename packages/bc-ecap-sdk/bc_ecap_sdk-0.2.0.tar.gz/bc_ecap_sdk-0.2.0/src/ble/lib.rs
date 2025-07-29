use crate::ble::c_utils::to_peripheral_id;
use crate::utils::runtime::get_runtime;

use super::{constants::*, enums::*, structs::*};
use btleplug::api::{Central, CharPropFlags, Characteristic, Peripheral as _, WriteType};
use btleplug::{
  api::{bleuuid::BleUuid, *},
  platform::{Adapter, Peripheral, PeripheralId},
};
use futures::StreamExt;
use parking_lot::Mutex;
use std::{
  collections::HashMap,
  sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
  },
};
use uuid::Uuid;

crate::cfg_import_logging!();

cfg_if::cfg_if! {
  if #[cfg(feature = "cbindgen")] {
    use super::core_c::*;
  } else {
    use super::core::*;
  }
}

// 使用 lazy_static 定义全局回调函数存储
lazy_static::lazy_static! {
  pub(crate) static ref MTU: Mutex<usize> = Mutex::new(23);
  pub(crate) static ref ADAPTER_STATE_CALLBACK: Mutex<Option<AdapterStateCallback>> = Mutex::new(None);
  pub(crate) static ref DEVICE_DISCOVERED_CALLBACK: Mutex<Option<ScanResultCallback>> = Mutex::new(None);
  pub(crate) static ref SCAN_RESULT_CALLBACK: Mutex<Option<ScanResultCallback>> = Mutex::new(None);
  pub(crate) static ref CONNECTION_STATE_CALLBACK: Mutex<Option<ConnectionStateCallback>> = Mutex::new(None);
  pub(crate) static ref RECEIVED_DATA_CALLBACK: Mutex<Option<ReceivedDataCallback>> = Mutex::new(None);
  pub(crate) static ref BATTERY_LEVEL_CALLBACK: Mutex<Option<BatteryLevelCallback>> = Mutex::new(None);
  pub(crate) static ref DEVICE_INFO_CALLBACK: Mutex<Option<DeviceInfoCallback>> = Mutex::new(None);
  pub(crate) static ref GLOBAL_CENTRAL: Arc<Mutex<Option<Adapter>>> = Arc::new(Mutex::new(None));
  pub(crate) static ref GLOBAL_SCANNING: Arc<AtomicBool> = Arc::new(AtomicBool::new(false));
}

pub(crate) fn is_registered_device_discovered() -> bool {
  DEVICE_DISCOVERED_CALLBACK.lock().is_some()
}

pub(crate) fn is_registered_manufacturer_data_adv() -> bool {
  SCAN_RESULT_CALLBACK.lock().is_some()
}

pub(crate) fn is_registered_device_info() -> bool {
  DEVICE_INFO_CALLBACK.lock().is_some()
}

#[allow(dead_code)]
pub(crate) fn is_registered_received_data() -> bool {
  RECEIVED_DATA_CALLBACK.lock().is_some()
}

pub(crate) fn get_central_adapter() -> Option<Adapter> {
  GLOBAL_CENTRAL.lock().clone()
}

pub fn is_scanning() -> bool {
  GLOBAL_SCANNING.load(Ordering::Acquire)
}

pub(crate) fn set_scanning(scanning: bool) {
  GLOBAL_SCANNING.store(scanning, Ordering::Release);
}

pub fn set_mtu(mtu: usize) {
  *MTU.lock() = mtu;
}

pub(crate) fn get_mtu() -> usize {
  *MTU.lock()
}

pub async fn initialize_central_adapter() -> Result<(), Box<dyn std::error::Error>> {
  let manager = btleplug::platform::Manager::new().await?;

  // 获取所有蓝牙适配器
  let adapters = manager.adapters().await?;

  // 确保至少有一个适配器
  if adapters.is_empty() {
    return Err("No Bluetooth adapters found.".into());
  }

  let central = adapters[0].clone();
  info!("Using adapter: {:?}", central.adapter_info().await?);

  // 打印其他适配器的信息
  for adapter in &adapters[1..] {
    debug!("Other adapter: {:?}", adapter.adapter_info().await?);
  }

  let mut global_central = GLOBAL_CENTRAL.lock();
  *global_central = Some(central.clone());
  info!("Central adapter initialized.");

  let rt = get_runtime();
  rt.spawn(async move {
    info!("Starting central event listener...");
    if let Err(e) = initialize_central_event_listener(central).await {
      warn!("Failed to initialize event listener: {:?}", e);
    }
  });

  Ok(())
}

pub async fn initialize_central_event_listener(
  central: btleplug::platform::Adapter,
) -> Result<(), Box<dyn std::error::Error>> {
  info!("Initializing central event listener...");
  let mut events = central.events().await?;
  info!("central.events listener started.");

  while let Some(event) = events.next().await {
    match event {
      CentralEvent::StateUpdate(state) => {
        info!("Central StateUpdate: {:?}", state);
        run_adapter_state_callback(state);
      }
      CentralEvent::DeviceDiscovered(id) => {
        trace!("DeviceDiscovered: {:?}", id);
        if !is_registered_device_discovered() || !is_scanning() {
          continue;
        }
        if let Ok(peripheral) = central.peripheral(&id).await {
          if let Ok(properties) = peripheral.properties().await {
            let device_address = id.to_string();
            let properties = properties.unwrap();
            let mut device_name = properties.local_name.clone().unwrap_or("N/A".to_string());

            // 如果设备名称是N/A，就使用Zephyr + MAC地址后5位格式
            if device_name == "N/A" {
              // 提取MAC地址的后5位, 去掉冒号
              let addr_without_colon = device_address.replace(":", "");
              if addr_without_colon.len() >= 5 {
                let last_five = &addr_without_colon[addr_without_colon.len() - 5..];
                device_name = format!("Zephyr [EEG-{}]", last_five);
              }
            }

            // Peripheral names are missing on Windows
            // https://github.com/deviceplug/btleplug/issues/267
            // info!("Device address: {:?}, name: {:?}, properties: {:?}, peripheral: {:?}", device_address, device_name, properties, peripheral);
            let rssi = properties.rssi.unwrap_or(0);
            let scan_result = ScanResult {
              id: device_address,
              name: device_name,
              rssi,
              ..Default::default()
            };
            run_device_discovered_callback(scan_result);
          }
        }
      }
      CentralEvent::DeviceUpdated(id) => {
        trace!("DeviceUpdated: {:?}", id);
      }
      CentralEvent::DeviceConnected(id) => {
        info!("DeviceConnected: {:?}", id);
      }
      CentralEvent::DeviceDisconnected(id) => {
        info!("DeviceDisconnected: {:?}", id);
        run_connection_state_callback(&id, ConnectionState::Disconnected);
      }
      CentralEvent::ManufacturerDataAdvertisement {
        id,
        manufacturer_data,
      } => {
        debug!(
          "ManufacturerDataAdvertisement: {:?}, {:?}",
          id, manufacturer_data
        );
        if !is_registered_manufacturer_data_adv() || !is_scanning() {
          continue;
        }
        let _ = handle_manufacturer_data(&central, &id, manufacturer_data).await;
      }
      CentralEvent::ServiceDataAdvertisement { id, service_data } => {
        trace!("ServiceDataAdvertisement: {:?}, {:?}", id, service_data);
      }
      CentralEvent::ServicesAdvertisement { id, services } => {
        let services: Vec<String> = services.into_iter().map(|s| s.to_short_string()).collect();
        trace!("ServicesAdvertisement: {:?}, {:?}", id, services);
      }
    }
  }

  info!("central.events stopped.");
  Ok(())
}

async fn handle_manufacturer_data(
  central: &Adapter,
  id: &PeripheralId,
  manufacturer_data: HashMap<u16, Vec<u8>>,
) -> Result<(), Box<dyn std::error::Error>> {
  trace!(
    "ManufacturerDataAdvertisement: {:?}, {:?}",
    id,
    manufacturer_data
  );

  let p = central.peripheral(id).await?;
  if let Some(properties) = p.properties().await? {
    let device_address = id.to_string();
    let device_name = properties.local_name;
    let rssi = properties.rssi.unwrap_or(0);
    let (is_in_pairing_mode, battery_level) =
      extract_values_from_manufacturer_data(&properties.services, &manufacturer_data);
    info!(
      "Device address: {:?}, name: {:?}, RSSI: {:?}, is_in_pairing_mode: {:?}, battery_level: {:?}",
      device_address, device_name, rssi, is_in_pairing_mode, battery_level
    );
    let scan_result = ScanResult {
      id: device_address,
      name: device_name.unwrap_or("N/A".to_string()),
      rssi,
      is_in_pairing_mode,
      battery_level,
    };
    run_scan_result_callback(scan_result);
  }

  Ok(())
}

fn extract_values_from_manufacturer_data(
  services: &[Uuid],
  manufacturer_data: &HashMap<u16, Vec<u8>>,
) -> (bool, u8) {
  let is_cmsn = services.contains(&CMSN_SERVICE_UUID);
  let is_oxyzen = services.contains(&OXYZ_SERVICE_UUID);
  if !is_cmsn && !is_oxyzen {
    return (false, 0);
  }
  warn!("is_cmsn: {:?}, is_oxyzen: {:?}", is_cmsn, is_oxyzen);

  let key_values: [u16; 2] = [0x5242, 0x4252];
  for &key in &key_values {
    if let Some(manufacturer_values) = manufacturer_data.get(&key) {
      if is_cmsn && manufacturer_values.len() >= 2 {
        let in_pairing_mode = manufacturer_values[1] == 1;
        let battery_level = manufacturer_values[0];
        return (in_pairing_mode, battery_level);
      } else if is_oxyzen && manufacturer_values.len() >= 8 {
        let in_pairing_mode = manufacturer_values[7] == 1;
        let battery_level = manufacturer_values[6];
        return (in_pairing_mode, battery_level);
      } else {
        return (false, 0);
      }
    }
  }

  warn!("No manufacturer data found.");
  (false, 0)
}

pub fn ble_init_adapter() -> Result<(), anyhow::Error> {
  info!("ble_init_adapter");
  // Initialize the central adapter
  if get_central_adapter().is_none() {
    // Use Tokio runtime to execute the async task
    let rt = get_runtime();
    rt.block_on(async {
      let _ = initialize_central_adapter().await;
      info!("ble_init_adapter done.");
    });
  }
  Ok(())
}

pub fn start_scan_with_uuids(service_uuids: Vec<Uuid>) -> Result<(), anyhow::Error> {
  info!("start_scan_with_uuids: {:?}", service_uuids);

  if is_scanning() {
    return Err(anyhow::anyhow!("Scan already running."));
  }
  set_scanning(true);

  // Use Tokio runtime to execute the async task
  let rt = get_runtime();
  rt.block_on(async {
    let central = get_central_adapter().unwrap();
    let _ = central
      .start_scan(ScanFilter {
        services: service_uuids,
      })
      .await;
  });

  Ok(())
}

pub fn stop_scan() -> Result<(), anyhow::Error> {
  info!("stop_scan");
  clear_scan_result_callback();
  clear_device_discovered_callback();

  if !is_scanning() {
    return Ok(());
    // return Err(anyhow::anyhow!("Scan not running."));
  }

  // Use Tokio runtime to execute the async task
  let rt = get_runtime();
  rt.block_on(async {
    let central = get_central_adapter().unwrap();
    let _ = central.stop_scan().await;
    set_scanning(false);
  });

  Ok(())
}

pub async fn find_peripheral(
  central: &Adapter,
  id: &PeripheralId,
) -> Result<Peripheral, anyhow::Error> {
  central.peripheral(id).await.map_err(|e| anyhow::anyhow!(e))
}

pub fn sync_connect_ble(id: &str) -> Result<(), anyhow::Error> {
  let rt = get_runtime();
  rt.block_on(async {
    connect_ble(id).await;
  });
  Ok(())
}

pub fn sync_disconnect_ble(id: &str) -> Result<(), anyhow::Error> {
  let rt = get_runtime();
  rt.block_on(async {
    disconnect_ble(id).await;
  });
  Ok(())
}

/// Connects to a BLE peripheral with the specified ID.
pub async fn connect_ble(id: &str) {
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id(id);
    info!("connect_ble, peripheral_id: {:?}", peripheral_id);

    run_connection_state_callback(&peripheral_id, ConnectionState::Connecting);
    match perform_connect(&central, &peripheral_id).await {
      Ok(_) => {
        info!("Successfully connected to peripheral: {:?}", id);
        run_connection_state_callback(&peripheral_id, ConnectionState::Connected);
      }
      Err(e) => {
        error!("Failed to connect to peripheral: {:?}", e);
        run_connection_state_callback(&peripheral_id, ConnectionState::Disconnected);
      }
    }
  } else {
    error!("No central adapter available.");
  }
}

/// Disconnects from a BLE peripheral with the specified ID.
pub async fn disconnect_ble(id: &str) {
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id(id);
    info!("disconnect_ble, peripheral_id: {:?}", peripheral_id);

    run_connection_state_callback(&peripheral_id, ConnectionState::Disconnecting);
    match perform_disconnect(&central, &peripheral_id).await {
      Ok(_) => {
        info!(
          "Successfully disconnected from peripheral: {:?}",
          peripheral_id
        );
      }
      Err(e) => {
        error!("Failed to disconnect from peripheral: {:?}", e);
      }
    }
  } else {
    error!("No central adapter available.");
  }
}

pub async fn perform_disconnect(central: &Adapter, id: &PeripheralId) -> Result<(), anyhow::Error> {
  let peripheral = find_peripheral(central, id).await?;
  peripheral.disconnect().await?;
  Ok(())
}

pub async fn perform_connect(central: &Adapter, id: &PeripheralId) -> Result<(), anyhow::Error> {
  let peripheral = find_peripheral(central, id).await?;

  // Attempt to connect to the device
  peripheral.connect().await?;

  // Attempt to request MTU in Android
  #[cfg(target_os = "android")]
  {
    let prefer_mtu = get_mtu();
    if prefer_mtu > 23 {
      // The value provided by Bluez includes an extra 3 bytes from the GATT header
      // https://github.com/deviceplug/btleplug/issues/246
      peripheral.request_mtu(prefer_mtu).await?;
    }
  }

  // Attempt to discover services and characteristics
  peripheral.discover_services().await?;

  // Setup data stream characteristics
  setup_data_stream_characteristics(&peripheral).await?;

  // Read device info
  if is_registered_device_info() {
    match read_ble_device_info(&peripheral).await {
      Ok(device_info) => {
        info!("Device info: {:?}", device_info);
        run_device_info_callback(id, device_info);
      }
      Err(e) => {
        warn!("Failed to read device info: {:?}", e);
      }
    }
  }

  let rt = get_runtime();
  rt.spawn(async move {
    if let Err(e) = process_notifications_stream(&peripheral).await {
      error!("Failed to process notifications data: {:?}", e);
    }
  });

  Ok(())
}

async fn read_characteristic(peripheral: &Peripheral, uuid: Uuid) -> Result<String, anyhow::Error> {
  if let Some(characteristic) = peripheral.characteristics().iter().find(|c| c.uuid == uuid) {
    match peripheral.read(characteristic).await {
      Ok(value) => Ok(String::from_utf8_lossy(&value).to_string()),
      Err(_) => Ok(String::new()), // 返回空字符串
    }
  } else {
    Ok(String::new()) // 找不到 characteristic 时返回空字符串
  }
}

async fn read_ble_device_info(peripheral: &Peripheral) -> Result<BLEDeviceInfo, anyhow::Error> {
  let manufacturer = read_characteristic(peripheral, MANUFACTURER_NAME_CHAR_UUID).await?;
  let model = read_characteristic(peripheral, MODEL_NUMBER_CHAR_UUID).await?;
  let serial = read_characteristic(peripheral, SERIAL_NUMBER_CHAR_UUID).await?;
  let hardware = read_characteristic(peripheral, HARDWARE_REVISION_CHAR_UUID).await?;
  let firmware = read_characteristic(peripheral, FIRMWARE_REVISION_CHAR_UUID).await?;

  let info = BLEDeviceInfo {
    manufacturer,
    model,
    serial,
    hardware,
    firmware,
  };
  Ok(info)
}

async fn read_battery_level(peripheral: &Peripheral, battery_char: &Characteristic) {
  // Read the initial battery level
  match peripheral.read(battery_char).await {
    Ok(value) => {
      let battery_level = value[0];
      info!("Read battery level: {:?}", battery_level);
      if battery_level < 100 {
        // Avoid sending notification for potentially inaccurate 100% readings
        // unsafe {
        //   if let Some(callback) = BLE_BATTERY_LEVEL_CALLBACK {
        //     callback(peripheral.id().to_cbytes(), battery_level);
        //   }
        // }
      }
    }
    Err(e) => {
      error!("Failed to read battery level: {:?}", e);
    }
  }
}

async fn get_device_name(peripheral: &Peripheral) -> Result<String, anyhow::Error> {
  let properties = peripheral.properties().await?;
  Ok(properties.unwrap().local_name.unwrap_or("N/A".to_string()))
}

async fn process_notifications_stream(peripheral: &Peripheral) -> Result<(), anyhow::Error> {
  let mut values = peripheral.notifications().await?;

  let id = peripheral.id();
  let name = get_device_name(peripheral).await?;

  while let Some(value) = values.next().await {
    trace!("Received uuid: {:?}, value: {:?}", value.uuid, value.value);

    let data = value.value;
    if ALL_RX_CHARACTERISTIC_UUIDS
      .iter()
      .any(|&uuid| uuid == value.uuid)
    {
      trace!("{}, Received data: {:?}", name, data);
      run_received_data_callback(&id, data);
    } else if value.uuid == BATTERY_LEVEL_CHAR_UUID {
      let battery_level = data[0];
      debug!("{}, battery level: {:?}", name, battery_level);
      run_battery_level_callback(&id, battery_level);
    }
  }
  Ok(())
}

async fn setup_data_stream_characteristics(p: &Peripheral) -> Result<(), anyhow::Error> {
  let chars = p.characteristics();
  for c in &chars {
    debug!("Characteristic: {:?}", c.uuid);
  }
  let rx_char = chars
    .iter()
    .find(|c| {
      (ALL_SERVICE_UUIDS.iter().any(|&uuid| uuid == c.service_uuid))
        && c.properties.contains(CharPropFlags::NOTIFY)
    })
    .ok_or_else(|| anyhow::anyhow!("Notify characteristic not found"))?;

  let tx_char = chars
    .iter()
    .find(|c| {
      (ALL_SERVICE_UUIDS.iter().any(|&uuid| uuid == c.service_uuid))
        && (c.properties.contains(CharPropFlags::WRITE)
          || c.properties.contains(CharPropFlags::WRITE_WITHOUT_RESPONSE))
    })
    .ok_or_else(|| anyhow::anyhow!("Write characteristic not found"))?;

  debug!("RX Characteristic: {:?}", rx_char);
  debug!("TX Characteristic: {:?}", tx_char);

  p.subscribe(rx_char).await?;
  debug!("Subscribed to RX characteristic.");

  if let Some(battery_char) = chars.iter().find(|c| c.uuid == BATTERY_LEVEL_CHAR_UUID) {
    if let Err(e) = p.subscribe(battery_char).await {
      error!("Failed to subscribe to battery characteristic: {:?}", e);
    }
    read_battery_level(p, battery_char).await;
  } else {
    info!("Battery characteristic not found.");
  }

  Ok(())
}

pub async fn perform_write_value(
  central: &Adapter,
  id: &PeripheralId,
  data: &[u8],
  without_response: bool,
) -> Result<(), anyhow::Error> {
  trace!("Writing value to peripheral: {:?}, data: {:?}", id, data);
  let peripheral = find_peripheral(central, id).await?;

  #[cfg(target_os = "linux")]
  peripheral.discover_services().await?; // FIXME

  // 查找支持写操作的特征
  let chars = peripheral.characteristics();
  let tx_char = chars
    .iter()
    .find(|c| {
      (ALL_SERVICE_UUIDS.iter().any(|&uuid| uuid == c.service_uuid))
        && (!without_response && c.properties.contains(CharPropFlags::WRITE)
          || (without_response && c.properties.contains(CharPropFlags::WRITE_WITHOUT_RESPONSE)))
    })
    .ok_or_else(|| anyhow::anyhow!("Write characteristic not found for peripheral: {:?}", id))?;

  // 执行写操作
  let write_type = if without_response {
    WriteType::WithoutResponse
  } else {
    WriteType::WithResponse
  };

  // if data len > MTU, split data into chunks
  let mtu = get_mtu() - 3; // 3 bytes for GATT header
  let mut data_len = data.len();
  let mut offset = 0;
  while data_len > 0 {
    let chunk_len = std::cmp::min(data_len, mtu);
    let chunk = &data[offset..offset + chunk_len];
    peripheral.write(tx_char, chunk, write_type).await?;
    data_len -= chunk_len;
    offset += chunk_len;
  }

  Ok(())
}

pub fn sync_write_value(
  id: &str,
  data: &[u8],
  without_response: bool,
) -> Result<(), anyhow::Error> {
  let rt = get_runtime();
  rt.block_on(async {
    ble_write_value(id, data, without_response).await;
  });
  Ok(())
}

/// Writes a value to a BLE peripheral with the specified ID.
///
/// # Arguments
///
/// * `id` - The ID of the peripheral to write to.
/// * `without_response` - Whether to write the data without a response.
pub async fn ble_write_value(id: &str, data: &[u8], without_response: bool) {
  if let Some(central) = get_central_adapter() {
    let peripheral_id = to_peripheral_id(id);
    trace!(
      "write_value, peripheral_id: {:?}, data: {:02x?}",
      peripheral_id,
      data
    );
    trace!("Writing value to peripheral...");
    if let Err(e) = perform_write_value(&central, &peripheral_id, data, without_response).await {
      error!("Write value process failed: {:?}", e);
    }
  } else {
    error!("No central adapter available.");
  }
}
