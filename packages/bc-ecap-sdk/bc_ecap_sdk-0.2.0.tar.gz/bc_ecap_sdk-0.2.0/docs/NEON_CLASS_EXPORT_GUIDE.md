# Neon 类导出指南

本文档说明如何在 Rust + Neon 项目中导出JavaScript类类型。

## 目录

1. [基本概念](#基本概念)
2. [使用 declare_types! 宏](#使用-declare_types-宏)
3. [手动导出类](#手动导出类)
4. [JavaScript使用示例](#javascript使用示例)
5. [TypeScript支持](#typescript支持)
6. [最佳实践](#最佳实践)
7. [常见问题](#常见问题)

## 基本概念

在Neon中，有多种方式可以将Rust结构体导出为JavaScript类：

1. **使用 `declare_types!` 宏**（推荐）
2. **手动创建类和方法**
3. **使用 `JsBox` 包装结构体**

## 使用 declare_types! 宏

### 1. 定义Rust结构体

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

// 必须实现Finalize trait
impl Finalize for EEGDevice {}
```

### 2. 使用declare_types!宏

```rust
neon::declare_types! {
    /// JavaScript EEGDevice 类
    pub class JsEEGDevice for EEGDevice {
        // 构造函数
        init(mut cx) {
            let id = cx.argument::<JsString>(0)?.value(&mut cx);
            let name = cx.argument::<JsString>(1)?.value(&mut cx);
            Ok(EEGDevice::new(id, name))
        }
        
        // 实例方法
        method getId(mut cx) {
            let this = cx.this();
            let id = {
                let guard = cx.lock();
                let device = this.borrow(&guard);
                device.id.clone()
            };
            Ok(cx.string(&id).upcast())
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
        
        // 返回对象的方法
        method getInfo(mut cx) {
            let this = cx.this();
            let (id, name, connected) = {
                let guard = cx.lock();
                let device = this.borrow(&guard);
                (device.id.clone(), device.name.clone(), device.is_connected)
            };
            
            let obj = cx.empty_object();
            obj.set(&mut cx, "id", cx.string(&id))?;
            obj.set(&mut cx, "name", cx.string(&name))?;
            obj.set(&mut cx, "isConnected", cx.boolean(connected))?;
            
            Ok(obj.upcast())
        }
    }
}
```

### 3. 导出类到模块

```rust
#[neon::main]
fn main(mut cx: ModuleContext) -> NeonResult<()> {
    // 导出类
    cx.export_class::<JsEEGDevice>("EEGDevice")?;
    
    // 也可以导出工厂函数
    cx.export_function("createDefaultDevice", create_default_device)?;
    
    Ok(())
}

fn create_default_device(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
    let device = EEGDevice::new("default".to_string(), "Default Device".to_string());
    Ok(cx.boxed(device))
}
```

## 手动导出类

对于更复杂的需求，可以手动创建类：

```rust
fn manual_export_class(cx: &mut ModuleContext) -> NeonResult<()> {
    // 创建构造函数
    let constructor = JsFunction::new(cx, |mut cx| {
        let id = cx.argument::<JsString>(0)?.value(&mut cx);
        let name = cx.argument::<JsString>(1)?.value(&mut cx);
        let device = EEGDevice::new(id, name);
        Ok(cx.boxed(device).upcast())
    })?;
    
    // 创建原型对象
    let prototype = cx.empty_object();
    
    // 添加方法到原型
    let get_id = JsFunction::new(cx, |mut cx| {
        let this = cx.this().downcast::<JsBox<EEGDevice>, _>(&mut cx)
            .or_throw(&mut cx)?;
        Ok(cx.string(&this.id).upcast())
    })?;
    prototype.set(cx, "getId", get_id)?;
    
    // 设置原型
    constructor.set(cx, "prototype", prototype)?;
    
    // 导出类
    cx.export_value("ManualEEGDevice", constructor)?;
    
    Ok(())
}
```

## JavaScript使用示例

```javascript
const { EEGDevice, EEGConfig, createDefaultDevice } = require('./index.node');

// 创建设备实例
const device = new EEGDevice("device123", "我的脑电设备");

console.log(device.getId());        // "device123"
console.log(device.getName());      // "我的脑电设备"
console.log(device.isConnected());  // false

// 连接设备
device.connect();
console.log(device.isConnected());  // true

// 设置采样率
device.setSampleRate(500);
console.log(device.getSampleRate()); // 500

// 获取设备信息
const info = device.getInfo();
console.log(info);
// {
//   id: "device123",
//   name: "我的脑电设备",
//   isConnected: true,
//   sampleRate: 500
// }

// 使用工厂函数
const defaultDevice = createDefaultDevice();
console.log(defaultDevice.getName()); // "Default Device"
```

## TypeScript支持

创建 `.d.ts` 文件来提供TypeScript类型定义：

```typescript
// types/index.d.ts
export declare class EEGDevice {
  constructor(id: string, name: string);
  getId(): string;
  getName(): string;
  isConnected(): boolean;
  getSampleRate(): number;
  setSampleRate(rate: number): void;
  connect(): void;
  disconnect(): void;
  getInfo(): {
    id: string;
    name: string;
    isConnected: boolean;
    sampleRate: number;
  };
}

export declare class EEGConfig {
  constructor(channels: number[], sampleRate: number, gain: number);
  getChannels(): number[];
  getSampleRate(): number;
  getGain(): number;
  toJson(): {
    channels: number[];
    sampleRate: number;
    gain: number;
  };
}

export declare function createDefaultDevice(): EEGDevice;
```

## 最佳实践

### 1. 内存管理
- 始终实现 `Finalize` trait
- 使用 `cx.lock()` 来安全地访问Rust数据
- 避免在JavaScript回调中长时间持有锁

### 2. 错误处理

```rust
fn connect(mut cx) {
    let this = cx.this();
    let result = {
        let guard = cx.lock();
        let mut device = this.borrow_mut(&guard);
        // 可能失败的操作
        device.try_connect()
    };
    
    match result {
        Ok(_) => Ok(cx.undefined().upcast()),
        Err(e) => cx.throw_error(format!("连接失败: {}", e))
    }
}
```

### 3. 异步操作

```rust
fn connectAsync(mut cx) {
    let this = cx.this();
    let device_id = {
        let guard = cx.lock();
        let device = this.borrow(&guard);
        device.id.clone()
    };
    
    let promise = cx.task(move || {
        // 异步连接操作
        connect_device(&device_id)
    }).promise(&mut cx, |mut cx, result| {
        match result {
            Ok(success) => Ok(cx.boolean(success)),
            Err(err) => cx.throw_error(err.to_string())
        }
    });
    
    Ok(promise)
}
```

### 4. 类型转换

```rust
// 将Rust Vec转换为JavaScript Array
fn getChannels(mut cx) {
    let this = cx.this();
    let channels = {
        let guard = cx.lock();
        let config = this.borrow(&guard);
        config.channels.clone()
    };
    
    let array = cx.empty_array();
    for (i, &channel) in channels.iter().enumerate() {
        let value = cx.number(channel as f64);
        array.set(&mut cx, i as u32, value)?;
    }
    
    Ok(array.upcast())
}
```

## 常见问题

### Q: 如何处理复杂的嵌套对象？
A: 创建多个类，并在方法中返回相应的实例：

```rust
fn getNestedConfig(mut cx) {
    let this = cx.this();
    let nested_data = {
        let guard = cx.lock();
        let device = this.borrow(&guard);
        device.get_nested_config()
    };
    
    // 创建嵌套配置对象实例
    let config = cx.boxed(nested_data);
    Ok(config.upcast())
}
```

### Q: 如何实现静态方法？
A: 在模块中导出普通函数：

```rust
fn create_from_config(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
    let config = cx.argument::<JsObject>(0)?;
    // 解析config并创建设备
    let device = EEGDevice::from_config(config);
    Ok(cx.boxed(device))
}

// 在main函数中导出
cx.export_function("EEGDevice_fromConfig", create_from_config)?;
```

### Q: 如何处理JavaScript回调？
A: 使用Channel和Root：

```rust
method setCallback(mut cx) {
    let callback = cx.argument::<JsFunction>(0)?;
    let channel = cx.channel();
    let callback = callback.root(&mut cx);
    
    let this = cx.this();
    {
        let guard = cx.lock();
        let mut device = this.borrow_mut(&guard);
        device.set_callback(move |data| {
            channel.send(move |mut task_cx| {
                let callback = callback.to_inner(&mut task_cx);
                let args = vec![task_cx.string(&data).upcast()];
                callback.call(&mut task_cx, task_cx.undefined(), args)?;
                Ok(())
            });
        });
    }
    
    Ok(cx.undefined().upcast())
}
```

### Q: 如何优化性能？
A: 
1. 减少锁的持有时间
2. 批量操作数据
3. 使用 `JsBox` 避免频繁的数据复制
4. 合理使用 `Channel` 进行异步操作

## 构建和测试

1. 添加到 `Cargo.toml`:

```toml
[dependencies]
neon = "1.0"
```

2. 构建:

```bash
npm run build
# 或
neon build --release
```

3. 测试:

```bash
node examples/neon_class_usage.js
```

这份指南涵盖了在Neon中导出类的主要方法和最佳实践。根据项目需求选择合适的方法，并注意内存管理和错误处理。
