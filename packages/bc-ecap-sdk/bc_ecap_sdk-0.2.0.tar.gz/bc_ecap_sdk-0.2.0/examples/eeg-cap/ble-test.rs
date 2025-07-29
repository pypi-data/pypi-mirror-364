//! Run with:
//!
//!     cargo run --no-default-features --example eeg-cap-ble-test --features="eeg-cap, examples, ble"
//!

// use async_std::task::sleep;
use bc_ecap_sdk::ble::constants::*;
use bc_ecap_sdk::ble::core::*;
use bc_ecap_sdk::ble::lib::*;
use bc_ecap_sdk::ble::structs::*;
#[allow(unused_imports)]
use bc_ecap_sdk::generated::eeg_cap_proto::WiFiSecurity;
use bc_ecap_sdk::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use bc_ecap_sdk::proto::enums::MsgType;
use bc_ecap_sdk::proto::msg_parser::Parser;
use bc_ecap_sdk::utils::logging_desktop::init_logging;
use btleplug::api::CentralState;
use parking_lot::Mutex;
use std::error::Error;
use std::sync::Arc;
use std::time::Duration;
use tokio::time::sleep;
use tokio_stream::StreamExt;

bc_ecap_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
  init_logging(log::Level::Debug);

  // let uuid = uuid::Uuid::parse_str("4de5a20c-0001-ae0b-bf63-0242ac130002")?;
  // info!("uuid: {:?}", uuid);
  // return Ok(());

  initialize_central_adapter().await?;
  let is_ble_scanning = is_scanning();
  info!("is_ble_scanning, {:?}", is_ble_scanning);
  if is_ble_scanning {
    return Err("already scanning".into());
  }
  set_adapter_state_callback(Box::new(adapter_state_handler));
  // set_scan_result_callback(scan_result_handler);
  set_device_discovered_callback(Box::new(on_device_discovered)); // 脑电帽的设备没有广播数据，所以使用设备发现回调
  set_battery_level_callback(Box::new(battery_level_handler));

  let parser = Parser::new("ecap-ble".into(), MsgType::EEGCap);
  let mut stream = parser.message_stream();
  tokio::spawn(async move {
    debug!("Starting read");
    while let Some(result) = stream.next().await {
      match result {
        Ok((device_id, message)) => {
          trace!(
            "Received message, device_id: {:?}, message: {:?}",
            device_id,
            message
          );
        }
        Err(e) => {
          error!("Error receiving message: {:?}", e);
        }
      }
    }
    debug!("Finished read");
  });

  let parser_arc = Arc::new(Mutex::new(parser));
  set_received_data_callback(Box::new(move |_id: String, data: Vec<u8>| {
    trace!("id: {}, received_data: {:02x?}", _id, data);
    parser_arc.lock().receive_data(&data);
  }));

  info!("prepare scan...");
  start_scan_with_uuids(vec![ECAP_SERVICE_UUID])?;
  sleep(Duration::from_secs(50)).await;
  Ok(())
}

fn adapter_state_handler(state: CentralState) {
  info!("adapter state: {:?}", state);
}

fn battery_level_handler(id: String, battery_level: u8) {
  info!("id: {}, battery_level: {}", id, battery_level);
}

fn on_device_discovered(result: ScanResult) {
  info!("on_device_discovered: {:?}", result);
  tokio::spawn(async {
    info!("stop_scan...");
    let _ = stop_scan();
    info!("stop_scan done");
    let id = result.id;
    connect_ble(&id).await;
    info!("connect_ble done");

    // let model = "EEG32".to_string();
    // let sn = "SN-12345678".to_string();
    // let (_, cmd) =
    //   eeg_cap_msg_builder::set_ble_device_info(model, sn, vec![0x00, 0x00, 0x00, 0x00, 0x00, 0x00]);
    // ble_write_value(&id, &cmd, true).await;

    // let ssid = "eeg-wifi".to_string();
    // let password = "123456789".to_string();
    // let (_, cmd) = eeg_cap_msg_builder::set_wifi_config(
    //   true,
    //   WiFiSecurity::SecurityWpa2MixedPsk as i32,
    //   ssid,
    //   password,
    // );
    // ble_write_value(&id, &cmd, true).await;

    let (_, cmd) = eeg_cap_msg_builder::get_ble_device_info();
    ble_write_value(&id, &cmd, true).await;
    let (_, cmd) = eeg_cap_msg_builder::get_wifi_status();
    ble_write_value(&id, &cmd, true).await;
    let (_, cmd) = eeg_cap_msg_builder::get_wifi_config();
    ble_write_value(&id, &cmd, true).await;
  });
}
