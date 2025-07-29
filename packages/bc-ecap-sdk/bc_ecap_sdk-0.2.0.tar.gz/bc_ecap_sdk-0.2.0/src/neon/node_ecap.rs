use super::handler::*;
use crate::callback::callback_rs::*;
use crate::data_handler::fft;
use crate::data_handler::filter;
use crate::data_handler::filter::{set_easy_eeg_filter, set_env_noise_cfg, EegFilterConfig};
use crate::eeg_cap::callback::set_next_leadoff_cb;
use crate::eeg_cap::data::get_imu_buffer;
use crate::eeg_cap::data::*;
use crate::proto::eeg_cap::enums::*;
use crate::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use crate::utils::mdns;
use neon::prelude::*;
use neon::types::buffer::TypedArray;
use tokio::io::AsyncWriteExt;

crate::cfg_import_logging!();

pub fn mdns_start_scan(mut cx: FunctionContext) -> JsResult<JsPromise> {
  JsPromiseManager::new(&mut cx).execute(|| mdns::mdns_start_scan_sync().map_err(|e| e.to_string()))
}

pub fn mdns_stop_scan(mut cx: FunctionContext) -> JsResult<JsPromise> {
  JsPromiseManager::new(&mut cx).execute(|| mdns::mdns_stop_scan().map_err(|e| e.to_string()))
}

pub fn set_mdns_scan_result_callback(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let handler = JsCallbackManager::new(&mut cx, 0)?;
  let ret = handler.register_callback(|callback| {
    mdns::set_mdns_scan_result_callback(callback);
    Ok(())
  });
  match ret {
    Ok(_) => Ok(cx.undefined()),
    Err(err) => cx.throw_error(format!("Failed to set msg resp callback: {:?}", err)),
  }
}

/***** BLE cmds *****/
pub fn get_ble_device_info(cx: FunctionContext) -> JsResult<JsPromise> {
  send_ble_command(cx, eeg_cap_msg_builder::get_ble_device_info)
}

pub fn get_wifi_status(cx: FunctionContext) -> JsResult<JsPromise> {
  send_ble_command(cx, eeg_cap_msg_builder::get_wifi_status)
}

pub fn get_wifi_config(cx: FunctionContext) -> JsResult<JsPromise> {
  send_ble_command(cx, eeg_cap_msg_builder::get_wifi_config)
}

pub fn set_ble_device_info(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let info = extract_string_args(&mut cx)?;
  let model: String = match info.get("model") {
    Some(value) => value.to_string(),
    None => return cx.throw_type_error("Missing model"),
  };
  let sn: String = match info.get("sn") {
    Some(value) => value.to_string(),
    None => return cx.throw_type_error("Missing sn"),
  };
  send_ble_command(cx, || {
    let mac = vec![0x00, 0x00, 0x00, 0x00, 0x00, 0x00];
    eeg_cap_msg_builder::set_ble_device_info(model.clone(), sn.clone(), mac)
  })
}

pub fn set_wifi_config(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let info = extract_string_args(&mut cx)?;
  let ssid: String = match info.get("ssid") {
    Some(value) => value.to_string(),
    None => return cx.throw_type_error("Missing ssid"),
  };
  let password: String = match info.get("password") {
    Some(value) => value.to_string(),
    None => return cx.throw_type_error("Missing password"),
  };
  send_ble_command(cx, || {
    eeg_cap_msg_builder::set_wifi_config(
      true,
      WiFiSecurity::SECURITY_WPA2_MIXED_PSK as i32,
      ssid,
      password,
    )
  })
}

/***** TCP cmds *****/
// get_device_info
pub fn get_device_info(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::get_device_info)
}

// get_battery_level
pub fn get_battery_level(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::get_battery_level)
}

// get_eeg_config
pub fn get_eeg_config(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::get_eeg_config)
}

