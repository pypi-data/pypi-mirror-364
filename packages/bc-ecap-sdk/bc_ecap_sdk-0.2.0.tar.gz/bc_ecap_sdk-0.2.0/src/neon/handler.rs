use crate::ble::core as ble;
use crate::ble::enums::ConnectionState;
use crate::ble::lib::*;
use crate::ble::structs::{BLEDeviceInfo, ScanResult};
use crate::callback::callback_rs as cb;
use crate::proto::enums::MsgType;
use crate::proto::msg_parser::Parser;
use crate::utils::mdns::MdnsScanResult;
use crate::utils::runtime::get_runtime;
use crate::utils::tcp_client::TcpClient;
use btleplug::api::CentralState;
use neon::prelude::*;
use neon::types::buffer::TypedArray;
use neon::types::Deferred;
use parking_lot::Mutex;
use std::collections::HashMap;
use std::sync::Arc;
use uuid::Uuid;

crate::cfg_import_logging!();

// --- Helper Structs and Functions ---

// Centralized callback handler
pub struct JsCallbackManager {
  channel: Arc<Channel>,
  callback: Arc<Root<JsFunction>>,
}

impl JsCallbackManager {
  pub fn new(cx: &mut FunctionContext, index: usize) -> NeonResult<Self> {
    let callback = cx.argument::<JsFunction>(index)?;
    Ok(Self {
      channel: Arc::new(cx.channel()),
      callback: Arc::new(callback.root(cx)),
    })
  }

  pub fn register_callback<T, F>(self, handler: F) -> Result<(), String>
  where
    T: 'static + Send + JsConvertible + std::fmt::Debug,
    F: FnOnce(Box<dyn Fn(T) + Send + Sync>) -> Result<(), String>,
  {
    let callback = self.callback.clone(); // Strong reference
    let channel = self.channel.clone();

    let boxed_callback: Box<dyn Fn(T) + Send + Sync> = Box::new(move |value: T| {
      let channel = channel.clone();
      let cb: Arc<Root<JsFunction>> = callback.clone();
      channel.send(move |mut task_cx| {
        let callback_root = cb.clone(); // Keep strong reference alive
        let callback = callback_root.to_inner(&mut task_cx);
        let js_value = value.into_js_value(&mut task_cx)?;
        let undefined = task_cx.undefined();
        callback.call(&mut task_cx, undefined, [js_value])?;
        Ok(())
      });
    });

    handler(boxed_callback)?;
    Ok(())
  }

  pub fn register_callback_with_id<T, F>(self, handler: F) -> Result<(), String>
  where
    T: 'static + Send + JsConvertibleWithId + std::fmt::Debug,
    F: FnOnce(Box<dyn Fn(String, T) + Send + Sync>) -> Result<(), String>,
  {
    let callback = self.callback.clone(); // Strong reference
    let channel = self.channel.clone();

    let boxed_callback: Box<dyn Fn(String, T) + Send + Sync> =
      Box::new(move |device_id, value: T| {
        let channel = channel.clone();
        let cb: Arc<Root<JsFunction>> = callback.clone();
        channel.send(move |mut task_cx| {
          let callback_root = cb.clone(); // Keep strong reference alive
          let callback = callback_root.to_inner(&mut task_cx);
          let js_value = value.into_js_value(&mut task_cx, device_id)?;
          let undefined = task_cx.undefined();
          callback.call(&mut task_cx, undefined, [js_value])?;
          Ok(())
        });
      });

    handler(boxed_callback)?;
    Ok(())
  }
}

// async promise handler
pub struct JsPromiseManager<'a> {
  deferred: Deferred,
  promise: Handle<'a, JsPromise>,
  channel: Channel,
}

impl<'a> JsPromiseManager<'a> {
  pub fn new(cx: &mut FunctionContext<'a>) -> Self {
    let (deferred, promise) = cx.promise();
    Self {
      deferred,
      promise,
      channel: cx.channel(),
    }
  }

  pub fn execute<F, T>(self, operation: F) -> JsResult<'a, JsPromise>
  where
    F: FnOnce() -> Result<T, String>,
    T: 'static + Send + IntoJsResult,
  {
    match operation() {
      Ok(result) => {
        self
          .deferred
          .settle_with(&self.channel, move |mut cx| result.into_js_result(&mut cx));
      }
      Err(err_msg) => {
        self
          .deferred
          .settle_with::<JsError, _>(&self.channel, move |mut cx| cx.throw_error(err_msg));
      }
    }
    Ok(self.promise)
  }
}

