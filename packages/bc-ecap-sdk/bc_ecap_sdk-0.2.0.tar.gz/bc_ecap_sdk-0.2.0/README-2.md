# BrainCo Proto Message SDK

```shell
cargo tree
cargo b --lib 
cargo test eeg_cap_parser_test -- --show-output -- --features="eeg-cap, tracing-log"
cargo run --no-default-features --example tcp-client --features="eeg-cap, examples"
cargo run --no-default-features --example sci-test --features="eeg-cap, examples"
cargo run --no-default-features --example fft-test --features="eeg-cap, examples"
cargo run --no-default-features --example ble-test --features="eeg-cap, examples"
cargo run --no-default-features --example ecap-msg-test --features="eeg-cap, examples"
cargo run --no-default-features --example ecap-imp-offline --features="eeg-cap, examples" # offline compute imp
cargo run --no-default-features --example ecap-tcp --features="eeg-cap, examples" # scan and connect by tcp

# pip install maturin
# maturin init --bindings pyo3

# NOTE: use feature "python3" in Cargo.toml
maturin dev
https://pypi.org/project/bc-ecap-sdk/

export PYTHON_SYS_EXECUTABLE=$(which python3)
cargo run --no-default-features --example pyo3
sh scripts/test_python.sh

# window conda
conda env list
conda activate py310

docker commit bc_ecap_sdk_x86_64 bc_ecap_sdk_image_amd64
docker stop bc_ecap_sdk_x86_64
docker rm bc_ecap_sdk_x86_64

# 使用Docker, ubuntu-20 x86_64 环境
docker run -dit --platform linux/x86_64 \
  -v ~/projects/eeg-32ch-sdk:/bc_ecap_sdk \
  -w /bc_ecap_sdk \
  --name ecap_sdk_x86_64 \
  bc_ecap_sdk_image_amd64 bash
# 进入实例
docker exec -it ecap_sdk_x86_64 bash   

# 使用Docker, ubuntu-20 arm64 环境
docker run -dit --platform linux/arm64 \
  -v ~/projects/eeg-32ch-sdk:/bc_ecap_sdk \
  -w /bc_ecap_sdk \
  --name ecap_sdk_arm64 \
  bc_ecap_sdk_image_arm64 bash
# 进入实例
docker exec -it ecap_sdk_arm64 bash  

# 使用Docker, ubuntu-22 arm64 环境
docker run -dit --platform linux/arm64 \
  -v ~/projects/eeg-32ch-sdk:/bc_ecap_sdk \
  -w /bc_ecap_sdk \
  --name bc_ecap_sdk_arm64_22 \
  ubuntu:22.04 bash
# 进入实例
docker exec -it bc_ecap_sdk_arm64_22 bash 

uname -m
sudo apt update
sudo apt-get install -y curl
sudo apt-get install -y curl libssl-dev protobuf-compiler libdbus-1-dev pkg-config

# 安装rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

pip install bc-ecap-sdk --index-url https://pypi.org/simple/

curl -O https://app.brainco.cn/universal/bc-ecap-sdk/libs/v0.3.6/bc_ecap_sdk-0.3.6-cp38-cp38-manylinux_2_31_aarch64.whl
pip install --no-index --no-deps --force-reinstall ./bc_ecap_sdk-0.3.6-cp38-cp38-manylinux_2_31_aarch64.whl -v

cat /etc/os-release

# 查看 glibc 版本
ldd --version

# 或者
/lib/x86_64-linux-gnu/libc.so.6
# 在某些系统上路径可能是
/lib64/libc.so.6

# 查看更详细的系统信息
ldconfig -p | grep libc

# 查看动态链接库路径
ldconfig -v | grep libc

# 检查特定程序依赖的 glibc 版本
objdump -T /bin/ls | grep GLIBC

# 在容器环境中检查 glibc 版本对 wheel 文件的兼容性
auditwheel show ./bc_ecap_sdk-0.3.6-cp38-cp38-manylinux_2_31_aarch64.whl

# 下载 Miniconda 安装脚本
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh

# 如果是 arm64 架构，使用：
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
chmod +x Miniconda3-latest-Linux-aarch64.sh
./Miniconda3-latest-Linux-aarch64.sh

# 更新软件包列表
apt update

# 安装依赖
sudo apt install -y wget

# 添加 Conda 的软件源
curl -O https://repo.anaconda.com/archive/Anaconda-2023.09-0-Linux-x86_64.sh
bash anaconda.sh

eval "$(/root/miniconda3/bin/conda shell.bash hook)" 
```

## TODO
- [ ] EEG+Sync项目支持, LSL架构，时间同步
- [ ] 滤波算法，sos, https://docs.rs/butterworth/latest/butterworth/
- py filter, stub-gen, save imp data, load imp data