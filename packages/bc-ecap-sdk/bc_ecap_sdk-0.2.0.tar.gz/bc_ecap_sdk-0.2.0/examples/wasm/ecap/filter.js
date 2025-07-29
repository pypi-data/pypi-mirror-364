const node_sdk = require("./ecap_node.js");

class LowPassFilter {
  constructor(order, fs, lowcut) {
    this._handle = node_sdk.create_lowpass(order, fs, lowcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.apply_lowpass(this._handle, input);
  }
}

class HighPassFilter {
  constructor(order, fs, highcut) {
    this._handle = node_sdk.create_highpass(order, fs, highcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.apply_highpass(this._handle, input);
  }
}

class BandPassFilter {
  constructor(order, fs, lowcut, highcut) {
    this._handle = node_sdk.create_bandpass(order, fs, lowcut, highcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.apply_bandpass(this._handle, input);
  }
}

class BandStopFilter {
  constructor(order, fs, lowcut, highcut) {
    this._handle = node_sdk.create_bandstop(order, fs, lowcut, highcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.apply_bandstop(this._handle, input);
  }
}

class SosLowPassFilter {
  constructor(order, fs, lowcut) {
    this._handle = node_sdk.sos_create_lowpass(order, fs, lowcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.sosfiltfilt_apply(this._handle, input);
  }
}

class SosHighPassFilter {
  constructor(order, fs, highcut) {
    this._handle = node_sdk.sos_create_highpass(order, fs, highcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.sosfiltfilt_apply(this._handle, input);
  }
}

class SosBandPassFilter {
  constructor(order, fs, lowcut, highcut) {
    this._handle = node_sdk.sos_create_bandpass(order, fs, lowcut, highcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.sosfiltfilt_apply(this._handle, input);
  }
}

class SosBandStopFilter {
  constructor(order, fs, lowcut, highcut) {
    this._handle = node_sdk.sos_create_bandstop(order, fs, lowcut, highcut);
  }

  // Float32Array
  apply(input) {
    if (!(input instanceof Float32Array)) {
      throw new TypeError("Input must be a Float32Array");
    }
    return node_sdk.sosfiltfilt_apply(this._handle, input);
  }
}

class NotchFilter {
  constructor(f0, fs, quality) {
    this._handle = node_sdk.sos_create_notch_filter(f0, fs, quality);
  }

  // Float32Array
  apply(signal) {
    if (!(signal instanceof Float32Array)) {
      throw new TypeError("Signal must be a Float32Array");
    }
    return node_sdk.sosfiltfilt_apply(this._handle, signal);
  }
}

module.exports = {
  LowPassFilter,
  HighPassFilter,
  BandPassFilter,
  BandStopFilter,
  SosLowPassFilter,
  SosHighPassFilter,
  SosBandPassFilter,
  SosBandStopFilter,
  NotchFilter,
};
