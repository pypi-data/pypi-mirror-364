#!/bin/bash
set -e

# conda
eval "$(/root/miniconda3/bin/conda shell.bash hook)"
conda env list
conda activate py310

# 下载 Miniconda 安装脚本
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh

# 如果是 arm64 架构，使用：
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
chmod +x Miniconda3-latest-Linux-aarch64.sh
./Miniconda3-latest-Linux-aarch64.sh

# 添加 Conda 的软件源
curl -O https://repo.anaconda.com/archive/Anaconda-2023.09-0-Linux-x86_64.sh
bash anaconda.sh

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

sudo apt update
sudo apt-get install -y wget curl libssl-dev protobuf-compiler libdbus-1-dev pkg-config

# 安装rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

curl -O https://app.brainco.cn/universal/bc-ecap-sdk/libs/v0.3.6/bc_ecap_sdk-0.3.6-cp38-cp38-manylinux_2_31_aarch64.whl
pip install bc-ecap-sdk --index-url https://pypi.org/simple/
pip install --no-index --no-deps --force-reinstall ./bc_ecap_sdk-0.3.6-cp38-cp38-manylinux_2_31_aarch64.whl -v
# 在容器环境中检查 glibc 版本对 wheel 文件的兼容性
auditwheel show ./bc_ecap_sdk-0.3.6-cp38-cp38-manylinux_2_31_aarch64.whl

uname -m
uname -a

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
