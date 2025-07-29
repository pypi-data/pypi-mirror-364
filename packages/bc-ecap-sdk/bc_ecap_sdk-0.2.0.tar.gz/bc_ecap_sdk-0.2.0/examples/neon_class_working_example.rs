// Neon 1.0 类导出实际示例
// 文件: examples/neon_class_working_example.rs

use neon::prelude::*;

// 定义Rust结构体
#[derive(Debug, Clone)]
pub struct EEGDevice {
  pub id: String,
  pub name: String,
  pub is_connected: bool,
  pub sample_rate: u32,
}

impl EEGDevice {
  pub fn new(id: String, name: String) -> Self {
    Self {
      id,
      name,
      is_connected: false,
      sample_rate: 250,
    }
  }

  pub fn connect(&mut self) -> Result<(), String> {
    if self.is_connected {
      return Err("Device is already connected".to_string());
    }
    self.is_connected = true;
    Ok(())
  }

  pub fn disconnect(&mut self) {
    self.is_connected = false;
  }

  pub fn set_sample_rate(&mut self, rate: u32) {
    self.sample_rate = rate;
  }
}

// 实现Finalize trait以便在Neon中使用
impl Finalize for EEGDevice {}

// 构造函数
fn eeg_device_new(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
  let id = cx.argument::<JsString>(0)?.value(&mut cx);
  let name = cx.argument::<JsString>(1)?.value(&mut cx);
  let device = EEGDevice::new(id, name);
  Ok(cx.boxed(device))
}

// Getter方法
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

fn eeg_device_get_sample_rate(mut cx: FunctionContext) -> JsResult<JsNumber> {
  let this = cx.argument::<JsBox<EEGDevice>>(0)?;
  Ok(cx.number(this.sample_rate as f64))
}

// Setter和方法
fn eeg_device_set_sample_rate(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
  let rate = cx.argument::<JsNumber>(1)?.value(&mut cx) as u32;
  this.set_sample_rate(rate);
  Ok(cx.undefined())
}

fn eeg_device_connect(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
  match this.connect() {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(err),
  }
}

fn eeg_device_disconnect(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
  this.disconnect();
  Ok(cx.undefined())
}

// 返回复杂对象
fn eeg_device_get_info(mut cx: FunctionContext) -> JsResult<JsObject> {
  let this = cx.argument::<JsBox<EEGDevice>>(0)?;

  let obj = cx.empty_object();

  let id = cx.string(&this.id);
  obj.set(&mut cx, "id", id)?;

  let name = cx.string(&this.name);
  obj.set(&mut cx, "name", name)?;

  let connected = cx.boolean(this.is_connected);
  obj.set(&mut cx, "isConnected", connected)?;

  let sample_rate = cx.number(this.sample_rate as f64);
  obj.set(&mut cx, "sampleRate", sample_rate)?;

  Ok(obj)
}

// 工厂函数
fn create_default_device(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
  let device = EEGDevice::new("default".to_string(), "Default EEG Device".to_string());
  Ok(cx.boxed(device))
}

// 配置类
#[derive(Debug, Clone)]
pub struct EEGConfig {
  pub channels: Vec<u8>,
  pub sample_rate: u32,
  pub gain: f32,
}

impl EEGConfig {
  pub fn new(channels: Vec<u8>, sample_rate: u32, gain: f32) -> Self {
    Self {
      channels,
      sample_rate,
      gain,
    }
  }
}

impl Finalize for EEGConfig {}

// EEGConfig相关函数
fn eeg_config_new(mut cx: FunctionContext) -> JsResult<JsBox<EEGConfig>> {
  let channels_array = cx.argument::<JsArray>(0)?;
  let sample_rate = cx.argument::<JsNumber>(1)?.value(&mut cx) as u32;
  let gain = cx.argument::<JsNumber>(2)?.value(&mut cx) as f32;

  let mut channels = Vec::new();
  let length = channels_array.len(&mut cx);

  for i in 0..length {
    let value: Handle<JsNumber> = channels_array.get(&mut cx, i)?;
    channels.push(value.value(&mut cx) as u8);
  }

  let config = EEGConfig::new(channels, sample_rate, gain);
  Ok(cx.boxed(config))
}

fn eeg_config_get_channels(mut cx: FunctionContext) -> JsResult<JsArray> {
  let this = cx.argument::<JsBox<EEGConfig>>(0)?;

  let array = cx.empty_array();
  for (i, &channel) in this.channels.iter().enumerate() {
    let value = cx.number(channel as f64);
    array.set(&mut cx, i as u32, value)?;
  }

  Ok(array)
}

fn eeg_config_to_json(mut cx: FunctionContext) -> JsResult<JsObject> {
  let this = cx.argument::<JsBox<EEGConfig>>(0)?;

  let obj = cx.empty_object();

  // 设置channels数组
  let channels_array = cx.empty_array();
  for (i, &channel) in this.channels.iter().enumerate() {
    let value = cx.number(channel as f64);
    channels_array.set(&mut cx, i as u32, value)?;
  }
  obj.set(&mut cx, "channels", channels_array)?;

  // 设置其他属性
  let sample_rate = cx.number(this.sample_rate as f64);
  obj.set(&mut cx, "sampleRate", sample_rate)?;

  let gain = cx.number(this.gain as f64);
  obj.set(&mut cx, "gain", gain)?;

  Ok(obj)
}

// 导出所有函数的主模块
#[neon::main]
fn main(mut cx: ModuleContext) -> NeonResult<()> {
  // EEGDevice相关函数
  cx.export_function("eeg_device_new", eeg_device_new)?;
  cx.export_function("eeg_device_get_id", eeg_device_get_id)?;
  cx.export_function("eeg_device_get_name", eeg_device_get_name)?;
  cx.export_function("eeg_device_is_connected", eeg_device_is_connected)?;
  cx.export_function("eeg_device_get_sample_rate", eeg_device_get_sample_rate)?;
  cx.export_function("eeg_device_set_sample_rate", eeg_device_set_sample_rate)?;
  cx.export_function("eeg_device_connect", eeg_device_connect)?;
  cx.export_function("eeg_device_disconnect", eeg_device_disconnect)?;
  cx.export_function("eeg_device_get_info", eeg_device_get_info)?;

  // EEGConfig相关函数
  cx.export_function("eeg_config_new", eeg_config_new)?;
  cx.export_function("eeg_config_get_channels", eeg_config_get_channels)?;
  cx.export_function("eeg_config_to_json", eeg_config_to_json)?;

  // 工厂函数
  cx.export_function("create_default_device", create_default_device)?;

  Ok(())
}
