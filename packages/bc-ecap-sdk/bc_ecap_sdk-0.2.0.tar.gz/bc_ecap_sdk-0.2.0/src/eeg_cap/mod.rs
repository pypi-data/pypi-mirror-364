pub mod data;

#[cfg(not(target_family = "wasm"))]
pub mod callback;
