use super::enums::{AggOperations, DownsamplingOperations, NoiseTypes};
use super::filter_bc::*;
use crate::data_handler::filter_sos::*;
use num_complex::Complex;
use num_traits::Float;
use parking_lot::{Mutex, RwLock};
use sci_rs::signal::filter::{design::*, sosfiltfilt_dyn};
use sci_rs::stats::*;
use std::f64::consts::PI;
crate::cfg_import_logging!();

const DEFAULT_ORDER: usize = 4; // Default filter order
const DEFAULT_FS: f64 = 250.0; // Default sampling frequency
const FS_50: f64 = 50.0; // 50Hz
const FS_60: f64 = 60.0; // 60Hz
const NOTCH_FILTER_QUALITY: f64 = 30.0; // Q factor for notch filter

const BAND_PASS_LOWER_CUTOFF: f64 = 2.0;
const BAND_PASS_HIGHER_CUTOFF: f64 = 45.0;

// Default FS is AC 31.2 Hz
const IMP_LOWER_CUTOFF: f64 = 30.0;
const IMP_HIGHER_CUTOFF: f64 = 32.0;

#[derive(Clone, Debug)]
pub struct EegFilterConfig {
  // 高通滤波器配置
  pub high_pass_enabled: bool,
  pub high_cut: f64,

  // 低通滤波器配置
  pub low_pass_enabled: bool,
  pub low_cut: f64,

  // 带通滤波器配置
  pub band_pass_enabled: bool,
  pub band_pass_low: f64,
  pub band_pass_high: f64,

  // 带阻滤波器配置
  pub band_stop_enabled: bool,
  pub band_stop_low: f64,
  pub band_stop_high: f64,

  // 采样率
  pub fs: f64,
}

lazy_static::lazy_static! {
  static ref ENV_NOISE_TYPE: RwLock<NoiseTypes> = RwLock::new(NoiseTypes::FIFTY_AND_SIXTY); // Default noise type is 50Hz and 60Hz
  static ref NOTCH_FILTER_50: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| design_notch_filter(FS_50, DEFAULT_FS, NOTCH_FILTER_QUALITY))); // Default FS is 250Hz
  static ref NOTCH_FILTER_60: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| design_notch_filter(FS_60, DEFAULT_FS, NOTCH_FILTER_QUALITY))); // Default FS is 250Hz
  static ref SOS_ENV_NOISE_FILTER_50: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_bandstop(DEFAULT_ORDER, DEFAULT_FS, FS_50-1.0, FS_50+1.0))); // Default FS is 250Hz
  static ref SOS_ENV_NOISE_FILTER_60: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_bandstop(DEFAULT_ORDER, DEFAULT_FS, FS_60-1.0, FS_60+1.0))); // Default FS is 250Hz
  static ref SOS_IMPEDANCE_FILTER_31_2: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_bandpass(DEFAULT_ORDER, DEFAULT_FS, IMP_LOWER_CUTOFF, IMP_HIGHER_CUTOFF))); // Default FS is AC 31.2 Hz
  static ref SOS_EEG_FILTER_2_45: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_bandpass(DEFAULT_ORDER, DEFAULT_FS, BAND_PASS_LOWER_CUTOFF, BAND_PASS_HIGHER_CUTOFF))); // Default FS is 250Hz

  static ref ENV_NOISE_FILTER_50: Mutex<[BandStopFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandStopFilter::new(DEFAULT_ORDER, DEFAULT_FS, FS_50-1.0, FS_50+1.0))); // Default FS is 250Hz
  static ref ENV_NOISE_FILTER_60: Mutex<[BandStopFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandStopFilter::new(DEFAULT_ORDER, DEFAULT_FS, FS_60-1.0, FS_60+1.0))); // Default FS is 250Hz
  static ref IMPEDANCE_FILTER_31_2: Mutex<[BandPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandPassFilter::new(DEFAULT_ORDER, DEFAULT_FS, IMP_LOWER_CUTOFF, IMP_HIGHER_CUTOFF))); // Default FS is AC 31.2 Hz
  static ref EEG_FILTER_2_45: Mutex<[BandPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandPassFilter::new(DEFAULT_ORDER, DEFAULT_FS, BAND_PASS_LOWER_CUTOFF, BAND_PASS_HIGHER_CUTOFF))); // Default FS is 250Hz

  // easy mode filters
  static ref EEG_FILTER_CONFIG: RwLock<EegFilterConfig> = RwLock::new(EegFilterConfig {
    high_pass_enabled: false,
    high_cut: 1.0,
    low_pass_enabled: false,
    low_cut: 30.0,
    band_pass_enabled: false,
    band_pass_low: 8.0,
    band_pass_high: 13.0,
    band_stop_enabled: false,
    band_stop_low: FS_50 - 1.0,
    band_stop_high: FS_50 + 1.0,
    fs: DEFAULT_FS,
  });

  // https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.filtfilt.html
  // https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html
  static ref SOS_FILTER_HIGH_PASS: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_highpass(DEFAULT_ORDER, DEFAULT_FS, 1.0))); // Default FS is 250Hz
  static ref SOS_FILTER_LOW_PASS: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_lowpass(DEFAULT_ORDER, DEFAULT_FS, 30.0))); // Default FS is 250Hz
  static ref SOS_FILTER_BAND_PASS: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_bandpass(DEFAULT_ORDER, DEFAULT_FS, 8.0, 13.0))); // Default FS is 250Hz
  static ref SOS_FILTER_BAND_STOP: RwLock<[Vec<Sos<f64>>; 32]> = RwLock::new(core::array::from_fn(|_| sos_butter_bandstop(DEFAULT_ORDER, DEFAULT_FS, FS_50-1.0, FS_50+1.0))); // Default FS is 250Hz

  static ref EEG_FILTER_HIGH_PASS: Mutex<[HighPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| HighPassFilter::new(DEFAULT_ORDER, DEFAULT_FS, 1.0))); // Default FS is 250Hz
  static ref EEG_FILTER_LOW_PASS: Mutex<[LowPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| LowPassFilter::new(DEFAULT_ORDER, DEFAULT_FS, 30.0))); // Default FS is 250Hz
  static ref EEG_FILTER_BAND_PASS: Mutex<[BandPassFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandPassFilter::new(DEFAULT_ORDER, DEFAULT_FS, 8.0, 13.0))); // Default FS is 250Hz
  static ref EEG_FILTER_BAND_STOP: Mutex<[BandStopFilter; 32]> = Mutex::new(core::array::from_fn(|_| BandStopFilter::new(DEFAULT_ORDER, DEFAULT_FS, FS_50-1.0, FS_50+1.0))); // Default FS is 250Hz
}

