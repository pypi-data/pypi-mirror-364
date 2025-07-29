use super::handler::*;
use crate::ble::core;
use crate::ble::lib::*;
use crate::neon::filter::*;
// use crate::proto::enums::MsgType;
use crate::utils::logging::LogLevel;
use crate::utils::logging_desktop::initialize_logging;

use neon::prelude::*;

crate::cfg_import_logging!();

// Main module exports
#[neon::main]
fn main(mut cx: ModuleContext) -> NeonResult<()> {
  cx.export_function("init_logging", init_logging)?;
  cx.export_function("init_ble_adapter", init_ble_adapter)?;
  cx.export_function("start_ble_scan", start_ble_scan)?;
  cx.export_function("stop_ble_scan", stop_ble_scan)?;
  cx.export_function("is_ble_scanning", is_ble_scanning)?;
  cx.export_function("connect_ble_device", connect_ble_device)?;
  cx.export_function("disconnect_ble_device", disconnect_ble_device)?;
  cx.export_function("set_adapter_state_callback", set_adapter_state_callback)?;
  cx.export_function("set_scan_result_callback", set_scan_result_callback)?; // 包含ManufacturerDataAdvertisementData
  #[rustfmt::skip]
  cx.export_function("set_device_discovered_callback", set_device_discovered_callback)?; // 不含ManufacturerDataAdvertisementData, 脑电帽BLE设备回调
  cx.export_function("set_connect_state_callback", set_connect_state_callback)?;
  cx.export_function("set_ble_device_info_callback", set_ble_device_info_callback)?;
  cx.export_function(
    "set_ble_battery_level_callback",
    set_ble_battery_level_callback,
  )?;
  cx.export_function("set_msg_resp_callback", set_msg_resp_callback)?;
  cx.export_function("set_tcp_stream_exit_callback", set_tcp_stream_exit_callback)?;
  cx.export_function("set_battery_level_callback", set_battery_level_callback)?;
  cx.export_function("did_receive_data", did_receive_data)?;
  cx.export_function("init_ble_parser", init_ble_parser)?;
  // cfg_if::cfg_if!(
  //   if #[cfg(feature = "oxyzen")] {
  //     use super::node_oyxz::*;
  //     cx.export_function("send_pair_cmd", send_pair_cmd)?;
  //   }
  // );
  cfg_if::cfg_if!(
    if #[cfg(feature = "eeg-cap")] {
      use super::node_ecap::*;
      // ble cmds
      cx.export_function("get_ble_device_info", get_ble_device_info)?;
      cx.export_function("get_wifi_status", get_wifi_status)?;
      cx.export_function("get_wifi_config", get_wifi_config)?;
      cx.export_function("set_ble_device_info", set_ble_device_info)?;
      cx.export_function("set_wifi_config", set_wifi_config)?;
      // mdns helpers
      cx.export_function("mdns_start_scan", mdns_start_scan)?;
      cx.export_function("mdns_stop_scan", mdns_stop_scan)?;
      cx.export_function("set_mdns_scan_result_callback", set_mdns_scan_result_callback)?;
      // tcp cmds
      cx.export_function("tcp_connect", tcp_connect)?;
      cx.export_function("tcp_disconnect", tcp_disconnect)?;
      cx.export_function("get_device_info", get_device_info)?;
      cx.export_function("get_battery_level", get_battery_level)?;
      cx.export_function("get_eeg_config", get_eeg_config)?;
      cx.export_function("set_eeg_config", set_eeg_config)?;
      cx.export_function("get_imu_config", get_imu_config)?;
      cx.export_function("set_imu_config", set_imu_config)?;
      cx.export_function("get_leadoff_config", get_leadoff_config)?;
      cx.export_function("start_eeg_stream", start_eeg_stream)?;
      cx.export_function("stop_eeg_stream", stop_eeg_stream)?;
      cx.export_function("start_imu_stream", start_imu_stream)?;
      cx.export_function("stop_imu_stream", stop_imu_stream)?;
      cx.export_function("start_leadoff_check", start_leadoff_check)?;
      cx.export_function("stop_leadoff_check", stop_leadoff_check)?;
      // data helpers
      cx.export_function("set_cfg", set_config)?;
      cx.export_function("get_eeg_buffer_arr", get_eeg_buffer_arr)?;
      cx.export_function("get_imu_buffer_json", get_imu_buffer_json)?;

      cx.export_function("set_env_noise_cfg", set_env_noise_config)?;
      cx.export_function("set_easy_eeg_filter_cfg", set_easy_eeg_filter_config)?;
      cx.export_function("apply_easy_mode_sosfiltfilt", apply_easy_mode_sosfiltfilt)?;
      cx.export_function("apply_easy_mode_filters", apply_easy_mode_filters)?;

      cx.export_function("sos_create_notch_filter", sos_create_notch_filter)?;
      cx.export_function("sos_create_lowpass", sos_create_lowpass)?;
      cx.export_function("sos_create_highpass", sos_create_highpass)?;
      cx.export_function("sos_create_bandpass", sos_create_bandpass)?;
      cx.export_function("sos_create_bandstop", sos_create_bandstop)?;
      cx.export_function("sosfiltfilt_apply", sosfiltfilt_apply)?;

      cx.export_function("create_lowpass", create_lowpass)?;
      cx.export_function("create_highpass", create_highpass)?;
      cx.export_function("create_bandpass", create_bandpass)?;
      cx.export_function("create_bandstop", create_bandstop)?;
      cx.export_function("apply_lowpass", apply_lowpass)?;
      cx.export_function("apply_highpass", apply_highpass)?;
      cx.export_function("apply_bandpass", apply_bandpass)?;
      cx.export_function("apply_bandstop", apply_bandstop)?;

      cx.export_function("fftfreq", fftfreq)?;
      cx.export_function("get_filtered_freq", get_filtered_freq)?;
      cx.export_function("get_filtered_fft", get_filtered_fft)?;
    }
  );
  Ok(())
}

