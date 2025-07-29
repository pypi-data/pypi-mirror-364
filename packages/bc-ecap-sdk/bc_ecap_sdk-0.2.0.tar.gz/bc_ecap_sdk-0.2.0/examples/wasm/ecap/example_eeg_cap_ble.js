const { MsgType } = require("../pkg/bc_ecap_sdk");
const lib = require("./ecap_node.js");

const ecap_service_uuid = "4de5a20c-0001-ae0b-bf63-0242ac130002";

let scanResultMap = new Map();

async function main() {
  init_callbacks();

  try {
    console.log("Initializing BLE adapter...");
    let log_level = 3; // 0: error, 1: warn, 2: info, 3: debug, 4: trace
    await lib.init_logging(log_level);
    await lib.init_ble_adapter();
    console.log("BLE adapter initialized.");

    console.log("Starting BLE scan...");
    await lib.start_ble_scan([ecap_service_uuid]);
    console.log("BLE scan started.");
  } catch (err) {
    console.error("Failed to initialize BLE adapter:", err);
  }
}

main();

function init_callbacks() {
  lib.set_adapter_state_callback((state) => {
    // BLE适配器状态变化时会回调
    console.log("Adapter state changed:", state);
  });

  lib.set_device_discovered_callback(async (result) => {
    if (lib.is_ble_scanning() === false) {
      // console.log("BLE scan is not running.");
      return;
    }
    // 扫描到设备时会回调
    console.log("Discovery result:", result);
    scanResultMap.set(result.deviceId, result);

    if (result.name === "Zephyr [EEG-E5FF3]") {
      console.warn("Found device:", result.name);
      console.log("Stopping BLE scan...");
      await lib.stop_ble_scan();
      console.log("BLE scan stopped.");
      console.log("Connecting to device...");
      await lib.connect_ble_device(result.deviceId);
      console.log("Connected to device.");
    }
  });

  lib.set_connect_state_callback(async (obj) => {
    // 连接状态变化时会回调
    console.log("Connect state changed:", obj);
    // { deviceId, state }
    // state:
    // ConnectionState,
    // Connecting = 0,
    // Connected = 1,
    // Disconnecting = 2,
    // Disconnected = 3

    if (obj.state === 1) {
      // Connected

      let deviceId = obj.deviceId;
      lib.init_ble_parser(deviceId, MsgType.EEGCap);

      // await lib.set_ble_device_info(deviceId, {
      //   model: "EEG32",
      //   sn: "SN-Yongle-dev",
      //   mac: "00:00:00:00:00:00",
      // });

      // await lib.set_wifi_config(deviceId, {
      //   ssid: "eeg-wifi",
      //   password: "0123456789",
      //   // security: 2, // WiFiSecurity::SecurityWpa2MixedPsk
      // });

      // await lib.set_wifi_config(deviceId, {
      //   ssid: "eeg01-wifi",
      //   password: "123456789",
      // });

      await lib.get_ble_device_info(deviceId);
      await lib.get_wifi_status(deviceId);
      await lib.get_wifi_config(deviceId);
    }
  });

  lib.set_msg_resp_callback((resp) => {
    console.log("ECAP msg response:", resp);
  });

  // BLE设备信息, 固件未实现，目前都是空
  // lib.set_ble_device_info_callback((info) => {
  //   console.log("Device info changed:", info);
  //   // { deviceId, manufacturer, model, serial, firmware, hardware }
  // });

  // BLE电量信息
  lib.set_ble_battery_level_callback((obj) => {
    // 电池电量变化时会回调
    console.log("Battery level changed:", obj);
  });
}
