// extern crate winapi;
use super::string_utils;

// use std::ffi::OsString;
// use std::os::windows::ffi::OsStringExt;
// use std::ptr;
crate::cfg_import_logging!();
// use winapi::ctypes::wchar_t;
// use winapi::shared::guiddef::GUID;
// use winapi::shared::minwindef::DWORD;
// use winapi::um::errhandlingapi::GetLastError;
// use winapi::um::handleapi::INVALID_HANDLE_VALUE;
// use winapi::um::setupapi::{SetupDiEnumDeviceInfo, SetupDiGetClassDevsW, SetupDiGetDeviceRegistryPropertyW};

pub fn get_win_system_uuid(desired_length: usize) -> Option<String> {
  // Get the UUID from the machine_uid crate
  let uuid: String = machine_uid::get().ok()?; // Handle possible errors from get()

  // Remove dashes from the UUID
  let uuid_no_dashes = uuid.replace("-", "").to_uppercase();

  trace!("win uuid: {:?}", uuid_no_dashes);

  // Pad or truncate the UUID to the desired length
  let padded_uuid = string_utils::pad_or_truncate(uuid_no_dashes, desired_length);

  trace!("padded uuid: {:?}", padded_uuid);

  // Return the processed UUID
  Some(padded_uuid)
}

// pub fn get_win_system_uuid2(desired_length: usize) -> Option<String> {
//     unsafe {
//         let guid: GUID = GUID {
//             Data1: 0,
//             Data2: 0,
//             Data3: 0,
//             Data4: [0; 8],
//         };
//           // 使用 null_mut() 作为 HWND 的默认值
//         let device_info_set = SetupDiGetClassDevsW(&guid, ptr::null_mut(), ptr::null_mut(), 0);

//         if device_info_set == INVALID_HANDLE_VALUE {
//             error!("Failed to get device info set.");
//             return None;
//         }

//         trace!("device_info_set: {:?}", device_info_set);
//         let mut device_info_data = winapi::um::setupapi::SP_DEVINFO_DATA {
//             cbSize: std::mem::size_of::<winapi::um::setupapi::SP_DEVINFO_DATA>() as DWORD,
//             ClassGuid: GUID {
//                 Data1: 0,
//                 Data2: 0,
//                 Data3: 0,
//                 Data4: [0; 8],
//             },
//             DevInst: 0,
//             Reserved: 0,
//         };

//         if SetupDiEnumDeviceInfo(device_info_set, 0, &mut device_info_data) == 0 {
//             let error_code = GetLastError();
//             error!("Failed to enumerate device info. Error code: {}", error_code);
//             return None;
//         }

//         let mut buffer: [wchar_t; 256] = [0; 256];
//         let mut required_size: DWORD = 0;

//         if SetupDiGetDeviceRegistryPropertyW(
//             device_info_set,
//             &mut device_info_data,
//             0x00000008,
//             &mut required_size,
//             buffer.as_mut_ptr() as *mut u8,
//             buffer.len() as DWORD,
//             &mut required_size,
//         ) == 0
//         {
//             error!("Failed to get device registry property.");
//             return None;
//         }

//         let uuid = OsString::from_wide(&buffer).to_string_lossy().into_owned();
//         if uuid.is_empty() || uuid == "00000000-0000-0000-0000-000000000000" {
//             error!("Failed to get device registry property.");
//             return None;
//         }
//         trace!("win uuid: {:?}", uuid);
//         let padding_uuid = string_utils::pad_or_truncate(uuid, desired_length);
//         Some(padding_uuid)
//     }
// }

// pub fn get_win_system_uuid(desired_length: usize)-> Option<String> {
//     // 获取系统 ID
//     let system_id = SystemIdentification::GetSystemIdForPublisher()?;

//     // 将系统 ID 编码为十六进制字符串
//     if let Some(id) = system_id.Id() {
//         trace!("System ID: {:?}", id);
//         // let encoded = CryptographicBuffer::EncodeToHexString(&id)?;
//         // let system_id_str = encoded.to_string_lossy();
//         // let uuid = system_id_str.to_uppercase();
//         // trace!("Unique System UUID: {}", uuid);
//         // if uuid.is_empty() || uuid == "00000000-0000-0000-0000-000000000000" {
//         //     error!("Failed to get device registry property.");
//         //     return None;
//         // }
//         // trace!("win uuid: {:?}", uuid);
//         // let padding_uuid = string_utils::pad_or_truncate(uuid, desired_length);
//         // Some(padding_uuid)
//         None
//     } else {
//         error!("Failed to retrieve System ID.");
//         None
//     }
// }

#[cfg(test)]
mod tests {
  use crate::utils::logging::init_logging;

  use super::get_win_system_uuid;
  use tracing::*;
  use tracing_subscriber::filter::LevelFilter;

  #[test]
  fn get_win_system_uuid_test() {
    init_logging(log::Level::Debug);
    let serial = get_win_system_uuid(16);
    match serial {
      Some(s) => trace!("System UUID: {}", s),
      None => trace!("Failed to get System UUID"),
    }
  }
}
