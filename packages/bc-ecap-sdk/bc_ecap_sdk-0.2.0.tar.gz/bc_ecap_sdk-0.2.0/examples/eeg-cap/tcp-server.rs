//! Run with:
//!
//!     cargo run --no-default-features --example tcp-server
//!

use bc_ecap_sdk::utils::logging_desktop::init_logging;
use std::net::IpAddr;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
bc_ecap_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() {
  init_logging(log::Level::Info);

  // create a server to listen, receive and handle the incoming connections
  let addr = IpAddr::V4(std::net::Ipv4Addr::new(127, 0, 0, 1));
  let port = 8080;
  let listener = tokio::net::TcpListener::bind((addr, port)).await.unwrap();
  info!("Listening on: {:?}", listener.local_addr().unwrap());

  loop {
    let (socket, _) = listener.accept().await.unwrap();
    info!(
      "Accepted connection from: {:?}",
      socket.peer_addr().unwrap()
    );

    tokio::spawn(async move {
      handle_connection(socket).await;
    });
  }
}

// handle the incoming connection
async fn handle_connection(mut socket: tokio::net::TcpStream) {
  // socket.set_nodelay(true).unwrap();
  // socket.write_all(b"Hello from the server!\n").await.unwrap();

  let mut buf = [0; 4096];
  while socket.readable().await.is_ok() {
    info!("Socket is readable");
    match socket.read(&mut buf).await {
      Ok(n) if n == 0 => {
        info!("Connection closed");
        break;
      }
      Ok(n) => {
        let data = &buf[..n];
        info!("Received: {:?}", data);
        info!("Received: {:?}", std::str::from_utf8(data).unwrap());
        let response = [data, b"from server"].concat();
        if let Err(e) = socket.write_all(&response).await {
          error!("Failed to write to socket: {:?}", e);
          break;
        }
      }
      Err(e) => {
        error!("Failed to read from socket: {:?}", e);
        break;
      }
    }
  }
}
