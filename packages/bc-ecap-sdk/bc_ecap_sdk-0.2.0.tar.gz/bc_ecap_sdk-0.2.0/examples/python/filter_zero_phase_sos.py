import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from utils import sdk, logger
from scipy.signal import butter, sosfiltfilt, filtfilt, lfilter, sosfilt
import numpy as np
import matplotlib.pyplot as plt

def plot_signals(t, signal, filtered_lfilter, filtered_sosfilt, filtered_zero_phase, filtered_zero_phase_sosfilt, filtered_zero_phase_sosfilt_sdk, filename):
    plt.figure(figsize=(20, 8))
    plt.plot(t, signal, label='Raw Signal', alpha=0.7)
    plt.plot(t, filtered_lfilter, label='lfilter (b,a)', alpha=0.8)
    plt.plot(t, filtered_sosfilt, label='sosfilt (SOS)', alpha=0.8)
    plt.plot(t, filtered_zero_phase, label='filtfilt (Zero-Phase)', alpha=0.8)
    plt.plot(t, filtered_zero_phase_sosfilt, label='sosfiltfilt (Zero-Phase SOS)', alpha=0.8)
    plt.plot(t, filtered_zero_phase_sosfilt_sdk, label='sosfiltfilt (Zero-Phase SDK)', alpha=0.8)
    plt.legend()
    plt.grid(True)
    plt.title("lfilter vs sosfilt vs sosfiltfilt comparison")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.savefig(filename)
    plt.show()
    # plt.close()

def plot_frequency_response(b, a, fs):
    w, h = signal.freqz(b, a, worN=8000)
    plt.figure(figsize=(10, 6))
    plt.plot(0.5 * fs * w / np.pi, np.abs(h), "b")
    plt.title("Filter Frequency Response")
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Gain")
    plt.grid(True)
    plt.savefig("python_frequency_response.png")
    plt.show()
    # plt.close()

order = 4  # Filter order

def main():
    # 生成测试信号
    fs = 100  # 采样率
    t = np.linspace(0, 5, fs*5)
    sig = np.sin(2*np.pi*1*t) + 0.5*np.sin(2*np.pi*20*t)  # 1Hz + 20Hz
    print(len(sig))

    # 构造低通滤波器（cutoff = 5Hz）
    low_cutoff = 5

    # 传统的 b, a 格式（用于比较）
    b, a = butter(order, low_cutoff / (0.5 * fs), btype='low')

    # 使用 SOS 格式
    sos = butter(order, low_cutoff / (0.5 * fs), btype='low', output='sos')

    # 单向滤波 - 传统方式
    filtered_lfilter = lfilter(b, a, sig)
    # 单向滤波 - SOS 方式
    filtered_sosfilt = sosfilt(sos, sig)

    # 零相位滤波 - 传统方式
    filtered_zero_phase = filtfilt(b, a, sig)
    # 零相位滤波 - SOS方式
    filtered_zero_phase_sosfilt = sosfiltfilt(sos, sig)
    # 零相位滤波 - SDK实现
    sos_filter = sdk.SosFilter.create_low_pass(order, fs, low_cutoff)
    filtered_zero_phase_sdk = sos_filter.apply(sig)

    if not np.allclose(filtered_zero_phase_sosfilt, filtered_zero_phase_sdk):
        logger.error("Filtered signals do not match!")
    else:
        logger.info("Filtered signals match successfully!")

    # 绘制信号和滤波结果
    plot_signals(t, sig, filtered_lfilter, filtered_sosfilt, filtered_zero_phase, filtered_zero_phase_sosfilt, filtered_zero_phase_sdk, "imgs/filter_zero_phase_comparison_sos.png")


if __name__ == "__main__":
    main()
