//! Run with:
//!
//!     cargo run --no-default-features --features "examples, tcp" --example tcp-server
//!

// use async_std::sync::Arc;
use bc_ecap_sdk::utils::logging_desktop::init_logging;
use std::net::IpAddr;
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::sync::Mutex;
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
  let counter = Arc::new(Mutex::new(0));

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

        let mut count = counter.lock().await;

        // let response = [data, b"from server"].concat();
        // if socket.write_all(&response).await.is_ok() {

        // Send the counter value back to the client
        loop {
          let response = format!("{}\n", count);
          if socket.write_all(response.as_bytes()).await.is_ok() {
            println!("Write {:?}", response);
            *count = *count + 1;
            sleep(Duration::from_micros(10));
          }
        }
      }
      Err(e) => {
        error!("Failed to read from socket: {:?}", e);
        break;
      }
    }
  }
}
