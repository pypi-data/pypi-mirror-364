crate::cfg_import_logging!();

use super::{constants::*, enums::*};

use crate::utils::crc::{calculate_crc16_modbus, calculate_crc32};

pub struct Builder {
  pub msg_type: MsgType,
  header_version: u8,
  header_flag: u8,
  header_prefix: Vec<u8>,
}

impl Builder {
  pub fn new(msg_type: MsgType) -> Self {
    let (project_id, header_version, header_length) = get_project_info(msg_type);
    let header_flag = 0;
    let payload_version = 1;
    let mut header_prefix = Vec::new();
    if msg_type == MsgType::Stark {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC_BNCP);
    } else {
      header_prefix.extend_from_slice(&PROTO_HEADER_MAGIC);
      header_prefix.push(header_version);
      header_prefix.push(project_id);
      if header_version == HEADER_VERSION_V2 && header_length == 12 {
        header_prefix.push(payload_version);
      }
    }
    debug!(
      "BuilderType: {:?}, Project ID: 0x{:x}, Header version: {}, header_prefix: {:x?}",
      msg_type, project_id, header_version, header_prefix,
    );

    Builder {
      msg_type,
      header_version,
      header_flag,
      header_prefix,
    }
  }

  pub fn build_stark_msg(&self, payload: &[u8], src_module: u8, dst_module: u8) -> Vec<u8> {
    let mut msg = Vec::new();
    msg.extend_from_slice(&self.header_prefix);
    msg.push(dst_module);
    msg.push(src_module);
    msg.extend_from_slice(&(payload.len() as u16).to_be_bytes());

    msg.extend_from_slice(payload);
    // payload的长度为4的倍数，否则需要补0
    if payload.len() % 4 != 0 {
      let padding_size: usize = (4 - (payload.len() % 4)) % 4;
      msg.extend(vec![0; padding_size]);
    }

    let crc32 = calculate_crc32(&msg);
    msg.extend_from_slice(&crc32.to_be_bytes());

    // 将消息编码为十六进制字符串，并用逗号分隔
    // let hex_string = msg
    //   .iter()
    //   .map(|&num| format!("0x{:02x}", num))
    //   .collect::<Vec<String>>()
    //   .join(",");
    // info!("build_stark_msg: {}", hex_string);

    msg
  }

  pub fn build(&self, payload: &[u8]) -> Vec<u8> {
    self.build_msg(payload, 0, 0)
  }

  pub fn build_msg(&self, payload: &[u8], src_module: u8, dst_module: u8) -> Vec<u8> {
    self.wrap_message(payload, src_module, dst_module)
  }

  pub fn wrap_message(&self, payload: &[u8], src_module: u8, dst_module: u8) -> Vec<u8> {
    let mut msg = Vec::new();
    msg.extend_from_slice(&self.header_prefix);
    msg.extend_from_slice(&(payload.len() as u16).to_le_bytes());
    // info!("header_version: {}", self.header_version);
    if self.header_version == HEADER_VERSION_V2 {
      msg.push(src_module);
      msg.push(dst_module);
      msg.push(self.header_flag);
    }
    msg.extend_from_slice(payload);
    let crc16 = calculate_crc16_modbus(&msg);
    msg.extend_from_slice(&crc16.to_le_bytes());
    msg
  }
}
