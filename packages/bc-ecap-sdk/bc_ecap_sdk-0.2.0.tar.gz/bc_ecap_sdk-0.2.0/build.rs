extern crate bindgen;
extern crate cc;

use cfg_if::cfg_if;
use std::fs::{copy, OpenOptions};
use std::io::BufWriter;
use std::path::Path;
use std::{env, fs, io::Write};

fn main() {
  // if in Github Actions
  if env::var("GITHUB_ACTIONS").is_ok() {
    return;
  }

  if env::var("CENTOS").is_ok() {
    return;
  }

  #[cfg(feature = "stub_gen")]
  {
    println!("cargo:rustc-link-lib=python3.10");
    println!(
      "cargo:rustc-link-search=native=/opt/homebrew/Caskroom/miniconda/base/envs/py310/lib/"
    );
  }

  // 重新编译触发机制
  println!("cargo:rerun-if-changed=proto3/");
  cfg_if! {
    if #[cfg(feature = "eeg-cap")] {
      let proto_files = [
          "proto3/eeg-cap/app_ble/app_to_ble.proto",
          "proto3/eeg-cap/app_ble/ble_to_app.proto",
          "proto3/eeg-cap/app_main/app_to_main.proto",
          "proto3/eeg-cap/app_main/main_to_app.proto",
      ];
      let include_dirs = [
          "proto3/eeg-cap",
          "proto3/eeg-cap/app_ble",
          "proto3/eeg-cap/app_main",
      ];
      compile_and_copy_protos(&proto_files, &include_dirs, "eeg_cap");

    //   cfg_if! {
    //     if #[cfg(not(target_family = "wasm"))] {
    //       println!("cargo:rerun-if-changed=src/c/filter.h");
    //       println!("cargo:rerun-if-changed=src/c/filter.c");
    //       let lib_name = "filter";
    //       cc::Build::new()
    //           .file("src/c/filter.c")
    //           .compile(lib_name);

    //       let header_path = "src/c/filter.h";

    //       let bindings = bindgen::Builder::default()
    //           .header(header_path)
    //           .generate()
    //           .expect("Unable to generate bindings");
    //       let output_path = Path::new("src").join("generated/filter_bindings.rs");

    //       // 将生成的绑定写入文件
    //       bindings
    //           .write_to_file(&output_path)
    //           .expect("Couldn't write bindings!");
    //     }
    // }
    }
  }

  // 格式化生成的代码
  // let _ = Command::new("cargo")
  //   .arg("fmt")
  //   .spawn()
  //   .expect("Failed to format code")
  //   .wait();
}

#[allow(dead_code)]
fn generate_bindings(header_path: &str, lib_name: &str) {
  println!("cargo:rerun-if-changed={}", header_path);
  let bindings = bindgen::Builder::default()
    .header(header_path)
    .generate()
    .expect("Unable to generate bindings");
  let output_path = Path::new("src").join(format!("generated/{}_bindings.rs", lib_name));
  bindings
    .write_to_file(&output_path)
    .expect("Couldn't write bindings!");
}

#[allow(dead_code)]
fn compile_and_copy_protos(proto_files: &[&str], proto_include_dirs: &[&str], package_name: &str) {
  let out_dir = env::var("OUT_DIR").expect("OUT_DIR not set");
  println!("out_dir: {}", out_dir);

  let descriptor_path = Path::new(&out_dir).join("proto_descriptor.bin");
  let package = format!("tech.brainco.{}", package_name);

  prost_build::Config::new()
    .file_descriptor_set_path(&descriptor_path)
    .compile_well_known_types()
    .extern_path(".google.protobuf", "::pbjson_types")
    // .type_attribute(".", format!("#[prost(message, package = \"{}\")]", package))
    .compile_protos(proto_files, proto_include_dirs)
    .expect("Failed to compile protos");

  let output_name = format!("{}_proto", package_name);
  let descriptor_set = std::fs::read(descriptor_path).unwrap();
  let mut binding = pbjson_build::Builder::new();
  let builder = binding.register_descriptors(&descriptor_set).unwrap();
  // if cfg!(feature = "ignore-unknown-fields") {
  //     builder.ignore_unknown_fields();
  // }
  // if cfg!(feature = "btree") {
  //     builder.btree_map([".test"]);
  // }
  // if cfg!(feature = "emit-fields") {
  //     builder.emit_fields();
  // }
  // if cfg!(feature = "use-integers-for-enums") {
  //     builder.use_integers_for_enums();
  // }
  // if cfg!(feature = "preserve-proto-field-names") {
  //     builder.preserve_proto_field_names();
  // }

  builder.build(&[format!(".{}", package)]).unwrap();

  // 自动生成模块文件的路径
  let module_path = Path::new(&out_dir).join(format!("{}.rs", package));
  println!("module_path {:?}", module_path);
  // 检查生成的文件是否存在
  if !module_path.exists() {
    panic!("Generated file does not exist: {:?}", module_path);
  }
  // 将生成的模块文件复制到指定的输出文件
  let output_path = Path::new("src").join(format!("generated/{}.rs", output_name));
  copy(&module_path, &output_path).expect("Failed to copy generated proto file");

  let module_path = Path::new(&out_dir).join(format!("tech.brainco.{}.serde.rs", package_name));
  if !module_path.exists() {
    panic!("Generated serde file does not exist: {:?}", module_path);
  }
  let output_path = Path::new("src").join(format!("generated/{}_serde.rs", output_name));
  copy(&module_path, &output_path).expect("Failed to copy generated serde proto file");

  let mut file = OpenOptions::new()
    .write(true)
    .truncate(true)
    .create(true)
    .open(&output_path)
    .unwrap();
  let mut writer = BufWriter::new(&mut file);

  // Write use statements manually
  writeln!(writer, "use crate::generated::{}::*;", output_name).unwrap();
  // writeln!(writer, "use serde::{{Serialize, Deserialize}};")?;

  // Write the rest of the content of the generated file
  let generated_content = fs::read_to_string(module_path).unwrap();
  write!(writer, "{}", generated_content).unwrap();
}
