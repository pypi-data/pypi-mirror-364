use super::eeg_cap::msg_builder::EEGCapMessage;
use super::{constants::*, enums::*};
use crate::utils::crc::calculate_crc16_modbus;
use byteorder::{ByteOrder, LittleEndian};
use std::pin::Pin;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};
use tokio_stream::wrappers::errors::BroadcastStreamRecvError;
use tokio_stream::wrappers::BroadcastStream;
use tokio_stream::Stream;

crate::cfg_import_logging!();

pub type StreamType =
  Pin<Box<dyn Stream<Item = Result<(String, ParsedMessage), BroadcastStreamRecvError>> + Send>>;

pub type ArcMutexStream = Arc<Mutex<StreamType>>;

pub type TcpStreamType =
  Pin<Box<dyn Stream<Item = Result<Vec<u8>, BroadcastStreamRecvError>> + Send>>;

pub type ArcMutexTcpStream = Arc<Mutex<TcpStreamType>>;

lazy_static::lazy_static! {
  static ref PREVIOUS_TIMESTAMP: parking_lot::Mutex<Option<u32>> = parking_lot::Mutex::new(None);
}
#[derive(Debug, Clone)]
pub struct Parser {
  pub device_id: String,
  pub msg_type: MsgType,
  pub tx: broadcast::Sender<(String, ParsedMessage)>,
  pub rx: Arc<broadcast::Receiver<(String, ParsedMessage)>>,

  header_version: u8,
  header_prefix: Vec<u8>,
  header_length: usize,

  buffer: Vec<u8>,
  expected_length: usize,
  padding_size: usize,

  // padding_size: u16,
  pub padding_4x: bool,
}

