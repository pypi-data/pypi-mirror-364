crate::cfg_import_logging!();

#[cfg(feature = "eeg-cap")]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn parse_32ch_eeg_data(data: &[u8], gain: i32) -> Vec<f64> {
  if (data.len()) != 108 {
    // (32+4) * 3 = 108 bytes, 32 channels, 4 bytes for stat
    error!("Invalid data length: {:?}", data.len());
    return vec![];
  }
  let singal_gain =
    crate::generated::eeg_cap_proto::EegSignalGain::try_from(gain).unwrap_or_default();
  let gain = singal_gain.get_gain() as f64;
  static REF_VOLTAGE: f64 = 2.0 * 4.5;
  let scale_factor: f64 = (2.0f64).powi(24);
  let lsb: f64 = (REF_VOLTAGE / gain) / scale_factor;
  parse_adc_data(data, lsb, true)
}

#[cfg(feature = "edu")]
#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn parse_afe_data(data: &[u8], gain: f64) -> Vec<f64> {
  static REF_VOLTAGE: f64 = 2.42;
  let scale_factor: f64 = (2.0f64).powi(23) - 1.0;
  let lsb: f64 = (REF_VOLTAGE / gain) / scale_factor;
  parse_adc_data(data, lsb, false)
}

pub fn parse_adc_data(data: &[u8], lsb: f64, skip: bool) -> Vec<f64> {
  if (data.len() % 3) != 0 {
    error!("Invalid data length: {:?}", data.len());
    return vec![];
  }

  data
    .chunks(3)
    .enumerate()
    .filter_map(|(i, chunk)| {
      // 跳过无效的 stat 数据
      if skip && i % 9 == 0 {
        return None;
      }
      let value = match chunk {
        [b1, b2, b3] => to_32bit_signed(*b1, *b2, *b3),
        _ => 0,
      };
      let voltage = value as f64 * lsb * 10f64.powi(6); // V to uV
      Some(voltage)
    })
    .collect()
}

// 24-bit signed integer (3 bytes) to 32-bit signed integer (4 bytes)
pub fn to_32bit_signed(a: u8, b: u8, c: u8) -> i32 {
  let mut bytes = [0; 4];
  bytes[1] = a;
  bytes[2] = b;
  bytes[3] = c;
  // 手动处理符号扩展
  if a & 0x80 != 0 {
    bytes[0] = 0xFF;
  }
  i32::from_be_bytes(bytes)
}

pub fn parse_imu_data(data: &[u8]) -> Vec<i16> {
  if data.len() % 6 != 0 {
    error!("Invalid data length: {}", data.len());
    return vec![];
  }

  data
    .chunks_exact(2)
    .map(|chunk| i16::from_le_bytes([chunk[0], chunk[1]]))
    .collect()
}
