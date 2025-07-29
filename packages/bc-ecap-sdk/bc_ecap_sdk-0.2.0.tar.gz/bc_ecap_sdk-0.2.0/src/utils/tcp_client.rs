use futures::{Stream, StreamExt};
// use parking_lot::Mutex;
use std::net::IpAddr;
use std::pin::Pin;
use std::sync::Arc;
use std::time::Duration;
use tokio::io::{self, AsyncReadExt, AsyncWriteExt, Interest};
use tokio::net::TcpStream;
use tokio::sync::broadcast;
use tokio::sync::Mutex;
use tokio::time::timeout;
use tokio_stream::wrappers::errors::BroadcastStreamRecvError;
use tokio_stream::wrappers::BroadcastStream;

use crate::callback::callback_rs::run_tcp_stream_exit_callback;
use crate::proto::msg_parser::Parser;

use super::runtime::get_runtime;
crate::cfg_import_logging!();

impl_enum_conversion!(
  TcpExitReason,
  Normal = 0,
  Disconnected = 1,
  Timeout = 2,
  ConnectionError = 3,
  // Aborted = 4,
);

pub type TcpDataStreamType =
  Pin<Box<dyn Stream<Item = Result<Vec<u8>, BroadcastStreamRecvError>> + Send>>;

pub struct TcpClient {
  pub addr: IpAddr,
  pub port: u16,
  pub reader: Arc<Mutex<Option<tokio::io::ReadHalf<TcpStream>>>>,
  pub writer: Arc<Mutex<Option<tokio::io::WriteHalf<TcpStream>>>>,
  pub tx: Arc<broadcast::Sender<Vec<u8>>>,
  pub read_hander: Option<tokio::task::JoinHandle<()>>,
  pub parse_handler: Option<tokio::task::JoinHandle<()>>,
}

impl Clone for TcpClient {
  fn clone(&self) -> Self {
    TcpClient {
      addr: self.addr,
      port: self.port,
      reader: self.reader.clone(),
      writer: self.writer.clone(),
      tx: self.tx.clone(),
      read_hander: None,   // 不克隆任务句柄
      parse_handler: None, // 不克隆任务句柄
    }
  }
}

impl TcpClient {
  pub fn new(addr: IpAddr, port: u16) -> Self {
    let (tx, _rx) = broadcast::channel(10000);
    TcpClient {
      addr,
      port,
      reader: Arc::new(Mutex::new(None)),
      writer: Arc::new(Mutex::new(None)),
      tx: Arc::new(tx),
      read_hander: None,
      parse_handler: None,
    }
  }

  pub fn connect_and_listen(&mut self, parser: Parser) -> Result<(), anyhow::Error> {
    info!("Connecting to {:?}:{:?}", self.addr, self.port);
    // 注册数据处理回调
    self.start_listen_with_parser(parser);

    let rt = get_runtime();
    rt.block_on(async {
      self.connect().await.map_err(|e| {
        error!("Connection error: {:?}", e);
        anyhow::anyhow!("TCP connection failed: {}", e)
      })
    })
  }

  fn abort_handlers(&mut self) {
    if let Some(handler) = self.read_hander.take() {
      handler.abort();
      debug!("Reading task aborted");
    }
    if let Some(handler) = self.parse_handler.take() {
      handler.abort();
      debug!("Parsing task aborted");
    }
  }

  async fn stop_tcp_stream(&mut self) -> Result<(), anyhow::Error> {
    info!("Stopping TCP stream for {:?}:{:?}", self.addr, self.port);
    // 关闭 reader
    let mut reader_guard = self.reader.lock().await;
    if let Some(_reader) = reader_guard.take() {
      // ReadHalf doesn't need explicit shutdown, just drop it
      debug!("Reader closed");
      *reader_guard = None;
    }

    // 关闭 writer
    let mut writer_guard = self.writer.lock().await;
    if let Some(ref mut writer) = writer_guard.take() {
      writer.shutdown().await.map_err(|e| {
        error!("Writer shutdown error: {:?}", e);
        anyhow::anyhow!("TCP writer shutdown failed: {}", e)
      })?;
      *writer_guard = None;
    }
    info!("TCP stream stopped for {:?}:{:?}", self.addr, self.port);
    Ok(())
  }

  pub async fn disconnect_async(&mut self) -> Result<(), anyhow::Error> {
    info!("Disconnecting from {:?}:{:?}", self.addr, self.port);
    self.abort_handlers();
    self.stop_tcp_stream().await
  }

  pub fn disconnect(&mut self) -> Result<(), anyhow::Error> {
    info!("Disconnecting from {:?}:{:?}", self.addr, self.port);
    self.abort_handlers();
    let rt = get_runtime();
    rt.block_on(async { self.stop_tcp_stream().await })
  }

  pub async fn connect(&mut self) -> io::Result<()> {
    let mut writer_guard = self.writer.lock().await;
    if writer_guard.is_some() {
      warn!("Connection already exists.");
      return Ok(());
    }
    let addr = format!("{}:{}", self.addr, self.port);
    info!("Connecting to {:?}", addr);
    let addr: std::net::SocketAddr = addr.parse().unwrap();
    let stream = TcpStream::connect(addr).await?;
    debug!("Connection established");
    stream
      .ready(Interest::WRITABLE | Interest::READABLE)
      .await?;
    let (reader, writer) = tokio::io::split(stream);
    debug!("TcpStream split into reader and writer");
    *self.reader.lock().await = Some(reader);
    debug!("TcpStream reader set");
    *writer_guard = Some(writer);
    debug!("TcpStream writer set");
    drop(writer_guard); // 释放锁
    self.enable_listening();
    debug!("TcpStream enabled");
    info!("Connected to {:?}", addr);
    Ok(())
  }

