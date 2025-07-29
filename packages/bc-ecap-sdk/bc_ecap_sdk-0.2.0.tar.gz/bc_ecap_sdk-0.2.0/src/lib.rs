#[rustfmt::skip]
pub mod generated;
pub mod callback;
pub mod data_handler;
pub mod eeg_cap;
pub mod proto;
pub mod utils;

#[cfg(feature = "ble")]
pub mod ble;

#[cfg(feature = "node_addons")]
pub mod neon;

#[cfg(feature = "python")]
pub mod python;

#[cfg(target_family = "wasm")]
pub mod wasm;
