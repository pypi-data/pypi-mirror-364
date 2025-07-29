pub mod c_utils;
pub mod constants;
pub mod enums;
pub mod lib;
pub mod structs;

#[cfg(feature = "ble-cbindgen")]
pub mod core_c;

cfg_if::cfg_if!(
  if #[cfg(feature = "ble-cbindgen")] {
  } else {
    pub mod core;
  }
);

#[cfg(feature = "ble-cbindgen")]
pub mod logging;
