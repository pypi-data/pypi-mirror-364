/* tslint:disable */
/* eslint-disable */
export function parse_32ch_eeg_data(data: Uint8Array, gain: number): Float64Array;
export function fftfreq(n: number, d: number): Float64Array;
export function get_filtered_freq(n: number, fs: number): Float64Array;
export function get_filtered_fft(data: Float64Array, fs: number): Float64Array;
export function get_device_info(): any;
export function start_eeg_stream(): any;
export function stop_eeg_stream(): any;
export function get_eeg_data_buffer(take: number, clean: boolean): any;
export function get_imu_data_buffer(take: number, clean: boolean): any;
export function get_eeg_config(): any;
export function set_eeg_config(sr: EegSampleRate, gain: EegSignalGain, signal: EegSignalSource): any;
export function get_leadoff_config(): any;
export function start_imu_stream(): any;
export function stop_imu_stream(): any;
export function get_imu_config(): any;
export function set_imu_config(sr: ImuSampleRate): any;
export function get_ble_device_info(): any;
export function set_ble_device_info(model: string, sn: string): any;
export function get_wifi_status(): any;
export function get_wifi_config(): any;
export function set_wifi_config(bandwidth_40mhz: boolean, security: WiFiSecurity, ssid: string, password: string): any;
export function send_start_dfu(file_size: number, file_md5: string, file_sha256: string): any;
export function send_dfu_data(offset: number, data: Uint8Array, finished: boolean): any;
export function send_dfu_reboot(): any;
export function set_env_noise_cfg(noise_type: NoiseTypes, fs: number): void;
export function remove_env_noise(data: Float64Array, channel: number): Float64Array;
export function remove_env_noise_sosfiltfilt(data: Float64Array, channel: number): Float64Array;
export function remove_env_noise_notch(data: Float64Array, channel: number): Float64Array;
export function set_eeg_filter_cfg(high_pass_enabled: boolean, high_cut: number, low_pass_enabled: boolean, low_cut: number, band_pass_enabled: boolean, band_pass_low: number, band_pass_high: number, band_stop_enabled: boolean, band_stop_low: number, band_stop_high: number, fs: number): void;
export function apply_easy_mode_filters(data: Float64Array, channel: number): Float64Array;
export function apply_easy_mode_sosfiltfilt(data: Float64Array, channel: number): Float64Array;
export function sosfiltfilt_highpass(filter: SosFilter, data: Float64Array): Float64Array;
export function sosfiltfilt_lowpass(filter: SosFilter, data: Float64Array): Float64Array;
export function sosfiltfilt_bandpass(filter: SosFilter, data: Float64Array): Float64Array;
export function sosfiltfilt_bandstop(filter: SosFilter, data: Float64Array): Float64Array;
export function apply_highpass(filter: HighPassFilter, data: Float64Array): Float64Array;
export function apply_lowpass(filter: LowPassFilter, data: Float64Array): Float64Array;
export function apply_bandpass(filter: BandPassFilter, data: Float64Array): Float64Array;
export function apply_bandstop(filter: BandStopFilter, data: Float64Array): Float64Array;
export function init_logging(level: LogLevel): void;
export enum AggOperations {
  Mean = 0,
  Median = 1,
}
export enum DownsamplingOperations {
  Mean = 0,
  Median = 1,
  Max = 2,
  Min = 3,
  Sum = 4,
  First = 5,
  Last = 6,
  Extremes = 7,
}
export enum EEGCapModuleId {
  MCU = 0,
  BLE = 1,
  APP = 2,
}
export enum EegSampleRate {
  SR_None = 0,
  SR_250Hz = 1,
  SR_500Hz = 2,
  SR_1000Hz = 3,
  SR_2000Hz = 4,
}
export enum EegSignalGain {
  GAIN_NONE = 0,
  GAIN_1 = 1,
  GAIN_2 = 2,
  GAIN_4 = 3,
  GAIN_6 = 4,
  GAIN_8 = 5,
  GAIN_12 = 6,
  GAIN_24 = 7,
}
export enum EegSignalSource {
  SIGNAL_NONE = 0,
  NORMAL = 1,
  SHORTED = 2,
  MVDD = 3,
  TEST_SIGNAL = 4,
}
export enum ImuSampleRate {
  SR_NONE = 0,
  SR_50Hz = 1,
  SR_100Hz = 2,
}
export enum LeadOffChip {
  None = 0,
  Chip1 = 1,
  Chip2 = 2,
  Chip3 = 3,
  Chip4 = 4,
}
export enum LeadOffCurrent {
  None = 0,
  Cur6nA = 1,
  Cur24nA = 2,
  Cur6uA = 3,
  Cur24uA = 4,
}
export enum LeadOffFreq {
  None = 0,
  Dc = 1,
  Ac7p8hz = 2,
  Ac31p2hz = 3,
  AcFdr4 = 4,
}
export enum LogLevel {
  Error = 0,
  Warn = 1,
  Info = 2,
  Debug = 3,
  Trace = 4,
}
export enum MsgType {
  Crimson = 0,
  OxyZen = 1,
  Mobius = 3,
  MobiusV1_5 = 4,
  Almond = 5,
  AlmondV2 = 6,
  Morpheus = 2,
  Luna = 7,
  REN = 8,
  Breeze = 9,
  Stark = 10,
  EEGCap = 11,
  Edu = 12,
  Clear = 13,
  Melody = 15,
  Aura = 16,
}
export enum NoiseTypes {
  FIFTY = 0,
  SIXTY = 1,
  FIFTY_AND_SIXTY = 2,
}
export enum WiFiSecurity {
  SECURITY_NONE = 0,
  SECURITY_OPEN = 1,
  SECURITY_WPA2_MIXED_PSK = 2,
}
export class BandPassFilter {
  free(): void;
  constructor(_order: number, s: number, fl: number, fu: number);
  a: number;
  d1: number;
  d2: number;
  d3: number;
  d4: number;
  w0: number;
  w1: number;
  w2: number;
  w3: number;
  w4: number;
}
export class BandStopFilter {
  free(): void;
  constructor(_order: number, s: number, fl: number, fu: number);
  a: number;
  d1: number;
  d2: number;
  d3: number;
  d4: number;
  w0: number;
  w1: number;
  w2: number;
  w3: number;
  w4: number;
  r: number;
  s: number;
}
export class HighPassFilter {
  free(): void;
  constructor(_order: number, s: number, f: number);
}
export class LowPassFilter {
  free(): void;
  constructor(_order: number, s: number, f: number);
}
export class SosFilter {
  private constructor();
  free(): void;
  static create_lowpass(order: number, fs: number, lowcut: number): SosFilter;
  static create_highpass(order: number, fs: number, highcut: number): SosFilter;
  static create_bandpass(order: number, fs: number, lowcut: number, highcut: number): SosFilter;
  static create_bandstop(order: number, fs: number, lowcut: number, highcut: number): SosFilter;
}
