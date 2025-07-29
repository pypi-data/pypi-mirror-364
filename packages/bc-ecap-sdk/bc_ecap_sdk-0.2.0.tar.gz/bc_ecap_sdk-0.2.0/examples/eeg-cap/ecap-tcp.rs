//! Run with:
//!
//!     cargo run --no-default-features --example ecap-tcp --features="eeg-cap, examples"
//!

use bc_ecap_sdk::callback::callback_rs::*;
use bc_ecap_sdk::data_handler::afe_handler::parse_32ch_eeg_data;
use bc_ecap_sdk::eeg_cap::callback::*;
use bc_ecap_sdk::eeg_cap::data::*;
use bc_ecap_sdk::generated::eeg_cap_proto::*;
use bc_ecap_sdk::proto::eeg_cap::enums::*;
use bc_ecap_sdk::proto::eeg_cap::msg_builder::*;
use bc_ecap_sdk::proto::enums::*;
use bc_ecap_sdk::proto::msg_parser::Parser;
use bc_ecap_sdk::utils::mdns::*;
use bc_ecap_sdk::utils::tcp_client::*;
use std::fs::OpenOptions;
use std::io::Write;
use std::net::IpAddr;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::sleep;
use tokio_stream::StreamExt;

use bc_ecap_sdk::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use bc_ecap_sdk::utils::logging_desktop::init_logging;
bc_ecap_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() -> Result<(), anyhow::Error> {
  // init_logging(log::Level::Debug);
  init_logging(log::Level::Info);

  info!("Starting ecap-tcp example");
  // let with_sn: Option<String> = Some("SN-Yongle-dev".to_string());
  // let (addr, port) = mdns_start_scan(with_sn).unwrap();
  // info!("Found service at: {}:{}", addr, port);
  let (addr, port) = (IpAddr::V4(std::net::Ipv4Addr::new(192, 168, 2, 19)), 53129);
  let mut client = connect_and_listen(&addr, port).await?;
  // wait for message stream
  tokio::time::sleep(tokio::time::Duration::from_secs(3600)).await;
  // tokio::time::sleep(tokio::time::Duration::from_secs(6)).await;
  info!("Stopping ecap-tcp example");
  client.disconnect_async().await?;
  info!("ecap-tcp example stopped");
  Ok(())
}

// const LOOP_CHECK: bool = false;
const LOOP_CHECK: bool = true;

#[allow(dead_code)]
pub async fn connect_and_listen(addr: &IpAddr, port: u16) -> Result<TcpClient, anyhow::Error> {
  set_tcp_stream_exit_callback(Box::new(move |exit_code| {
    info!(
      "TCP stream exited with code: {:?}",
      TcpExitReason::from(exit_code as u8)
    );
  }));
  set_msg_resp_callback(Box::new(move |_device_id, string| {
    info!("Received message: {:?}", string);
  }));
  set_battery_level_callback(Box::new(move |level| {
    info!("Battery level: {}", level);
  }));

  let _ = mdns_stop_scan();

  // let addr = IpAddr::V4(std::net::Ipv4Addr::new(127, 0, 0, 1));
  // let port = 8080;
  let mut client = TcpClient::new(*addr, port);
  info!("Connecting to {:?}:{:?}", addr, port);
  client.connect().await?;
  info!("Connected to {:?}:{:?}", addr, port);
  start_listen(&client);

  // sleep(tokio::time::Duration::from_secs(1)).await;

  // let _ = client
  //   .send_command(eeg_cap_msg_builder::get_device_info)
  //   .await;
  // let _ = client
  //   .send_command(eeg_cap_msg_builder::get_eeg_config)
  //   .await;

  // start_leadoff_check(client.clone()).await?;
  // stop_leadoff_check(&client).await?;
  // start_data_stream(&client).await?;
  // stop_data_stream(&client).await?;

  Ok(client)
}

