use core::iter::Sum;
use nalgebra::RealField;
use num_traits::Float;
use sci_rs::signal::filter::{design::*, sosfiltfilt_dyn};

crate::cfg_import_logging!();

#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
pub struct SosFilter {
  sos_filter: Vec<Sos<f64>>,
}

#[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
impl SosFilter {
  // pub fn new(sos: Vec<Sos<f64>>) -> Self {
  //   SosFilter { sos }
  // }

  pub fn create_lowpass(order: usize, fs: f64, lowcut: f64) -> Self {
    let sos_filter = sos_butter_lowpass(order, fs, lowcut);
    SosFilter { sos_filter }
  }

  pub fn create_highpass(order: usize, fs: f64, highcut: f64) -> Self {
    let sos_filter = sos_butter_highpass(order, fs, highcut);
    SosFilter { sos_filter }
  }

  pub fn create_bandpass(order: usize, fs: f64, lowcut: f64, highcut: f64) -> Self {
    let sos_filter = sos_butter_bandpass(order, fs, lowcut, highcut);
    SosFilter { sos_filter }
  }

  pub fn create_bandstop(order: usize, fs: f64, lowcut: f64, highcut: f64) -> Self {
    let sos_filter = sos_butter_bandstop(order, fs, lowcut, highcut);
    SosFilter { sos_filter }
  }
}

impl SosFilter {
  pub fn perform<I>(&self, input: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  }

  // pub fn perform_lowpass<I>(self, input: I) -> Vec<f64>
  // where
  //   I: IntoIterator<Item = f64>,
  // {
  //   sosfiltfilt_dyn(input.into_iter(), &self.sos_filter)
  // }
}

/// 设计陷波滤波器
pub fn design_notch_filter(f0: f64, fs: f64, q: f64) -> Vec<Sos<f64>> {
  let notch_coeffs = get_notch_coeffs(fs, f0, q);
  vec![Sos {
    b: notch_coeffs.b,
    a: notch_coeffs.a,
    zi0: 0.0,
    zi1: 0.0,
  }]
}

pub fn design_notch_filter_f32(f0: f32, fs: f32, q: f32) -> Vec<Sos<f32>> {
  let notch_coeffs = get_notch_coeffs(fs as f64, f0 as f64, q as f64);
  vec![Sos {
    b: notch_coeffs.b.map(|x| x as f32),
    a: notch_coeffs.a.map(|x| x as f32),
    zi0: 0.0,
    zi1: 0.0,
  }]
}

/// 应用陷波滤波器
pub fn apply_notch_filter(sos: &Vec<Sos<f64>>, signal: &[f64]) -> Vec<f64> {
  sosfiltfilt_dyn(signal.iter().copied(), sos)
}