  pub fn get_receiver(&self) -> broadcast::Receiver<Vec<u8>> {
    info!("tcp data stream subscribe");
    self.tx.subscribe()
  }

  pub fn broadcast_stream(&self) -> TcpDataStreamType {
    info!("tcp data stream subscribe");
    let rx = self.tx.subscribe(); // 每次调用都创建一个新的 Receiver
    Box::pin(BroadcastStream::new(rx))
  }

  pub fn start_listen_with_parser(&mut self, mut parser: Parser) {
    let mut stream = self.broadcast_stream();
    let rt = get_runtime();
    let hander = rt.spawn(async move {
      debug!("Starting receive tcp data");
      while let Some(result) = stream.next().await {
        match result {
          Ok(data) => {
            // trace!("Received tcp data: {:?}", data);
            parser.receive_data(&data);
          }
          Err(e) => {
            error!("Error receiving tcp data: {:?}", e);
          }
        }
      }
    });
    self.parse_handler = Some(hander);
    debug!("tcp start_listen_with_parser done");
  }

  pub fn start_listen(&mut self, mut callback: impl FnMut(Vec<u8>) + Send + 'static) {
    let mut stream = self.broadcast_stream();
    let hander = tokio::spawn(async move {
      debug!("Starting receive tcp data");
      while let Some(result) = stream.next().await {
        match result {
          Ok(data) => {
            // trace!("Received tcp data: {:?}", data);
            callback(data);
          }
          Err(e) => {
            error!("Error receiving tcp data: {:?}", e);
          }
        }
      }
    });
    self.parse_handler = Some(hander);
    debug!("tcp start_listen done");
  }

  pub fn enable_listening(&mut self) {
    debug!("tcp enable_listening");
    let reader_clone = self.reader.clone();
    let tx: Arc<broadcast::Sender<Vec<u8>>> = self.tx.clone();
    let hander = tokio::spawn(async move {
      let mut buf = Vec::with_capacity(81920);
      let mut reader_guard = reader_clone.lock().await;
      if let Some(ref mut stream) = *reader_guard {
        loop {
          buf.clear();
          // trace!("tcp read_buf");
          // https://www.cloudflare.com/zh-cn/learning/network-layer/what-is-mss/
          // MTU - (TCP 标头 + IP 标头) = MSS
          // 1,500 - (20 + 20) = 1,460

          // 设置读取超时时间为 5 秒
          let read_timeout = Duration::from_secs(5);
          match timeout(read_timeout, stream.read_buf(&mut buf)).await {
            Ok(read_result) => {
              match read_result {
                Ok(0) => {
                  warn!("Connection closed by peer.");
                  run_tcp_stream_exit_callback(TcpExitReason::Disconnected);
                  return;
                }
                Ok(n) => {
                  // info!("tcp read {} bytes", n);
                  if n > 80000 {
                    warn!("tcp read {} bytes", n);
                  }
                  // trace!("Received data: {:?}", &buf[..n]);
                  if let Err(e) = tx.send(buf[..n].to_vec()) {
                    error!("Failed to send message: {:?}", e);
                  }
                }
                Err(ref e) if e.kind() == io::ErrorKind::WouldBlock => {
                  // info!("Would block: {:?}", e);
                  continue;
                }
                Err(e) => {
                  run_tcp_stream_exit_callback(TcpExitReason::ConnectionError);
                  warn!("Failed to read: {:?}", e);
                  return;
                }
              }
            }
            Err(_) => {
              warn!("TCP read timeout occurred");
              run_tcp_stream_exit_callback(TcpExitReason::Timeout);
              return; // 读取超时，退出循环
            }
          }
        }
      } else {
        info!("No active stream.");
      }
    });
    self.read_hander = Some(hander);
    debug!("tcp enable_listening done");
  }

  pub async fn send_command_data(&self, msg_id: u32, data: &[u8]) -> tokio::io::Result<()> {
    let mut stream_guard = self.writer.lock().await;
    if let Some(ref mut stream) = *stream_guard {
      trace!("Sending message with ID: {:?}", msg_id);
      stream.write_all(data).await?;
      Ok(())
    } else {
      Err(tokio::io::Error::new(
        tokio::io::ErrorKind::NotConnected,
        "No active connection",
      ))
    }
  }

  pub async fn send_command<F>(&self, command_builder: F) -> tokio::io::Result<()>
  where
    F: FnOnce() -> (u32, Vec<u8>),
  {
    let (msg_id, vec) = command_builder();
    trace!("send_command msg_id: {}", msg_id);
    let mut stream_guard = self.writer.lock().await;
    if let Some(ref mut stream) = *stream_guard {
      debug!("Sending message with ID: {:?}", msg_id);
      stream.write_all(&vec).await?;
      debug!("Sent message with ID: {:?}", msg_id);
      Ok(())
    } else {
      Err(tokio::io::Error::new(
        tokio::io::ErrorKind::NotConnected,
        "No active connection",
      ))
    }
  }
}
