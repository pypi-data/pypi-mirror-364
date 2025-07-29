use crate::utils::logging::LogLevel;
use wasm_bindgen::prelude::*;
crate::cfg_import_logging!();

// #[wasm_bindgen]
// pub fn greet(name: &str) -> String {
//   format!("Hello, {}!", name)
// }

#[wasm_bindgen]
pub fn init_logging(level: LogLevel) {
  let config = tracing_wasm::WASMLayerConfigBuilder::default()
    .set_max_level(level.into())
    .build();
  tracing_wasm::set_as_global_default_with_config(config);
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );
}

pub fn build_message<F>(builder: F) -> JsValue
where
  F: FnOnce() -> (u32, Vec<u8>),
{
  let (msg_id, buf) = builder();
  let message = serde_json::to_string(&serde_json::json!({
    "msg_id": msg_id,
    "buf": buf
  }))
  .unwrap();

  // 将 serde_json::Value 转换为 JsValue
  JsValue::from_str(&message)
}
