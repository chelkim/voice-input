#!/bin/bash
#
# 语音输入卸载脚本
#

set -e

echo "============================================"
echo "  语音输入系统卸载"
echo "============================================"
echo ""

# 停止守护进程
echo "停止守护进程..."
pkill -f voice-daemon.py 2>/dev/null || true

# 移除 autostart
echo "移除开机自启..."
rm -f "$HOME/.config/autostart/voice-input.desktop"
rm -f "$HOME/.voice-input/voice-input.desktop"

echo ""
echo "============================================"
echo "  卸载完成"
echo "============================================"
echo ""
echo "注意: ~/.voice-input 目录需要手动删除"
echo "如需完全清理，运行: rm -rf ~/.voice-input"
