import asyncio
import logging
import numpy as np

from utils import sdk, libecap, logger
from eeg_cap_model import (
    EEGData,
    IMUData,
    get_addr_port,
    set_cfg,
)

# EEG数据
fs = 250  # 采样频率
num_channels = 32  # 通道数
eeg_buffer_length = 2000  # 默认缓冲区长度，注意采样率应该小于此数
eeg_seq_num = None  # EEG数据包序号
eeg_values = np.zeros((num_channels, eeg_buffer_length))  # 32通道的EEG数据

# 滤波器参数设置
order = 4  # 滤波器阶数
low_cut = 2  # 低通滤波截止频率
high_cut = 45  # 高通滤波截止频率
# bs_filters = [sdk.BandPassFilter(fs, low_cut, high_cut) for i in range(num_channels)]

q = 30  # 品质因数
notch_filters_50 = [sdk.NotchFilter(50, fs, q) for i in range(num_channels)]
notch_filters_60 = [sdk.NotchFilter(60, fs, q) for i in range(num_channels)]
sos_eeg_filters = [sdk.SosFilter.create_band_pass(order, fs, 2, 45) for i in range(num_channels)]

imu_buffer_length = 2000  # IMU缓冲区长度, 默认2000个数据点

imp_window_length = 250  # 阻抗检测窗口长度, 默认250组

def print_imu_data():
    fetch_num = 2000  # 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
    clean = True  # 是否清空缓冲区
    imu_buff = libecap.get_imu_buffer(fetch_num, clean)
    imu_result = []
    for i in range(len(imu_buff)):
        imu_result.append(IMUData.from_data(imu_buff[i]))

    # result_str = "\n\t".join(map(str, imu_result))
    # logger.info(f"Got IMU buffer result:\n\t{result_str}")


def print_eeg_data():
    # 获取EEG数据
    fetch_num = 2000  # 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
    clean = True  # 是否清空缓冲区
    eeg_buff = libecap.get_eeg_buffer(fetch_num, clean)
    # logger.info(f"Got EEG buffer len={len(eeg_buff)}")
    if len(eeg_buff) == 0:
        return

    eeg_data_arr = []
    for row in eeg_buff:
        eeg_data = EEGData.from_data(row)
        eeg_data_arr.append(eeg_data)

        # 检查数据包序号
        timestamp = eeg_data.timestamp
        global eeg_seq_num
        # logger.info(f"timestamp={timestamp}")
        if eeg_seq_num is not None and timestamp != eeg_seq_num + 1:
            logger.warning(f"EEG SeqNum not continuous, {eeg_seq_num} => {timestamp}")
        if eeg_seq_num is not None or timestamp == 2:  # 第一个数据包的时间戳有误
            eeg_seq_num = timestamp

        channel_values = eeg_data.channel_values
        # 更新每个通道的数据
        for channel in range(len(channel_values)):
            # fmt: off
            eeg_values[channel] = np.roll(eeg_values[channel], -1)  # 数据向左滚动，腾出最后一个位置
            eeg_values[channel, -1] = channel_values[channel]  # 更新最新的数据值

    # 打印数据
    # print_eeg_timestamps(eeg_data_arr)
    for channel in range(len(eeg_values)):
        raw_data = eeg_values[channel]
        data = notch_filters_50[channel].apply(raw_data)
        data = notch_filters_60[channel].apply(data)
        data = sos_eeg_filters[channel].apply(data)
        # 打印通道1数据
        # if channel == 0:
        #     # logger.info(f"raw_data: {raw_data}")
        #     # logger.info(f"data: {data}")
        #     logger.info(f"data len: {len(data)}")


def print_eeg_timestamps(data):
    if len(data) <= 6:
        for item in data:
            logger.info(f"{item}")
        return

    for item in data[:3]:
        logger.info(f"{item}")
    logger.info("...")
    for item in data[-3:]:
        logger.info(f"{item}")


async def scan_and_connect():
    (addr, port) = await get_addr_port()
    client: libecap.ECapClient = libecap.ECapClient(addr, port)

    # 连接设备，监听消息
    parser = sdk.MessageParser("eeg-cap-device", sdk.MsgType.EEGCap)
    await client.start_data_stream(parser)

    # await client.set_eeg_config(libecap.EegSampleRate.SR_500Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    # await client.set_imu_config(libecap.ImuSampleRate.SR_50Hz)

    # FIXME: 1000Hz 采样率下，有丢包，待优化解决
    # await client.set_eeg_config(libecap.EegSampleRate.SR_1000Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    await client.set_eeg_config(libecap.EegSampleRate.SR_500Hz, libecap.EegSignalGain.GAIN_6, libecap.EegSignalSource.TEST_SIGNAL)
    # await client.set_imu_config(libecap.ImuSampleRate.SR_100Hz)

    # 获取EEG配置
    msgId = await client.get_eeg_config()
    logger.warning(f"msgId: {msgId}")

    # 开始EEG数据流
    msgId = await client.start_eeg_stream()
    logger.warning(f"msgId: {msgId}")

    # 开始IMU数据流
    msgId = await client.start_imu_stream()
    logger.warning(f"msgId: {msgId}")


def init_cfg():
    """初始化配置"""
    logger.info("Init cfg")
    set_cfg(eeg_buffer_length, imu_buffer_length, imp_window_length)  # 设置EEG数据缓冲区长度
    sdk.set_msg_resp_callback(
        lambda _id, msg: logger.warning(f"Message response: {msg}")
    )


async def main():
    init_cfg()
    await scan_and_connect()
    while True:
        print_eeg_data()
        print_imu_data()
        await asyncio.sleep(1.0)  # 1000ms


if __name__ == "__main__":
    asyncio.run(main())
