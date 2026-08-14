#!/usr/bin/env bash
# 构建脚本 — 在 Linux 上打包 Piggy Meadow 为独立可执行文件。
#
# 产物: dist/PiggyMeadow (通用 Linux x86-64 ELF, 无需安装 Python)
#
# 用法: ./build-linux.sh

set -euo pipefail

cd "$(dirname "$0")"

# 1. 准备虚拟环境 (若不存在)
if [ ! -d venv ]; then
    echo "==> 创建虚拟环境 venv ..."
    if python3 -m venv venv 2>/dev/null; then
        echo "    使用 python3 -m venv"
    else
        echo "    ensurepip 不可用, 改用 virtualenv ..."
        pip3 install --user --break-system-packages virtualenv >/dev/null 2>&1 || \
            pip3 install --user virtualenv >/dev/null
        ~/.local/bin/virtualenv venv
    fi
fi

# 2. 安装依赖
echo "==> 安装依赖 (pygame / Pillow / PyInstaller) ..."
./venv/bin/pip install --quiet pygame Pillow pyinstaller

# 3. 处理资源 (生成 processed/ 目录)
echo "==> 处理资源 ..."
./venv/bin/python process_assets.py >/dev/null

# 4. 打包
echo "==> PyInstaller 打包 ..."
./venv/bin/pyinstaller --onefile --windowed \
    --name PiggyMeadow \
    --add-data "processed:processed" \
    main.py >/dev/null 2>&1

# 5. 清理中间产物
rm -rf build
rm -f PiggyMeadow.spec

echo ""
echo "构建完成: $(pwd)/dist/PiggyMeadow"
ls -lh dist/PiggyMeadow | awk '{print "  大小: " $5}'
