// 内部核心实现，禁止直接调用
#[macro_export]
macro_rules! __impl_enum_conversion_inner {
    ($module:expr, $repr:ty, $name:ident, $first_variant:ident = $first_value:expr, $($variant:ident = $value:expr),+ $(,)?) => {
        #[repr($repr)]
        #[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass_enum)]
        #[cfg_attr(feature = "python", pyo3::pyclass(module = "bc_ecap_sdk.main_mod.ecap", eq, eq_int))]
        // #[cfg_attr(feature = "python", pyo3::pyclass(module = $module, eq, eq_int))]
        #[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
        pub enum $name {
            $first_variant = $first_value,
            $($variant = $value),+
        }

        // Default 实现：默认值为第一个
        impl Default for $name {
            fn default() -> Self {
                Self::$first_variant
            }
        }

        // From<$repr>：不panic，非法值→默认值
        impl From<$repr> for $name {
            fn from(value: $repr) -> Self {
                match value {
                    $first_value => Self::$first_variant,
                    $($value => Self::$variant,)+
                    _ => Self::default(),
                }
            }
        }

        // From<$name> → $repr
        impl From<$name> for $repr {
            fn from(value: $name) -> Self {
                value as $repr
            }
        }

        // Python 绑定
        #[cfg(feature = "python")]
        #[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pymethods)]
        #[cfg_attr(feature = "python", pyo3::pymethods)]
        impl $name {
            #[allow(dead_code)]
            #[new]
            fn py_new(value: i64) -> Self {
                (value as $repr).into()
            }

            #[getter]
            pub fn int_value(&self) -> $repr {
                *self as $repr
            }
        }
    };
}

// === 外部宏1：默认ecap、u8 ===
#[macro_export]
macro_rules! impl_enum_conversion {
  ($name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
    $crate::__impl_enum_conversion_inner!("bc_ecap_sdk.main_mod.ecap", u8, $name, $($variant = $value),+);
  };
}

// === 外部宏2：默认ecap、u16 ===
#[macro_export]
macro_rules! impl_enum_u16_conversion {
  ($name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
    $crate::__impl_enum_conversion_inner!("bc_ecap_sdk.main_mod.ecap", u16, $name, $($variant = $value),+);
  };
}

// === 外部宏3：默认ecap、u32 ===
#[macro_export]
macro_rules! impl_enum_u32_conversion {
  ($name:ident, $($variant:ident = $value:expr),+ $(,)?) => {
    $crate::__impl_enum_conversion_inner!("bc_ecap_sdk.main_mod.ecap", u32, $name, $($variant = $value),+);
  };
}

// === 日志宏：根据特性导入不同的日志库 ===
// 该宏会根据编译时的特性配置，导入不同的日志库（tracing 或 log）
// 注意：在使用该宏之前，请确保已启用
#[macro_export]
macro_rules! cfg_import_logging {
  () => {
    cfg_if::cfg_if! {
      if #[cfg(all(feature = "tracing-log", not(target_os = "android"), not(target_family = "wasm"), not(feature = "python")))] {
        #[allow(unused_imports)]
        use tracing::*;
      } else {
        #[allow(unused_imports)]
        use log::*;
      }
    }
  };
}

// cfg_import_logging!();
