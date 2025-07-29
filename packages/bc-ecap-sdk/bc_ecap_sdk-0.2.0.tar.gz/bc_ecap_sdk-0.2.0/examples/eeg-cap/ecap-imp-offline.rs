//! Run with:
//!
//!     cargo run --no-default-features --example ecap-imp-offline --features="eeg-cap, examples"
//!

#![allow(unused_imports)]
use async_std::channel;
use bc_ecap_sdk::data_handler::enums::*;
use bc_ecap_sdk::data_handler::filter::*;
use bc_ecap_sdk::data_handler::filter_bc::*;
use bc_ecap_sdk::eeg_cap::data::*;
// use bc_ecap_sdk::generated::filter_bindings::*;
use bc_ecap_sdk::proto::eeg_cap::enums::*;
use sci_rs::signal::filter::sosfiltfilt_dyn;
use std::fs::File;
use std::io::BufRead;
use std::io::BufReader;
use tokio::task;

// use bc_ecap_sdk::proto::eeg_cap::msg_builder::eeg_cap_msg_builder;
use bc_ecap_sdk::utils::logging_desktop::init_logging;
bc_ecap_sdk::cfg_import_logging!();

#[tokio::main]
async fn main() {
  init_logging(log::Level::Info);

  read_values();

  // wait for message stream
  tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
}

pub fn read_values() {
  // const LOOP_CHECK: bool = false;
  const LOOP_CHECK: bool = true;
  // let freq = LeadOffFreq::Ac31p2hz;
  // let current = LeadOffCurrent::Cur6nA;

  let chip_label = if LOOP_CHECK { "chip_all" } else { "chip_1" };
  let file_path = format!("logs/eeg_leadoff_{}.log", chip_label);
  // read from file and process
  let f = File::open(file_path).unwrap();

  // const FS: f64 = 250.0;
  // set_env_noise_cfg(NoiseTypes::FIFTY, FS);

  let freq = LeadOffFreq::Ac31p2hz;
  let current = LeadOffCurrent::Cur6nA;
  // let current_u_a = current.get_current_uA();

  let loop_check = false;
  // let loop_check = true; // TODO: check filter issue
  save_lead_off_cfg(loop_check, freq, current);

  task::spawn(async move {
    let mut reader = BufReader::new(f);
    let mut buffer = String::new();
    // line e.g.
    // [1.0,2.0,-431.8356513977051,-591.1588668823242,-583.1122398376465,-340.1041030883789,-484.4069480895996,-547.7070808410645,-534.2960357666016,-588.4766578674316,-2308126.151561737,-2294752.1209716797,-2257635.176181793,-2252461.7314338684,-2302629.232406616,-2368510.1866722107,-2285399.7945785522,-2331550.9557724,-2315109.5509529114,-2307815.5517578125,-2234074.115753174,-2272400.736808777,-2297991.693019867,-2315408.8854789734,-2232686.3408088684,-2314976.5133857727,-2228841.1259651184,-2240532.875061035,-2165902.554988861,-2188736.2003326416,-2253507.7929496765,-2254178.8816452026,-2180167.078971863,-2272059.5598220825]
    // 0: timestamp, 1: seq_num, 2: 9 channels 0 ~ 7

    let mut segments: Vec<Vec<Vec<f64>>> = Vec::new();
    let mut current_segment: Vec<Vec<f64>> = Vec::new();

    // split into segments, per 250 samples
    while reader.read_line(&mut buffer).unwrap() > 0 {
      let data: Vec<f64> = serde_json::from_str(&buffer).unwrap();
      current_segment.push(data[2..10].to_vec());

      if current_segment.len() == 250 {
        segments.push(current_segment.clone());
        current_segment.clear();
      }

      buffer.clear();
    }

    // process each segment, 将 each segment row col swapped
    let mut transposed_segments: Vec<Vec<Vec<f64>>> = Vec::new();
    for segment in segments.iter() {
      let mut transposed_segment: Vec<Vec<f64>> = vec![vec![0.0; segment.len()]; segment[0].len()];
      for i in 0..segment.len() {
        for j in 0..segment[0].len() {
          transposed_segment[j][i] = segment[i][j];
        }
      }
      transposed_segments.push(transposed_segment);
    }

    // 打印处理后的数据
    for (i, segment) in transposed_segments.iter().enumerate() {
      info!("Segment {}: channel_num={:?}", i + 1, segment.len());
      for (channnel, data) in segment.iter().enumerate() {
        compute_test(channnel, data);
      }
      // break;
    }
  });
}