impl Parser {
  pub fn new(device_id: String, msg_type: MsgType) -> Self {
    let (project_id, header_version, header_length) = get_project_info(msg_type);
    let mut header_prefix = Vec::new();

    let mut padding_4x: bool = false;
    if msg_type == MsgType::Stark {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC_BNCP);
      padding_4x = true;
    } else {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC);
      header_prefix.push(header_version);
      header_prefix.push(project_id);
      let payload_version = 1;
      if header_version == HEADER_VERSION_V2 && header_length == 12 {
        header_prefix.push(payload_version);
      }
    }
    debug!(
      "ParserType: {:?}, Project ID: 0x{:x}, Header version: {}, header_prefix: {:x?}",
      msg_type, project_id, header_version, header_prefix,
    );

    let (tx, rx) = broadcast::channel(10000); // 创建消息发送器和接收器
    Parser {
      device_id,
      msg_type,
      tx,
      rx: Arc::new(rx),
      header_version,
      header_prefix,
      header_length,
      buffer: Vec::with_capacity(BUFFER_MAX_SIZE),
      expected_length: 0,
      padding_size: 0,
      padding_4x,
    }
  }

  pub fn message_stream(&self) -> StreamType {
    let rx = self.tx.subscribe(); // 每次调用都创建一个新的 Receiver
    Box::pin(BroadcastStream::new(rx))
  }

  pub fn receive_data(&mut self, data: &[u8]) {
    if data.is_empty() {
      error!("Data should not be empty");
      return;
    }

    if self.buffer.len() + data.len() > BUFFER_MAX_SIZE {
      self.clear_buffer();
      error!(
        "Buffer is out of space. (BUFFER_MAX_SIZE = {}), buffer length: {}, data len: {}",
        BUFFER_MAX_SIZE,
        self.buffer.len(),
        data.len()
      );
      return;
    }
    self.buffer.extend_from_slice(data);
    self.process_buffer();
  }

  fn process_buffer(&mut self) {
    if self.buffer.len() <= self.header_length {
      trace!("Buffer length: {}", self.buffer.len());
      return;
    }

    if self.expected_length == 0 {
      match self.find_header_index() {
        Some(index) => {
          if index > 0 {
            warn!(
              "Found header at index: {}, unexpected_data: {:?}",
              index,
              &self.buffer[..index]
            );
            self.trim_buffer(index);
          }
        }
        None => {
          warn!(
            "Proto header is mismatch, drop the message, buffer: {:02x?}",
            self.buffer
          );
          warn!("header_prefix: {:?}", self.header_prefix);
          self.handle_unexpected_data();
          return;
        }
      }

      if let Ok((expected_length, padding_size)) = self.get_expected_length() {
        self.expected_length = expected_length;
        self.padding_size = padding_size;
      } else {
        error!(
          "Failed to calculate expected length, buffer: {:02x?}",
          self.buffer
        );
        self.handle_unexpected_data();
        return;
      }
    }

    // info!(
    //   "Expected length: {}, buffer length: {}",
    //   self.expected_length,
    //   self.buffer.len()
    // );
    if self.expected_length > self.buffer.len() {
      trace!(
        "Expected length: {}, buffer length: {}",
        self.expected_length,
        self.buffer.len()
      );
      return;
    }

    if self.verify_crc_footer() {
      trace!(
        "CRC verification passed, buffer: {:02x?}",
        &self.buffer[..self.expected_length]
      );
      let footer_len = if self.header_version == HEADER_VERSION_STARK {
        PROTO_FOOTER_CRC32
      } else {
        PROTO_FOOTER_CRC16
      };
      let begin_idx = self.header_length;
      let end_idx = self.expected_length - self.padding_size - footer_len;
      let payload = &self.buffer[begin_idx..end_idx];
      if let Err(e) = self.parse_message(payload) {
        error!("Failed to parse message, error: {:?}", e);
        self.handle_unexpected_data();
        return;
      }
    } else {
      error!("CRC verification failed");
      self.handle_unexpected_data();
      return;
    }

    self.handle_complete_message();
  }

  fn parse_next_message(&mut self) {
    if self.find_header_index().is_some() {
      trace!("parsing next message");
      self.process_buffer();
    }
  }

  fn handle_complete_message(&mut self) {
    self.trim_buffer(self.expected_length);
    self.expected_length = 0;
    self.padding_size = 0;
    self.parse_next_message();
  }

  fn handle_unexpected_data(&mut self) {
    self.trim_buffer(self.header_prefix.len());
    match self.find_header_index() {
      Some(index) => {
        if index > 0 {
          self.trim_buffer(index);
        }
        self.expected_length = 0;
        self.padding_size = 0;
        self.parse_next_message();
      }
      _ => {
        self.clear_buffer();
      }
    }
  }

  fn trim_buffer(&mut self, shift_amount: usize) {
    self.buffer.drain(..shift_amount);
  }

  fn clear_buffer(&mut self) {
    self.buffer.clear();
    self.expected_length = 0;
  }

  fn find_header_index(&self) -> Option<usize> {
    let prefix_len = self.header_prefix.len();

    if self.buffer.len() < prefix_len {
      return None;
    }

    (0..=(self.buffer.len() - prefix_len))
      .find(|&i| self.buffer[i..i + prefix_len] == self.header_prefix[..])
  }

  fn get_expected_length(&self) -> Result<(usize, usize), ()> {
    if self.buffer.len() < self.header_length {
      return Err(());
    }

    let len = self.header_prefix.len();
    let mut padding_size: usize = 0;
    let expected_length = if self.header_version == HEADER_VERSION_STARK {
      let pkt_size = usize::from(self.buffer[6]) * 256
        + usize::from(self.buffer[7])
        + self.header_length
        + PROTO_FOOTER_CRC32;
      // info!("self.header_length: {}", self.header_length);
      // info!("Packet size: {}", pkt_size);
      padding_size = (4 - (pkt_size % 4)) % 4;
      // info!("Padding size: {}", padding_size);
      pkt_size + padding_size
    } else {
      usize::from(self.buffer[len])
        + usize::from(self.buffer[len + 1]) * 256
        + self.header_length
        + PROTO_FOOTER_CRC16
    };

    // if self.padding_4x {
    //   let padding_size = (4 - (expected_length % 4)) % 4;
    //   return Ok(expected_length + padding_size);
    // }

    Ok((expected_length, padding_size))
  }

  fn verify_crc_footer(&self) -> bool {
    let end_idx = self.expected_length;
    if self.header_version == HEADER_VERSION_STARK {
      warn!("CRC32 verification is not implemented for Stark protocol");
      false
    } else {
      let begin_idx = self.expected_length - PROTO_FOOTER_CRC16;
      let crc16 = LittleEndian::read_u16(&self.buffer[begin_idx..end_idx]);
      let crc_calc = calculate_crc16_modbus(&self.buffer[..begin_idx]);
      if crc16 == crc_calc {
        true
      } else {
        error!(
          "CRC16 verification failed, expected: {:04X}, calculated: {:04X}, expected_length: {:?}, buffer: {:02x?}",
          crc16, crc_calc, self.expected_length, &self.buffer[..end_idx]
        );
        false
      }
    }
  }

  fn parse_message(&self, payload: &[u8]) -> Result<(), ParseError> {
    match self.header_version {
      HEADER_VERSION_V2 => {
        let src_module = self.buffer[self.header_length - 3];
        let dst_module = self.buffer[self.header_length - 2];
        trace!(
          "Source module: {}, Destination module: {}, payload: {:?}",
          src_module,
          dst_module,
          payload
        );
        self.parse_message_for_header_v2(src_module, dst_module, payload)
      }
      _ => Err(ParseError::UnsupportedHeaderVersion(
        self.msg_type,
        self.header_version,
      )),
    }
  }

  #[allow(unused_variables, unreachable_code)]
  fn parse_message_for_header_v2(
    &self,
    src_module: u8,
    dst_module: u8,
    payload: &[u8],
  ) -> Result<(), ParseError> {
    let result = match self.msg_type {
      MsgType::EEGCap => {
        let message = EEGCapMessage::parse_message(src_module, dst_module, payload)?;
        ParsedMessage::EEGCap(message)
      }
      #[allow(unreachable_patterns)]
      _ => return Err(ParseError::UnknownProtoType(self.msg_type)),
    };

    #[cfg(feature = "examples")]
    match serde_json::to_string(&result) {
      Ok(json) => debug!("Decoded message: {:?}", json),
      Err(e) => return Err(ParseError::JsonError(e)),
    }

    // 通知消息
    self.notify_message(result);
    Ok(())
  }

  pub fn notify_message(&self, result: ParsedMessage) {
    let device_id = self.device_id.clone();

    handle_resp_message(device_id.clone(), &result);

    let tx = self.tx.clone();
    let _ = tx.send((device_id, result));
  }
}

