use std::{
  f64::consts::PI,
  sync::{Arc},
};
use parking_lot::Mutex;

use crate::generated::filter_bindings::*;
crate::cfg_import_logging!();

// #[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
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
  pub filter: Arc<Mutex<*mut BWBandPass>>,
}

impl BandPassFilter {
  pub fn new(_order: usize, s: f64, fl: f64, fu: f64) -> Self {
    if fu <= fl {
      panic!("ERROR: Lower half-power frequency is smaller than higher half-power frequency");
    }

    let mut filter = BandPassFilter {
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
      filter: Arc::new(Mutex::new(unsafe {
        create_bw_band_pass_filter(4, s, fl, fu)
      })),
    };

    let a = (f64::cos(PI * (fu + fl) / s)) / f64::cos(PI * (fu - fl) / s);
    let a2 = a * a;
    let b = f64::tan(PI * (fu - fl) / s);
    let b2 = b * b;

    let r = f64::sin(PI * 0.25);
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

  pub fn process(&mut self, x: f64) -> f64 {
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

  pub fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    self.process_iter_c(iter)
    // iter.into_iter().map(move |x| self.process(x)).collect()
  }

  pub fn process_iter_c<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    unsafe {
      let bp_filter = self.filter.lock();
      let bp_filter = *bp_filter;
      iter
        .into_iter()
        .map(move |x| band_pass(bp_filter, x))
        .collect()
    }
  }
}

// #[cfg_attr(target_family = "wasm", wasm_bindgen::prelude::wasm_bindgen)]
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
  pub filter: Arc<Mutex<*mut BWBandStop>>,
}

impl BandStopFilter {
  pub fn new(_order: usize, s: f64, fl: f64, fu: f64) -> Self {
    if fu <= fl {
      panic!("ERROR: Lower half-power frequency is smaller than higher half-power frequency");
    }

    let mut filter = BandStopFilter {
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
      filter: Arc::new(Mutex::new(unsafe {
        create_bw_band_stop_filter(4, s, fl, fu)
      })),
    };

    let a = (f64::cos(PI * (fu + fl) / s)) / f64::cos(PI * (fu - fl) / s);
    let a2 = a * a;
    let b = f64::tan(PI * (fu - fl) / s);
    let b2 = b * b;
    filter.r = 4.0 * a;
    filter.s = 4.0 * a2 + 2.0;

    let r = f64::sin(PI * 0.25);
    let s = b2 + 2.0 * b * r + 1.0;
    filter.a = 1.0 / s;
    filter.d1 = 4.0 * a * (1.0 + b * r) / s;
    filter.d2 = 2.0 * (b2 - 2.0 * a2 - 1.0) / s;
    filter.d3 = 4.0 * a * (1.0 - b * r) / s;
    filter.d4 = -(b2 - 2.0 * b * r + 1.0) / s;

    filter
  }

  pub fn process(&mut self, x: f64) -> f64 {
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

  pub fn process_iter<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    self.process_iter_c(iter)
    // iter.into_iter().map(move |x| self.process(x)).collect()
  }

  pub fn process_iter_c<I>(&mut self, iter: I) -> Vec<f64>
  where
    I: IntoIterator<Item = f64>,
  {
    unsafe {
      let bs_filter = self.filter.lock();
      let bs_filter = *bs_filter;
      iter
        .into_iter()
        .map(move |x| band_stop(bs_filter, x))
        .collect()
    }
  }
}

unsafe impl Send for BandPassFilter {}
unsafe impl Sync for BandPassFilter {}
unsafe impl Send for BandStopFilter {}
unsafe impl Sync for BandStopFilter {}

impl Drop for BandPassFilter {
  fn drop(&mut self) {
    info!("Drop BandPassFilter");
    let filter = self.filter.lock();
    unsafe {
      free_bw_band_pass(*filter);
    }
  }
}

impl Drop for BandStopFilter {
  fn drop(&mut self) {
    // info!("Drop BandStopFilter");
    let filter = self.filter.lock();
    unsafe {
      free_bw_band_stop(*filter);
    }
  }
}
