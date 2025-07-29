// #![allow(unused_variables)]

use std::f64::consts::PI;

crate::cfg_import_logging!();

pub trait BrainCoFilter {
  fn process(&mut self, x: f64) -> f64;
  fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>;
}

#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone, PartialEq)]
pub struct BandPassFilter {
  pub a: f64,
  pub d1: f64,
  pub d2: f64,
  pub d3: f64,
  pub d4: f64,
  pub w0: f64,
  pub w1: f64,
  pub w2: f64,
  pub w3: f64,
  pub w4: f64,
  // pub filter: Arc<Mutex<*mut BWBandPass>>,
}

impl BandPassFilter {
  pub fn new(_order: usize, s: f64, fl: f64, fu: f64) -> Self {
    if fu <= fl {
      panic!("ERROR: Lower half-power frequency is smaller than higher half-power frequency");
    }

    let mut filter = Self {
      a: 0.0,
      d1: 0.0,
      d2: 0.0,
      d3: 0.0,
      d4: 0.0,
      w0: 0.0,
      w1: 0.0,
      w2: 0.0,
      w3: 0.0,
      w4: 0.0,
      // filter: Arc::new(Mutex::new(unsafe {
      //   create_bw_band_pass_filter(4, s, fl, fu)
      // })),
    };

    let a = (PI * (fu + fl) / s).cos() / (PI * (fu - fl) / s).cos();
    let a2 = a * a;
    let b = (PI * (fu - fl) / s).tan();
    let b2 = b * b;

    let r = (PI * 0.25).sin();
    let s = b2 + 2.0 * b * r + 1.0;
    filter.a = b2 / s;
    filter.d1 = 4.0 * a * (1.0 + b * r) / s;
    filter.d2 = 2.0 * (b2 - 2.0 * a2 - 1.0) / s;
    filter.d3 = 4.0 * a * (1.0 - b * r) / s;
    filter.d4 = -(b2 - 2.0 * b * r + 1.0) / s;
    // info!(
    //   "a: {}, d1: {}, d2: {}, d3: {}, d4: {}, fu: {}, fl: {}, s: {}",
    //   filter.a, filter.d1, filter.d2, filter.d3, filter.d4, fu, fl, s
    // );

    filter
  }
}

impl BrainCoFilter for BandPassFilter {
  fn process(&mut self, x: f64) -> f64 {
    // info!(
    //   "x: {}, w0: {}, w1: {}, w2: {}, w3: {}, w4: {}, a: {}, d1: {}, d2: {}, d3: {}, d4: {}",
    //   x, self.w0, self.w1, self.w2, self.w3, self.w4, self.a, self.d1, self.d2, self.d3, self.d4
    // );
    self.w0 = self.d1 * self.w1 + self.d2 * self.w2 + self.d3 * self.w3 + self.d4 * self.w4 + x;
    let x = self.a * (self.w0 - 2.0 * self.w2 + self.w4);
    // info!("x: {}, w0: {}", x, self.w0);
    self.w4 = self.w3;
    self.w3 = self.w2;
    self.w2 = self.w1;
    self.w1 = self.w0;
    // info!(
    //   "w1: {}, w2: {}, w3: {}, w4: {}",
    //   self.w1, self.w2, self.w3, self.w4
    // );
    x
  }

  fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    // self.process_iter_c(iter)
    iter.into_iter().map(move |x| self.process(x)).collect()
  }
}

#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone, PartialEq)]
pub struct BandStopFilter {
  pub a: f64,
  pub d1: f64,
  pub d2: f64,
  pub d3: f64,
  pub d4: f64,
  pub w0: f64,
  pub w1: f64,
  pub w2: f64,
  pub w3: f64,
  pub w4: f64,
  pub r: f64,
  pub s: f64,
  // pub filter: Arc<Mutex<*mut BWBandStop>>,
}

impl BandStopFilter {
  pub fn new(_order: usize, s: f64, fl: f64, fu: f64) -> Self {
    if fu <= fl {
      panic!("ERROR: Lower half-power frequency is smaller than higher half-power frequency");
    }

    let mut filter = Self {
      a: 0.0,
      d1: 0.0,
      d2: 0.0,
      d3: 0.0,
      d4: 0.0,
      w0: 0.0,
      w1: 0.0,
      w2: 0.0,
      w3: 0.0,
      w4: 0.0,
      r: 0.0,
      s: 0.0,
      // filter: Arc::new(Mutex::new(unsafe {
      //   create_bw_band_stop_filter(4, s, fl, fu)
      // })),
    };

    let a = (PI * (fu + fl) / s).cos() / (PI * (fu - fl) / s).cos();
    let a2 = a * a;
    let b = (PI * (fu - fl) / s).tan();
    let b2 = b * b;
    filter.r = 4.0 * a;
    filter.s = 4.0 * a2 + 2.0;

    let r = (PI * 0.25).sin();
    let s = b2 + 2.0 * b * r + 1.0;
    filter.a = 1.0 / s;
    filter.d1 = 4.0 * a * (1.0 + b * r) / s;
    filter.d2 = 2.0 * (b2 - 2.0 * a2 - 1.0) / s;
    filter.d3 = 4.0 * a * (1.0 - b * r) / s;
    filter.d4 = -(b2 - 2.0 * b * r + 1.0) / s;

    filter
  }
}

