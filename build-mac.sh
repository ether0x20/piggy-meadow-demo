#!/usr/bin/env bash
# 构建脚本 — 在 macOS 上打包 Piggy Meadow 为 .app 应用。
#
# 产物: dist/PiggyMeadow.app (独立应用, 无需安装 Python)
#
# 用法: ./build-mac.sh
#
# 注意: 可选图标 processed/icon.icns (macOS 应用图标格式),
#       若不存在则跳过图标, 不影响构建。

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

# 3. 打包 (macOS 图标需 .icns 格式, 缺失则跳过)
ICON_ARG=""
if [ -f "processed/icon.icns" ]; then
    ICON_ARG="--icon=processed/icon.icns"
fi

echo "==> PyInstaller 打包 ..."
./venv/bin/pyinstaller --onefile --windowed \
    $ICON_ARG \
    --name PiggyMeadow \
    --add-data "processed:processed" \
    main.py >/dev/null 2>&1

# 4. 清理中间产物
rm -rf build
rm -f PiggyMeadow.spec

echo ""
echo "构建完成: $(pwd)/dist/PiggyMeadow.app"
du -sh dist/PiggyMeadow.app | awk '{print "  大小: " $1}'
