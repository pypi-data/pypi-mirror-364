import matplotlib.pyplot as plt
import matplotlib
import sys
import numpy as np
from utils import sdk, logger
from filters_sdk import BWBandPassFilter, BWBandStopFilter

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# EEG数据
fs = 250  # 采样频率
# num_channels = 32  # 通道数

# 滤波器参数设置
order = 4  # 滤波器阶数

env_noise_filter_50_Hz = BWBandStopFilter(order, sample_rate=fs, fl=49, fu=51)
env_noise_filter_60_Hz = BWBandStopFilter(order, sample_rate=fs, fl=59, fu=61)
eeg_filter = BWBandPassFilter(order, sample_rate=fs, fl=2, fu=45)

q = 30  # 品质因数
notch_filter_50 = sdk.NotchFilter(50, fs, q)
notch_filter_60 = sdk.NotchFilter(60, fs, q)
sos_eeg_filter = sdk.SosFilter.create_band_pass(order, fs, 2, 45)  # 创建SosFilter实例

# 生成一段EEG原始信号，电压值范围在-100μV到100μV之间
raw_signal = np.random.uniform(low=-100e-6, high=100e-6, size=(1, 10000))

# 例如，绘制第1个通道的信号前1000个点
sig = raw_signal[0, :1000] # 第1个通道的信号
filter_sig = env_noise_filter_50_Hz.filter(sig)
filter_sig = env_noise_filter_60_Hz.filter(filter_sig)
# eeg_filter_sig = eeg_filter.filter(filter_sig)

sig = raw_signal[0, :1000] # 第1个通道的信号
notch_filter_sig = notch_filter_50.apply(sig)
notch_filter_sig = notch_filter_60.apply(notch_filter_sig)
# sos_eeg_filter_sig = sos_eeg_filter.apply(notch_filter_sig)

# 比较 filter_sig和notch_filter_sig差异
diff = filter_sig - notch_filter_sig
print(f"raw_signal: {sig[:3]}")
print(f"filter_sig: {filter_sig[:3]}")
print(f"notch__sig: {notch_filter_sig[:3]}")
print(f"Filter Signal and Notch Filter Signal Difference: {np.mean(diff)}")
sys.exit(0)

plt_sig = eeg_filter_sig
# plt_sig = sos_eeg_filter_sig
# plt.plot(filter_sig, label='Filtered Signal (50/60 Hz Bandstop)')
# plt.plot(notch_filter_sig, label='Notch Filtered Signal (50/60 Hz)')
plt.plot(plt_sig, label='EEG Filtered Signal (2-45 Hz Bandpass)')
# plt.plot(sos_eeg_filter_sig, label='SOS Filtered Signal (2-45 Hz Bandpass)')
plt.title(f"Signal Example")
plt.xlabel("Sample Points")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.savefig("imgs/eeg_filter_example.png")
# plt.show()

fft = np.fft.fft(plt_sig)
freqs = np.fft.fftfreq(len(plt_sig), d=1/fs)
plt.figure(figsize=(10, 6))
plt.plot(freqs[:len(freqs)//2], np.abs(fft)[:len(fft)//2])
plt.title("FFT of Filtered Signal")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.savefig("imgs/eeg_filter_fft.png")
plt.show()