pub(crate) fn handle_resp_message(device_id: String, message: &ParsedMessage) {
  match message {
    #[cfg(feature = "eeg-cap")]
    ParsedMessage::EEGCap(msg) => {
      crate::eeg_cap::data::handle_eeg_cap_message(device_id, msg);
    }
  }
}

#[cfg(not(target_family = "wasm"))]
#[cfg(test)]
mod tests {
  use futures::StreamExt;
  crate::cfg_import_logging!();

  use super::StreamType;
  use crate::proto::{enums::MsgType, msg_parser::Parser};
  use crate::utils::logging_desktop::init_logging;
  #[cfg(feature = "eeg-cap")]
  #[allow(unused_imports)]
  use crate::{generated::eeg_cap_proto, proto::eeg_cap::msg_builder::eeg_cap_msg_builder};

  fn _test() {
    init_logging(log::Level::Debug);
    let parser = Parser::new("test-device".into(), MsgType::EEGCap);
    let stream: StreamType = parser.message_stream();
    read_data(stream);
  }

  #[cfg(feature = "eeg-cap")]
  #[tokio::test]
  async fn eeg_cap_parser_test() {
    init_logging(log::Level::Debug);
    let mut parser = Parser::new("test-device".into(), MsgType::EEGCap);
    let stream: StreamType = parser.message_stream();
    parser.receive_data(&[
      66, 82, 78, 67, 2, 11, 121, 0, 0, 2, 0, 8, 1, 26, 117, 18, 115, 10, 113, 8, 176, 45, 18, 108,
      192, 0, 0, 79, 123, 241, 79, 160, 202, 79, 161, 203, 79, 189, 141, 79, 189, 235, 79, 118,
      236, 79, 104, 101, 79, 149, 65, 192, 0, 0, 128, 0, 0, 79, 141, 170, 79, 132, 128, 135, 35,
      214, 79, 85, 216, 22, 95, 245, 79, 181, 153, 133, 154, 43, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 207,
    ]);
    parser.receive_data(&[
      66, 82, 78, 67, 2, 11, 121, 0, 0, 2, 0, 8, 1, 26, 117, 18, 115, 10, 113, 8, 175, 106, 18,
      108, 192, 0, 0, 255, 169, 244, 255, 169, 171, 255, 169, 243, 255, 169, 118, 255, 170, 58,
      255, 170, 11, 255, 169, 196, 255, 169, 200, 192, 0, 0, 255, 169, 180, 255, 170, 69, 255, 169,
      215, 255, 170, 7, 255, 170, 130, 255, 169, 113, 255, 170, 97, 255, 170, 135, 192, 0, 0, 255,
      169, 152, 255, 170, 105, 255, 169, 178, 255, 169, 144, 255, 170, 114, 255, 169, 147, 255,
      170, 114, 255, 169, 240, 192, 0, 0, 255, 170, 64, 255, 170, 89, 255, 170, 111, 255, 170, 86,
      255, 170, 49, 255, 170, 133, 255, 170, 2, 255, 169, 216, 71, 113,
    ]);
    read_data(stream);
  }

  #[allow(dead_code)]
  fn read_data(mut stream: StreamType) {
    // 处理流中的消息
    tokio::spawn(async move {
      while let Some(result) = stream.next().await {
        match result {
          Ok(message) => {
            info!("Received message: {:?}", message);
          }
          Err(e) => {
            error!("Error receiving message: {:?}", e);
          }
        }
      }
      info!("Stream finished");
    });
  }
}