// easy mode filters
pub fn set_easy_eeg_filter(config: EegFilterConfig) {
  let mut eeg_filter_config = EEG_FILTER_CONFIG.write();
  *eeg_filter_config = config.clone();

  let mut eeg_filter_high_pass = EEG_FILTER_HIGH_PASS.lock();
  let mut eeg_filter_low_pass = EEG_FILTER_LOW_PASS.lock();
  let mut eeg_filter_band_pass = EEG_FILTER_BAND_PASS.lock();
  let mut eeg_filter_band_stop = EEG_FILTER_BAND_STOP.lock();
  let mut sos_filter_high_pass = SOS_FILTER_HIGH_PASS.write();
  let mut sos_filter_low_pass = SOS_FILTER_LOW_PASS.write();
  let mut sos_filter_band_pass = SOS_FILTER_BAND_PASS.write();
  let mut sos_filter_band_stop = SOS_FILTER_BAND_STOP.write();

  let fs = config.fs;
  for i in 0..32 {
    eeg_filter_high_pass[i] = HighPassFilter::new(DEFAULT_ORDER, fs, config.high_cut);
    eeg_filter_low_pass[i] = LowPassFilter::new(DEFAULT_ORDER, fs, config.low_cut);
    eeg_filter_band_pass[i] = BandPassFilter::new(
      DEFAULT_ORDER,
      fs,
      config.band_pass_low,
      config.band_pass_high,
    );
    eeg_filter_band_stop[i] = BandStopFilter::new(
      DEFAULT_ORDER,
      fs,
      config.band_stop_low,
      config.band_stop_high,
    );

    let low_cut = config.low_cut;
    let high_cut = config.high_cut;
    let band_pass_low = config.band_pass_low;
    let band_pass_high = config.band_pass_high;
    let band_stop_low = config.band_stop_low;
    let band_stop_high = config.band_stop_high;
    sos_filter_high_pass[i] = sos_butter_highpass(DEFAULT_ORDER, fs, high_cut);
    sos_filter_low_pass[i] = sos_butter_lowpass(DEFAULT_ORDER, fs, low_cut);
    sos_filter_band_pass[i] = sos_butter_bandpass(DEFAULT_ORDER, fs, band_pass_low, band_pass_high);
    sos_filter_band_stop[i] = sos_butter_bandstop(DEFAULT_ORDER, fs, band_stop_low, band_stop_high);
  }
}