// set_eeg_config
pub fn set_eeg_config(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let info: std::collections::HashMap<String, f64> = extract_number_args(&mut cx, 2)?;
  let sample_rate: EegSampleRate = match info.get("sample_rate") {
    Some(value) => {
      let sample_rate = *value as u8;
      sample_rate.try_into().unwrap_or(EegSampleRate::SR_250Hz)
    }
    None => return cx.throw_type_error("Missing sample_rate"),
  };
  let gain: EegSignalGain = match info.get("gain") {
    Some(value) => {
      let gain = *value as u8;
      gain.try_into().unwrap_or(EegSignalGain::GAIN_6)
    }
    None => return cx.throw_type_error("Missing gain"),
  };
  let signal_source: EegSignalSource = match info.get("signal_source") {
    Some(value) => {
      let signal_source = *value as u8;
      signal_source.try_into().unwrap_or(EegSignalSource::NORMAL)
    }
    None => return cx.throw_type_error("Missing signal_source"),
  };
  send_tcp_command(cx, || {
    eeg_cap_msg_builder::set_eeg_config(sample_rate as i32, gain as i32, signal_source as i32)
  })
}

// get_imu_config
pub fn get_imu_config(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::get_imu_config)
}

// set_imu_config
pub fn set_imu_config(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let info: std::collections::HashMap<String, f64> = extract_number_args(&mut cx, 2)?;
  let sample_rate: ImuSampleRate = match info.get("sample_rate") {
    Some(value) => {
      let sample_rate = *value as u8;
      sample_rate.try_into().unwrap_or(ImuSampleRate::SR_50Hz)
    }
    None => return cx.throw_type_error("Missing sample_rate"),
  };
  send_tcp_command(cx, || {
    eeg_cap_msg_builder::set_imu_config(sample_rate as i32)
  })
}

pub fn start_eeg_stream(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::start_eeg_stream)
}

pub fn stop_eeg_stream(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::stop_eeg_stream)
}

pub fn start_imu_stream(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::start_imu_stream)
}

pub fn stop_imu_stream(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::stop_imu_stream)
}

pub fn get_leadoff_config(cx: FunctionContext) -> JsResult<JsPromise> {
  send_tcp_command(cx, eeg_cap_msg_builder::get_leadoff_config)
}

pub fn start_leadoff_check(mut cx: FunctionContext) -> JsResult<JsPromise> {
  let args = cx
    .argument::<JsObject>(2)?
    .downcast_or_throw::<JsObject, _>(&mut cx)?;
  let loop_check: bool = args
    .get::<JsValue, _, _>(&mut cx, "loop_check")?
    .downcast_or_throw::<JsBoolean, _>(&mut cx)?
    .value(&mut cx);
  let freq: u8 = args
    .get::<JsValue, _, _>(&mut cx, "freq")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx) as u8;
  let current: u8 = args
    .get::<JsValue, _, _>(&mut cx, "current")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx) as u8;
  let freq: LeadOffFreq = freq.try_into().unwrap_or(LeadOffFreq::Ac31p2hz);
  let current: LeadOffCurrent = current.try_into().unwrap_or(LeadOffCurrent::Cur6nA);
  info!(
    "start_leadoff_check: loop_check: {}, freq: {:?}, current: {:?}",
    loop_check, freq, current
  );
  save_lead_off_cfg(loop_check, freq, current);

  let handler = JsCallbackManager::new(&mut cx, 3)?;
  let _ = handler.register_callback(|callback| {
    set_impedance_callback(callback);
    Ok(())
  });

  let addr = cx.argument::<JsString>(0)?.value(&mut cx);
  let port: u16 = cx.argument::<JsNumber>(1)?.value(&mut cx) as u16;
  let device_id = format!("{}:{}", addr, port);
  let client = get_tcp_client(&device_id).unwrap();

  set_next_leadoff_cb(Box::new(move |chip, freq, current| {
    // info!(
    //   "set_next_leadoff_cb: chip: {:?}, freq: {:?}, current: {:?}",
    //   chip, freq, current
    // );
    let client = client.lock();
    let stream = client.writer.clone();

    tokio::spawn(async move {
      let mut stream_guard = stream.lock().await;
      if let Some(ref mut stream) = *stream_guard {
        info!(
          "Sending leadoff chip: {:?}, freq: {:?}, current: {:?}",
          chip, freq, current
        );
        let msg = eeg_cap_msg_builder::switch_and_start_leadoff_check(
          chip as i32,
          freq as i32,
          current as i32,
        );
        stream.write_all(&msg.1).await.unwrap();
      } else {
        warn!("No active stream.");
      }
    });
  }));

  send_tcp_command(cx, || {
    eeg_cap_msg_builder::switch_and_start_leadoff_check(
      LeadOffChip::Chip1 as i32,
      freq as i32,
      current as i32,
    )
  })
}

