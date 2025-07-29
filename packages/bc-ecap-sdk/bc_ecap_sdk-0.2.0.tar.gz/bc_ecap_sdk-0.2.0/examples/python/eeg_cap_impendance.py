import asyncio
from utils import sdk, logger, libecap
from eeg_cap_model import get_addr_port

# EEG数据
fs = 250  # 采样频率
num_channels = 32  # 通道数


async def scan_and_connect():
    (addr, port) = await get_addr_port()
    client: libecap.ECapClient = libecap.ECapClient(addr, port)

    # 连接设备，监听消息
    parser = sdk.MessageParser("eeg-cap-device", sdk.MsgType.EEGCap)
    await client.start_data_stream(parser)

    # 开始检测阻抗
    await start_leadoff_check(client)


# 开始阻抗检测，与正常EEG模式互斥，注意：从阻抗检测模式切换到正常EEG模式, 需要先停止阻抗检测
async def start_leadoff_check(client):
    # fmt: off
    # 设置阻抗检测结果回调
    sdk.set_imp_data_callback(lambda chip, values: logger.info(f"chip: {chip}, impendance values: {values}"))
    # 是否循环检测芯片1~4
    loop_check = True
    # loop_check = False
    await client.start_leadoff_check(loop_check, libecap.LeadOffFreq.Ac31p2hz, libecap.LeadOffCurrent.Cur6nA)


# 停止阻抗检测，与正常EEG模式互斥，注意：从阻抗检测模式切换到正常EEG模式, 需要先停止阻抗检测
async def stop_leadoff_check(client):
    await client.stop_leadoff_check()


def init_cfg():
    logger.info("Init cfg")
    sdk.set_env_noise_cfg(sdk.NoiseTypes.FIFTY, fs)  # 滤波器参数设置，去除50Hz电流干扰
    sdk.set_msg_resp_callback(lambda _id, msg: logger.warning(f"Message response: {msg}"))


async def main():
    init_cfg()
    await scan_and_connect()
    await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
