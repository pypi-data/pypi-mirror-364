use bc_ecap_sdk::data_handler::fft::calculate_fft;
use plotters::prelude::*;
use std::f64::consts::PI;

fn main() {
  // 采样率
  let fs = 250.0;
  // 输入信号长度
  let n = 100;

  // 构造一个简单的实数输入信号（示例：正弦波）
  let data: Vec<f64> = (0..n)
    .map(|x| (2.0 * PI * x as f64 / n as f64).sin())
    .collect();

  let (freq, fft) = calculate_fft(&data, fs);
  println!("Filtered Frequencies: {:?}", freq);
  println!("Filtered FFT: {:?}", fft);

  // 创建绘图区域
  let root = BitMapBackend::new("output.png", (640, 480)).into_drawing_area();
  root.fill(&WHITE).unwrap();
  let (upper, lower) = root.split_vertically(240);

  // 绘制时域图
  let mut chart = ChartBuilder::on(&upper)
    .caption("Time Domain", ("sans-serif", 20))
    .margin(10)
    .x_label_area_size(30)
    .y_label_area_size(30)
    .build_cartesian_2d(0..n, -1.0..1.0)
    .unwrap();

  chart.configure_mesh().draw().unwrap();
  chart
    .draw_series(LineSeries::new((0..n).map(|i| (i, data[i])), &BLUE))
    .unwrap();

  // 绘制频域图
  let mut chart = ChartBuilder::on(&lower)
    .caption("Frequency Domain", ("sans-serif", 20))
    .margin(10)
    .x_label_area_size(30)
    .y_label_area_size(30)
    .build_cartesian_2d(
      *freq.first().unwrap()..*freq.last().unwrap(),
      0.0..*fft.iter().max_by(|a, b| a.partial_cmp(b).unwrap()).unwrap(),
    )
    .unwrap();

  chart.configure_mesh().draw().unwrap();
  chart
    .draw_series(
      freq
        .iter()
        .zip(fft.iter())
        .map(|(&f, &m)| Rectangle::new([(f, 0.0), (f, m)], BLUE.filled())),
    )
    .unwrap();
}