// Parse UUIDs from JS array
pub fn parse_uuids(cx: &mut FunctionContext, uuids: Handle<JsArray>) -> NeonResult<Vec<Uuid>> {
  (0..uuids.len(cx))
    .map(|i| {
      let uuid_str = uuids.get::<JsString, _, _>(cx, i)?.value(cx);
      let uuid = match Uuid::parse_str(&uuid_str) {
        Ok(uuid) => uuid,
        Err(e) => return cx.throw_error(format!("Invalid UUID: {}", e)),
      };
      Ok(uuid)
    })
    .collect::<Result<Vec<Uuid>, _>>()
}

// --- Type Conversion Traits ---

pub trait JsConvertible {
  fn into_js_value<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue>;
}

pub trait JsConvertibleWithId {
  fn into_js_value<'a, C: Context<'a>>(
    self,

    cx: &mut C,
    device_id: String,
  ) -> JsResult<'a, JsValue>;
}

impl JsConvertible for CentralState {
  fn into_js_value<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue> {
    Ok(cx.number(self as u8 as f64).upcast())
  }
}

macro_rules! impl_js_convertible_for_numbers {
  ($($t:ty),*) => {
    $(
      impl JsConvertible for $t {
        fn into_js_value<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue> {
          Ok(cx.number(self as f64).upcast())
        }
      }
    )*
  };
}

impl_js_convertible_for_numbers!(i8, i16, i32, i64, u8, u16, u32, u64, f32, f64, usize);

impl JsConvertibleWithId for ConnectionState {
  fn into_js_value<'a, C: Context<'a>>(
    self,
    cx: &mut C,
    device_id: String,
  ) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let device_id = cx.string(&device_id);
    obj.set(cx, "deviceId", device_id)?;
    let state = cx.number(self as u8 as f64);
    obj.set(cx, "state", state)?;
    Ok(obj.upcast())
  }
}

impl JsConvertibleWithId for BLEDeviceInfo {
  fn into_js_value<'a, C: Context<'a>>(
    self,
    cx: &mut C,
    device_id: String,
  ) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let device_id = cx.string(&device_id);
    obj.set(cx, "deviceId", device_id)?;
    let manufacturer = cx.string(&self.manufacturer);
    obj.set(cx, "manufacturer", manufacturer)?;
    let model = cx.string(&self.model);
    obj.set(cx, "model", model)?;
    let serial = cx.string(&self.serial);
    obj.set(cx, "serial", serial)?;
    let hardware = cx.string(&self.hardware);
    obj.set(cx, "hardware", hardware)?;
    let firmware = cx.string(&self.firmware);
    obj.set(cx, "firmware", firmware)?;
    Ok(obj.upcast())
  }
}

impl JsConvertibleWithId for u8 {
  fn into_js_value<'a, C: Context<'a>>(
    self,
    cx: &mut C,
    device_id: String,
  ) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let device_id = cx.string(&device_id);
    obj.set(cx, "deviceId", device_id)?;
    let value = cx.number(self as f64);
    obj.set(cx, "value", value)?;
    Ok(obj.upcast())
  }
}

impl JsConvertibleWithId for String {
  fn into_js_value<'a, C: Context<'a>>(
    self,
    cx: &mut C,
    device_id: String,
  ) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let device_id: Handle<'_, JsString> = cx.string(&device_id);
    obj.set(cx, "deviceId", device_id)?;
    let value = cx.string(&self);
    obj.set(cx, "message", value)?;
    Ok(obj.upcast())
  }
}

impl JsConvertible for ScanResult {
  fn into_js_value<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let device_id = cx.string(&self.id);
    obj.set(cx, "deviceId", device_id)?;

    let name = cx.string(&self.name);
    obj.set(cx, "name", name)?;

    let rssi = cx.number(self.rssi as f64);
    obj.set(cx, "rssi", rssi)?;

    // cfg_if::cfg_if!(
    //   if #[cfg(feature = "oxyzen")] {
    //     let battery_level = cx.number(self.battery_level as f64);
    //     obj.set(cx, "batteryLevel", battery_level)?;

    //     let is_in_pairing_mode = cx.boolean(self.is_in_pairing_mode);
    //     obj.set(cx, "isInPairingMode", is_in_pairing_mode)?;
    //   }
    // );

    Ok(obj.upcast())
  }
}

impl JsConvertible for MdnsScanResult {
  fn into_js_value<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let fullname = cx.string(&self.fullname);
    obj.set(cx, "fullname", fullname)?;
    let hostname = cx.string(&self.hostname);
    obj.set(cx, "hostname", hostname)?;
    let addr = cx.string(&self.addr);
    obj.set(cx, "addr", addr)?;
    let port = cx.number(self.port as f64);
    obj.set(cx, "port", port)?;
    let sn = cx.string(&self.sn);
    obj.set(cx, "sn", sn)?;
    let model = cx.string(&self.model);
    obj.set(cx, "model", model)?;
    Ok(obj.upcast())
  }
}

