import numpy as np
import matplotlib.pyplot as plt

# from filters import BandPassFilter, BandStopFilter
from filters_sdk import BWBandPassFilter, BWBandStopFilter

from utils import logger

# EEG数据
fs = 250  # 采样频率
num_channels = 32  # 通道数

# 滤波器参数设置
order = 4  # 滤波器阶数

# bs_filter_50 = BandStopFilter(4, fs, 49, 51)
# bs_filter_60 = BandStopFilter(4, fs, 59, 61)
# imp_filter = BandPassFilter(4, fs, 30, 32)

bs_filter_50_3 = BWBandStopFilter(order=4, sample_rate=250, fl=49, fu=51)
bs_filter_60_3 = BWBandStopFilter(order=4, sample_rate=250, fl=59, fu=61)
imp_filter_3 = BWBandPassFilter(order=4, sample_rate=250, fl=30, fu=32)


def calculate_impedance(filtered_array):
    input_current_nA = 6  # nA
    Vrms = np.sqrt(np.mean(filtered_array**2)) * (10**-6)  # V
    impedance = Vrms * np.sqrt(2) / (input_current_nA * 10**-9)  # Ω
    impedance = (impedance / 1000) - 10  # IMPEDANCE_INPUT_RESISTANCE  # KΩ
    # print(f"impedance: {impedance} KΩ")
    return impedance


def draw_plot(data):
    # Plot the data
    plt.plot(data)

    # Add labels and title
    plt.title("Simple Plot")
    plt.xlabel("Index")
    plt.ylabel("Value")

    # Show the plot
    plt.show()


def read_chip_1_data():
    channel_values = []
    # file_path = "logs/eeg_leadoff_chip_1.log"
    file_path = "logs/eeg_leadoff_chip_1 copy.log"
    with open(file_path, "r") as f:
        for line in f:
            raw_data = [float(x) for x in line[1:-2].strip().split(",")]
            chip = raw_data[0]
            if chip != 1.0:
                continue
            channel_values.append(raw_data)

    channel_values = sorted(channel_values, key=lambda x: x[1])

    # 分割数据，每250个数据为一个段
    segment_values = []
    current_segment = []
    for data in channel_values:
        if len(current_segment) < 250:
            current_segment.append(data)
        else:
            segment_values.append(current_segment)
            current_segment = []
    return segment_values


def read_chip_all_data():
    segment_values = []
    current_segment = []
    current_chip = None
    file_path = "logs/eeg_leadoff_chip_all.log"

    with open(file_path, "r") as f:
        for line in f:
            raw_data = [float(x) for x in line[1:-2].strip().split(",")]
            chip = raw_data[0]
            if current_chip is None or chip != current_chip:
                current_chip = chip
                if current_segment:
                    # logger.info(f"current_segment length: {len(current_segment)}")
                    segment_values.append(np.array(current_segment))
                current_segment = []

            current_segment.append(raw_data)

        # 添加最后一个段
        if current_segment and current_chip == 1.0:
            segment_values.append(np.array(current_segment))
    return segment_values


if __name__ == "__main__":
    segment_values = read_chip_all_data()
    # segment_values = read_chip_1_data()

    counter = 0
    for segment in segment_values:
        chip = int(segment[0][0])
        logger.info(f"chip: {chip}, segment length: {len(segment)}")
        if chip != 1:
            continue

        if len(segment) < 250:
            logger.warning(f"segment length: {len(segment)}")
            continue

        counter += 1

        # 先对数据进行排序, 用timestamp排序，从小到大
        segment = sorted(segment, key=lambda x: x[1])

        # 取通道0数据，前250个数据, 通道0数据在第3行，第1行是chip，第2行是timestamp
        # timestamp_arr = np.array(segment[:250]).T[1]
        # logger.info(
        #     f"[{counter}] timestamp_arr: {len(timestamp_arr)}, {timestamp_arr[:250]}"
        # )
        channel_0_data = np.array(segment[:250], dtype=np.float64).T[2]
        logger.info(
            f"[{counter}] channel_0_data: {len(channel_0_data)}, {channel_0_data[:3]}"
        )

        data = channel_0_data
        # 计算
        # data = bs_filter_50_3.filter(data)
        # data = bs_filter_60_3.filter(data)
        data = imp_filter_3.filter(data)
        logger.info(f"[{counter}] fil_data: {data[:3]}")
        uVrms = np.sqrt(np.mean(np.array(data) ** 2))
        impedance = calculate_impedance(data)
        logger.info(f"[{counter}] uVrms: {uVrms}, impedance: {impedance}KΩ\n")
        if counter == 3:
            draw_plot(channel_0_data)
            break
