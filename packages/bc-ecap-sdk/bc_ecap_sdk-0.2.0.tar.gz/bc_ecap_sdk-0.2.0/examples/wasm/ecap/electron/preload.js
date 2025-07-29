const { BandStopFilter, BandPassFilter, NotchFilter } = require("../filter.js");
const Chart = require("chart.js/auto");

// EEG数据参数
const fs = 250; // 采样频率
const order = 4; // 滤波器阶数

// 创建SOS滤波器
// const notchFilter50 = new BandStopFilter(order, fs, 49, 51);
// const notchFilter60 = new BandStopFilter(order, fs, 59, 61);
const Q = 30; // 品质因子
const notchFilter50 = new NotchFilter(50, fs, Q);
const notchFilter60 = new NotchFilter(60, fs, Q);
const sosEegFilter = new BandPassFilter(order, fs, 2, 45);

// 数据存储
let dataEeg = new Float32Array(0);
let eegIndex = 0;
const EEG_WIN_LEN = 1250; // 250Hz * 5s = 1250 samples

// 辅助函数：合并Float32Array
function concatFloat32Arrays(arr1, arr2) {
  const result = new Float32Array(arr1.length + arr2.length);
  result.set(arr1, 0);
  result.set(arr2, arr1.length);
  return result;
}

// 创建图表
function createCharts() {
  // EEG时域图
  const eegCtx = document.getElementById("eegChart").getContext("2d");
  const eegChart = new Chart(eegCtx, {
    type: "line",
    data: {
      labels: Array.from({ length: EEG_WIN_LEN }, (_, i) => i),
      datasets: [
        {
          label: "EEG Signal (uV)",
          data: [],
          borderColor: "rgb(75, 192, 192)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          borderWidth: 1,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Sample Points",
          },
        },
        y: {
          title: {
            display: true,
            text: "Amplitude (uV)",
          },
        },
      },
      animation: {
        duration: 0,
      },
    },
  });

  // FFT频域图
  const fftCtx = document.getElementById("fftChart").getContext("2d");
  const fftChart = new Chart(fftCtx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "FFT Magnitude (uV/Hz)",
          data: [],
          borderColor: "rgb(255, 99, 132)",
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          borderWidth: 1,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          title: {
            display: true,
            text: "Frequency (Hz)",
          },
        },
        y: {
          title: {
            display: true,
            text: "Magnitude (uV/Hz)",
          },
          min: 0,
          max: 1,
        },
      },
      animation: {
        duration: 0,
      },
    },
  });

  return { eegChart, fftChart };
}

// FFT计算函数
function computeFFT(data) {
  const N = data.length;
  const frequencies = [];
  const magnitudes = [];

  for (let k = 0; k < N / 2; k++) {
    frequencies.push((k * fs) / N);

    let real = 0;
    let imag = 0;
    for (let n = 0; n < N; n++) {
      const angle = (-2 * Math.PI * k * n) / N;
      real += data[n] * Math.cos(angle);
      imag += data[n] * Math.sin(angle);
    }

    magnitudes.push(Math.sqrt(real * real + imag * imag) / N);
  }

  return { frequencies, magnitudes };
}

// 更新图表
function updatePlots(eegChart, fftChart) {
  if (eegIndex * 50 >= dataEeg.length) {
    eegIndex = 0;
  }

  const index = eegIndex * 50;
  const values = dataEeg.slice(index, index + EEG_WIN_LEN);
  // console.log(
  //   `Updating plots: index=${eegIndex}, values[0]=${values[0]},  length=${values.length}`
  // );

  if (values.length < EEG_WIN_LEN) {
    return;
  }

  // 更新EEG图
  eegChart.data.datasets[0].data = values;
  eegChart.update("activate");

  // 计算并更新FFT图
  const fftResult = computeFFT(values);
  fftChart.data.labels = fftResult.frequencies;
  fftChart.data.datasets[0].data = fftResult.magnitudes;
  fftChart.update("activate");

  eegIndex++;
  // console.log(
  //   `Updated plots: index=${eegIndex}, ${values[0]}...${
  //     values[values.length - 1]
  //   }`
  // );
}

// 验证数据格式
function isValidData(item) {
  if (Array.isArray(item) && item.length === 3) {
    const [ts, idx, values] = item;
    return (
      typeof ts === "number" &&
      typeof idx === "number" &&
      Array.isArray(values) &&
      values.every((v) => typeof v === "number")
    );
  }
  return false;
}

// 读取EEG数据
async function readEegData() {
  try {
    const response = await fetch("eeg-sample.log");
    const text = await response.text();
    const lines = text.split("\n").slice(1, -1);

    console.log(`Processing ${lines.length} lines`);

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const cleanLine = line
          .trim()
          .replace(/，/g, ",") // 替换中文逗号
          .replace(/, /g, ",") // 移除逗号后的空格
          .trim();
        // console.log("cleanLine", cleanLine);
        const parts = cleanLine.split("[");
        // console.log(parts[0]);
        // console.log(parts[1]);
        const values = parts[1]
          .replace("]", "")
          .split(",")
          .map((v) => parseFloat(v.trim()));
        // console.log("values", values);
        // console.log("values.length", values.length);
        if (values.length !== 50) {
          console.warn(`Unexpected number of values: ${values.length}`);
          continue;
        }

        // 转换为Float32Array
        const float32Values = new Float32Array(values);

        // 应用滤波器
        let filteredValues = notchFilter50.apply(float32Values);
        filteredValues = notchFilter60.apply(filteredValues);
        filteredValues = sosEegFilter.apply(filteredValues);

        // 合并到dataEeg Float32Array中
        dataEeg = concatFloat32Arrays(dataEeg, filteredValues);
      } catch (e) {
        console.warn(`Error parsing line: ${line}`, e);
      }
    }

    console.log(`Total data points: ${dataEeg.length}`);
  } catch (error) {
    console.error("Error reading EEG data:", error);
  }
}

// 初始化定时器
function initTimer(eegChart, fftChart) {
  console.log("Init timer");
  const timer = setInterval(() => {
    updatePlots(eegChart, fftChart);
  }, 200);
  return timer;
}

// 主函数
async function main() {
  const { eegChart, fftChart } = createCharts();
  await readEegData();
  const timer = initTimer(eegChart, fftChart);

  document.getElementById("stopButton").addEventListener("click", () => {
    clearInterval(timer);
    console.log("Timer stopped");
  });
}

// 启动应用
document.addEventListener("DOMContentLoaded", main);