fn compute_test(channel: usize, raw_data: &[f64]) {
  // info!("[{}] data: {:?}\n", channel, raw_data.len());
  // info!("[{}] data: {:?}\n", channel, &raw_data[..3]);
  // let rms_raw = compute_rms(&raw_data);
  // let impedance_raw = compute_impedance_value(rms_raw, current_u_a);
  // info!("Raw RMS: {}, impedance: {}", rms_raw, impedance_raw);

  let current = LeadOffCurrent::Cur6nA;
  let current_u_a = current.get_current_uA();

  // BrainCo Filter
  let data = remove_env_noise(raw_data.iter().copied(), channel);
  let filter_mtx = perform_impendance_filter(data, channel);
  // info!("filter data: {:?}\n", &filter_mtx[..3]);
  let rms_mtx = compute_rms(&filter_mtx);
  let impedance_mtx = compute_impedance_value(rms_mtx, current_u_a);
  info!(
    "[{}] filter RMS: {}, impedance: {}",
    channel, rms_mtx, impedance_mtx
  );

  // C bindings Filter
  // let mut c_filter_data: Vec<f64> = vec![];
  // unsafe {
  //   for x in data.iter() {
  //     let mut value = band_stop(bs_filter_50, *x);
  //     value = band_stop(bs_filter_60, value);
  //     value = band_pass(bp_filter, value);
  //     // value = band_stop(bs_filter_60, value);
  //     // let value = band_pass(bp_filter_2, *x);
  //     c_filter_data.push(value);
  //   }
  // }
  // info!("c_filter_data: {:?}\n", &c_filter_data[..5]);
  // let rms_c = compute_rms(&c_filter_data);
  // let impedance_c = compute_impedance_value(rms_c, current_u_a);
  // info!("C bindings RMS: {}, impedance: {}", rms_c, impedance_c);

  // SOS filter
  // let filter_sos = sosfiltfilt_dyn(raw_data.into_iter(), &sos_bs_50);
  // let filter_sos = sosfiltfilt_dyn(filter_sos.into_iter(), &sos_bs_60);
  // let filter_sos = sosfiltfilt_dyn(filter_sos.into_iter(), &sos_bp);
  // // info!("filter sos: {:?}\n", &filter_sos[..5]);
  // let rms_sos = compute_rms(&filter_sos);
  // let impedance_sos = compute_impedance_value(rms_sos, current_u_a);
  // info!("Sos RMS: {}, impedance: {}", rms_sos, impedance_sos);
}

// C bindings Filter
// let bs_filter_50: *mut BWBandStop = unsafe { create_bw_band_stop_filter(4, FS, 49.0, 51.0) };
// let bs_filter_60: *mut BWBandStop = unsafe { create_bw_band_stop_filter(4, FS, 59.0, 61.0) };
// let bp_filter: *mut BWBandPass = unsafe { create_bw_band_pass_filter(4, FS, 30.0, 32.0) };

// BrainCo Filter
// let mut bs_50 = BandStopFilter::new(4, FS, 49.0, 51.0);
// let mut bs_60 = BandStopFilter::new(4, FS, 59.0, 61.0);
// let mut bp_imp = BandPassFilter::new(4, FS, 30.0, 32.0);

// SOS filter
// let sos_bs_50 = sos_butter_bandstop(4, 49.0, 51.0, FS);
// let sos_bs_60 = sos_butter_bandstop(4, 59.0, 61.0, FS);
// let sos_bp = sos_butter_bandpass(4, 30.0, 32.0, FS);
