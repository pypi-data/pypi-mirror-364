use super::handler::send_ble_command;
use crate::proto::oxyzen::msg_builder::oxyz_msg_builder;
use neon::prelude::*;

crate::cfg_import_logging!();

pub fn send_pair_cmd(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let device_id = cx.argument::<JsString>(0)?.value(&mut cx);
  let in_pairing_mode = cx.argument::<JsBoolean>(1)?.value(&mut cx);
  info!(
    "send_pair_cmd, device_id: {:?}, in_pairing_mode: {:?}",
    device_id, in_pairing_mode
  );
  send_ble_command(cx, || oxyz_msg_builder::pair(in_pairing_mode))
}
