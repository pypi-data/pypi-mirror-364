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
SRC="examples/python"
DST_ROOT="$HOME/projects/eeg-32ch-example"
DST="$DST_ROOT/python"

echo_y "Source directory: $SRC"
echo_y "Destination directory: $DST"

# cargo b --target wasm32-unknown-unknown --release
# wasm-bindgen --target nodejs --out-dir ./pkg ../target/wasm32-unknown-unknown/release/bc_ecap_sdk.wasm
# wasm-pack build --release --target nodejs
# rsync -av ./pkg/ $DST/pkg --exclude README.md

# 更新 requirements.txt 中的版本号
CARGO_PKG_VERSION=$(grep '^version =' Cargo.toml | awk -F'"' '{print $2}')
echo_y "Cargo.toml version: $CARGO_PKG_VERSION"
sed -i '' "s/bc-ecap-sdk==[0-9]*\.[0-9]*\.[0-9]*/bc-ecap-sdk==$CARGO_PKG_VERSION/g" $SRC/requirements.txt
echo_y "requirements.txt updated"

sed -i '' "s/v[0-9]*\.[0-9]*\.[0-9]\/mac.node/v$CARGO_PKG_VERSION\/mac.node/g" scripts/download-node.sh
sed -i '' "s/v[0-9]*\.[0-9]*\.[0-9]\/win.node/v$CARGO_PKG_VERSION\/win.node/g" scripts/download-node.sh
sed -i '' "s/v[0-9]*\.[0-9]*\.[0-9]\/mac.node/v$CARGO_PKG_VERSION\/mac.node/g" examples/wasm/ecap/package.json
sed -i '' "s/v[0-9]*\.[0-9]*\.[0-9]\/win.node/v$CARGO_PKG_VERSION\/win.node/g" examples/wasm/ecap/package.json
echo_y "download-node.sh updated"
# exit 0

cp -vf $SRC/requirements.txt $DST/requirements.txt
cp -vf $SRC/logger.py $DST/logger.py
cp -vf $SRC/utils.py $DST/utils.py
cp -vf $SRC/eeg_cap_*.py $DST/

SRC="examples/wasm"
DST="$DST_ROOT/nodejs"

echo_y "Source directory: $SRC"
echo_y "Destination directory: $DST"
cp -f scripts/download-node.sh $DST/eeg-cap/download-node.sh
rsync -av $SRC/pkg/ $DST/pkg --exclude README.md --exclude bc_ecap_sdk_bg.wasm.d.ts --exclude bc_ecap_sdk_bg.wasm --exclude bc_ecap_sdk.d.ts --exclude bc_ecap_sdk.js

# cp eeg-cap to example
rsync -av $SRC/ecap/ $DST/eeg-cap --exclude node_modules --exclude package-dev.json --exclude test.js --exclude test_tcp_con.js