// Initialize  logging
fn init_logging(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let log_level: u8 = (cx.argument::<JsNumber>(0)?.value(&mut cx) as u8)
    .clamp(LogLevel::min_value(), LogLevel::max_value());
  initialize_logging(log_level.into());
  Ok(cx.undefined())
}

// Initialize BLE adapter with logging
fn init_ble_adapter(mut cx: FunctionContext) -> JsResult<JsPromise> {
  JsPromiseManager::new(&mut cx).execute(|| ble_init_adapter().map_err(|e| e.to_string()))
}

// Start BLE scan with UUID filtering
fn start_ble_scan(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let uuids = cx.argument::<JsArray>(0)?;
  let uuids_vec = parse_uuids(&mut cx, uuids)?;
  JsPromiseManager::new(&mut cx)
    .execute(|| start_scan_with_uuids(uuids_vec).map_err(|e| e.to_string()))
}

// Stop BLE scan
fn stop_ble_scan(mut cx: FunctionContext) -> JsResult<JsPromise> {
  JsPromiseManager::new(&mut cx).execute(|| stop_scan().map_err(|e| e.to_string()))
}

fn is_ble_scanning(mut cx: FunctionContext) -> JsResult<JsBoolean> {
  let scanning = is_scanning();
  Ok(cx.boolean(scanning))
}

fn connect_ble_device(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let device_id = cx.argument::<JsString>(0)?.value(&mut cx);
  let device_id = device_id.as_str();
  let promise_manager = JsPromiseManager::new(&mut cx);
  promise_manager.execute(move || sync_connect_ble(device_id).map_err(|e| e.to_string()))
}

fn disconnect_ble_device(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let device_id = cx.argument::<JsString>(0)?.value(&mut cx);
  let device_id = device_id.as_str();
  let promise_manager = JsPromiseManager::new(&mut cx);
  promise_manager.execute(move || sync_disconnect_ble(device_id).map_err(|e| e.to_string()))
}

// Set adapter state callback
fn set_adapter_state_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback(|callback| {
    core::set_adapter_state_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set adapter state callback: {:?}", err)),
  }
}

// set_scan_result_callback
fn set_scan_result_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback(|callback| {
    core::set_scan_result_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set scan result callback: {:?}", err)),
  }
}