// MATLAB style function to generate Second Order Section (SOS) lowpass filter
pub fn sos_butter_lowpass<F>(order: usize, fs: F, lowcut: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    [lowcut].to_vec(),
    Some(FilterBandType::Lowpass),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// MATLAB style function to generate Second Order Section (SOS) highpass filter
pub fn sos_butter_highpass<F>(order: usize, fs: F, highcut: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    [highcut].to_vec(),
    Some(FilterBandType::Highpass),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// MATLAB style function to generate Second Order Section (SOS) bandpass filter
pub fn sos_butter_bandpass<F>(order: usize, fs: F, lowcut: F, highcut: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    vec![lowcut, highcut],
    Some(FilterBandType::Bandpass),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// MATLAB style function to generate Second Order Section (SOS) bandstop filter
pub fn sos_butter_bandstop<F>(order: usize, fs: F, lowcut: F, highcut: F) -> Vec<Sos<F>>
where
  F: Float + RealField + Sum,
{
  // Design Second Order Section (SOS) filter
  let filter = butter_dyn(
    order,
    vec![lowcut, highcut],
    Some(FilterBandType::Bandstop),
    Some(false),
    Some(FilterOutputType::Sos),
    Some(fs),
  );
  let DigitalFilter::Sos(SosFormatFilter { sos }) = filter else {
    panic!("Failed to design filter");
  };
  sos
}

// pub fn perform_lowpass<I>(input: I, order: usize, fs: f64, lowcut: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_lowpass(order, fs, lowcut);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// pub fn perform_highpass<I>(input: I, order: usize, fs: f64, highcut: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_highpass(order, fs, highcut);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// pub fn perform_bandpass<I>(input: I, order: usize, fs: f64, lowcut: f64, highcut: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_bandpass(order, fs, lowcut, highcut);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

// pub fn perform_bandstop<I>(input: I, order: usize, fs: f64, lowcut: f64, highcut: f64) -> Vec<f64>
// where
//   I: IntoIterator<Item = f64>,
// {
//   let sos_filter = sos_butter_bandstop(order, fs, lowcut, highcut);
//   sosfiltfilt_dyn(input.into_iter(), &sos_filter)
// }

/// 完全等价scipy.signal.iirnotch
fn iirnotch(f0: f64, q: f64, fs: f64) -> ([f64; 3], [f64; 3]) {
  let t = 2.0 * std::f64::consts::PI * f0 / fs;
  let alpha = t.sin() / (2.0 * q);
  let b0 = 1.0;
  let b1 = -2.0 * t.cos();
  let b2 = 1.0;
  let a0 = 1.0 + alpha;
  let a1 = -2.0 * t.cos();
  let a2 = 1.0 - alpha;
  let b = [b0 / a0, b1 / a0, b2 / a0];
  let a = [1.0, a1 / a0, a2 / a0];
  (b, a)
}

/// 计算陷波滤波器（notch）系数
/// fs: 采样率, f0: 陷波频率, q: 品质因数
/// 返回 NotchCoeffs 结构体，包含b, a系数
pub struct NotchCoeffs<T>
where
  T: Float,
{
  pub b: [T; 3],
  pub a: [T; 3],
}

/// 获取指定采样率和陷波频率的滤波器系数
pub fn get_notch_coeffs(fs: f64, f0: f64, q: f64) -> NotchCoeffs<f64> {
  // 检查是否在预定义的采样率和陷波频率范围内
  let is_predefined = matches!(
    (fs, f0),
    (250.0, 50.0)
      | (500.0, 50.0)
      | (1000.0, 50.0)
      | (2000.0, 50.0)
      | (4000.0, 50.0)
      | (250.0, 60.0)
      | (500.0, 60.0)
      | (1000.0, 60.0)
      | (2000.0, 60.0)
      | (4000.0, 60.0)
  );

  if is_predefined {
    // 使用Python生成的系数
    match (fs, f0) {
      // 50Hz陷波
      (250.0, 50.0) => NotchCoeffs {
        b: [0.9794827609814495, -0.6053536376811252, 0.9794827609814495],
        a: [1.0, -0.6053536376811252, 0.958965521962899],
      },
      (500.0, 50.0) => NotchCoeffs {
        b: [0.9896361753628921, -1.6012649682336106, 0.9896361753628921],
        a: [1.0, -1.6012649682336106, 0.9792723507257841],
      },
      (1000.0, 50.0) => NotchCoeffs {
        b: [0.9947912376593769, -1.8922053778585424, 0.9947912376593769],
        a: [1.0, -1.8922053778585424, 0.9895824753187539],
      },
      (2000.0, 50.0) => NotchCoeffs {
        b: [0.9973888361673892, -1.9702186490445686, 0.9973888361673892],
        a: [1.0, -1.9702186490445686, 0.9947776723347783],
      },
      (4000.0, 50.0) => NotchCoeffs {
        b: [0.9986927135483012, -1.99122815441855, 0.9986927135483012],
        a: [1.0, -1.99122815441855, 0.9973854270966025],
      },
      // 60Hz陷波
      (250.0, 60.0) => NotchCoeffs {
        b: [0.975478390750534, -0.12250158988968947, 0.975478390750534],
        a: [1.0, -0.12250158988968947, 0.950956781501068],
      },
      (500.0, 60.0) => NotchCoeffs {
        b: [0.9875889380903247, -1.4398427053125467, 0.9875889380903247],
        a: [1.0, -1.4398427053125467, 0.9751778761806493],
      },
      (1000.0, 60.0) => NotchCoeffs {
        b: [0.9937559649536571, -1.8479418578501994, 0.9937559649536571],
        a: [1.0, -1.8479418578501994, 0.9875119299073143],
      },
      (2000.0, 60.0) => NotchCoeffs {
        b: [0.9968682357708074, -1.9584219173081294, 0.9968682357708074],
        a: [1.0, -1.9584219173081294, 0.9937364715416148],
      },
      (4000.0, 60.0) => NotchCoeffs {
        b: [0.998431665916719, -1.9880011816839496, 0.998431665916719],
        a: [1.0, -1.9880011816839496, 0.9968633318334379],
      },
      _ => unreachable!(),
    }
  } else {
    let (b, a) = iirnotch(f0, q, fs);
    NotchCoeffs { b, a }
  }
}
