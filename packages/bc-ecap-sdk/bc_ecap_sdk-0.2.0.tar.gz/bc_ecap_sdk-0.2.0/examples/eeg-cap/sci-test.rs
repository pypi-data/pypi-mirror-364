use bc_ecap_sdk::{
  data_handler::{
    enums::*,
    filter::*,
    filter_bc::{BandPassFilter, BrainCoFilter},
    filter_sos::*,
  },
  // generated::filter_bindings::*,
  utils::logging_desktop::init_logging,
};
use sci_rs::signal::filter::sosfiltfilt_dyn;
bc_ecap_sdk::cfg_import_logging!();
// use std::rand;

// cargo run --no-default-features --example sci-test --features="eeg-cap, examples"
fn main() {
  init_logging(log::Level::Debug);

  // Example usage of sos_butter_lowpass
  let sos_lowpass = sos_butter_lowpass(4, 250.0, 10.0);
  let data = (0..100000).map(|i| i as f32);
  let filtered_lowpass: Vec<f32> = sosfiltfilt_dyn(data.clone(), &sos_lowpass);

  // Example usage of sos_butter_highpass
  let sos_highpass = sos_butter_highpass(4, 250.0, 50.0);
  let filtered_highpass: Vec<f32> = sosfiltfilt_dyn(data.clone(), &sos_highpass);

  // Example usage of sos_butter_bandpass
  let sos_bandpass = sos_butter_bandpass(4, 250.0, 10.0, 50.0);
  let filtered_bandpass: Vec<f32> = sosfiltfilt_dyn(data.clone(), &sos_bandpass);

  // Example usage of sos_butter_bandstop
  let sos_bandstop = sos_butter_bandstop(4, 250.0, 10.0, 50.0);
  let filtered_bandstop: Vec<f32> = sosfiltfilt_dyn(data, &sos_bandstop);

  // Print the first few filtered values for demonstration
  info!("Filtered lowpass: {:?}", &filtered_lowpass[..10]);
  info!("Filtered highpass: {:?}", &filtered_highpass[..10]);
  info!("Filtered bandpass: {:?}", &filtered_bandpass[..10]);
  info!("Filtered bandstop: {:?}", &filtered_bandstop[..10]);

  // Example usage of sos_butter_lowpass
  let data1: Vec<f32> = (0..1000).map(|i| i as f32).collect();
  let data2: Vec<f32> = (1000..2000).map(|i| i as f32).collect();
  let filtered_lowpass1: Vec<f32> = sosfiltfilt_dyn(data1.clone().into_iter(), &sos_lowpass);
  let filtered_lowpass2: Vec<f32> = sosfiltfilt_dyn(data2.clone().into_iter(), &sos_lowpass);

  // Example usage of sos_butter_bandstop
  let filtered_bandstop1: Vec<f32> = sosfiltfilt_dyn(data1.into_iter(), &sos_bandstop);
  let filtered_bandstop2: Vec<f32> = sosfiltfilt_dyn(data2.into_iter(), &sos_bandstop);

  // Print the first few filtered values for demonstration
  info!("Filtered lowpass1: {:?}", &filtered_lowpass1[..10]);
  info!("Filtered lowpass2: {:?}", &filtered_lowpass2[..10]);
  info!("Filtered bandstop1: {:?}", &filtered_bandstop1[..10]);
  info!("Filtered bandstop2: {:?}", &filtered_bandstop2[..10]);

  // Example usage of set_env_noise_cfg and remove_env_noise
  set_env_noise_cfg(NoiseTypes::FIFTY, 250.0);
  let data = (0..1000).map(|i| i as f64);
  let filtered_data = remove_env_noise(data, 0);
  info!("Filtered data: {:?}", &filtered_data[..10]);

  test_perform_rolling_filter();
  test_easy_eeg_filter();
}

fn test_perform_rolling_filter() {
  // 示例数据
  let data: Vec<f64> = (0..1000)
    .map(|i| (i as f64).sin() + 0.5 * rand::random::<f64>())
    .collect();
  info!("Raw data: {:?}", &data[..10]);

  let window_size = 50;

  // 使用滚动均值滤波器
  let smoothed_data = perform_rolling_filter(data.clone(), window_size, AggOperations::Mean);
  let median_smoothed_data = perform_rolling_filter(data, window_size, AggOperations::Median);

  // 打印平滑后的前几个值以示范
  info!("Smoothed data: {:?}", &smoothed_data[..10]);
  info!("Median smoothed data: {:?}", &median_smoothed_data[..10]);
}

fn test_easy_eeg_filter() {
  let config = EegFilterConfig {
    fs: 250.0,
    high_pass_enabled: false,
    low_pass_enabled: false,
    band_pass_enabled: true,
    band_stop_enabled: true,
    high_cut: 0.5,
    low_cut: 49.0,
    band_pass_low: 2.0,
    band_pass_high: 45.0,
    band_stop_low: 49.0,
    band_stop_high: 51.0,
  };
  set_easy_eeg_filter(config);

  // 示例数据
  let data: Vec<f64> = (0..1000)
    .map(|i| (i as f64).sin() + 0.5 * rand::random::<f64>())
    .collect();
  info!("Raw data: {:?}", &data[..10]);
  let mut bp = BandPassFilter::new(4, 250.0, 2.0, 45.0);
  let filtered_data = bp.process_iter(data.clone());
  info!("Filtered data: {:?}", &filtered_data[..10]);

  // let bp_filter: *mut BWBandPass = unsafe { create_bw_band_pass_filter(4, 250.0, 2.0, 45.0) };
  // let filtered_data_2 = unsafe {
  //   data
  //     .iter()
  //     .map(|x| band_pass(bp_filter, *x))
  //     .collect::<Vec<f64>>()
  // };
  // info!("Filtered data 2: {:?}", &filtered_data_2[..10]);

  // let highpass_filter_data = perform_highpass(data.clone(), 4, 50.0, 250.0);
  // info!("Highpass filter data: {:?}", &highpass_filter_data);

  // let filter_data = apply_easy_mode_filters(data);
  // info!("Filtered data: {:?}", &filter_data[..10]);
}