pub fn stop_leadoff_check(cx: FunctionContext) -> JsResult<JsPromise> {
  clear_impedance_callback();
  send_tcp_command(cx, eeg_cap_msg_builder::stop_leadoff_check)
}

// TODO: 区分多个设备
pub fn get_eeg_buffer_arr(mut cx: FunctionContext) -> JsResult<JsArray> {
  let cx = &mut cx;
  let take: usize = cx.argument::<JsNumber>(0)?.value(cx) as usize;
  let clean: bool = cx.argument::<JsBoolean>(1)?.value(cx);
  let data: Vec<Vec<f64>> = get_eeg_buffer(take, clean);

  let arr = cx.empty_array();
  for (i, item) in data.iter().enumerate() {
    let mut js_array = JsFloat32Array::new(cx, item.len())?;
    let slice = js_array.as_mut_slice(cx);
    for (i, value) in item.iter().enumerate() {
      slice[i] = *value as f32;
    }
    arr.set(cx, i as u32, js_array)?;
  }
  Ok(arr)
}

pub fn get_imu_buffer_json(mut cx: FunctionContext) -> JsResult<JsString> {
  let cx = &mut cx;
  let take: usize = cx.argument::<JsNumber>(0)?.value(cx) as usize;
  let clean: bool = cx.argument::<JsBoolean>(1)?.value(cx);
  let data = get_imu_buffer(take, clean);
  let json = serde_json::to_string(&data).unwrap();
  let js_string = cx.string(&json);
  Ok(js_string)
}

pub fn set_config(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let eeg_buf_len: usize = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let imu_buf_len: usize = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
  let imp_win_len: usize = cx.argument::<JsNumber>(2)?.value(&mut cx) as usize;
  set_cfg(eeg_buf_len, imu_buf_len, imp_win_len);
  Ok(cx.undefined())
}

pub fn set_env_noise_config(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let noise_type: u8 = cx.argument::<JsNumber>(0)?.value(&mut cx) as u8;
  let fs: f64 = cx.argument::<JsNumber>(1)?.value(&mut cx);
  set_env_noise_cfg(noise_type.into(), fs);
  Ok(cx.undefined())
}

pub fn set_easy_eeg_filter_config(mut cx: FunctionContext) -> JsResult<JsUndefined> {
  let args = cx
    .argument::<JsObject>(0)?
    .downcast_or_throw::<JsObject, _>(&mut cx)?;
  let fs: f64 = args
    .get::<JsValue, _, _>(&mut cx, "fs")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);
  let high_pass_enabled: bool = args
    .get::<JsValue, _, _>(&mut cx, "enable_highpass")?
    .downcast_or_throw::<JsBoolean, _>(&mut cx)?
    .value(&mut cx);
  let high_cut: f64 = args
    .get::<JsValue, _, _>(&mut cx, "high_cut")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);
  let low_pass_enabled: bool = args
    .get::<JsValue, _, _>(&mut cx, "enable_lowpass")?
    .downcast_or_throw::<JsBoolean, _>(&mut cx)?
    .value(&mut cx);
  let low_cut: f64 = args
    .get::<JsValue, _, _>(&mut cx, "low_cut")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);
  let band_pass_enabled: bool = args
    .get::<JsValue, _, _>(&mut cx, "enable_bandpass")?
    .downcast_or_throw::<JsBoolean, _>(&mut cx)?
    .value(&mut cx);
  let band_pass_low: f64 = args
    .get::<JsValue, _, _>(&mut cx, "bandpass_low")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);
  let band_pass_high: f64 = args
    .get::<JsValue, _, _>(&mut cx, "bandpass_high")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);
  let band_stop_enabled: bool = args
    .get::<JsValue, _, _>(&mut cx, "enable_bandstop")?
    .downcast_or_throw::<JsBoolean, _>(&mut cx)?
    .value(&mut cx);
  let band_stop_low: f64 = args
    .get::<JsValue, _, _>(&mut cx, "bandstop_low")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);
  let band_stop_high: f64 = args
    .get::<JsValue, _, _>(&mut cx, "bandstop_high")?
    .downcast_or_throw::<JsNumber, _>(&mut cx)?
    .value(&mut cx);

  let config = EegFilterConfig {
    fs,
    high_pass_enabled,
    high_cut,
    low_pass_enabled,
    low_cut,
    band_pass_enabled,
    band_pass_low,
    band_pass_high,
    band_stop_enabled,
    band_stop_low,
    band_stop_high,
  };
  set_easy_eeg_filter(config);
  Ok(cx.undefined())
}