impl BrainCoFilter for BandStopFilter {
  fn process(&mut self, x: f64) -> f64 {
    self.w0 = self.d1 * self.w1 + self.d2 * self.w2 + self.d3 * self.w3 + self.d4 * self.w4 + x;
    // info!(
    //   "x: {:.2}, w0: {:.2}, w1: {:.2}, w2: {:.2}, w3: {:.2}, w4: {:.2}, a: {:.2}, d1: {:.2}, d2: {:.2}, d3: {:.2}, d4: {:.2}",
    //   x, self.w0, self.w1, self.w2, self.w3, self.w4, self.a, self.d1, self.d2, self.d3, self.d4
    // );
    // if self.w0.abs() > 50000.0 {
    //   panic!("ERROR: BandStopFilter output is too large");
    // } else {
    //   // info!("w0: {:.2}", self.w0);
    // }
    let result =
      self.a * (self.w0 - self.r * self.w1 + self.s * self.w2 - self.r * self.w3 + self.w4);
    self.w4 = self.w3;
    self.w3 = self.w2;
    self.w2 = self.w1;
    // if result.abs() > 5000.0 {
    //   info!(
    //       "result: {:.2}, x: {:.2}, w0: {:.2}, w1: {:.2}, w2: {:.2}, w3: {:.2}, w4: {:.2}, a: {:.2}, d1: {:.2}, d2: {:.2}, d3: {:.2}, d4: {:.2}",
    //       result, x, self.w0, self.w1, self.w2, self.w3, self.w4, self.a, self.d1, self.d2, self.d3, self.d4
    //   );
    //   panic!("ERROR: BandStopFilter output is too large");
    // }
    self.w1 = self.w0;

    result
  }

  fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }
}

#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone, PartialEq)]
pub struct LowPassFilter {
  a: f64,
  d1: f64,
  d2: f64,
  w0: f64,
  w1: f64,
  w2: f64,
}

impl LowPassFilter {
  pub fn new(_order: usize, s: f64, f: f64) -> Self {
    let a = (PI * f / s).tan();
    let a2 = a * a;
    let r = (PI * 0.25).sin();
    let s = a2 + 2.0 * a * r + 1.0;

    Self {
      a: a2 / s,
      d1: 2.0 * (1.0 - a2) / s,
      d2: -(a2 - 2.0 * a * r + 1.0) / s,
      w0: 0.0,
      w1: 0.0,
      w2: 0.0,
    }
  }
}

impl BrainCoFilter for LowPassFilter {
  fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }

  fn process(&mut self, x: f64) -> f64 {
    self.w0 = self.d1 * self.w1 + self.d2 * self.w2 + x;
    let result = self.a * (self.w0 + 2.0 * self.w1 + self.w2);
    self.w2 = self.w1;
    self.w1 = self.w0;
    result
  }
}

#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone, PartialEq)]
pub struct HighPassFilter {
  a: f64,
  d1: f64,
  d2: f64,
  w0: f64,
  w1: f64,
  w2: f64,
}

impl HighPassFilter {
  pub fn new(_order: usize, s: f64, f: f64) -> Self {
    let a = (PI * f / s).tan();
    let a2 = a * a;
    let r = (PI * 0.25).sin();
    let s = a2 + 2.0 * a * r + 1.0;

    Self {
      a: 1.0 / s,
      d1: 2.0 * (1.0 - a2) / s,
      d2: -(a2 - 2.0 * a * r + 1.0) / s,
      w0: 0.0,
      w1: 0.0,
      w2: 0.0,
    }
  }
}

impl BrainCoFilter for HighPassFilter {
  fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    iter.into_iter().map(move |x| self.process(x)).collect()
  }

  fn process(&mut self, x: f64) -> f64 {
    self.w0 = self.d1 * self.w1 + self.d2 * self.w2 + x;
    let result = self.a * (self.w0 - 2.0 * self.w1 + self.w2);
    self.w2 = self.w1;
    self.w1 = self.w0;
    result
  }
}

cfg_if::cfg_if! {
  if #[cfg(feature = "node_addons")] {
    use neon::types::Finalize;
    impl Finalize for LowPassFilter {}
    impl Finalize for HighPassFilter {}
    impl Finalize for BandPassFilter {}
    impl Finalize for BandStopFilter {}
  }
}