pub fn apply_easy_mode_filters(data: Vec<f64>, channel: usize) -> Vec<f64> {
  let eeg_filter = EEG_FILTER_CONFIG.read();

  let mut filter_data = data;
  if eeg_filter.high_pass_enabled {
    let mut high_pass = EEG_FILTER_HIGH_PASS.lock();
    filter_data = high_pass[channel].process_iter(filter_data);
  }
  if eeg_filter.low_pass_enabled {
    let mut low_pass = EEG_FILTER_LOW_PASS.lock();
    filter_data = low_pass[channel].process_iter(filter_data);
  }
  if eeg_filter.band_pass_enabled {
    let mut band_pass = EEG_FILTER_BAND_PASS.lock();
    filter_data = band_pass[channel].process_iter(filter_data);
  }
  if eeg_filter.band_stop_enabled {
    let mut band_stop = EEG_FILTER_BAND_STOP.lock();
    filter_data = band_stop[channel].process_iter(filter_data);
  }
  filter_data
}

pub fn apply_easy_mode_sosfiltfilt(data: Vec<f64>, channel: usize) -> Vec<f64> {
  let eeg_filter = EEG_FILTER_CONFIG.read();

  let mut filter_data = data;
  if eeg_filter.high_pass_enabled {
    let high_pass = SOS_FILTER_HIGH_PASS.read();
    filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &high_pass[channel]);
  }
  if eeg_filter.low_pass_enabled {
    let low_pass = SOS_FILTER_LOW_PASS.read();
    filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &low_pass[channel]);
  }
  if eeg_filter.band_pass_enabled {
    let band_pass = SOS_FILTER_BAND_PASS.read();
    filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &band_pass[channel]);
  }
  if eeg_filter.band_stop_enabled {
    let band_stop = SOS_FILTER_BAND_STOP.read();
    filter_data = sosfiltfilt_dyn(filter_data.into_iter(), &band_stop[channel]);
  }
  filter_data
}

// Set the noise type & FS for the environment
pub fn set_env_noise_cfg(noise_type: NoiseTypes, fs: f64) {
  let mut env_noise_type = ENV_NOISE_TYPE.write();
  *env_noise_type = noise_type;

  let mut notch_filter_50 = NOTCH_FILTER_50.write();
  let mut notch_filter_60 = NOTCH_FILTER_60.write();
  let mut env_noise_filter_50 = ENV_NOISE_FILTER_50.lock();
  let mut env_noise_filter_60 = ENV_NOISE_FILTER_60.lock();
  let mut sos_env_noise_filter_50 = SOS_ENV_NOISE_FILTER_50.write();
  let mut sos_env_noise_filter_60 = SOS_ENV_NOISE_FILTER_60.write();

  let mut eeg_filter = EEG_FILTER_2_45.lock();
  let mut impedance_filter = IMPEDANCE_FILTER_31_2.lock();
  let mut sos_eeg_filter = SOS_EEG_FILTER_2_45.write();
  let mut sos_impedance_filter = SOS_IMPEDANCE_FILTER_31_2.write();

  let sample_rate = fs;
  for i in 0..32 {
    notch_filter_50[i] = design_notch_filter(FS_50, fs, NOTCH_FILTER_QUALITY);
    notch_filter_60[i] = design_notch_filter(FS_60, fs, NOTCH_FILTER_QUALITY);
    env_noise_filter_50[i] =
      BandStopFilter::new(DEFAULT_ORDER, sample_rate, FS_50 - 1.0, FS_50 + 1.0);
    env_noise_filter_60[i] =
      BandStopFilter::new(DEFAULT_ORDER, sample_rate, FS_60 - 1.0, FS_60 + 1.0);
    sos_env_noise_filter_50[i] = sos_butter_bandstop(DEFAULT_ORDER, fs, FS_50 - 1.0, FS_50 + 1.0);
    sos_env_noise_filter_60[i] = sos_butter_bandstop(DEFAULT_ORDER, fs, FS_60 - 1.0, FS_60 + 1.0);

    eeg_filter[i] = BandPassFilter::new(
      4,
      sample_rate,
      BAND_PASS_LOWER_CUTOFF,
      BAND_PASS_HIGHER_CUTOFF,
    );
    sos_eeg_filter[i] = sos_butter_bandpass(
      DEFAULT_ORDER,
      fs,
      BAND_PASS_LOWER_CUTOFF,
      BAND_PASS_HIGHER_CUTOFF,
    );
    impedance_filter[i] = BandPassFilter::new(
      DEFAULT_ORDER,
      sample_rate,
      IMP_LOWER_CUTOFF,
      IMP_HIGHER_CUTOFF,
    );
    sos_impedance_filter[i] =
      sos_butter_bandpass(DEFAULT_ORDER, fs, IMP_LOWER_CUTOFF, IMP_HIGHER_CUTOFF);
  }
}

