#![allow(non_camel_case_types)]
use crate::impl_enum_conversion;
#[allow(unused_imports)]
use serde::{Deserialize, Serialize};

// impl_enum_conversion!(
//   FilterTypes,
//   BUTTERWORTH = 0,
//   CHEBYSHEV_TYPE_1 = 1,
//   BESSEL = 2,
//   BUTTERWORTH_ZERO_PHASE = 3,
//   CHEBYSHEV_TYPE_1_ZERO_PHASE = 4,
//   BESSEL_ZERO_PHASE = 5
// );

impl_enum_conversion!(AggOperations, Mean = 0, Median = 1);

impl_enum_conversion!(
  DownsamplingOperations,
  Mean = 0,
  Median = 1,
  Max = 2,
  Min = 3,
  Sum = 4,
  First = 5,
  Last = 6,
  Extremes = 7
);

// impl_enum_conversion!(
//   WindowOperations,
//   NO_WINDOW = 0,
//   HANNING = 1,
//   HAMMING = 2,
//   BLACKMAN_HARRIS = 3
// );

// impl_enum_conversion!(DetrendOperations, NO_DETREND = 0, CONSTANT = 1, LINEAR = 2);

impl_enum_conversion!(NoiseTypes, FIFTY = 0, SIXTY = 1, FIFTY_AND_SIXTY = 2);

// impl_enum_conversion!(WaveletDenoisingTypes, VISUSHRINK = 0, SURESHRINK = 1);

// impl_enum_conversion!(ThresholdTypes, SOFT = 0, HARD = 1);

// impl_enum_conversion!(WaveletExtensionTypes, SYMMETRIC = 0, PERIODIC = 1);

// impl_enum_conversion!(NoiseEstimationLevelTypes, FIRST_LEVEL = 0, ALL_LEVELS = 1);
