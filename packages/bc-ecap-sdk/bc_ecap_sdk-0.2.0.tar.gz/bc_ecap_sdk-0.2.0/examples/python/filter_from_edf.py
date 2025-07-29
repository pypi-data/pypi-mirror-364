# Neo 适合的场景
# 需求	是否推荐用Neo
# 只解析EDF/BDF	❌ pyedflib或mne更简单
# EEG科学分析（滤波、ICA、脑图）	❌ 推荐mne
# 多格式、多类型神经科学数据整合	✅ Neo最佳
# 需要统一API/标准化/时间对齐	✅ Neo最佳
# Spike Train、LFP、Event分析	✅ Neo + Elephant

import mne
import matplotlib.pyplot as plt
import matplotlib
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

# 读取EDF文件，返回Raw对象
file_path = 'EEG_Test_250Hz.edf'
raw = mne.io.read_raw_edf(file_path, preload=True)

# 查看文件信息，比如采样率、通道数
logger.info(raw.info)

# 获取通道名列表
channels = raw.info['ch_names']
logger.info(f"Number of channels: {len(channels)}")
logger.info(f"Channel names: {channels}")

# 提取所有通道的数据，shape = (n_channels, n_samples)
data = raw.get_data()

# 打印数据形状
logger.info(f"Data shape: {data.shape}")

# 打印采样率
sfreq = raw.info['sfreq']
logger.info(f"Sampling rate: {sfreq} Hz")

# 例如，绘制第1个通道的信号前1000个点
sig = data[0, :1000] # 第1个通道的信号
filter_sig = env_noise_filter_50_Hz.filter(sig)
filter_sig = env_noise_filter_60_Hz.filter(filter_sig)
eeg_filter_sig = eeg_filter.filter(filter_sig)

sig = data[0, :1000] # 第1个通道的信号
notch_filter_sig = notch_filter_50.apply(sig)
notch_filter_sig = notch_filter_60.apply(notch_filter_sig)
sos_eeg_filter_sig = sos_eeg_filter.apply(notch_filter_sig)

plt.plot(filter_sig, label='Filtered Signal (50/60 Hz Bandstop)')
plt.plot(notch_filter_sig, label='Notch Filtered Signal (50/60 Hz)')
plt.plot(eeg_filter_sig, label='EEG Filtered Signal (2-45 Hz Bandpass)')
plt.plot(sos_eeg_filter_sig, label='SOS Filtered Signal (2-45 Hz Bandpass)')

plt.title(f"Channel {channels[0]} Signal Example")
plt.xlabel("Sample Points")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.savefig("imgs/eeg_filter_example.png")
plt.show()