// Remove environmental noise from input data by notch filter
pub fn remove_env_noise_notch<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let env_noise_type = ENV_NOISE_TYPE.read();
  match *env_noise_type {
    NoiseTypes::FIFTY => {
      let notch_filter_50 = NOTCH_FILTER_50.read();
      // apply_notch_filter(&notch_filter_50[channel], input)
      sosfiltfilt_dyn(input.into_iter(), &notch_filter_50[channel])
    }
    NoiseTypes::SIXTY => {
      let notch_filter_60 = NOTCH_FILTER_60.read();
      // apply_notch_filter(&notch_filter_60[channel], input)
      sosfiltfilt_dyn(input.into_iter(), &notch_filter_60[channel])
    }
    NoiseTypes::FIFTY_AND_SIXTY => {
      let notch_filter_50 = NOTCH_FILTER_50.read();
      let notch_filter_60 = NOTCH_FILTER_60.read();
      // let data = apply_notch_filter(&notch_filter_50[channel], input);
      // apply_notch_filter(&notch_filter_60[channel], data)
      let data = sosfiltfilt_dyn(input.into_iter(), &notch_filter_50[channel]);
      sosfiltfilt_dyn(data.into_iter(), &notch_filter_60[channel])
    }
  }
}

// Remove environmental noise from input data by sosfiltfilt
pub fn remove_env_noise_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let env_noise_type = ENV_NOISE_TYPE.read();
  match *env_noise_type {
    NoiseTypes::FIFTY => {
      let sos_env_noise_filter_50 = SOS_ENV_NOISE_FILTER_50.read();
      sosfiltfilt_dyn(input.into_iter(), &sos_env_noise_filter_50[channel])
    }
    NoiseTypes::SIXTY => {
      let sos_env_noise_filter_60 = SOS_ENV_NOISE_FILTER_60.read();
      sosfiltfilt_dyn(input.into_iter(), &sos_env_noise_filter_60[channel])
    }
    NoiseTypes::FIFTY_AND_SIXTY => {
      let sos_env_noise_filter_50 = SOS_ENV_NOISE_FILTER_50.read();
      let sos_env_noise_filter_60 = SOS_ENV_NOISE_FILTER_60.read();
      let data = sosfiltfilt_dyn(input.into_iter(), &sos_env_noise_filter_50[channel]);
      sosfiltfilt_dyn(data.into_iter(), &sos_env_noise_filter_60[channel])
    }
  }
}

// Remove environmental noise from input data
pub fn remove_env_noise<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let env_noise_type = ENV_NOISE_TYPE.read();
  match *env_noise_type {
    NoiseTypes::FIFTY => {
      // info!("Removing 50Hz noise");
      let mut env_noise_filter_50 = ENV_NOISE_FILTER_50.lock();
      env_noise_filter_50[channel].process_iter(input)
    }
    NoiseTypes::SIXTY => {
      // info!("Removing 60Hz noise");
      let mut env_noise_filter_60 = ENV_NOISE_FILTER_60.lock();
      env_noise_filter_60[channel].process_iter(input)
    }
    NoiseTypes::FIFTY_AND_SIXTY => {
      // info!("Removing 50Hz and 60Hz noise");
      let mut env_noise_filter_50 = ENV_NOISE_FILTER_50.lock();
      let mut env_noise_filter_60 = ENV_NOISE_FILTER_60.lock();
      let data = env_noise_filter_50[channel].process_iter(input);
      env_noise_filter_60[channel].process_iter(data)
    }
  }
}

