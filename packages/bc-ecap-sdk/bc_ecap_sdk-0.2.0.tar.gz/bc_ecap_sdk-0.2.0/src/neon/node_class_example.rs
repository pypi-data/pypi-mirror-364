// Neon导出类类型示例
// 文件: src/neon/node_class_example.rs

use neon::prelude::*;

// 定义一个Rust结构体作为JavaScript类的后端
pub struct EEGDevice {
  id: String,
  name: String,
  is_connected: bool,
  sample_rate: u32,
}

// 为EEGDevice实现构造函数
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

// 将EEGDevice包装为JavaScript类
impl Finalize for EEGDevice {}

// 定义JavaScript类的方法
impl EEGDevice {
  // 构造函数
  fn js_new(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
    let id = cx.argument::<JsString>(0)?.value(&mut cx);
    let name = cx.argument::<JsString>(1)?.value(&mut cx);

    let device = EEGDevice::new(id, name);
    Ok(cx.boxed(device))
  }

  // getter方法 - 获取设备ID
  fn js_get_id(mut cx: FunctionContext) -> JsResult<JsString> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.string(&this.id))
  }

  // getter方法 - 获取设备名称
  fn js_get_name(mut cx: FunctionContext) -> JsResult<JsString> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.string(&this.name))
  }

  // getter方法 - 获取连接状态
  fn js_is_connected(mut cx: FunctionContext) -> JsResult<JsBoolean> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.boolean(this.is_connected))
  }

  // getter方法 - 获取采样率
  fn js_get_sample_rate(mut cx: FunctionContext) -> JsResult<JsNumber> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.number(this.sample_rate as f64))
  }

  // setter方法 - 设置采样率
  fn js_set_sample_rate(mut cx: FunctionContext) -> JsResult<JsUndefined> {
    let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
    let sample_rate = cx.argument::<JsNumber>(1)?.value(&mut cx) as u32;

    this.sample_rate = sample_rate;
    Ok(cx.undefined())
  }

  // 实例方法 - 连接设备
  fn js_connect(mut cx: FunctionContext) -> JsResult<JsPromise> {
    let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
    let id = this.id.clone();

    let promise = cx
      .task(move || {
        // 模拟异步连接操作
        std::thread::sleep(std::time::Duration::from_millis(100));
        Ok(format!("Connected to device: {}", id))
      })
      .promise(&mut cx, move |mut cx, result| {
        match result {
          Ok(message) => {
            // 更新连接状态
            this.is_connected = true;
            Ok(cx.string(message))
          }
          Err(err) => cx.throw_error(err.to_string()),
        }
      });

    Ok(promise)
  }

  // 实例方法 - 断开连接
  fn js_disconnect(mut cx: FunctionContext) -> JsResult<JsUndefined> {
    let mut this = cx.argument::<JsBox<EEGDevice>>(0)?;
    this.is_connected = false;
    Ok(cx.undefined())
  }

  // 静态方法 - 创建默认设备
  fn js_create_default(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
    let device = EEGDevice::new("default".to_string(), "Default EEG Device".to_string());
    Ok(cx.boxed(device))
  }
}

// 定义配置对象类
pub struct EEGConfig {
  channels: Vec<u8>,
  sample_rate: u32,
  gain: f32,
}

impl Finalize for EEGConfig {}

impl EEGConfig {
  fn js_new(mut cx: FunctionContext) -> JsResult<JsBox<EEGConfig>> {
    let channels_array = cx.argument::<JsArray>(0)?;
    let sample_rate = cx.argument::<JsNumber>(1)?.value(&mut cx) as u32;
    let gain = cx.argument::<JsNumber>(2)?.value(&mut cx) as f32;

    let mut channels = Vec::new();
    let length = channels_array.len(&mut cx);

    for i in 0..length {
      let value: Handle<JsNumber> = channels_array.get(&mut cx, i)?;
      channels.push(value.value(&mut cx) as u8);
    }

    let config = EEGConfig {
      channels,
      sample_rate,
      gain,
    };

    Ok(cx.boxed(config))
  }

  fn js_get_channels(mut cx: FunctionContext) -> JsResult<JsArray> {
    let this = cx.argument::<JsBox<EEGConfig>>(0)?;
    let array = cx.empty_array();

    for (i, &channel) in this.channels.iter().enumerate() {
      let value = cx.number(channel as f64);
      array.set(&mut cx, i as u32, value)?;
    }

    Ok(array)
  }