pub fn apply_easy_mode_filters(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let data = cx.argument::<JsFloat32Array>(0)?;
  let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
  let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
  let result = filter::apply_easy_mode_filters(data_vec, channel);
  let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in result.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}

pub fn apply_easy_mode_sosfiltfilt(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let data = cx.argument::<JsFloat32Array>(0)?;
  let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
  let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
  let result = filter::apply_easy_mode_sosfiltfilt(data_vec, channel);
  let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in result.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}

pub fn remove_env_noise_notch(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let data = cx.argument::<JsFloat32Array>(0)?;
  let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
  let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
  let result = filter::remove_env_noise_notch(data_vec, channel);
  let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in result.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}

pub fn remove_env_noise(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let data = cx.argument::<JsFloat32Array>(0)?;
  let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
  let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
  let result = filter::remove_env_noise(data_vec, channel);
  let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in result.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}

// pub fn sosfiltfilt_lowpass(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
//   let data = cx.argument::<JsFloat32Array>(0)?;
//   let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
//   let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
//   let result = filter::perform_lowpass_sosfiltfilt(data_vec, channel);
//   let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
//   let slice = js_float_array.as_mut_slice(&mut cx);
//   for (i, &value) in result.iter().enumerate() {
//     slice[i] = value as f32;
//   }
//   Ok(js_float_array)
// }

// pub fn sosfiltfilt_highpass(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
//   let data = cx.argument::<JsFloat32Array>(0)?;
//   let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
//   let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
//   let result = filter::perform_highpass_sosfiltfilt(data_vec, channel);
//   let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
//   let slice = js_float_array.as_mut_slice(&mut cx);
//   for (i, &value) in result.iter().enumerate() {
//     slice[i] = value as f32;
//   }
//   Ok(js_float_array)
// }

// pub fn sosfiltfilt_bandpass(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
//   let data = cx.argument::<JsFloat32Array>(0)?;
//   let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
//   let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
//   let result = filter::perform_bandpass_sosfiltfilt(data_vec, channel);
//   let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
//   let slice = js_float_array.as_mut_slice(&mut cx);
//   for (i, &value) in result.iter().enumerate() {
//     slice[i] = value as f32;
//   }
//   Ok(js_float_array)
// }

// pub fn sosfiltfilt_bandstop(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
//   let data = cx.argument::<JsFloat32Array>(0)?;
//   let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
//   let channel = cx.argument::<JsNumber>(1)?.value(&mut cx) as usize;
//   let result = filter::perform_bandstop_sosfiltfilt(data_vec, channel);
//   let mut js_float_array = JsFloat32Array::new(&mut cx, result.len())?;
//   let slice = js_float_array.as_mut_slice(&mut cx);
//   for (i, &value) in result.iter().enumerate() {
//     slice[i] = value as f32;
//   }
//   Ok(js_float_array)
// }

pub fn fftfreq(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let n: usize = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let d: f64 = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let freq = fft::fftfreq(n, d);
  let mut js_float_array = JsFloat32Array::new(&mut cx, freq.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in freq.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}

pub fn get_filtered_freq(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let n: usize = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let fs: f64 = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let freq = fft::get_filtered_freq(n, fs);
  let mut js_float_array = JsFloat32Array::new(&mut cx, freq.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in freq.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}

pub fn get_filtered_fft(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let data = cx.argument::<JsFloat32Array>(0)?;
  let fs: f64 = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let data_vec: Vec<f64> = data.as_slice(&mut cx).iter().map(|&x| x as f64).collect();
  let freq = fft::get_filtered_fft(&data_vec, fs);
  let mut js_float_array = JsFloat32Array::new(&mut cx, freq.len())?;
  let slice = js_float_array.as_mut_slice(&mut cx);
  for (i, &value) in freq.iter().enumerate() {
    slice[i] = value as f32;
  }
  Ok(js_float_array)
}