pub fn perform_impendance_filter<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  // info!("Performing impedance filter");
  let mut filter = IMPEDANCE_FILTER_31_2.lock();
  filter[channel].process_iter(input)
}

pub fn perform_impendance_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let filter = SOS_IMPEDANCE_FILTER_31_2.read();
  sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

pub fn perform_eeg_filter<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let mut eeg_filter = EEG_FILTER_2_45.lock();
  eeg_filter[channel].process_iter(input)
}

pub fn perform_eeg_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let filter = SOS_EEG_FILTER_2_45.read();
  sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

pub fn perform_lowpass_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let filter = SOS_FILTER_LOW_PASS.read();
  sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

pub fn perform_highpass_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let filter = SOS_FILTER_HIGH_PASS.read();
  sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

pub fn perform_bandpass_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let filter = SOS_FILTER_BAND_PASS.read();
  sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

pub fn perform_bandstop_sosfiltfilt<I>(input: I, channel: usize) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let filter = SOS_FILTER_BAND_STOP.read();
  sosfiltfilt_dyn(input.into_iter(), &filter[channel])
}

// Perform rolling filter operation
pub fn perform_rolling_filter<I>(
  input: I,
  window_size: usize,
  agg_operation: AggOperations,
) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let input: Vec<f64> = input.into_iter().collect();
  let input_len = input.len();
  let mut output = Vec::with_capacity(input_len);

  for i in 0..input_len {
    let start = if i >= window_size / 2 {
      i - window_size / 2
    } else {
      0
    };
    let end = if i + window_size / 2 < input_len {
      i + window_size / 2
    } else {
      input_len - 1
    };
    let window_slice = (input[start..=end]).iter();

    let value = match agg_operation {
      AggOperations::Mean => {
        let (mean_value, _) = mean(window_slice);
        mean_value
      }
      AggOperations::Median => {
        let (median_value, _) = median(window_slice);
        median_value
      }
    };

    output.push(value);
  }

  output
}

// perform_downsampling
pub fn perform_downsampling<I>(
  input: I,
  window_size: usize,
  operation: DownsamplingOperations,
) -> Vec<f64>
where
  I: IntoIterator<Item = f64>,
{
  let input: Vec<f64> = input.into_iter().collect();
  let num_values = input.len() / window_size;
  let mut output = Vec::with_capacity(match operation {
    DownsamplingOperations::Extremes => num_values * 2,
    _ => num_values,
  });

  for i in 0..num_values {
    let segment = &input[i * window_size..(i + 1) * window_size];
    match operation {
      DownsamplingOperations::Mean => {
        let (mean_value, _) = mean(segment.iter());
        output.push(mean_value);
      }
      DownsamplingOperations::Median => {
        let (media_value, _) = median(segment.iter());
        output.push(media_value);
      }
      DownsamplingOperations::Max => {
        if let Some(max) = segment
          .iter()
          .cloned()
          .max_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(max);
        }
      }
      DownsamplingOperations::Min => {
        if let Some(min) = segment
          .iter()
          .cloned()
          .min_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(min);
        }
      }
      DownsamplingOperations::Sum => {
        let sum: f64 = segment.iter().sum();
        output.push(sum);
      }
      DownsamplingOperations::First => {
        output.push(segment[0]);
      }
      DownsamplingOperations::Last => {
        output.push(segment[window_size - 1]);
      }
      DownsamplingOperations::Extremes => {
        if let Some(min) = segment
          .iter()
          .cloned()
          .min_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(min);
        }
        if let Some(max) = segment
          .iter()
          .cloned()
          .max_by(|a, b| a.partial_cmp(b).unwrap())
        {
          output.push(max);
        }
      }
    }
  }

  output
}

