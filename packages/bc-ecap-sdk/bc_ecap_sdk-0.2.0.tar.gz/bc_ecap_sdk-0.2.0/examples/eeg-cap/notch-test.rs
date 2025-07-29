use bc_ecap_sdk::data_handler::filter::*;
use bc_ecap_sdk::data_handler::filter_sos::*;
use bc_ecap_sdk::utils::logging_desktop::init_logging;
use plotters::prelude::LineSeries;
use plotters::prelude::*;
bc_ecap_sdk::cfg_import_logging!();

// use std::rand;

// cargo run --no-default-features --example notch-test --features="eeg-cap, examples"
fn main() {
  init_logging(log::Level::Debug);
  // test_multi_sampling_rates();
  // return;

  #[allow(unreachable_code)]
  // 采样率
  let fs = 250.0;
  // let fs = 500.0;
  // let fs = 1000.0;
  // let fs = 2000.0;
  let f0 = 50.0; // 50Hz干扰
  let f2 = 10.0; // 10Hz信号

  // 生成测试信号
  let (_signal_clean, signal_noise) = generate_test_signal(fs, f0, f2);

  // 应用滤波器
  let sos_filter = design_notch_filter(f0, fs, 30.0);
  let filtered_signal = apply_notch_filter(&sos_filter, &signal_noise);

  // 打印信号统计信息
  info!("\n原始信号统计:");
  let (mean, std, min, max) = calculate_signal_stats(&signal_noise);
  info!("Mean: {:.6}", mean);
  info!("Std: {:.6}", std);
  info!("Min: {:.6}, Max: {:.6}", min, max);

  info!("\n滤波后信号统计:");
  let (mean, std, min, max) = calculate_signal_stats(&filtered_signal);
  info!("Mean: {:.6}", mean);
  info!("Std: {:.6}", std);
  info!("Min: {:.6}, Max: {:.6}", min, max);

  // 计算信号差异
  let (max_diff, mean_diff) = calculate_signal_diff(&signal_noise, &filtered_signal);
  info!("\n信号差异:");
  info!("Max difference: {:.6}", max_diff);
  info!("Mean difference: {:.6}", mean_diff);

  // 保存图片
  if let Err(e) = plot_signals(&signal_noise, &filtered_signal, "rs_signal_comparison.png") {
    error!("Failed to plot signals: {}", e);
  }
}

fn plot_signals(
  signal: &[f64],
  filtered: &[f64],
  filename: &str,
) -> Result<(), Box<dyn std::error::Error>> {
  // 匹配 Python 的 figsize=(10, 6)，按 100 DPI 计算
  let root = BitMapBackend::new(filename, (1000, 600)).into_drawing_area();
  root.fill(&WHITE)?;

  // 计算信号的实际最大最小值来设置 Y 轴范围
  let signal_min = signal
    .iter()
    .chain(filtered.iter())
    .fold(f64::INFINITY, |a, &b| a.min(b));
  let signal_max = signal
    .iter()
    .chain(filtered.iter())
    .fold(f64::NEG_INFINITY, |a, &b| a.max(b));

  // 添加一些边距
  let y_margin = (signal_max - signal_min) * 0.1;
  let y_min = signal_min - y_margin;
  let y_max = signal_max + y_margin;

  // X 轴范围：0 到信号长度
  let max_sample = signal.len() as f64;

  let mut chart = ChartBuilder::on(&root)
    .caption("Rust Signal Comparison", ("sans-serif", 30))
    .margin(15) // 匹配 Python 的边距
    .x_label_area_size(50)
    .y_label_area_size(60)
    .build_cartesian_2d(0f64..max_sample, y_min..y_max)?;

  chart
    .configure_mesh()
    .x_desc("Sample")
    .y_desc("Amplitude")
    .axis_desc_style(("sans-serif", 12))
    .label_style(("sans-serif", 10))
    // .x_label_formatter(&|x| {
    //   // 只在特定值处显示标签
    //   if (*x as i32) % 250 == 0 {
    //     format!("{:.0}", x)
    //   } else {
    //     String::new()
    //   }
    // })
    .x_labels(12) // 设置 X 轴刻度数量
    // 或者手动设置特定刻度值
    // .x_tick_size(250.0) // 设置刻度间隔为 250
    // 设置 X 轴刻度间隔为 250
    .x_label_formatter(&|x| format!("{:.0}", x))
    .draw()?;

  // 绘制原始信号（红色，匹配 Python 的 "r"）
  chart
    .draw_series(LineSeries::new(
      signal.iter().enumerate().map(|(i, &v)| (i as f64, v)),
      &RED,
    ))?
    .label("Original")
    .legend(|(x, y)| PathElement::new(vec![(x, y), (x + 10, y)], RED));

  // 绘制滤波后信号（蓝色，匹配 Python 的 "b"）
  chart
    .draw_series(LineSeries::new(
      filtered.iter().enumerate().map(|(i, &v)| (i as f64, v)),
      &BLUE,
    ))?
    .label("Filtered")
    .legend(|(x, y)| PathElement::new(vec![(x, y), (x + 10, y)], BLUE));

  // 配置图例样式，匹配 Python
  chart
    .configure_series_labels()
    .background_style(&WHITE.mix(0.8))
    .border_style(&BLACK)
    .label_font(("sans-serif", 12))
    .draw()?;

  root.present()?;
  Ok(())
}

#[allow(dead_code)]
fn test_multi_sampling_rates() {
  let sampling_rates = [250.0, 500.0, 1000.0, 2000.0];
  let f0 = 50.0; // 50Hz干扰
  let f2 = 10.0; // 10Hz信号

  for fs in sampling_rates.iter() {
    info!("\n======= 测试采样率: {} Hz =======", fs);

    let (_signal_clean, signal_noise) = generate_test_signal(*fs, f0, f2);
    let sos_filter = design_notch_filter(f0, *fs, 30.0);
    let filtered_signal = apply_notch_filter(&sos_filter, &signal_noise);

    // 计算滤波效果
    let (_, original_std, origin_min, origin_max) = calculate_signal_stats(&signal_noise);
    let (_, filtered_std, filtered_min, filtered_max) = calculate_signal_stats(&filtered_signal);
    let noise_reduction = (original_std - filtered_std) / original_std * 100.0;

    info!("原始信号标准差: {:.6}", original_std);
    info!("滤波后标准差: {:.6}", filtered_std);
    info!(
      "原始信号最小值: {:.6}, 最大值: {:.6}",
      origin_min, origin_max
    );
    info!(
      "滤波后信号最小值: {:.6}, 最大值: {:.6}",
      filtered_min, filtered_max
    );
    info!("噪声降低: {:.2}%", noise_reduction);
  }
}
