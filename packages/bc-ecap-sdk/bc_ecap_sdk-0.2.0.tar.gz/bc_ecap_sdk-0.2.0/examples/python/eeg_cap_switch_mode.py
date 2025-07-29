import asyncio
import numpy as np

from utils import sdk, libecap, logger
from eeg_cap_model import (
    EEGData,
    IMUData,
    get_addr_port,
    set_env_noise_cfg,
    remove_env_noise,
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
bs_filters = [sdk.BandPassFilter(fs, low_cut, high_cut) for i in range(num_channels)]


def print_eeg_data():
    # 获取EEG数据
    fetch_num = 100  # 每次获取的数据点数, 超过缓冲区长度时，返回缓冲区中的所有数据
    clean = True  # 是否清空缓冲区
    eeg_buff = libecap.get_eeg_buffer(fetch_num, clean)
    logger.info(f"Got EEG buffer len={len(eeg_buff)}")
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
            logger.warning(f"eeg_seq_num={eeg_seq_num}, timestamp={timestamp}")
        if eeg_seq_num is not None or timestamp == 2:  # 第一个数据包的时间戳有误
            eeg_seq_num = timestamp

        channel_values = eeg_data.channel_values
        # 更新每个通道的数据
        for channel in range(len(channel_values)):
            # fmt: off
            eeg_values[channel] = np.roll(eeg_values[channel], -1)  # 数据向左滚动，腾出最后一个位置
            eeg_values[channel, -1] = channel_values[channel]  # 更新最新的数据值

    # 打印数据
    print_eeg_timestamps(eeg_data_arr)
    for channel in range(len(eeg_values)):
        raw_data = eeg_values[channel]
        data = remove_env_noise(raw_data, channel)
        # fmt: off
        data = libecap.apply_eeg_sosfiltfilt(raw_data, channel) # 使用sosfiltfilt滤波器, zero-phase滤波
        # data = bs_filters[channel].filter(data)
        # 打印通道1数据
        if channel == 0:
            # logger.debug(f"raw_data: {raw_data}")
            # logger.debug(f"data: {data}")
            logger.info(f"data len: {len(data)}")


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


async def app_start_leadoff(client):
    # 开启阻抗监测
    logger.info("APP开启阻抗监测")
    # 由于不知道设备状态，提前关闭数据传输
    await client.stop_eeg_stream()  # start_leadoff_check 切换检测芯片会先发送停止EEG数据传输, 此处不需要重复发送
    await asyncio.sleep(1)
    loop_check = False
    await client.start_leadoff_check(
        loop_check, libecap.LeadOffFreq.Ac31p2hz, libecap.LeadOffCurrent.Cur6nA
    )


async def app_stop_leadoff(client):
    # 结束阻抗监测
    logger.info("APP结束阻抗监测")
    await client.stop_leadoff_check()
    await asyncio.sleep(1)
    # 开启数据传输
    client.start_eeg_stream()


async def scan_and_connect():
    (addr, port) = await get_addr_port()
    client: libecap.ECapClient = libecap.ECapClient(addr, port)

    # 连接设备，监听消息
    parser = sdk.MessageParser("eeg-cap-device", sdk.MsgType.EEGCap)
    await client.start_data_stream(parser)

    sdk.set_imp_data_callback(
        lambda chip, values: logger.info(f"chip: {chip}, impendance values: {values}")
    )

    # 获取EEG配置
    msgId = await client.get_eeg_config()
    logger.warning(f"msgId: {msgId}")

    # 初始化计时器，用于控制leadoff检查的周期
    last_leadoff_check = 0
    leadoff_state = "stopped"  # 可能的状态: "stopped", "running"
    leadoff_start_time = 0

    # 合并两个循环，使用状态机控制leadoff检查
    while True:
        # 打印EEG数据
        print_eeg_data()

        # 当前时间
        now = asyncio.get_event_loop().time()

        # 状态机处理leadoff检查
        if leadoff_state == "stopped" and (
            now - last_leadoff_check >= 13
        ):  # 5秒停止 + 8秒运行
            # 开始新的leadoff检查
            await app_start_leadoff(client)
            leadoff_state = "running"
            leadoff_start_time = now
            last_leadoff_check = now
            logger.info("开始阻抗监测周期")
        elif leadoff_state == "running" and (now - leadoff_start_time >= 8):
            # 停止当前leadoff检查
            await app_stop_leadoff(client)
            leadoff_state = "stopped"
            logger.info("结束阻抗监测周期")

        # 短暂休眠，避免CPU使用率过高
        await asyncio.sleep(0.1)  # 100ms


def init_cfg():
    logger.info("Init cfg")
    set_env_noise_cfg(sdk.NoiseTypes.FIFTY, fs)  # 滤波器参数设置，去除50Hz电流干扰
    set_cfg(eeg_buffer_length, imu_buffer_length, imp_window_length)  # 设置EEG数据缓冲区长度
    sdk.set_msg_resp_callback(lambda _id, msg: logger.warning(f"Message response: {msg}"))


async def main():
    init_cfg()
    await scan_and_connect()
    while True:
        print_eeg_data()
        await asyncio.sleep(0.1)  # 100ms


if __name__ == "__main__":
    asyncio.run(main())
