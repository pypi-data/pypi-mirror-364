use crate::data_handler::filter_bc::*;
use crate::data_handler::filter_sos::*;
use neon::prelude::*;
use neon::types::buffer::TypedArray;
use sci_rs::signal::filter::design::Sos;
use sci_rs::signal::filter::sosfiltfilt_dyn;
use std::cell::RefCell;

// crate::cfg_import_logging!();

pub struct SosFilter {
  pub sos_filter: Vec<Sos<f32>>,
}

impl SosFilter {
  pub fn create_notch_filter(f0: f32, fs: f32, quality: f32) -> Self {
    let sos_filter = design_notch_filter_f32(f0, fs, quality);
    SosFilter { sos_filter }
  }

  pub fn create_low_pass(order: u32, fs: f32, lowcut: f32) -> Self {
    let sos_filter = sos_butter_lowpass(order as usize, fs, lowcut);
    SosFilter { sos_filter }
  }

  pub fn create_high_pass(order: u32, fs: f32, highcut: f32) -> Self {
    let sos_filter = sos_butter_highpass(order as usize, fs, highcut);
    SosFilter { sos_filter }
  }

  pub fn create_band_pass(order: u32, fs: f32, lowcut: f32, highcut: f32) -> Self {
    let sos_filter = sos_butter_bandpass(order as usize, fs, lowcut, highcut);
    SosFilter { sos_filter }
  }

  pub fn create_band_stop(order: u32, fs: f32, lowcut: f32, highcut: f32) -> Self {
    let sos_filter = sos_butter_bandstop(order as usize, fs, lowcut, highcut);
    SosFilter { sos_filter }
  }

  // pub fn apply(&self, input: &[f32], output: &mut [f32]) {
  //   let filtered = sosfiltfilt_dyn(input.iter().copied(), &self.sos_filter);
  //   output.copy_from_slice(&filtered);
  // }

  pub fn apply(&self, input: &[f32]) -> Vec<f32> {
    sosfiltfilt_dyn(input.iter().copied(), &self.sos_filter)
  }
}

impl Finalize for SosFilter {}

// 构造函数
pub fn sos_create_notch_filter(mut cx: FunctionContext) -> JsResult<JsBox<SosFilter>> {
  let f0 = cx.argument::<JsNumber>(0)?.value(&mut cx);
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let quality = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let filter = SosFilter::create_notch_filter(f0 as f32, fs as f32, quality as f32);
  Ok(cx.boxed(filter))
}

pub fn sos_create_lowpass(mut cx: FunctionContext) -> JsResult<JsBox<SosFilter>> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as u32;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let lowcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let filter = SosFilter::create_low_pass(order, fs as f32, lowcut as f32);
  Ok(cx.boxed(filter))
}

pub fn sos_create_highpass(mut cx: FunctionContext) -> JsResult<JsBox<SosFilter>> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as u32;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let highcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let filter = SosFilter::create_high_pass(order, fs as f32, highcut as f32);
  Ok(cx.boxed(filter))
}

pub fn sos_create_bandpass(mut cx: FunctionContext) -> JsResult<JsBox<SosFilter>> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as u32;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let lowcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let highcut = cx.argument::<JsNumber>(3)?.value(&mut cx);
  let filter = SosFilter::create_band_pass(order, fs as f32, lowcut as f32, highcut as f32);
  Ok(cx.boxed(filter))
}

pub fn sos_create_bandstop(mut cx: FunctionContext) -> JsResult<JsBox<SosFilter>> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as u32;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let lowcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let highcut = cx.argument::<JsNumber>(3)?.value(&mut cx);
  let filter = SosFilter::create_band_stop(order, fs as f32, lowcut as f32, highcut as f32);
  Ok(cx.boxed(filter))
}

pub fn sosfiltfilt_apply(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let this = cx.argument::<JsBox<SosFilter>>(0)?;
  let signal = cx.argument::<JsFloat32Array>(1)?;

  let filtered_data = {
    let input_slice = signal.as_slice(&mut cx);
    this.apply(input_slice)
  };

  // 创建并填充输出数组
  let mut result_array = JsFloat32Array::new(&mut cx, filtered_data.len())?;
  result_array
    .as_mut_slice(&mut cx)
    .copy_from_slice(&filtered_data);

  Ok(result_array)
}

