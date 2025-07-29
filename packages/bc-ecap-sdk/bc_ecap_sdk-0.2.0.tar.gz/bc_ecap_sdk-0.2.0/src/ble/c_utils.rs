#![allow(clippy::not_unsafe_ptr_arg_deref)]
use btleplug::{api::BDAddr, platform::PeripheralId};
use std::ffi::{c_char, CStr, CString};
use uuid::Uuid;

use crate::utils::c_utils::CStringExt;

crate::cfg_import_logging!();

impl CStringExt for BDAddr {
  fn to_c_string(&self) -> CString {
    self.to_string().to_c_string()
  }
  fn to_cbytes(&self) -> *const c_char {
    self.to_string().to_cbytes()
  }
}
pub trait PeripheralIdExt {
  fn to_cbytes(&self) -> *const c_char;
}

impl PeripheralIdExt for PeripheralId {
  fn to_cbytes(&self) -> *const c_char {
    let peripheral_id_str = format!("{}", self);
    peripheral_id_str.to_cbytes()
  }
}

pub fn to_peripheral_id(id: &str) -> PeripheralId {
  // info!("to_peripheral_id: {:?}", id);
  match () {
    #[cfg(any(target_os = "macos", target_os = "ios"))]
    () => PeripheralId::from(uuid::Uuid::parse_str(id).unwrap()),

    #[cfg(target_os = "linux")]
    () => {
      let id = format!("/org/bluez/{}", id);
      // let device_id = bluez_async::DeviceId::new(&id);
      // PeripheralId::from(device_id)
      PeripheralId::from_str(&id)
    }

    #[cfg(any(target_os = "windows", target_os = "android"))]
    () => PeripheralId::from(BDAddr::from_str_delim(id).unwrap()),

    #[cfg(not(any(
      target_os = "macos",
      target_os = "ios",
      target_os = "linux",
      target_os = "windows",
      target_os = "android"
    )))]
    () => panic!("Unsupported operating system"),
  }
}

pub fn to_peripheral_id_with_char(id: *const c_char) -> PeripheralId {
  // let id_str = unsafe { std::str::from_utf8_unchecked(std::slice::from_raw_parts(id as *const u8, 36)) };
  // info!("to_peripheral_id, id_str: {:?}", id_str);

  // 由于 `id` 是一个 `*const c_char` 类型的指针，我们需要将其转换为 `CStr`。
  // `CStr` 处理的是 C 风格的字符串，即以 null 结尾的字符数组。

  let id_str = unsafe { CStr::from_ptr(id) };
  // info!("to_peripheral_id, id_str: {:?}", id_str);

  // 将 `CStr` 转换为 Rust 字符串切片
  let id_str = id_str.to_str().expect("Invalid UTF-8 sequence");
  // info!("to_peripheral_id, id_str: {:?}", id_str);

  to_peripheral_id(id_str)
}

// 先解析为 MAC 地址
// 将 MAC 地址转换为自定义格式的 UUID
// let uuid_bytes = BDAddr::into_inner(bd_addr);
// let uuid = Uuid::from_bytes([
//     0x00, 0x00, uuid_bytes[0], uuid_bytes[1],
//     uuid_bytes[2], uuid_bytes[3], uuid_bytes[4], uuid_bytes[5],
//     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
// ]);

pub fn convert_to_uuids(
  services: *const *const c_char,
) -> Result<Vec<Uuid>, Box<dyn std::error::Error>> {
  let mut uuids = Vec::new();

  // 将指针转换为 Rust 的 slice
  let mut current = services;

  unsafe {
    while !(*current).is_null() {
      // 将 C 字符串转换为 Rust 字符串
      let c_str = CStr::from_ptr(*current);
      let str_slice = c_str.to_str()?;
      trace!("convert_to_uuids, str_slice: {:?}", str_slice);

      // 尝试解析字符串为 UUID
      match Uuid::parse_str(str_slice) {
        Ok(uuid) => uuids.push(uuid),
        Err(e) => {
          warn!("Failed to parse UUID from string '{}': {:?}", str_slice, e);
          return Err(Box::new(e));
        }
      }

      // 移动到下一个指针
      current = current.add(1);
    }
  }
  debug!("convert_to_uuids, uuids: {:?}", uuids);
  Ok(uuids)
}

/// 释放 C 字符串
#[no_mangle]
pub extern "C" fn free_string(s: *const c_char) {
  if !s.is_null() {
    // Recreate the CString from the raw pointer and drop it
    unsafe {
      let _ = CString::from_raw(s as *mut c_char);
    }
  }
}
