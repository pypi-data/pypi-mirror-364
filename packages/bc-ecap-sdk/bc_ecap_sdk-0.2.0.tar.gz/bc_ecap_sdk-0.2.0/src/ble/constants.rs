use btleplug::api::bleuuid::uuid_from_u16;

use uuid::Uuid;

/// UUID of the characteristic for which we should subscribe to notifications.
pub static CMSN_SERVICE_UUID: Uuid = Uuid::from_u128(0x0d740001_d26f_4dbb_95e8_a4f5c55c57a9);
pub static ECAP_SERVICE_UUID: Uuid = Uuid::from_u128(0x4de5a20c_0001_ae0b_bf63_0242ac130002);
pub static EDU_SERVICE_UUID: Uuid = Uuid::from_u128(0x4de50001_a20c_ae0c_bf63_0242ac130002);
pub static OXYZ_SERVICE_UUID: Uuid = Uuid::from_u128(0x4de50001_a20c_ae01_bf63_0242ac130002);

pub static ALL_SERVICE_UUIDS: [Uuid; 4] = [
  CMSN_SERVICE_UUID,
  ECAP_SERVICE_UUID,
  EDU_SERVICE_UUID,
  OXYZ_SERVICE_UUID,
];

pub static ALL_RX_CHARACTERISTIC_UUIDS: [Uuid; 4] = [
  CMSN_RX_CHARACTERISTIC_UUID,
  ECAP_RX_CHARACTERISTIC_UUID,
  EDU_RX_CHARACTERISTIC_UUID,
  OXYZ_RX_CHARACTERISTIC_UUID,
];

#[allow(dead_code)]
pub(crate) static OXYZ_TX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x4de50002_a20c_ae01_bf63_0242ac130002);
#[allow(dead_code)]
pub(crate) static OXYZ_RX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x4de50003_a20c_ae01_bf63_0242ac130002);

#[allow(dead_code)]
pub(crate) static CMSN_TX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x0d740002_d26f_4dbb_95e8_a4f5c55c57a9);
#[allow(dead_code)]
pub(crate) static CMSN_RX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x0d740003_d26f_4dbb_95e8_a4f5c55c57a9);

#[allow(dead_code)]
pub static ECAP_TX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x4de5a20c_0002_ae0b_bf63_0242ac130002);

#[allow(dead_code)]
pub static ECAP_RX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x4de5a20c_0003_ae0b_bf63_0242ac130002);

#[allow(dead_code)]
pub static EDU_TX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x4de50002_a20c_ae0c_bf63_0242ac130002);

#[allow(dead_code)]
pub static EDU_RX_CHARACTERISTIC_UUID: Uuid =
  Uuid::from_u128(0x4de50003_a20c_ae0c_bf63_0242ac130002);

pub static BLE_SCAN_RESULT_CALLBACK: Uuid = uuid_from_u16(0x180f); // 电池服务 UUID
pub static BATTERY_LEVEL_CHAR_UUID: Uuid = uuid_from_u16(0x2A19); // 电池电量特征 UUID

// device info UUIDs
pub static DEVICE_INFO_SERVICE_UUID: Uuid = uuid_from_u16(0x180A); // 设备信息服务
pub static MANUFACTURER_NAME_CHAR_UUID: Uuid = uuid_from_u16(0x2A29); // 制造商名称特征 UUID
pub static MODEL_NUMBER_CHAR_UUID: Uuid = uuid_from_u16(0x2A24); // 型号编号特征 UUID
pub static SERIAL_NUMBER_CHAR_UUID: Uuid = uuid_from_u16(0x2A25); // 序列号特征 UUID
pub static HARDWARE_REVISION_CHAR_UUID: Uuid = uuid_from_u16(0x2A27); // 硬件版本特征 UUID
pub static FIRMWARE_REVISION_CHAR_UUID: Uuid = uuid_from_u16(0x2A26); // 固件版本特征 UUID
