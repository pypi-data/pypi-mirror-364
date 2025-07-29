#![allow(non_camel_case_types)]

use crate::impl_enum_conversion;

// crate::cfg_import_logging!();

impl_enum_conversion!(
  EegSampleRate,
  SR_None = 0,
  SR_250Hz = 1,
  SR_500Hz = 2,
  SR_1000Hz = 3,
  SR_2000Hz = 4
);

// 设备默认值是GAIN_6
impl_enum_conversion!(
  EegSignalGain,
  GAIN_NONE = 0,
  GAIN_1 = 1, // 原始信号
  GAIN_2 = 2, // 原始信号放大2倍
  GAIN_4 = 3,
  GAIN_6 = 4,
  GAIN_8 = 5,
  GAIN_12 = 6,
  GAIN_24 = 7
);

// 设备默认值是NORMAL
impl_enum_conversion!(
  EegSignalSource,
  SIGNAL_NONE = 0,
  NORMAL = 1,      // 用户EEG输入信号
  SHORTED = 2,     // INxP, INxN短接， 用于测量偏置或噪声
  MVDD = 3,        // 供电检测
  TEST_SIGNAL = 4  // 内部测试信号，为1Hz的方波
);

impl_enum_conversion!(ImuSampleRate, SR_NONE = 0, SR_50Hz = 1, SR_100Hz = 2);

impl_enum_conversion!(
  WiFiSecurity,
  SECURITY_NONE = 0,
  SECURITY_OPEN = 1,
  SECURITY_WPA2_MIXED_PSK = 2
);

impl_enum_conversion!(
  LeadOffChip,
  None = 0,
  Chip1 = 1,
  Chip2 = 2,
  Chip3 = 3,
  Chip4 = 4
);

impl_enum_conversion!(
  LeadOffFreq,
  None = 0,
  Dc = 1,
  Ac7p8hz = 2,
  Ac31p2hz = 3,
  AcFdr4 = 4
);

impl_enum_conversion!(
  LeadOffCurrent,
  None = 0,
  Cur6nA = 1,
  Cur24nA = 2,
  Cur6uA = 3,
  Cur24uA = 4
);

impl LeadOffChip {
  pub fn get_next_chip(self) -> LeadOffChip {
    ((self as u8 % 4) + 1).into()
  }

  pub fn get_imp_offset(self) -> usize {
    match self {
      LeadOffChip::Chip1 => 0,
      LeadOffChip::Chip2 => 8,
      LeadOffChip::Chip3 => 16,
      LeadOffChip::Chip4 => 24,
      _ => 0,
    }
  }
}

impl LeadOffCurrent {
  #[allow(non_snake_case)]
  pub fn get_current_uA(self) -> f64 {
    match self {
      LeadOffCurrent::Cur6nA => 0.006,
      LeadOffCurrent::Cur24nA => 0.024,
      LeadOffCurrent::Cur6uA => 6.0,
      LeadOffCurrent::Cur24uA => 24.0,
      _ => 0.006,
    }
  }
}
