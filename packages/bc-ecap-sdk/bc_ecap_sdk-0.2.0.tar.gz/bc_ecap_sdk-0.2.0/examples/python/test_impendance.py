# import asyncio
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


def compute_test():
    file_path = "logs/eeg_leadoff_chip_1.log"
    last_timestamp = None
    with open(file_path, "r") as f:
        for line in f:
            raw_data = [float(x) for x in line[1:-2].strip().split(",")]
            # chip = raw_data[0]

            timestamp = raw_data[1]
            if last_timestamp is not None and timestamp != last_timestamp + 1:
                logger.error(
                    f"timestamp: {timestamp}, last_timestamp: {last_timestamp}"
                )
            # else:
            # logger.info(f"timestamp: {timestamp}")

            last_timestamp = timestamp

        # data = np.array(raw_data[2:10], dtype=np.float64)
        # uVrms = np.sqrt(np.mean(np.array(data, dtype=np.float64) ** 2))
        # impedance = calculate_impedance(data)
        # logger.info(f"raw uVrms: {uVrms}, impedance: {impedance}KΩ\n")

        # data = bs_filter_50_3.filter(data)
        # data = imp_filter_3.filter(data)
        # logger.info(data[:3])
        # uVrms = np.sqrt(np.mean(np.array(data, dtype=np.float64) ** 2))
        # impedance = calculate_impedance(data)
        # logger.info(f"filter uVrms: {uVrms}, impedance: {impedance}KΩ\n")


if __name__ == "__main__":
    compute_test()
