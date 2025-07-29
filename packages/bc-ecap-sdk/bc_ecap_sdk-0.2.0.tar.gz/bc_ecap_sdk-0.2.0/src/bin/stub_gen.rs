#[cfg(feature = "python")]
use bc_ecap_sdk::utils::logging::LogLevel;
#[cfg(feature = "python")]
use bc_ecap_sdk::utils::logging_desktop::initialize_logging;
bc_ecap_sdk::cfg_import_logging!();

// export PYO3_PYTHON=/opt/homebrew/Caskroom/miniconda/base/envs/py310/bin/python
// export DYLD_LIBRARY_PATH=/opt/homebrew/Caskroom/miniconda/base/envs/py310/lib:$DYLD_LIBRARY_PATH
// cargo run --bin stub_gen --features "python stub_gen"
#[cfg(feature = "python")]
fn main() -> pyo3_stub_gen::Result<()> {
  initialize_logging(LogLevel::Info);
  // `stub_info` is a function defined by `define_stub_info_gatherer!` macro.
  // let stub = crate::stub_info()?;
  let stub = bc_ecap_sdk::python::py_mod::stub_info()?;
  stub.generate()?;
  Ok(())
}

#[cfg(not(feature = "python"))]
fn main() {
  eprintln!("This binary requires the 'python' feature to be enabled.");
}

// `env -u CARGO PYO3_ENVIRONMENT_SIGNATURE="cpython-3.8-64bit"
// PYO3_PYTHON="/opt/homebrew/Caskroom/miniconda/base/envs/py38/bin/python"
// PYTHON_SYS_EXECUTABLE="/opt/homebrew/Caskroom/miniconda/base/envs/py38/bin/python"
// "cargo" "rustc" "--features" "pyo3/extension-module"
// "--message-format" "json-render-diagnostics"
// "--manifest-path" "/Volumes/Ss-990/projects/bc-stark-sdk/Cargo.toml"
// "--lib" "--crate-type" "cdylib"
// "--no-default-features" "--features" "python stark edu serial"
// "-C" "link-arg=-undefined"
// "-C" "link-arg=dynamic_lookup"
// "-C" "link-args=-Wl,-install_name,@rpath/crate.abi3.so"`