#[allow(dead_code)]
async fn start_data_stream(client: &TcpClient) -> tokio::io::Result<()> {
  use bc_ecap_sdk::proto::eeg_cap::enums::*;
  // let sr = EegSampleRate::SR_2000Hz as i32;
  let sr = EegSampleRate::SR_1000Hz as i32;
  // let sr = EegSampleRate::SR_500Hz as i32;
  // let sr = EegSampleRate::SR_250Hz as i32;
  let builder = || {
    eeg_cap_msg_builder::set_eeg_config(
      sr,
      EegSignalGain::GAIN_6 as i32,
      EegSignalSource::NORMAL as i32,
    )
  };
  client.send_command(builder).await?;
  // sleep(tokio::time::Duration::from_secs(2)).await;
  let builder = || eeg_cap_msg_builder::set_imu_config(ImuSampleRate::SR_100Hz as i32);
  client.send_command(builder).await?;
  // sleep(tokio::time::Duration::from_secs(1)).await;
  client
    .send_command(eeg_cap_msg_builder::start_eeg_stream)
    .await?;
  sleep(tokio::time::Duration::from_secs(1)).await;
  client
    .send_command(eeg_cap_msg_builder::start_imu_stream)
    .await?;
  // sleep(tokio::time::Duration::from_secs(1)).await;
  Ok(())
}

#[allow(dead_code)]
async fn stop_data_stream(client: &TcpClient) -> tokio::io::Result<()> {
  client
    .send_command(eeg_cap_msg_builder::stop_eeg_stream)
    .await?;
  client
    .send_command(eeg_cap_msg_builder::stop_imu_stream)
    .await?;
  Ok(())
}

#[allow(dead_code)]
async fn stop_leadoff_check(client: &TcpClient) -> tokio::io::Result<()> {
  let _ = client
    .send_command(eeg_cap_msg_builder::stop_leadoff_check)
    .await;
  Ok(())
}

#[allow(dead_code)]
async fn start_leadoff_check(client: TcpClient) -> tokio::io::Result<()> {
  // 设置回调，发送切换芯片命令
  let client_arc = Arc::new(Mutex::new(client));
  set_next_leadoff_cb(Box::new(move |chip, freq, current| {
    let client_clone = client_arc.clone();
    tokio::spawn(async move {
      // sleep(Duration::from_secs(1)).await;
      let client = client_clone.lock().await;
      let _ = client
        .send_command(|| {
          eeg_cap_msg_builder::switch_and_start_leadoff_check(
            chip as i32,
            freq as i32,
            current as i32,
          )
        })
        .await;
    });
  }));

  let freq = LeadOffFreq::Ac31p2hz;
  let current = LeadOffCurrent::Cur6nA;
  bc_ecap_sdk::eeg_cap::callback::start_leadoff_check(LOOP_CHECK, freq, current);

  Ok(())
}

