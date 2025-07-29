from ast import literal_eval
import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QApplication
import numpy as np
import asyncio
import os
import io
import numpy as np
import sys
from qasync import QEventLoop
from filters_sdk import BWBandPassFilter, BWBandStopFilter
import time
from utils import sdk, logger

# EEG数据
fs = 250  # 采样频率
# num_channels = 32  # 通道数

# 滤波器参数设置
order = 4  # 滤波器阶数

env_noise_filter_50_Hz = BWBandStopFilter(order, sample_rate=fs, fl=49, fu=51)
env_noise_filter_60_Hz = BWBandStopFilter(order, sample_rate=fs, fl=59, fu=61)
eeg_filter = BWBandPassFilter(order, sample_rate=fs, fl=2, fu=45)

q = 30  # 品质因数
# notch_filter_50 = sdk.NotchFilter(50, fs, q)
# notch_filter_60 = sdk.NotchFilter(60, fs, q)
notch_filter_50 = sdk.SosFilter.create_band_stop(order, fs, 49, 51)  # 创建SosFilter实例
notch_filter_60 = sdk.SosFilter.create_band_stop(order, fs, 59, 61)  # 创建SosFilter实例
sos_eeg_filter = sdk.SosFilter.create_band_pass(order, fs, 2, 45)  # 创建SosFilter实例

curves = []

# 创建主窗口
app = QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="EEG Data Visualization")
win.resize(2000, 1600)

plot_eeg_py = win.addPlot(title=f"EEG Data Plot")
# plot_eeg_py.setYRange(-200, 200)  # 设置Y轴范围
plot_eeg_py.setLabel('left', 'Amplitude (uV)')
plot_eeg_py.setLabel('bottom', 'Sample Points')
curve = plot_eeg_py.plot()
curves.append(curve)

plot_eeg_sdk = win.addPlot(title=f"EEG Data Plot (SDK)")
# plot_eeg_sdk.setYRange(-200, 200)  # 设置Y轴范围
plot_eeg_sdk.setLabel('left', 'Amplitude (uV)')
plot_eeg_sdk.setLabel('bottom', 'Sample Points')
curve_sdk = plot_eeg_sdk.plot()
curves.append(curve_sdk)

win.nextRow()

# FFT plot
fft_plot = win.addPlot(title="FFT Plot")
fft_plot.setYRange(0, 1)  # 设置Y轴范围
fft_plot.setLabel('left', 'Magnitude (uV/Hz)')
fft_plot.setLabel('bottom', 'Frequency (Hz)')
curve_fft = fft_plot.plot()
curves.append(curve_fft)

# FFT plot sdk
fft_plot_sdk = win.addPlot(title="FFT Plot (SDK)")
fft_plot_sdk.setYRange(0, 1)  # 设置Y轴范围
fft_plot_sdk.setLabel('left', 'Magnitude (uV/Hz)')
fft_plot_sdk.setLabel('bottom', 'Frequency (Hz)')
curve_fft_sdk = fft_plot_sdk.plot()
curves.append(curve_fft_sdk)

def init_timer():
    logger.info("Init timer")
    # 定时器
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(mock_update_plot)
    timer.start(200)  # 每200ms更新一次
    return timer

eeg_index = 0
data_eeg = []
data_eeg_sdk = []
EEG_WIN_LEN = 1250  # 250Hz * 5s = 1250 samples

# 更新函数
def mock_update_plot():
    global eeg_index, data_eeg, data_eeg_sdk

    if eeg_index * 50 >= len(data_eeg):
        eeg_index = 0

    # 使用 rfft 计算实数FFT (推荐方法，效率更高)
    index = eeg_index * 50
    values = data_eeg[index:index+EEG_WIN_LEN]
    y_rfft = np.fft.rfft(values)
    l = EEG_WIN_LEN
    s2 = np.abs(y_rfft / l)  # 幅度谱
    f2 = np.linspace(0.0, fs / 2, l // 2 + 1)  # 频率轴
    curve.setData(values)
    curve_fft.setData(f2, s2)

    values_sdk = data_eeg_sdk[index:index+EEG_WIN_LEN]
    y_rfft = np.fft.rfft(values_sdk)
    l = EEG_WIN_LEN
    s2 = np.abs(y_rfft / l)  # 幅度谱
    f2 = np.linspace(0.0, fs / 2, l // 2 + 1)  # 频率轴
    curve_sdk.setData(values_sdk)
    curve_fft_sdk.setData(f2, s2)

    eeg_index += 1


def is_valid_data(item):
    if isinstance(item, (list, tuple)) and len(item) == 3:
        ts, idx, values = item
        return (
            isinstance(ts, (int, float)) and
            isinstance(idx, (int, float)) and
            isinstance(values, (list, tuple)) and
            all(isinstance(v, (int, float)) for v in values)
        )
    return False

def read_eeg_data():
    file = io.open("eeg-sample.log", "r")
    print(f"file.name:{file.name}")

    # i = 1
    lines = file.readlines()
    for line in lines[1:-1]: # Skip the first and last lines
        line = line.replace(", ", ",")
        line = line.replace("，", ",")
        parts = literal_eval(line.strip())
        if not is_valid_data(parts):
            continue
        # print("EEG Timestamp:" + str(parts[0]) + ", SeqNum: " + str(parts[1]))
        values = parts[-1]
        if not isinstance(values, (list, tuple)):
            print(f"Invalid data format: {values}")
            continue
        if len(values) != 50:
            print(f"Unexpected number of values: {len(values)}")
            continue

        # if len(data_eeg) >= EEG_WIN_LEN:
        #     data_eeg = data_eeg[-50:]
        for d in values:
            d = env_noise_filter_50_Hz.filter(d)
            d = env_noise_filter_60_Hz.filter(d)
            d = eeg_filter.filter(d)
            data_eeg.append(d)
        # print(f"data length: {len(data_eeg)}")
        # print(f"data: {data_eeg[:3]}")

        # SDK处理
        filter_values = notch_filter_50.apply(values)
        filter_values = notch_filter_60.apply(filter_values)
        d = sos_eeg_filter.apply(filter_values)
        data_eeg_sdk.extend(d)
    logger.info(f"Total data points: {len(data_eeg)}")
    logger.info(f"Total data points SDK: {len(data_eeg_sdk)}")
    file.close()

if __name__ == "__main__":
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    read_eeg_data()
    timer = init_timer()
    try:
        loop.run_forever()  # 事件循环运行直到手动退出
    finally:
        loop.close()
