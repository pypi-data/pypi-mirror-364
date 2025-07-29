use std::sync::Arc;

use tokio::runtime::Runtime;

lazy_static::lazy_static! {
  pub(crate) static ref GLOBAL_RUNTIME: Arc<Runtime> = Arc::new(Runtime::new().unwrap());
}

pub(crate) fn get_runtime() -> Arc<Runtime> {
  GLOBAL_RUNTIME.clone()
}
