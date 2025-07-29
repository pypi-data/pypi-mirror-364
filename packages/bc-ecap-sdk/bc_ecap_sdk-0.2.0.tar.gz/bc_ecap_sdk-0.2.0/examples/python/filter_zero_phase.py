import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from utils import sdk, libecap, logger
from scipy.signal import butter, filtfilt, lfilter
import numpy as np
import matplotlib.pyplot as plt

def plot_signals(t, signal, filtered, filtered_zero_phase, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(t, signal, label='Raw Signal')
    plt.plot(t, filtered, label='lfilter Filtered')
    plt.plot(t, filtered_zero_phase, label='filtfilt (Zero-Phase)')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.title("filter() vs filtfilt()")
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

def main():
    # 生成测试信号
    fs = 100  # 采样率
    t = np.linspace(0, 5, fs*5)
    sig = np.sin(2*np.pi*1*t) + 0.5*np.sin(2*np.pi*20*t)  # 1Hz + 20Hz

    # 构造低通滤波器（cutoff = 5Hz）
    b, a = butter(4, 5 / (0.5 * fs), btype='low')

    # 单向滤波
    filtered = lfilter(b, a, sig)

    # 零相位滤波
    filtered_zero_phase = filtfilt(b, a, sig)

    # 绘制信号和滤波结果
    plot_signals(t, sig, filtered, filtered_zero_phase, "imgs/filter_zero_phase_comparison.png")


if __name__ == "__main__":
    main()
