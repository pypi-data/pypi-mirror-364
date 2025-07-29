#!/bin/bash
set -e

# colorful echo functions
function echo_y() { echo -e "\033[1;33m$@\033[0m"; } # yellow
function echo_r() { echo -e "\033[0;31m$@\033[0m"; } # red

# 获取脚本所在目录
SCRIPT_DIR="$(dirname $0)"

# 切换到脚本所在目录（如果当前目录不是脚本所在目录）
[ "$(pwd)" != "$SCRIPT_DIR" ] && cd "$SCRIPT_DIR"
echo_y "current dir: $(pwd)"

cd ..

SRC="index.node"
DST="examples/wasm/pkg"
mkdir -p $DST

# if windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
  cp -f $SRC $DST/win.node
elif [[ "$OSTYPE" == "darwin"* ]]; then
  rm -f $DST/mac.node
  cp -f $SRC $DST/mac.node
# elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
#   cp -f $SRC $DST/linux.node
else
  echo_r "Unsupported OS: $OSTYPE"
  exit 1
fi

echo_y "Copy $SRC to $DST"
echo_y "Copy done"

rm -f $SRC
echo_y "Remove $SRC"
echo_y "Done"
