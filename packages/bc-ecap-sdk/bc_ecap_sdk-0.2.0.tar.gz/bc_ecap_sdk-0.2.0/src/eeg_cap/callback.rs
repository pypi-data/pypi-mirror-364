use parking_lot::Mutex;

use crate::proto::eeg_cap::enums::*;

use super::data::save_lead_off_cfg;

type LeadOffCheckCallback = Box<dyn Fn(LeadOffChip, LeadOffFreq, LeadOffCurrent) + Send + Sync>;

lazy_static::lazy_static! {
  static ref SET_LEADOFF_CFG: Mutex<Option<LeadOffCheckCallback>> = Mutex::new(None); // check next leadoff chip
}

pub fn start_leadoff_check(loop_check: bool, freq: LeadOffFreq, current: LeadOffCurrent) {
  save_lead_off_cfg(loop_check, freq, current);
  run_next_leadoff_chek(LeadOffChip::Chip1, freq, current);
}

pub fn set_next_leadoff_cb(callback: LeadOffCheckCallback) {
  let mut cb = SET_LEADOFF_CFG.lock();
  *cb = Some(callback);
}

pub fn run_next_leadoff_chek(chip: LeadOffChip, freq: LeadOffFreq, current: LeadOffCurrent) {
  let cb = SET_LEADOFF_CFG.lock();
  if let Some(ref callback) = *cb {
    callback(chip, freq, current);
  }
}