  fn js_to_json(mut cx: FunctionContext) -> JsResult<JsObject> {
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
}

// 导出类的函数
pub fn export_eeg_device_class(cx: &mut ModuleContext) -> NeonResult<()> {
  // 创建EEGDevice类
  let eeg_device_class = cx.empty_object();

  // 添加构造函数
  let constructor = JsFunction::new(cx, EEGDevice::js_new)?;
  eeg_device_class.set(cx, "new", constructor)?;

  // 添加静态方法
  let create_default = JsFunction::new(cx, EEGDevice::js_create_default)?;
  eeg_device_class.set(cx, "createDefault", create_default)?;

  // 添加实例方法
  let get_id = JsFunction::new(cx, EEGDevice::js_get_id)?;
  eeg_device_class.set(cx, "getId", get_id)?;

  let get_name = JsFunction::new(cx, EEGDevice::js_get_name)?;
  eeg_device_class.set(cx, "getName", get_name)?;

  let is_connected = JsFunction::new(cx, EEGDevice::js_is_connected)?;
  eeg_device_class.set(cx, "isConnected", is_connected)?;

  let get_sample_rate = JsFunction::new(cx, EEGDevice::js_get_sample_rate)?;
  eeg_device_class.set(cx, "getSampleRate", get_sample_rate)?;

  let set_sample_rate = JsFunction::new(cx, EEGDevice::js_set_sample_rate)?;
  eeg_device_class.set(cx, "setSampleRate", set_sample_rate)?;

  let connect = JsFunction::new(cx, EEGDevice::js_connect)?;
  eeg_device_class.set(cx, "connect", connect)?;

  let disconnect = JsFunction::new(cx, EEGDevice::js_disconnect)?;
  eeg_device_class.set(cx, "disconnect", disconnect)?;

  // 导出EEGDevice类
  cx.export_value("EEGDevice", eeg_device_class)?;

  // 创建并导出EEGConfig类
  let eeg_config_class = cx.empty_object();

  let config_constructor = JsFunction::new(cx, EEGConfig::js_new)?;
  eeg_config_class.set(cx, "new", config_constructor)?;

  let get_channels = JsFunction::new(cx, EEGConfig::js_get_channels)?;
  eeg_config_class.set(cx, "getChannels", get_channels)?;

  let to_json = JsFunction::new(cx, EEGConfig::js_to_json)?;
  eeg_config_class.set(cx, "toJson", to_json)?;

  cx.export_value("EEGConfig", eeg_config_class)?;

  Ok(())
}

// 简化版本 - 使用declare_types宏
neon::declare_types! {
    /// JavaScript EEGDeviceSimple class
    pub class JsEEGDeviceSimple for EEGDevice {
        init(mut cx) {
            let id = cx.argument::<JsString>(0)?.value(&mut cx);
            let name = cx.argument::<JsString>(1)?.value(&mut cx);
            Ok(EEGDevice::new(id, name))
        }

        method getId(mut cx) {
            let this = cx.this();
            let id = {
                let guard = cx.lock();
                let device = this.borrow(&guard);
                device.id.clone()
            };
            Ok(cx.string(&id).upcast())
        }

        method getName(mut cx) {
            let this = cx.this();
            let name = {
                let guard = cx.lock();
                let device = this.borrow(&guard);
                device.name.clone()
            };
            Ok(cx.string(&name).upcast())
        }

        method isConnected(mut cx) {
            let this = cx.this();
            let connected = {
                let guard = cx.lock();
                let device = this.borrow(&guard);
                device.is_connected
            };
            Ok(cx.boolean(connected).upcast())
        }

        method connect(mut cx) {
            let this = cx.this();
            {
                let guard = cx.lock();
                let mut device = this.borrow_mut(&guard);
                device.is_connected = true;
            }
            Ok(cx.undefined().upcast())
        }

        method disconnect(mut cx) {
            let this = cx.this();
            {
                let guard = cx.lock();
                let mut device = this.borrow_mut(&guard);
                device.is_connected = false;
            }
            Ok(cx.undefined().upcast())
        }
    }
}
