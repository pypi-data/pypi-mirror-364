//! Run with:
//!
//!     cargo run --no-default-features --example ecap-tcp-client
//!

use bc_ecap_sdk::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use bc_ecap_sdk::proto::enums::MsgType;
use bc_ecap_sdk::proto::msg_parser::Parser;
use bc_ecap_sdk::utils::logging_desktop::init_logging;
use bc_ecap_sdk::utils::tcp_client::*;
use futures::StreamExt;
use std::net::IpAddr;
bc_ecap_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() {
  init_logging(log::Level::Debug);

  if let Err(e) = scan_and_connect().await {
    error!("Failed to scan and connect to service: {:?}", e);
  }
}

// 封装的扫描和连接函数
async fn scan_and_connect() -> Result<(), Box<dyn std::error::Error>> {
  let addr = IpAddr::V4(std::net::Ipv4Addr::new(127, 0, 0, 1));
  let port = 8080;
  if let Err(e) = connect_and_listen(&addr, port).await {
    error!("Connection error: {:?}", e);
    return Err(Box::new(e));
  }
  Ok(())
}

// 连接并监听的函数，包含连接和监听逻辑
async fn connect_and_listen(addr: &IpAddr, port: u16) -> tokio::io::Result<()> {
  let mut parser = Parser::new("test-device".into(), MsgType::EEGCap);
  let mut msg_stream = parser.message_stream();
  tokio::spawn(async move {
    info!("Starting read message");
    while let Some(result) = msg_stream.next().await {
      match result {
        Ok(message) => {
          info!("Received message: {:?}", message);
        }
        Err(e) => {
          error!("Error receiving message: {:?}", e);
        }
      }
    }
    info!("Finished read");
  });

  let mut client = TcpClient::new(*addr, port);
  let mut stream = client.broadcast_stream();
  tokio::spawn(async move {
    info!("Starting read tcp data");
    while let Some(result) = stream.next().await {
      match result {
        Ok(data) => {
          info!("Received tcp data: {:?}", data);
          parser.receive_data(&data);
        }
        Err(e) => {
          error!("Error receiving tcp data: {:?}", e);
        }
      }
    }
    info!("Finished read tcp data");
  });

  client.connect().await?;
  client
    .send_command(eeg_cap_msg_builder::get_eeg_config)
    .await?;
  client
    .send_command(eeg_cap_msg_builder::get_imu_config)
    .await?;
  Ok(())
}
