import numpy as np
from scipy import signal


class Filter:
    def __init__(self, order, fs):
        self.order = order
        self.fs = fs

    def apply(self, x):
        raise NotImplementedError("This method should be implemented by subclasses.")


class HighPassFilter(Filter):
    def __init__(self, order, fs, f0):
        super().__init__(order, fs)
        self.sos = signal.butter(order, f0, 'hp', fs=fs, output='sos')
        self.zi = signal.sosfilt_zi(self.sos)

    def apply(self, x):
        y, self.zi = signal.sosfilt(self.sos, x, zi=self.zi)
        return y


class LowPassFilter(Filter):
    def __init__(self, order, fs, f0):
        super().__init__(order, fs)
        self.sos = signal.butter(order, f0, 'lp', fs=fs, output='sos')
        self.zi = signal.sosfilt_zi(self.sos)

    def apply(self, x):
        y, self.zi = signal.sosfilt(self.sos, x, zi=self.zi)
        return y


class NotchFilter(Filter):
    def __init__(self, fs, f0, Q):
        super().__init__(order=2, fs=fs)  # Order can be fixed for notch filter
        self.b, self.a = signal.iirnotch(f0, Q, fs)
        self.zi = signal.lfilter_zi(self.b, self.a)

        # Q：品质因数，表示滤波器的选择性或带宽，影响滤波器的抑制效果。 Q 值越高，滤波器的带宽越窄，抑制特定频率的能力越强。对于陷波滤波器，较高的 Q 值可以更精确地抑制目标频率周围的信号。
        # Q 值在 1 到 10 之间是常见的选择

    def apply(self, x):
        y, self.zi = signal.lfilter(self.b, self.a, x, zi=self.zi)
        return y


class BandPassFilter(Filter):
    def __init__(self, order, fs, f_low, f_high):
        super().__init__(order, fs)
        self.sos = signal.butter(order, [f_low, f_high], 'bp', fs=fs, output='sos')
        self.zi = signal.sosfilt_zi(self.sos)

    def apply(self, x):
        y, self.zi = signal.sosfilt(self.sos, x, zi=self.zi)
        return y


class BandStopFilter(Filter):
    def __init__(self, order, fs, f_low, f_high):
        super().__init__(order, fs)
        self.sos = signal.butter(order, [f_low, f_high], 'bs', fs=fs, output='sos')
        self.zi = signal.sosfilt_zi(self.sos)

    def apply(self, x):
        y, self.zi = signal.sosfilt(self.sos, x, zi=self.zi)
        return y


# Example usage
if __name__ == "__main__":
    # Sample parameters
    fs = 256  # Sampling frequency
    order = 4  # Order of the filters
    f_hp = 0.5  # High-pass filter cutoff frequency
    f_lp = 30.0  # Low-pass filter cutoff frequency
    f_notch = 50.0  # Notch filter frequency
    f_bp_low = 8.0  # Band-pass filter low frequency
    f_bp_high = 12.0  # Band-pass filter high frequency
    f_bs_low = 45.0  # Band-stop filter low frequency
    f_bs_high = 55.0  # Band-stop filter high frequency
    Q = 30  # Quality factor for the notch filter

    # Create filter instances
    hp_filter = HighPassFilter(order, fs, f_hp)
    lp_filter = LowPassFilter(order, fs, f_lp)
    notch_filter = NotchFilter(fs, f_notch, Q)
    bp_filter = BandPassFilter(order, fs, f_bp_low, f_bp_high)
    bs_filter = BandStopFilter(order, fs, f_bs_low, f_bs_high)

    # Example input signal: a sine wave with noise
    t = np.arange(0, 10, 1/fs)
    x = np.sin(2 * np.pi * 10 * t) + 0.5 * np.random.normal(size=len(t))  # 10 Hz sine wave + noise

    # Apply filters
    y_hp = hp_filter.apply(x)
    y_lp = lp_filter.apply(x)
    y_notch = notch_filter.apply(x)
    y_bp = bp_filter.apply(x)
    y_bs = bs_filter.apply(x)

    # You can visualize or analyze y_hp, y_lp, y_notch, y_bp, and y_bs as needed.