pub fn create_lowpass(mut cx: FunctionContext) -> JsResult<JsValue> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let lowcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let filter = LowPassFilter::new(order, fs, lowcut);
  Ok(cx.boxed(RefCell::new(filter)).upcast())
}

pub fn apply_lowpass(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let filter = cx.argument::<JsBox<RefCell<LowPassFilter>>>(0)?;
  let signal = cx.argument::<JsFloat32Array>(1)?;
  let filtered_data = {
    let input_slice = signal.as_slice(&mut cx).iter().map(|&x| x as f64);
    filter.borrow_mut().process_iter(input_slice)
  };

  // 创建并填充输出数组
  let mut result_array = JsFloat32Array::new(&mut cx, filtered_data.len())?;
  let f32_data: Vec<f32> = filtered_data.iter().map(|&x| x as f32).collect();
  result_array
    .as_mut_slice(&mut cx)
    .copy_from_slice(&f32_data);

  Ok(result_array)
}

pub fn create_highpass(mut cx: FunctionContext) -> JsResult<JsValue> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let highcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let filter = HighPassFilter::new(order, fs, highcut);
  Ok(cx.boxed(RefCell::new(filter)).upcast())
}

pub fn apply_highpass(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let filter = cx.argument::<JsBox<RefCell<HighPassFilter>>>(0)?;
  let signal = cx.argument::<JsFloat32Array>(1)?;
  let filtered_data = {
    let input_slice = signal.as_slice(&mut cx).iter().map(|&x| x as f64);
    filter.borrow_mut().process_iter(input_slice)
  };

  // 创建并填充输出数组
  let mut result_array = JsFloat32Array::new(&mut cx, filtered_data.len())?;
  let f32_data: Vec<f32> = filtered_data.iter().map(|&x| x as f32).collect();
  result_array
    .as_mut_slice(&mut cx)
    .copy_from_slice(&f32_data);

  Ok(result_array)
}

pub fn create_bandpass(mut cx: FunctionContext) -> JsResult<JsValue> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let lowcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let highcut = cx.argument::<JsNumber>(3)?.value(&mut cx);
  let filter = BandPassFilter::new(order, fs, lowcut, highcut);
  Ok(cx.boxed(RefCell::new(filter)).upcast())
}

pub fn apply_bandpass(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let filter = cx.argument::<JsBox<RefCell<BandPassFilter>>>(0)?;
  let signal = cx.argument::<JsFloat32Array>(1)?;
  let filtered_data = {
    let input_slice = signal.as_slice(&mut cx).iter().map(|&x| x as f64);
    filter.borrow_mut().process_iter(input_slice)
  };

  // 创建并填充输出数组
  let mut result_array = JsFloat32Array::new(&mut cx, filtered_data.len())?;
  let f32_data: Vec<f32> = filtered_data.iter().map(|&x| x as f32).collect();
  result_array
    .as_mut_slice(&mut cx)
    .copy_from_slice(&f32_data);

  Ok(result_array)
}

pub fn create_bandstop(mut cx: FunctionContext) -> JsResult<JsValue> {
  let order = cx.argument::<JsNumber>(0)?.value(&mut cx) as usize;
  let fs = cx.argument::<JsNumber>(1)?.value(&mut cx);
  let lowcut = cx.argument::<JsNumber>(2)?.value(&mut cx);
  let highcut = cx.argument::<JsNumber>(3)?.value(&mut cx);
  let filter = BandStopFilter::new(order, fs, lowcut, highcut);
  Ok(cx.boxed(RefCell::new(filter)).upcast())
}

pub fn apply_bandstop(mut cx: FunctionContext) -> JsResult<JsFloat32Array> {
  let filter = cx.argument::<JsBox<RefCell<BandStopFilter>>>(0)?;
  let signal = cx.argument::<JsFloat32Array>(1)?;
  let filtered_data = {
    let input_slice = signal.as_slice(&mut cx).iter().map(|&x| x as f64);
    filter.borrow_mut().process_iter(input_slice)
  };

  // 创建并填充输出数组
  let mut result_array = JsFloat32Array::new(&mut cx, filtered_data.len())?;
  let f32_data: Vec<f32> = filtered_data.iter().map(|&x| x as f32).collect();
  result_array
    .as_mut_slice(&mut cx)
    .copy_from_slice(&f32_data);

  Ok(result_array)
}
