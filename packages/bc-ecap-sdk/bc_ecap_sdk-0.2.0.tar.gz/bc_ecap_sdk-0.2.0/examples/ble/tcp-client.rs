//! Run with:
//!
//!     cargo run --no-default-features --features "examples, tcp" --example tcp-client
//!

// use std::sync::Arc;
use tokio::io::{self, AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
// use tokio::sync::Mutex;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() -> io::Result<()> {
  // 设置初始重连间隔
  let mut interval = Duration::from_secs(2);

  loop {
    // 尝试连接服务器
    match TcpStream::connect("127.0.0.1:8080").await {
      Ok(mut stream) => {
        println!("Connected to server!");

        // 重置重连间隔
        interval = Duration::from_secs(2);

        let message = b"Hello, server!";
        if let Err(e) = stream.write_all(message).await {
          eprintln!("Failed to send message: {:?}", e);
        }
        println!("Sent: {:?}", message);

        // 持续接收服务器的响应
        let mut buf = vec![0; 4096];
        let mut string = String::new();
        let mut previous_value: Option<i32> = None;

        loop {
          match stream.read(&mut buf).await {
            Ok(0) => {
              println!("Connection closed by server");
              break;
            }
            Ok(n) => {
              let received_str = std::str::from_utf8(&buf[0..n]).unwrap();
              string.push_str(received_str);

              // 处理接收到的数字，以\n结束，剩下的保留到下一次接收
              while let Some(pos) = string.find('\n') {
                let line = string[..pos].trim().to_string();
                string = string[pos + 1..].to_string();

                if let Ok(current_value) = line.parse::<i32>() {
                  if let Some(prev) = previous_value {
                    if current_value != prev + 1 {
                      eprintln!(
                        "Non-incremental value detected: previous = {}, current = {}",
                        prev, current_value
                      );
                      panic!("Non-incremental value detected");
                    } else {
                      println!("current_value: {:?}", current_value);
                    }
                  }
                  previous_value = Some(current_value);
                } else {
                  println!("Failed to parse value: {:?}", line);
                }
              }
            }
            Err(e) => {
              eprintln!("Failed to read from server: {:?}", e);
              break;
            }
          }
        }
      }
      Err(e) => {
        eprintln!("Failed to connect: {:?}", e);
      }
    }

    // 如果连接失败或中断，等待一段时间后重试
    println!("Retrying in {:?}...", interval);
    sleep(interval).await;

    // 增加重连间隔，避免频繁尝试
    interval = std::cmp::min(interval * 2, Duration::from_secs(60));
  }
  // Ok(())
}
