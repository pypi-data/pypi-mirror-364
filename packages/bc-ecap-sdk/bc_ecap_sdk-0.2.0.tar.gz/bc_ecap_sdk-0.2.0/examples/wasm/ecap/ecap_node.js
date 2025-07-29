const os = require("os");
const isWindows = os.platform() === "win32";
// const isMac = os.platform() === "darwin";
// const isLinux = os.platform() === "linux";
const node_sdk = isWindows
  ? require("../pkg/win.node")
  : require("../pkg/mac.node");

// 创建导出对象
function export_symbols() {
  return node_sdk;
}

// CommonJS
if (typeof module !== "undefined" && module.exports) {
  // module.exports = async function () {
  //   await initWasm();
  //   return export_symbols();
  // };
  module.exports = export_symbols();
}
