import asyncio
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QApplication
from qasync import QEventLoop

from utils import sdk, libecap, logger
from eeg_cap_model import (
    EEGData,
    get_addr_port,
    set_cfg,
)

# EEG数据
fs = 250  # 采样频率
num_channels = 32  # 通道数
eeg_buffer_length = 2000  # 默认缓冲区长度，注意采样率应该小于此数
eeg_seq_num = None  # EEG数据包序号
eeg_values = np.zeros((num_channels, eeg_buffer_length))  # 32通道的EEG数据

imu_buffer_length = 2000  # IMU缓冲区长度, 默认2000个数据点

imp_window_length = 250  # 阻抗检测窗口长度, 默认250组

# 滤波器参数设置
order = 4  # 滤波器阶数
low_cut = 2  # 低通滤波截止频率
high_cut = 45  # 高通滤波截止频率
# bs_filters = [sdk.BandPassFilter(fs, low_cut, high_cut) for i in range(num_channels)]
q = 30  # 品质因数
q = 30  # 品质因数
notch_filters_50 = [sdk.NotchFilter(50, fs, q) for i in range(num_channels)]
notch_filters_60 = [sdk.NotchFilter(60, fs, q) for i in range(num_channels)]
sos_eeg_filters = [sdk.SosFilter.create_band_pass(order, fs, 2, 45) for i in range(num_channels)]

# 创建32个通道的图表
plots = []
curves = []


def update_plot():
    # 获取EEG数据
    max_len = 250  # 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
    clean = True  # 是否清空缓冲区
    eeg_buff = libecap.get_eeg_buffer(max_len, clean)
    logger.info(f"get_eeg_buffer result len={len(eeg_buff)}")
    if len(eeg_buff) == 0:
        return

    for row in eeg_buff:
        eeg_data = EEGData.from_data(row)
        channel_values = eeg_data.channel_values

        # 更新每个通道的数据
        for i in range(len(channel_values)):
            eeg_values[i] = np.roll(eeg_values[i], -1)  # 数据向左滚动，腾出最后一个位置
            eeg_values[i, -1] = channel_values[i]  # 更新最新的数据值

    # 绘制更新后的数据
    for channel in range(len(eeg_values)):
        raw_data = eeg_values[channel]
        data = notch_filters_50[channel].apply(raw_data)
        data = notch_filters_60[channel].apply(data)
        data = sos_eeg_filters[channel].apply(data)
        curves[channel].setData(data)  # 更新曲线


async def scan_and_connect(loop):
    (addr, port) = await get_addr_port()
    client: libecap.ECapClient = libecap.ECapClient(addr, port)

    # 连接设备，监听消息
    parser = sdk.MessageParser("eeg-cap-device", sdk.MsgType.EEGCap)
    await client.start_data_stream(parser)

    # 获取设备信息
    # await client.get_device_info()

    # 读取配置
    # await client.get_eeg_config()
    # await client.get_imu_config()

    # fmt: off
    # 配置EEG/IMU
    # 测试信号
    # await client.set_eeg_config(libecap.EegSampleRate.SR_2000Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    # await client.set_eeg_config(libecap.EegSampleRate.SR_1000Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    # await client.set_eeg_config(libecap.EegSampleRate.SR_500Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    # await client.set_eeg_config(libecap.EegSampleRate.SR_250Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    # 正常信号
    await client.set_eeg_config(libecap.EegSampleRate.SR_250Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.NORMAL)
    # await client.set_imu_config(libecap.ImuSampleRate.SR_50Hz)
    await client.set_imu_config(libecap.ImuSampleRate.SR_100Hz)

    # 开始/停止EEG/IMU数据流
    # await client.stop_eeg_stream()
    # await client.stop_imu_stream()
    await client.start_eeg_stream()
    await client.start_imu_stream()


    try:
        loop.run_forever()  # 事件循环运行直到手动退出
    finally:
        loop.close()


# 创建主窗口
app = QApplication([])

win = pg.GraphicsLayoutWidget(show=True, title="32-Channel Dynamic Plot")
win.resize(2000, 1600)
win.setWindowTitle("32-Channel Dynamic Plot")

# 生成32个图表，每个图表表示一个通道
for i in range(num_channels):
    plot = win.addPlot(title=f"Channel {i + 1}")
    # plot.setYRange(-200, 200)  # 设置Y轴范围
    plot.enableAutoRange(axis=pg.ViewBox.YAxis)  # 设置Y轴范围动态调整
    plots.append(plot)
    curve = plot.plot(
        pen=pg.mkPen(color=(i * 8 % 255, i * 16 % 255, i * 32 % 255), width=1.5)
    )  # 设置曲线颜色
    curves.append(curve)
    if (i + 1) % 4 == 0:  # 每4个通道换一行
        win.nextRow()


def init_cfg():
    logger.info("Init cfg")
    set_cfg(eeg_buffer_length, imu_buffer_length, imp_window_length)  # 设置EEG数据缓冲区长度


def init_timer():
    logger.info("Init timer")
    # 定时器
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update_plot)
    timer.start(50)  # 每50ms更新一次
    return timer


if __name__ == "__main__":
    init_cfg()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    timer = init_timer()  # 需要持有timer
    asyncio.run(scan_and_connect(loop))