impl JsConvertible for cb::ImpedanceResult {
  fn into_js_value<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue> {
    let obj = cx.empty_object();
    let chip = cx.number(self.chip as f64);
    obj.set(cx, "chip", chip)?;

    let len = self.values.len();
    let mut values = JsFloat32Array::new(cx, len)?;
    let slice = values.as_mut_slice(cx);
    for (i, value) in self.values.iter().enumerate() {
      slice[i] = *value;
    }
    obj.set(cx, "values", values)?;
    Ok(obj.upcast())
  }
}

pub trait IntoJsResult {
  fn into_js_result<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue>;
}

impl IntoJsResult for () {
  fn into_js_result<'a, C: Context<'a>>(self, cx: &mut C) -> JsResult<'a, JsValue> {
    Ok(cx.undefined().upcast())
  }
}

pub fn extract_args<'a>(
  cx: &'a mut FunctionContext<'a>,
) -> Result<std::collections::HashMap<String, Handle<'a, JsValue>>, neon::result::Throw> {
  let args = cx
    .argument::<JsObject>(1)?
    .downcast_or_throw::<JsObject, _>(cx)?;

  let keys = args.get_own_property_names(cx)?;
  let mut info = std::collections::HashMap::new();
  for i in 0..keys.len(cx) {
    let key: Handle<JsString> = keys.get::<JsValue, _, _>(cx, i)?.downcast_or_throw(cx)?;
    let key = key.to_string(cx)?.value(cx);
    let value: Handle<JsValue> = args.get(cx, key.as_str())?;
    info.insert(key, value);
  }
  Ok(info)
}

pub fn extract_number_args(
  cx: &mut FunctionContext<'_>,
  index: usize,
) -> Result<std::collections::HashMap<String, f64>, neon::result::Throw> {
  let args = cx
    .argument::<JsObject>(index)?
    .downcast_or_throw::<JsObject, _>(cx)?;

  let keys = args.get_own_property_names(cx)?;
  let mut info = std::collections::HashMap::new();
  for i in 0..keys.len(cx) {
    let key: Handle<JsString> = keys.get::<JsValue, _, _>(cx, i)?.downcast_or_throw(cx)?;
    let key_str = key.to_string(cx)?.value(cx);
    // info!("key: {:?}", key_str);
    let value: Handle<JsValue> = args.get(cx, key_str.as_str())?;
    let num_value = value.downcast_or_throw::<JsNumber, _>(cx)?.value(cx);
    info.insert(key_str, num_value);
  }
  Ok(info)
}

pub fn extract_string_args(
  cx: &mut FunctionContext<'_>,
) -> Result<std::collections::HashMap<String, String>, neon::result::Throw> {
  let args = cx
    .argument::<JsObject>(1)?
    .downcast_or_throw::<JsObject, _>(cx)?;

  let keys = args.get_own_property_names(cx)?;
  let mut info = std::collections::HashMap::new();
  for i in 0..keys.len(cx) {
    let key: Handle<JsString> = keys.get::<JsValue, _, _>(cx, i)?.downcast_or_throw(cx)?;
    let key_str = key.to_string(cx)?.value(cx);
    // info!("key: {:?}", key_str);
    let value: Handle<JsValue> = args.get(cx, key_str.as_str())?;
    // 将值转换为字符串，无论其原始类型是什么
    let string_value = if value.is_a::<JsString, _>(cx) {
      value.downcast_or_throw::<JsString, _>(cx)?.value(cx)
    } else if value.is_a::<JsNumber, _>(cx) {
      let num_val = value.downcast_or_throw::<JsNumber, _>(cx)?.value(cx);
      num_val.to_string()
    } else if value.is_a::<JsBoolean, _>(cx) {
      let bool_val = value.downcast_or_throw::<JsBoolean, _>(cx)?.value(cx);
      bool_val.to_string()
    } else if value.is_a::<JsNull, _>(cx) || value.is_a::<JsUndefined, _>(cx) {
      "".to_string()
    } else {
      // 对于其他类型（对象、数组等），尝试调用 toString()
      value.to_string(cx)?.value(cx)
    };
    info.insert(key_str, string_value);
  }
  Ok(info)
}

lazy_static::lazy_static! {
  static ref PARSER: Mutex<HashMap<String, Parser>> = Mutex::new(HashMap::new());
  static ref TCP_CLIENT: Mutex<HashMap<String, Arc<Mutex<TcpClient>>>> = Mutex::new(HashMap::new());
}

pub fn init_ble_parser(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let device_id = cx.argument::<JsString>(0)?.value(&mut cx);
  let mut parser_map = PARSER.lock();
  if !parser_map.contains_key(&device_id) {
    let msg_type = cx.argument::<JsNumber>(1)?.value(&mut cx) as u8;
    let parser = Parser::new(device_id.clone(), msg_type.into());
    parser_map.insert(device_id, parser);
  }
  // let is_ble = cx.argument::<JsBoolean>(2)?.value(&mut cx);
  register_ble_data_callback();
  Ok(cx.undefined())
}

