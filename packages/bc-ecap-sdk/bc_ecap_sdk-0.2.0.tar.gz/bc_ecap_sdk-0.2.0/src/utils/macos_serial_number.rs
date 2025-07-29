use std::ffi::{c_char, CStr};
use tracing::trace;
use CoreFoundation_sys::{
  kCFAllocatorDefault, kCFStringEncodingUTF8, CFStringCreateWithCString, CFStringGetCString,
  CFStringRef,
};
use IOKit_sys::{
  kIOMasterPortDefault, IOObjectRelease, IORegistryEntryCreateCFProperty,
  IOServiceGetMatchingService, IOServiceMatching,
};

use super::string_utils;

// other implementations, https://github.com/Hanaasagi/machine-uid/blob/master/src/lib.rs
// ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID
// ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformSerialNumber
pub fn get_serial_num(desired_length: usize) -> Option<String> {
  unsafe {
    let platform_expert = IOServiceGetMatchingService(
      kIOMasterPortDefault,
      IOServiceMatching(b"IOPlatformExpertDevice\0".as_ptr() as *const c_char),
    );
    if platform_expert != 0 {
      let key = CFStringCreateWithCString(
        kCFAllocatorDefault,
        // b"IOPlatformUUID\0".as_ptr() as *const c_char,
        b"IOPlatformSerialNumber\0".as_ptr() as *const c_char,
        kCFStringEncodingUTF8,
      );
      let serial_number_as_cfstring =
        IORegistryEntryCreateCFProperty(platform_expert, key, kCFAllocatorDefault, 0);
      IOObjectRelease(platform_expert);

      if !serial_number_as_cfstring.is_null() {
        let buffer = [0u8; 256]; // 256 是一个足够大的缓冲区，用于存储序列号
        let success = CFStringGetCString(
          serial_number_as_cfstring as CFStringRef,
          buffer.as_ptr() as *mut c_char,
          buffer.len() as i64,
          kCFStringEncodingUTF8,
        );
        if success != 0 {
          let c_str = CStr::from_ptr(buffer.as_ptr() as *const c_char);
          let mut full_serial = c_str.to_string_lossy().into_owned();
          trace!("macos serial: {:?}", full_serial);
          full_serial = string_utils::pad_or_truncate(full_serial, desired_length);
          return Some(full_serial);
        }
      }
    }
  }
  None
}

#[cfg(test)]
mod tests {
  use crate::utils::logging::init_logging;

  use super::get_serial_num;
  crate::cfg_import_logging!();
  use tracing_subscriber::filter::LevelFilter;

  #[test]
  fn get_serial_num_test() {
    init_logging(log::Level::Debug);
    let serial = get_serial_num(16);
    match serial {
      Some(s) => trace!("Serial Number: {}", s),
      None => trace!("Failed to get Serial Number"),
    }
  }
}
