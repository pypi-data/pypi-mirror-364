// import path from "path";
// import { fileURLToPath } from "url";
// import fileSystem from "fs";
const fs = require("fs");
const path = require("path");
// const { fileURLToPath } = require("url");
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

// read from file, eeg_cap_sample_eeg.log
// console.log(path.resolve(__dirname, "eeg_cap_sample_eeg.log"));
// const f = fs.readFileSync(
//   path.resolve(__dirname, "eeg_cap_sample_eeg.log")
// );
const f = fs.readFileSync(path.resolve(__dirname, "eeg-sample.log"));
// const lines = f.toString().split("\n");
// console.log(`lines, len=${lines.length}`);
// for (let i = 0; i < lines.length; i++) {
//   const line = lines[i];
//   if (line.startsWith("0x42, 0x52, 0x4e, 0x43, 0x02, 0x0b, 0xee, 0x00")) {
//     const data = line.split(", ");
//     if (data.length !== 251) console.log("line", i, data.length);
//   }
// }

const lines = f.toString().split("\n").slice(1, -1);
const cleanLine = lines[0]
  .trim()
  .replace(/，/g, ",") // 替换中文逗号
  .replace(/, /g, ",") // 移除逗号后的空格
  .trim();
console.log("cleanLine", cleanLine);
const parts = cleanLine.split("[");
console.log(parts[0]);
console.log(parts[1]);
const values = parts[1]
  .replace("]", "")
  .split(",")
  .map((v) => parseFloat(v.trim()));
console.log("values", values);
console.log("values.length", values.length);