/// 生成测试信号，完全匹配Python的np.linspace实现
pub fn generate_test_signal(fs: f64, f1: f64, f2: f64) -> (Vec<f64>, Vec<f64>) {
  let n = fs as usize; // 采样点数
  let t: Vec<f64> = (0..n)
    .map(|i| i as f64 / (n - 1) as f64) // 除以(n-1)确保最后一个点是1.0
    .collect();

  let signal_clean: Vec<f64> = t.iter().map(|&x| (2.0 * PI * f2 * x).sin()).collect();
  let signal_noise: Vec<f64> = signal_clean
    .iter()
    .zip(t.iter())
    .map(|(&clean, &x)| clean + 0.5 * (2.0 * PI * f1 * x).sin())
    .collect();

  (signal_clean, signal_noise)
}

/// 计算信号的统计信息
pub fn calculate_signal_stats(signal: &[f64]) -> (f64, f64, f64, f64) {
  let mean = signal.iter().sum::<f64>() / signal.len() as f64;
  let std = calculate_std(signal);
  let min = signal.iter().fold(f64::INFINITY, |a, &b| a.min(b));
  let max = signal.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
  (mean, std, min, max)
}

/// 计算信号的标准差
pub fn calculate_std(signal: &[f64]) -> f64 {
  let mean = signal.iter().sum::<f64>() / signal.len() as f64;
  let variance = signal.iter().map(|&x| (x - mean).powi(2)).sum::<f64>() / signal.len() as f64;
  variance.sqrt()
}

/// 计算两个信号之间的差异
pub fn calculate_signal_diff(signal1: &[f64], signal2: &[f64]) -> (f64, f64) {
  let max_diff = signal1
    .iter()
    .zip(signal2.iter())
    .map(|(&x, &y)| (x - y).abs())
    .fold(0.0, f64::max);
  let mean_diff = signal1
    .iter()
    .zip(signal2.iter())
    .map(|(&x, &y)| (x - y).abs())
    .sum::<f64>()
    / signal1.len() as f64;
  (max_diff, mean_diff)
}

/// 多项式相乘
/// a, b: 系数数组，返回相乘后的新多项式系数
pub fn poly_mul<T: Float>(a: &[T], b: &[T]) -> Vec<T> {
  let mut result = vec![T::zero(); a.len() + b.len() - 1];
  for (i, &ai) in a.iter().enumerate() {
    for (j, &bj) in b.iter().enumerate() {
      result[i + j] = result[i + j] + ai * bj;
    }
  }
  result
}

/// 零极点-增益(zpk)转传递函数(tf)
/// zeros: 零点，poles: 极点，k: 增益
/// 返回(b, a): 分子分母多项式系数
pub fn zpk2tf<T: Float>(zeros: &[Complex<T>], poles: &[Complex<T>], k: T) -> (Vec<T>, Vec<T>) {
  let mut b = vec![k];
  for &z in zeros {
    b = poly_mul(&b, &[T::one(), -z.re]);
  }
  let mut a = vec![T::one()];
  for &p in poles {
    a = poly_mul(&a, &[T::one(), -p.re]);
  }
  (b, a)
}

/// 组合数
pub fn binomial<T: Float>(n: usize, k: usize) -> T {
  (0..k).fold(T::one(), |acc, i| {
    acc * T::from(n - i).unwrap() / T::from(i + 1).unwrap()
  })
}

/// 双线性变换（模拟域->数字域）
/// b, a: 模拟域分子分母系数，fs: 采样率
/// 返回(bz, az): 数字域分子分母系数
pub fn bilinear<T: Float>(b: &[T], a: &[T], fs: T) -> (Vec<T>, Vec<T>) {
  let degree = a.len().max(b.len()) - 1;
  let mut b_pad = b.to_vec();
  let mut a_pad = a.to_vec();
  b_pad.resize(degree + 1, T::zero());
  a_pad.resize(degree + 1, T::zero());
  let t = T::from(2.0).unwrap() * fs;
  let mut bz = vec![T::zero(); degree + 1];
  let mut az = vec![T::zero(); degree + 1];
  for i in 0..=degree {
    for j in 0..=i {
      let c = binomial::<T>(i, j) * binomial::<T>(degree, i);
      bz[j] = bz[j] + c * b_pad[i] * t.powi(i as i32 - j as i32);
      az[j] = az[j] + c * a_pad[i] * t.powi(i as i32 - j as i32);
    }
  }
  // 归一化
  let a0 = az[0];
  for v in bz.iter_mut() {
    *v = *v / a0;
  }
  for v in az.iter_mut() {
    *v = *v / a0;
  }
  (bz, az)
}
