#!/usr/bin/env bash
# Breathing Pet 启动脚本（macOS / Linux）

cd "$(dirname "$0")"

# 优先用 python3，回退到 python
if command -v python3 &> /dev/null; then
    python3 breathing_pet.py
elif command -v python &> /dev/null; then
    python breathing_pet.py
else
    echo "错误：找不到 Python，请先安装 Python 3.8+"
    echo "macOS:  brew install python"
    echo "Linux:  sudo apt install python3 python3-tk  (或对应包管理器)"
    exit 1
fi
