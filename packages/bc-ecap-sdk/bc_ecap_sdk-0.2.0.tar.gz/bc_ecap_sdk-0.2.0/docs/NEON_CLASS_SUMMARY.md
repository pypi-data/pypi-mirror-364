# Neon 类导出总结

基于你当前的项目结构和Neon 1.0版本，这里是关于在Neon中导出类类型的完整指南。

## 核心概念

在Neon 1.0中，推荐的类导出方式是：
1. **Rust端导出函数**（而不是直接导出类）
2. **JavaScript端创建类包装器**

## 实现步骤

### 1. Rust端实现（推荐方式）

```rust
// 定义Rust结构体
#[derive(Debug, Clone)]
pub struct EEGDevice {
    pub id: String,
    pub name: String,
    pub is_connected: bool,
    pub sample_rate: u32,
}

impl Finalize for EEGDevice {}

// 导出构造函数
fn eeg_device_new(mut cx: FunctionContext) -> JsResult<JsBox<EEGDevice>> {
    let id = cx.argument::<JsString>(0)?.value(&mut cx);
    let name = cx.argument::<JsString>(1)?.value(&mut cx);
    let device = EEGDevice { id, name, is_connected: false, sample_rate: 250 };
    Ok(cx.boxed(device))
}

// 导出方法
fn eeg_device_get_id(mut cx: FunctionContext) -> JsResult<JsString> {
    let this = cx.argument::<JsBox<EEGDevice>>(0)?;
    Ok(cx.string(&this.id))
}

// 在主模块中导出函数
#[neon::main]
fn main(mut cx: ModuleContext) -> NeonResult<()> {
    cx.export_function("eeg_device_new", eeg_device_new)?;
    cx.export_function("eeg_device_get_id", eeg_device_get_id)?;
    // ... 其他方法
    Ok(())
}
```

### 2. JavaScript端类包装器

```javascript
const nativeModule = require('./index.node');

class EEGDevice {
    constructor(id, name) {
        this._handle = nativeModule.eeg_device_new(id, name);
    }

    getId() {
        return nativeModule.eeg_device_get_id(this._handle);
    }

    // ... 其他方法
}

module.exports = { EEGDevice };
```

### 3. TypeScript类型定义

```typescript
export declare class EEGDevice {
    constructor(id: string, name: string);
    getId(): string;
    getName(): string;
    // ... 其他方法
}
```

## 在你的项目中应用

基于你当前的`node.rs`文件，你可以添加类似的类导出功能：

```rust
// 在现有的main函数中添加
#[neon::main]
fn main(mut cx: ModuleContext) -> NeonResult<()> {
    // 现有的函数导出...
    cx.export_function("init_logging", init_logging)?;
    // ...

    // 添加类相关的函数导出
    cx.export_function("eeg_device_new", eeg_device_new)?;
    cx.export_function("eeg_device_get_id", eeg_device_get_id)?;
    // ...

    Ok(())
}
```

## 文件结构

基于你的项目，建议的文件组织：

```
src/neon/
├── node.rs                    # 主模块，导出所有函数
├── device_types.rs           # 设备相关的类型和函数
├── config_types.rs           # 配置相关的类型和函数
└── handler.rs                # 现有的处理器（保持不变）

examples/
├── js/
│   ├── device_wrapper.js     # JavaScript类包装器
│   └── usage_example.js      # 使用示例
└── types/
    └── index.d.ts            # TypeScript类型定义
```

## 最佳实践

1. **使用JsBox**：对于复杂的Rust结构体，使用`JsBox`进行包装
2. **错误处理**：在Rust端提供详细的错误信息
3. **内存安全**：确保实现`Finalize` trait
4. **异步支持**：使用Neon的Promise支持处理异步操作
5. **类型安全**：提供完整的TypeScript类型定义

## 示例文件

我已经为你创建了以下示例文件：

1. `examples/neon_class_working_example.rs` - Rust端实现示例
2. `examples/neon_class_wrapper.js` - JavaScript包装器示例
3. `examples/neon_class_usage.js` - 使用示例
4. `types/neon_classes.d.ts` - TypeScript类型定义
5. `docs/NEON_CLASS_EXPORT_GUIDE.md` - 详细指南

## 与现有代码集成

你可以在现有的`node.rs`文件中添加设备类相关的导出，而不影响现有的BLE和其他功能。这样可以提供更高级的API，同时保持向后兼容性。

## 下一步

1. 决定哪些现有的结构体需要导出为类
2. 创建相应的函数导出
3. 编写JavaScript包装器
4. 添加TypeScript类型定义
5. 编写测试用例

这种方法提供了最大的灵活性和类型安全性，同时保持了Neon 1.0的最佳实践。