// set_device_discovered_callback
fn set_device_discovered_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback(|callback| {
    core::set_device_discovered_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!(
      "Failed to set discovery result callback: {:?}",
      err
    )),
  }
}

// Set connection state callback
fn set_connect_state_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback_with_id(|callback| {
    core::set_connection_state_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!(
      "Failed to set connection state callback: {:?}",
      err
    )),
  }
}

// Set device info callback
fn set_ble_device_info_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback_with_id(|callback| {
    core::set_device_info_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set device info callback: {:?}", err)),
  }
}

// Set battery level callback
fn set_ble_battery_level_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback_with_id(|callback| {
    core::set_battery_level_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set battery level callback: {:?}", err)),
  }
}

// ==================== Neon 类导出示例 (注释掉，仅作参考) ====================

/*
注意：以下代码展示了在Neon中导出类的方法，但根据当前Neon版本可能需要调整语法。

在Neon 1.0中，推荐的方法是：

1. 使用 JsBox 包装Rust结构体
2. 通过函数导出类的构造器和方法
3. 在JavaScript端创建类的包装

示例代码：

```rust
use neon::prelude::*;

// 定义Rust结构体
pub struct EEGDevice {
    id: String,
    name: String,
    is_connected: bool,
    sample_rate: u32,
}

impl EEGDevice {
    fn new(id: String, name: String) -> Self {
        Self {
            id,
            name,
            is_connected: false,
            sample_rate: 250,
        }
    }
}

impl Finalize for EEGDevice {}

// 构造函数
fn eeg_device_new(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
    let id = cx.argument::<JsString>(0)?.value(&mut cx);
    let name = cx.argument::<JsString>(1)?.value(&mut cx);
    let device = EEGDevice::new(id, name);
    Ok(cx.boxed(device))
}

// getter方法
fn eeg_device_get_id(mut cx: FunctionContext) -> JsResult<JsString> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.string(&this.id))
}

fn eeg_device_get_name(mut cx: FunctionContext) -> JsResult<JsString> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.string(&this.name))
}

fn eeg_device_is_connected(mut cx: FunctionContext) -> JsResult<JsBoolean> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.boolean(this.is_connected))
}

fn eeg_device_connect(mut cx: FunctionContext) -> JsResult<JsUndefined> {
    let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
    this.is_connected = true;
    Ok(cx.undefined())
}

fn eeg_device_disconnect(mut cx: FunctionContext) -> JsResult<JsUndefined> {
    let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
    this.is_connected = false;
    Ok(cx.undefined())
}

// 在主模块中导出这些函数
// cx.export_function("eeg_device_new", eeg_device_new)?;
// cx.export_function("eeg_device_get_id", eeg_device_get_id)?;
// cx.export_function("eeg_device_get_name", eeg_device_get_name)?;
// cx.export_function("eeg_device_is_connected", eeg_device_is_connected)?;
// cx.export_function("eeg_device_connect", eeg_device_connect)?;
// cx.export_function("eeg_device_disconnect", eeg_device_disconnect)?;
```

然后在JavaScript端创建类包装：

```javascript
// 在JavaScript/TypeScript中创建类包装
class EEGDevice {
  constructor(id, name) {
    this._handle = nativeModule.eeg_device_new(id, name);
  }

  getId() {
    return nativeModule.eeg_device_get_id(this._handle);
  }

  getName() {
    return nativeModule.eeg_device_get_name(this._handle);
  }

  isConnected() {
    return nativeModule.eeg_device_is_connected(this._handle);
  }

  connect() {
    return nativeModule.eeg_device_connect(this._handle);
  }

  disconnect() {
    return nativeModule.eeg_device_disconnect(this._handle);
  }
}

module.exports = { EEGDevice };
```

这种方式的优势：
1. 更好的类型安全
2. 更清晰的API
3. 更容易调试
4. 支持继承和多态

Neon 1.0的主要变化：
- 移除了旧的class宏
- 推荐使用JsBox和函数导出
- 更强的类型检查
- 更好的错误处理

*/
