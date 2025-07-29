use lazy_static::lazy_static;
use mdns_sd::{ServiceDaemon, ServiceEvent};
use parking_lot::Mutex;
use std::net::IpAddr;
use std::sync::Arc;
use std::time::Instant;

use crate::utils::runtime::get_runtime;

crate::cfg_import_logging!();

const SERVICE_NAME: &str = "_brainco-eeg._tcp.local.";

#[cfg_attr(feature = "python", pyo3_stub_gen::derive::gen_stub_pyclass)]
#[cfg_attr(feature = "python", pyo3::pyclass(get_all))]
#[derive(Debug, Clone, Default)]
pub struct MdnsScanResult {
  pub fullname: String,
  pub hostname: String,
  pub addr: String,
  pub port: u16,
  pub sn: String,
  pub model: String,
}

pub type MdnsScanResultCallback = Box<dyn Fn(MdnsScanResult) + Send + Sync>;

lazy_static! {
  static ref MDNS: Arc<Mutex<ServiceDaemon>> = Arc::new(Mutex::new(ServiceDaemon::new().unwrap()));
  static ref MDNS_SCAN_RESULT_CALLBACK: Arc<Mutex<Option<MdnsScanResultCallback>>> =
    Arc::new(Mutex::new(None));
}

pub fn mdns_start_scan_sync() -> Result<(), anyhow::Error> {
  info!("Starting mdns scan");
  let rt = get_runtime();
  rt.spawn(async {
    let _ = mdns_start_scan_with_cb();
  });
  Ok(())
}

fn mdns_start_scan_with_cb() {
  debug!("Starting mdns scan with callback");
  let now = Instant::now();

  let mdns = MDNS.lock();
  let receiver = mdns.browse(SERVICE_NAME).unwrap();
  drop(mdns);
  loop {
    if receiver.is_disconnected() {
      info!("Receiver disconnected");
      break;
    }
    match receiver.recv() {
      Ok(event) => match event {
        ServiceEvent::ServiceResolved(service_info) => {
          let fullname = service_info.get_fullname();
          let hostname = service_info.get_hostname();
          let port = service_info.get_port();
          debug!(
            "At {:?}: Resolved a new service: \n{}\n host: {}\n port: {}",
            now.elapsed(),
            fullname,
            hostname,
            port,
          );
          if service_info.get_addresses().is_empty() {
            warn!(
              "No address found for service: {}",
              service_info.get_fullname()
            );
            continue;
          }
          for addr in service_info.get_addresses().iter() {
            info!("Resolved Address: {}", addr);
          }

          let mut sn: &str = "";
          let mut model: &str = "";
          if let Some(prop) = service_info.get_properties().get("model") {
            model = prop.val_str();
            info!("Model: {}", model);
          }
          if let Some(sn_prop) = service_info.get_properties().get("sn") {
            sn = sn_prop.val_str();
            info!("SN: {}", sn);
          }
          if let Some(addr) = service_info.get_addresses().iter().next() {
            if let Some(ref cb) = *MDNS_SCAN_RESULT_CALLBACK.lock() {
              let result = MdnsScanResult {
                fullname: fullname.to_string(),
                hostname: hostname.to_string(),
                addr: addr.to_string(),
                port,
                sn: sn.to_string(),
                model: model.to_string(),
              };
              cb(result);
            }
          }
        }
        ServiceEvent::SearchStopped(_service) => {
          info!("SearchStopped");
        }
        other_event => {
          debug!("At {:?}: {:?}", now.elapsed(), &other_event);
        }
      },
      Err(err) => {
        warn!("Error receiving event: {:?}", err);
        break;
      }
    }
  }
  info!("mdns scan stopped");
}

pub fn set_mdns_scan_result_callback(callback: MdnsScanResultCallback) {
  let mut cb = MDNS_SCAN_RESULT_CALLBACK.lock();
  *cb = Some(callback);
}

pub fn clear_mdns_scan_result_callback() {
  debug!("Clearing mdns scan result callback");
  let mut cb = MDNS_SCAN_RESULT_CALLBACK.lock();
  *cb = None;
}

// pub fn async mdns_start_scan_async(
//   with_sn: Option<String>,
// ) -> Result<(IpAddr, u16), Box<dyn std::error::Error>> {
//   info!("Starting mdns scan");
//   let rt = get_runtime();
//   rt.block_on(async {
//     mdns_start_scan(with_sn).await
//   })
// }

pub fn mdns_start_scan(
  with_sn: Option<String>,
) -> Result<(IpAddr, u16), Box<dyn std::error::Error>> {
  info!("Starting mdns scan");
  let now = Instant::now();
  let mdns = MDNS.lock();
  let receiver = mdns.browse(SERVICE_NAME)?;
  loop {
    if receiver.is_disconnected() {
      info!("Receiver disconnected");
      break;
    }
    match receiver.recv() {
      Ok(event) => match event {
        ServiceEvent::ServiceResolved(service_info) => {
          debug!(
            "At {:?}: Resolved a new service: \n{}\n host: {}\n port: {}",
            now.elapsed(),
            service_info.get_fullname(),
            service_info.get_hostname(),
            service_info.get_port(),
          );
          if service_info.get_addresses().is_empty() {
            warn!(
              "No address found for service: {}",
              service_info.get_fullname()
            );
            continue;
          }
          for addr in service_info.get_addresses().iter() {
            info!("Resolved Address: {}", addr);
          }
          if let Some(ref sn) = with_sn {
            if let Some(prop) = service_info.get_properties().get("model") {
              info!("Model: {}", prop.val_str());
            }
            if let Some(sn_prop) = service_info.get_properties().get("sn") {
              let device_sn = sn_prop.val_str();
              info!("SN: {}", device_sn);
              if device_sn != sn {
                continue;
              }
            }
          }
          if let Some(addr) = service_info.get_addresses().iter().next() {
            let port = service_info.get_port();
            return Ok((*addr, port));
          } else {
            return Err("No address found".into());
          }
        }
        ServiceEvent::SearchStopped(_service) => {
          info!("SearchStopped");
        }
        other_event => {
          debug!("At {:?}: {:?}", now.elapsed(), &other_event);
        }
      },
      Err(err) => {
        warn!("Error receiving event: {:?}", err);
        break;
      }
    }
  }

  Err("No service found".into())
}

pub fn mdns_stop_scan() -> Result<(), anyhow::Error> {
  info!("Stopping mdns scan");
  clear_mdns_scan_result_callback();
  // info!("Stopping mdns scan 0 ");
  let mdns = MDNS.lock();
  // info!("Stopping mdns scan 1 ");
  if let Err(e) = mdns.stop_browse(SERVICE_NAME) {
    warn!("Failed to stop browsing: {}", e);
  }
  // if let Err(e) = mdns.shutdown() {
  //   warn!("Failed to shutdown mdns: {}", e);
  // }
  Ok(())
}
