use std::sync::Once;

#[allow(unused_imports)]
use super::logging::LogLevel;
#[allow(unused_imports)]
use fern::colors::{Color, ColoredLevelConfig};
use tracing_subscriber::{filter::LevelFilter, layer::SubscriberExt, *};

crate::cfg_import_logging!();

pub fn initialize_logging(level: LogLevel) {
  let level: log::Level = level.into();
  init_logging(level);
  info!(
    "{} version: {}",
    env!("CARGO_PKG_NAME"),
    env!("CARGO_PKG_VERSION")
  );
}

pub fn init_logging(level: log::Level) {
  static INIT: Once = Once::new();
  INIT.call_once(|| {
    // 配置颜色
    #[cfg(feature = "examples")]
    let colors = ColoredLevelConfig::new()
      .error(Color::Red)
      .warn(Color::Yellow)
      .info(Color::Green)
      .debug(Color::Blue)
      .trace(Color::White);

    // log::set_max_level(log::LevelFilter::Debug);
    // log::set_max_level(to_log_filter(level));

    // 配置 fern
    #[cfg(feature = "examples")]
    fern::Dispatch::new()
      .format(move |out, message, record| {
        out.finish(format_args!(
          "{}[{}][{}:{}] {}",
          // chrono::Local::now().format("[%Y-%m-%d %H:%M:%S]"),
          humantime::format_rfc3339_micros(std::time::SystemTime::now()),
          colors.color(record.level()),
          record.file().unwrap_or("unknown"),
          record.line().unwrap_or(0),
          message
        ))
      })
      .level(level.to_level_filter())
      .chain(std::io::stdout())
      // .chain(fern::log_file("output.log")?)
      // .chain(fern::log_file("output.log")
      //   .unwrap_or_else(|_| fern::log_file("output.log").expect("Failed to create log file")))
      .apply()
      .expect("Failed to initialize logging");

    let console_layer = fmt::Layer::new()
      .with_file(true)
      .with_line_number(true)
      .with_filter(to_log_level_filter(level));

    let subscriber: layer::Layered<
      filter::Filtered<fmt::Layer<Registry>, LevelFilter, Registry>,
      Registry,
    > = Registry::default().with(console_layer);

    tracing::subscriber::set_global_default(subscriber).expect("Failed to set subscriber");
  });
}

fn to_log_level_filter(level: log::Level) -> LevelFilter {
  match level {
    log::Level::Error => LevelFilter::ERROR,
    log::Level::Warn => LevelFilter::WARN,
    log::Level::Info => LevelFilter::INFO,
    log::Level::Debug => LevelFilter::DEBUG,
    log::Level::Trace => LevelFilter::TRACE,
  }
}

#[allow(dead_code)]
fn to_log_filter(level: log::Level) -> log::LevelFilter {
  match level {
    log::Level::Error => log::LevelFilter::Error,
    log::Level::Warn => log::LevelFilter::Warn,
    log::Level::Info => log::LevelFilter::Info,
    log::Level::Debug => log::LevelFilter::Debug,
    log::Level::Trace => log::LevelFilter::Trace,
  }
}
