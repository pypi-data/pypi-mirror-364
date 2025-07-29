use rustfft::num_complex::Complex;
use rustfft::FftPlanner;

#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn fftfreq(n: usize, d: f64) -> Vec<f64> {
  let mut freqs = Vec::with_capacity(n);
  let val = 1.0 / (n as f64 * d);
  let half_n = n / 2;

  for i in 0..half_n {
    freqs.push(i as f64 * val);
  }
  for i in half_n..n {
    freqs.push((i as f64 - n as f64) * val);
  }

  freqs
}

#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn get_filtered_freq(n: usize, fs: f64) -> Vec<f64> {
  let d = 1.0 / fs;
  let freq = fftfreq(n, d);
  // 提取频率在 0 到 80 Hz 之间的部分
  let pidxs: Vec<usize> = freq
    .iter()
    .enumerate()
    .filter(|&(_, &freq)| freq > 0.0 && freq < 80.0)
    .map(|(i, _)| i)
    .collect();

  let filtered_freq: Vec<f64> = pidxs.iter().map(|&i| freq[i]).collect();
  filtered_freq
}

#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub fn get_filtered_fft(data: &[f64], fs: f64) -> Vec<f64> {
  let (_, fft) = calculate_fft(data, fs);
  fft
}

pub fn calculate_fft(data: &[f64], fs: f64) -> (Vec<f64>, Vec<f64>) {
  let n = data.len();
  let d = 1.0 / fs;

  // 计算频率轴
  let freq = fftfreq(n, d);

  // 将实数数据转成 Complex<f64>
  let mut complex_data: Vec<Complex<f64>> =
    data.iter().map(|&re| Complex { re, im: 0.0 }).collect();

  // 创建 FFT 规划器
  let mut planner = FftPlanner::new();
  let fft = planner.plan_fft_forward(n);

  // 执行 FFT
  fft.process(&mut complex_data);

  // 计算 FFT 幅度
  let mag_fft: Vec<f64> = complex_data.iter().map(|c| c.norm() / (fs / 2.0)).collect();

  // 提取频率在 0 到 80 Hz 之间的部分
  let pidxs: Vec<usize> = freq
    .iter()
    .enumerate()
    .filter(|&(_, &freq)| freq > 0.0 && freq < 80.0)
    .map(|(i, _)| i)
    .collect();

  let filtered_freq: Vec<f64> = pidxs.iter().map(|&i| freq[i]).collect();
  let filtered_fft: Vec<f64> = pidxs.iter().map(|&i| mag_fft[i]).collect();

  (filtered_freq, filtered_fft)
}
