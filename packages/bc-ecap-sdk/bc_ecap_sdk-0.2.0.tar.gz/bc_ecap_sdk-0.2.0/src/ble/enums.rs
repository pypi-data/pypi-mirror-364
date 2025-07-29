#[cfg(not(feature = "cbindgen"))]
use crate::impl_enum_conversion;

#[cfg(not(feature = "cbindgen"))]
impl_enum_conversion!(
  CentralAdapterState,
  Unknown = 0,
  PoweredOn = 1,
  PoweredOff = 2
);

#[cfg(feature = "cbindgen")]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum CentralAdapterState {
  Unknown = 0,
  PoweredOn = 1,
  PoweredOff = 2,
}

#[cfg(feature = "cbindgen")]
impl From<CentralAdapterState> for u8 {
  fn from(val: CentralAdapterState) -> Self {
    val as u8
  }
}

#[cfg(feature = "cbindgen")]
impl From<u8> for CentralAdapterState {
  fn from(value: u8) -> Self {
    match value {
      0 => CentralAdapterState::Unknown,
      1 => CentralAdapterState::PoweredOn,
      2 => CentralAdapterState::PoweredOff,
      _ => panic!("Invalid value for enum CentralAdapterState"),
    }
  }
}

#[cfg(not(feature = "cbindgen"))]
impl_enum_conversion!(
  ConnectionState,
  Connecting = 0,
  Connected = 1,
  Disconnecting = 2,
  Disconnected = 3
);

#[cfg(feature = "cbindgen")]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum ConnectionState {
  Connecting = 0,
  Connected = 1,
  Disconnecting = 2,
  Disconnected = 3,
}

#[cfg(feature = "cbindgen")]
impl From<ConnectionState> for u8 {
  fn from(val: ConnectionState) -> Self {
    val as u8
  }
}

#[cfg(feature = "cbindgen")]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum AfeSr {
  AfeNone = 0,
  AfeOff = 1,
  AfeSr128hz = 2,
  AfeSr256hz = 3,
}

#[cfg(feature = "cbindgen")]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum ImuSr {
  ImuNone = 0,
  ImuOff = 1,
  ImuSr25hz = 2,
  ImuSr50hz = 3,
  ImuSr100hz = 4,
  ImuSr200hz = 5,
  ImuSr400hz = 6,
  ImuSr800hz = 7,
}

#[cfg(feature = "cbindgen")]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum PpgUr {
  PpgNone = 0,
  PpgOff = 1,
  PpgUr1hz = 2,
  PpgUr5hz = 3,
  PpgUr25hz = 4,
  PpgUr50hz = 5,
  PpgUr100hz = 6,
}

#[cfg(feature = "cbindgen")]
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum PpgMode {
  None = 0,
  Raw = 1,
  Algo = 2,
  Spo2 = 3,
  Hr = 4,
  Hrv = 5,
}