pub fn tcp_connect(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let addr = cx.argument::<JsString>(0)?.value(&mut cx);
  let port: u16 = cx.argument::<JsNumber>(1)?.value(&mut cx) as u16;
  let device_id = format!("{}:{}", addr, port);
  info!("tcp_connect: {}", device_id);
  let mut client_map = TCP_CLIENT.lock();
  if client_map.contains_key(&device_id) {
    return cx.throw_error(format!("TCP client already exists for {}", device_id));
  }
  let client = TcpClient::new(addr.parse().unwrap(), port);
  let client_arc = Arc::new(Mutex::new(client));
  client_map.insert(device_id.clone(), client_arc.clone());

  let parser = Parser::new(device_id.clone(), MsgType::EEGCap);
  JsPromiseManager::new(&mut cx).execute(|| {
    client_arc
      .lock()
      .connect_and_listen(parser)
      .map_err(|e| e.to_string())
  })
}

pub fn tcp_disconnect(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let addr = cx.argument::<JsString>(0)?.value(&mut cx);
  let port: u16 = cx.argument::<JsNumber>(1)?.value(&mut cx) as u16;
  let device_id = format!("{}:{}", addr, port);
  info!("tcp_disconnect: {}", device_id);
  let mut client_map = TCP_CLIENT.lock();
  if !client_map.contains_key(&device_id) {
    return cx.throw_error(format!("TCP client not found for {}", device_id));
  }
  let client_arc = client_map.remove(&device_id).unwrap();
  JsPromiseManager::new(&mut cx)
    .execute(move || client_arc.lock().disconnect().map_err(|e| e.to_string()))
}

pub fn get_tcp_client(device_id: &str) -> Option<Arc<Mutex<TcpClient>>> {
  let client_map = TCP_CLIENT.lock();
  client_map.get(device_id).cloned()
}

pub fn did_receive_data(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let device_id = cx.argument::<JsString>(0)?.value(&mut cx);
  let mut parser_map = PARSER.lock();
  if let Some(parser) = parser_map.get_mut(&device_id) {
    let data = cx.argument::<JsUint8Array>(1)?;
    let data_vec = data.as_slice(&mut cx).to_vec();
    parser.receive_data(&data_vec);
  }

  Ok(cx.undefined())
}

fn register_ble_data_callback() {
  if is_registered_received_data() {
    return;
  }
  ble::set_received_data_callback(Box::new(move |id: String, data: Vec<u8>| {
    trace!("id: {}, received_data: {:02x?}", id, data);
    let mut parser_map = PARSER.lock();
    if let Some(parser) = parser_map.get_mut(&id) {
      parser.receive_data(&data);
    }
  }));
}

pub fn set_msg_resp_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback_with_id(|callback| {
    cb::set_msg_resp_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set msg resp callback: {:?}", err)),
  }
}

pub fn set_battery_level_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback(|callback| {
    cb::set_battery_level_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set battery level callback: {:?}", err)),
  }
}

pub fn set_tcp_stream_exit_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback(|callback| {
    cb::set_tcp_stream_exit_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set TCP stream exit callback: {:?}", err)),
  }
}

pub fn send_tcp_command<F>(mut cx: FunctionContext, cmd_builder: F) -> JsResult<JsPromise>
where
  F: FnOnce() -> (u32, Vec<u8>),
{
  let addr = cx.argument::<JsString>(0)?.value(&mut cx);
  let port: u16 = cx.argument::<JsNumber>(1)?.value(&mut cx) as u16;
  let device_id = format!("{}:{}", addr, port);
  let client = get_tcp_client(&device_id).unwrap();

  // 执行命令并返回Promise
  let promise_manager = JsPromiseManager::new(&mut cx);
  promise_manager.execute(move || {
    let client = client.lock();
    let rt = get_runtime();
    rt.block_on(client.send_command(cmd_builder))
      .map_err(|e| e.to_string())?; // 发送命令并等待响应
    Ok(())
  })
}

pub fn send_ble_command<F>(mut cx: FunctionContext, cmd_builder: F) -> JsResult<JsPromise>
where
  F: FnOnce() -> (u32, Vec<u8>),
{
  let device_id = cx.argument::<JsString>(0)?.value(&mut cx);
  let (_, cmd) = cmd_builder();

  // 执行命令并返回Promise
  let promise_manager = JsPromiseManager::new(&mut cx);
  promise_manager
    .execute(move || sync_write_value(&device_id, &cmd, true).map_err(|e| e.to_string()))
}
