# 创建 Python环境
# conda create -n py38 python=3.8
# conda create -n py39 python=3.9
# conda create -n py310 python=3.10
# conda create -n py311 python=3.11
# conda create -n py312 python=3.12

# 激活 Python环境
# conda activate py38
# conda activate py39
# conda activate py310
# conda activate py311
# conda activate py312
# conda activate base

# 安装 maturin 和 patchelf
# pip install maturin patchelf

# code ~/.zprofile
cargo fmt
maturin publish --no-default-features --features "python eeg-cap ble" --username $MATURIN_USERNAME --password $MATURIN_PASSWORD