pub fn start_listen(client: &TcpClient) {
  let chip_label = if LOOP_CHECK { "chip_all" } else { "chip_1" };

  let file_path = format!("logs/proto_data_{}.log", chip_label);
  info!("Writing data to file: {:?}", file_path);
  let mut file_proto = OpenOptions::new()
    .create(true)
    .write(true)
    .truncate(true)
    .open(file_path)
    .unwrap();

  let file_path = format!("logs/proto_json_{}.log", chip_label);
  let mut file_json = OpenOptions::new()
    .create(true)
    .write(true)
    .truncate(true)
    .open(file_path)
    .unwrap();

  let file_path = format!("logs/eeg_leadoff_{}.log", chip_label);
  let mut file_leadoff = OpenOptions::new()
    .create(true)
    .write(true)
    .truncate(true)
    .open(file_path)
    .unwrap();

  let last_timestamp_arc = Arc::new(Mutex::new(0u32));

  let mut parser = Parser::new("test-device".into(), MsgType::EEGCap);
  let mut msg_stream = parser.message_stream();
  tokio::spawn(async move {
    info!("Starting read message");
    while let Some(result) = msg_stream.next().await {
      match result {
        Ok((_device_id, message)) => {
          // info!("received mesage: {:?}", serde_json::to_string(&message).unwrap());
          match &message {
            ParsedMessage::EEGCap(msg) => match msg {
              EEGCapMessage::Mcu2App(ref mcu_msg) => {
                // save data to file
                let data_str = serde_json::to_string(&mcu_msg).unwrap_or_else(|_| "".to_string());
                file_json.write_all(data_str.as_bytes()).unwrap();
                file_json.write_all(b"\n").unwrap();

                if let Some(eeg) = &mcu_msg.eeg {
                  if let Some(eeg_cfg) = &eeg.config {
                    info!(
                      "Received eeg config: {:?}",
                      serde_json::to_string(eeg_cfg).unwrap_or_else(|_| "".to_string())
                    );
                    set_eeg_cfg(eeg_cfg);
                  }
                  if let Some(leadoff_cfg) = &eeg.lead_off {
                    info!(
                      "Received eeg leadoff config: {:?}",
                      serde_json::to_string(leadoff_cfg).unwrap_or_else(|_| "".to_string())
                    );
                  }
                  // if eeg.mode > 0 {
                  //   info!(
                  //     "Received eeg mode: {:?}",
                  //     EegMode::try_from(eeg.mode).unwrap().as_str_name()
                  //   );
                  // }
                  if let Some(eeg_data) = &eeg.data {
                    if eeg_data.lead_off_chip != EegLeadOffChip::ChipNone as i32 {
                      let mut eeg_data_buffer = vec![];
                      if let Some(sample) = &eeg_data.sample_1 {
                        eeg_data_buffer.push(sample.clone());
                        if !LOOP_CHECK {
                          let timestamp = sample.timestamp;
                          let mut last_timestamp = last_timestamp_arc.lock().await;
                          if *last_timestamp != timestamp - 2 {
                            warn!(
                              "msg Timestamp not continuous: {} -> {}",
                              *last_timestamp, timestamp
                            );
                          }
                          *last_timestamp = timestamp;
                        }
                      }
                      if let Some(sample) = &eeg_data.sample_2 {
                        eeg_data_buffer.push(sample.clone());
                      }
                      if let Some(sample) = &eeg_data.sample_3 {
                        eeg_data_buffer.push(sample.clone());
                      }
                      if let Some(sample) = &eeg_data.sample_4 {
                        eeg_data_buffer.push(sample.clone());
                      }
                      for data in eeg_data_buffer.iter() {
                        let mut eeg_values = parse_32ch_eeg_data(&data.data, 1);
                        eeg_values.insert(0, data.timestamp as f64);
                        eeg_values.insert(0, eeg_data.lead_off_chip as f64);
                        // let map = json!({
                        //   "timestamp": data.timestamp,
                        //   "data": eeg_values,
                        // });
                        let data_str = serde_json::to_string(&eeg_values).unwrap();
                        file_leadoff.write_all(data_str.as_bytes()).unwrap();
                        file_leadoff.write_all(b"\n").unwrap();
                      }
                    }
                  }
                }
              }
              _ => {}
            },
            #[allow(unreachable_patterns)]
            _ => {}
          }
        }
        Err(e) => {
          error!("Error receiving message: {:?}", e);
        }
      }
    }
    info!("Finished read message");
  });

  let mut rx = client.get_receiver();
  tokio::spawn(async move {
    info!("Starting read tcp data");
    loop {
      if let Ok(data) = rx.recv().await {
        // trace!("Received tcp data: {:?}", data);
        parser.receive_data(&data);
        // 以0x形式写入文件
        let data_hex: String = data.iter().map(|byte| format!("{:02x}, ", byte)).collect();
        let data_str = format!("{}\n", data_hex);
        file_proto.write_all(data_str.as_bytes()).unwrap();
      }
    }
  });
}
