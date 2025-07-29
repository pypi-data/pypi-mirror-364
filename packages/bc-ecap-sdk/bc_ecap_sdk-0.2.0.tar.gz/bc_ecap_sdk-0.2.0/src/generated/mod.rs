#![allow(clippy::all)]

use cfg_if::cfg_if;

cfg_if! {
  if #[cfg(feature = "eeg-cap")] {
      pub mod eeg_cap_proto;
      pub mod eeg_cap_proto_serde;
      // cfg_if! {
      //     if #[cfg(not(target_family = "wasm"))] {
      //         pub mod filter_bindings;
      //     }
      // }
  }
}
