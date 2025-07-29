use bc_ecap_sdk::{
  data_handler::afe_handler::parse_32ch_eeg_data,
  proto::{
    eeg_cap::msg_builder::*,
    enums::{MsgType, ParsedMessage},
    msg_parser::Parser,
  },
  utils::logging_desktop::init_logging,
};
use futures::StreamExt;
use tracing::*;

// cargo run --no-default-features --example ecap-imp-offline --features="eeg-cap, examples"
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
  msg_decode_test().await;
  Ok(())
}

async fn msg_decode_test() {
  init_logging(log::Level::Debug);

  let mut parser = Parser::new("test-device".into(), MsgType::EEGCap);
  let mut stream = parser.message_stream();

  debug!("mock receive_data");
  parser.receive_data(&[
    66, 82, 78, 67, 2, 11, 121, 0, 0, 2, 0, 8, 1, 26, 117, 18, 115, 10, 113, 8, 213, 8, 18, 108,
    192, 0, 0, 17, 177, 229, 17, 176, 135, 17, 181, 47, 17, 189, 18, 17, 191, 248, 17, 184, 115,
    17, 192, 86, 17, 194, 105, 192, 0, 0, 219, 237, 13, 221, 144, 42, 15, 77, 164, 13, 9, 104, 219,
    221, 63, 217, 90, 108, 13, 27, 136, 13, 90, 223, 192, 0, 0, 13, 0, 65, 12, 234, 68, 17, 188,
    254, 13, 219, 151, 12, 221, 3, 13, 18, 253, 16, 175, 80, 13, 14, 152, 192, 0, 0, 13, 28, 40,
    13, 2, 123, 13, 28, 153, 13, 3, 246, 13, 40, 144, 12, 245, 37, 17, 191, 50, 17, 196, 51, 151,
    63,
  ]);
  parser.receive_data(&[
    66, 82, 78, 67, 2, 11, 121, 0, 0, 2, 0, 8, 1, 26, 117, 18, 115, 10, 113, 8, 214, 8, 18, 108,
    192, 0, 0, 17, 171, 152, 17, 170, 61, 17, 174, 231, 17, 182, 195, 17, 185, 173, 17, 178, 41,
    17, 186, 8, 17, 188, 33, 192, 0, 0, 219, 243, 101, 221, 150, 129, 15, 77, 190, 13, 6, 210, 219,
    227, 131, 217, 96, 162, 13, 19, 229, 13, 90, 185, 192, 0, 0, 12, 255, 201, 12, 228, 181, 17,
    182, 186, 13, 218, 119, 12, 219, 216, 13, 18, 5, 16, 174, 225, 13, 13, 50, 192, 0, 0, 13, 27,
    229, 12, 251, 200, 13, 20, 219, 12, 251, 65, 13, 40, 130, 12, 242, 249, 17, 184, 212, 17, 189,
    214, 174, 78,
  ]);

  let mut gain = 6;
  let mut eeg_buffer: Vec<Vec<f64>> = vec![];

  // 处理流中的消息
  tokio::spawn(async move {
    debug!("Starting read");
    while let Some(result) = stream.next().await {
      match result {
        Ok((device_id, message)) => {
          trace!(
            "Received message, device_id: {:?}, message: {:?}",
            device_id,
            message
          );
          match message {
            ParsedMessage::EEGCap(EEGCapMessage::Mcu2App(ref mcu_msg)) => {
              if let Some(eeg) = &mcu_msg.eeg {
                if let Some(eeg_cfg) = &eeg.config {
                  gain = eeg_cfg.gain;
                  warn!("gain: {:?}", gain);
                }
                if let Some(eeg_data) = &eeg.data {
                  trace!("eeg data: {:?}", eeg_data);
                  if let Some(sample_1) = &eeg_data.sample_1 {
                    // debug!("Sample 1 data : {:?} {}", &sample_1.data, sample_1.data.len());
                    let buffer = parse_32ch_eeg_data(&sample_1.data, gain);
                    if buffer.is_empty() {
                      error!("Invalid eeg data");
                    } else {
                      debug!("Buffer, len={} {:?}", buffer.len(), buffer);
                      eeg_buffer.push(buffer);
                    }
                  }
                }
              }
            }
            #[allow(unreachable_patterns)]
            _ => {}
          }
        }
        Err(e) => {
          error!("Error receiving message: {:?}", e);
        }
      }
    }
    debug!("Finished read");
  });

  debug!("Finished test");
  // wait for stream to finish
  tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
}
