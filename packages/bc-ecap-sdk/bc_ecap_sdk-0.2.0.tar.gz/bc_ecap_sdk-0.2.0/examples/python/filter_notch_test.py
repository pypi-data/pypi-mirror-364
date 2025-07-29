import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from utils import sdk, logger

def plot_signals(signal, filtered, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(signal, "r", label="Original")
    plt.plot(filtered, "b", label="Filtered")
    plt.title("Signal Comparison")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    # plt.show()
    plt.close()

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

def generate_notch_coeffs(f0, q, fs):
    b, a = signal.iirnotch(f0, q, fs)
    return b, a

def main():
    # 生成测试信号
    fs = 250.0  # 采样率
    # fs = 500.0  # 采样率
    # fs = 1000.0  # 采样率
    # fs = 2000.0  # 采样率
    t = np.linspace(0, 1, int(fs))  # 1秒的时间序列
    f1 = 50.0  # 50Hz干扰
    f2 = 10.0  # 10Hz信号
    signal_clean = np.sin(2 * np.pi * f2 * t)
    signal_noise = signal_clean + 0.5 * np.sin(2 * np.pi * f1 * t)

    # 设计陷波滤波器
    f0 = 50.0  # 陷波频率
    q = 30.0   # 品质因数

    # 使用scipy的iirnotch函数
    b, a = signal.iirnotch(f0, q, fs)

    # 打印滤波器系数
    logger.info("Python生成的滤波器系数:")
    logger.info(f"b: {list(b)}")
    logger.info(f"a: {list(a)}")

    # 应用滤波器 - Python实现
    sos = signal.tf2sos(b, a)
    logger.info("使用Python实现陷波滤波器...")
    filtered_signal = signal.sosfiltfilt(sos, signal_noise)

    # SDK实现陷波滤波器
    logger.info("使用SDK实现陷波滤波器...")
    notch_filter = sdk.NotchFilter(f0, fs, q)  # 创建NotchFilter实例
    filtered_signal_sdk = notch_filter.apply(signal_noise)
    if not np.allclose(filtered_signal, filtered_signal_sdk):
        logger.error("Filtered signals do not match!")
    else:
        logger.info("Filtered signals match successfully!")

    # 打印信号统计信息
    logger.info("\n原始信号统计:")
    logger.info(f"Mean: {np.mean(signal_noise):.6f}")
    logger.info(f"Std: {np.std(signal_noise):.6f}")
    logger.info(f"Min: {np.min(signal_noise):.6f}, Max: {np.max(signal_noise):.6f}")

    logger.info("\n滤波后信号统计:")
    logger.info(f"Mean: {np.mean(filtered_signal):.6f}")
    logger.info(f"Std: {np.std(filtered_signal):.6f}")
    logger.info(f"Min: {np.min(filtered_signal):.6f}, Max: {np.max(filtered_signal):.6f}")

    # 计算信号差异
    max_diff = np.max(np.abs(signal_noise - filtered_signal))
    mean_diff = np.mean(np.abs(signal_noise - filtered_signal))
    logger.info(f"\n信号差异:")
    logger.info(f"Max difference: {max_diff:.6f}")
    logger.info(f"Mean difference: {mean_diff:.6f}")

    # 绘制信号和滤波器响应
    plot_signals(signal_noise, filtered_signal, "python_signal_comparison.png")
    plot_frequency_response(b, a, fs)
    logger.info("绘图完成，结果已保存。")

if __name__ == "__main__":
    main()
