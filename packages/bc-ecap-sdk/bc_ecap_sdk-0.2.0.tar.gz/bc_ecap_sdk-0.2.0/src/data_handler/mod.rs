// use cfg_if::cfg_if;

pub mod afe_handler;
pub mod enums;
pub mod fft;
pub mod filter;
pub mod filter_bc;
pub mod filter_sos;

// cfg_if::cfg_if! {
//     if #[cfg(feature = "examples")] {
//         #[allow(non_upper_case_globals)]
//         pub mod filter_c_bindings;
//     }
// }

// SHARED_EXPORT int CALLING_CONVENTION perform_wavelet_transform (double *data, int data_len,
//     int wavelet, int decomposition_level, int extension, double *output_data,
//     int *decomposition_lengths);
// SHARED_EXPORT int CALLING_CONVENTION perform_inverse_wavelet_transform (double *wavelet_coeffs,
//     int original_data_len, int wavelet, int decomposition_level, int extension,
//     int *decomposition_lengths, double *output_data);
// SHARED_EXPORT int CALLING_CONVENTION perform_wavelet_denoising (double *data, int data_len,
//     int wavelet, int decomposition_level, int wavelet_denoising, int threshold,
//     int extenstion_type, int noise_level);
// SHARED_EXPORT int CALLING_CONVENTION get_csp (const double *data, const double *labels,
//     int n_epochs, int n_channels, int n_times, double *output_w, double *output_d);
// SHARED_EXPORT int CALLING_CONVENTION get_window (
//     int window_function, int window_len, double *output_window);
// SHARED_EXPORT int CALLING_CONVENTION get_nearest_power_of_two (int value, int *output);
// SHARED_EXPORT int CALLING_CONVENTION get_psd (double *data, int data_len, int sampling_rate,
//     int window_function, double *output_ampl, double *output_freq);
// SHARED_EXPORT int CALLING_CONVENTION detrend (
//     double *data, int data_len, int detrend_operation);
// SHARED_EXPORT int CALLING_CONVENTION calc_stddev (
//     double *data, int start_pos, int end_pos, double *output);
// SHARED_EXPORT int CALLING_CONVENTION get_psd_welch (double *data, int data_len, int nfft,
//     int overlap, int sampling_rate, int window_function, double *output_ampl,
//     double *output_freq);
// SHARED_EXPORT int CALLING_CONVENTION get_band_power (double *ampl, double *freq, int data_len,
//     double freq_start, double freq_end, double *band_power);
// SHARED_EXPORT int CALLING_CONVENTION get_custom_band_powers (double *raw_data, int rows,
//     int cols, double *start_freqs, double *stop_freqs, int num_bands, int sampling_rate,
//     int apply_filters, double *avg_band_powers, double *stddev_band_powers);
