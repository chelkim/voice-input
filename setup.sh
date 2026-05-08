#!/bin/bash
#
# Voice Input 安装脚本
# 将 ~/.voice-input 目录配置为开机自启
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv-voice"
VENV_PYTHON="$VENV_DIR/bin/python3"
DAEMON_SCRIPT="$SCRIPT_DIR/src/daemon.py"
AUTOSTART_DESKTOP="$SCRIPT_DIR/voice-input.desktop"
AUTOSTART_LINK="$HOME/.config/autostart/voice-input.desktop"
MODEL_DIR="$SCRIPT_DIR/models"

echo "============================================"
echo "  语音输入系统安装脚本"
echo "============================================"
echo ""

# 检查 daemon 脚本是否存在
if [ ! -f "$DAEMON_SCRIPT" ]; then
    echo "✗ 错误: 找不到 voice-daemon.py"
    exit 1
fi

# ========== 1. 创建 Python 虚拟环境 ==========
echo ""
echo "检查 Python 环境..."

if [ ! -f "$VENV_PYTHON" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✓ 虚拟环境已创建"
else
    echo "✓ 虚拟环境已存在"
fi

# ========== 2. 安装 Python 依赖 ==========
echo ""
echo "安装 Python 依赖..."
$VENV_PYTHON -m pip install --upgrade pip -q
$VENV_PYTHON -m pip install sherpa-onnx pynput sounddevice soundfile evdev numpy -q
echo "✓ Python 依赖安装完成"

# ========== 3. 下载模型文件 ==========
echo ""
echo "检查模型文件..."

if [ ! -f "$MODEL_DIR/model.int8.onnx" ] || [ ! -f "$MODEL_DIR/tokens.txt" ]; then
    echo "下载 SenseVoice 模型..."
    mkdir -p "$MODEL_DIR"

    # 下载模型
    MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-2024-12-04/model.int8.onnx"
    echo "  下载模型文件 (约 240MB)..."
    curl -L -o "$MODEL_DIR/model.int8.onnx" "$MODEL_URL" || {
        echo "✗ 模型下载失败，请手动下载并放到 $MODEL_DIR"
        exit 1
    }

    # 下载 tokens 文件
    TOKENS_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-2024-12-04/tokens.txt"
    echo "  下载 tokens 文件..."
    curl -L -o "$MODEL_DIR/tokens.txt" "$TOKENS_URL" || {
        echo "✗ tokens 下载失败"
        exit 1
    }

    echo "✓ 模型文件下载完成"
else
    echo "✓ 模型文件已存在"
fi

# ========== 4. 安装系统依赖 ==========
echo ""
echo "安装系统依赖..."

# 检查 sudo 权限
if sudo -v 2>/dev/null; then
    NEED_SUDO=true
else
    NEED_SUDO=false
fi

install_if_missing() {
    local cmd=$1
    local pkg=${2:-$cmd}
    if ! command -v $cmd &> /dev/null 2>/dev/null; then
        echo "  安装 $pkg..."
        if [ "$NEED_SUDO" = true ]; then
            sudo apt-get install -y $pkg
        else
            apt-get install -y $pkg
        fi
    else
        echo "  ✓ $cmd 已安装"
    fi
}

# X11/Wayland 通用工具
install_if_missing xsel
install_if_missing xdotool

# Wayland 工具
install_if_missing ydotool
install_if_missing ydotoold
install_if_missing wl-copy wl-clipboard

# 录音工具
install_if_missing arecord alsa-utils

echo "✓ 系统依赖安装完成"

# ========== 5. Wayland 额外配置 ==========
echo ""
echo "配置 Wayland 支持..."

# 设置 /dev/uinput 权限
if [ -e /dev/uinput ]; then
    if [ "$NEED_SUDO" = true ]; then
        echo "  设置 /dev/uinput 权限..."
        sudo chmod 666 /dev/uinput 2>/dev/null || true
    fi

    # 检查权限
    perms=$(stat -c '%a' /dev/uinput 2>/dev/null)
    if [ "$perms" = "666" ] || [ "$perms" = "662" ]; then
        echo "  ✓ /dev/uinput 权限正确"
    else
        echo "  ⚠ /dev/uinput 权限可能需要手动设置"
        echo "    运行: sudo chmod 666 /dev/uinput"
    fi
fi

# 创建 udev 规则（持久化）
if [ "$NEED_SUDO" = true ] && [ ! -f /etc/udev/rules.d/99-uinput.rules ]; then
    echo "  创建 udev 规则..."
    echo 'KERNEL=="uinput", MODE="0666", GROUP="input"' | sudo tee /etc/udev/rules.d/99-uinput.rules > /dev/null 2>&1 || true
fi

echo "✓ Wayland 配置完成"

# ========== 6. 创建 autostart 配置 ==========
echo ""
echo "配置开机自启..."

# 确保 autostart 目录存在
mkdir -p "$HOME/.config/autostart"

# 创建 desktop 文件
cat > "$AUTOSTART_DESKTOP" << EOF
[Desktop Entry]
Type=Application
Name=Voice Input Daemon
Comment=Voice input with Ctrl+Q
Exec=$SCRIPT_DIR/venv-voice/bin/python3 $SCRIPT_DIR/src/daemon.py
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF

# 创建软链接
ln -sf "$AUTOSTART_DESKTOP" "$AUTOSTART_LINK" 2>/dev/null || true

echo "✓ 开机自启配置完成"

# ========== 7. 设置权限 ==========
chmod +x "$DAEMON_SCRIPT"
chmod +x "$SCRIPT_DIR/setup.sh"

# ========== 8. 启动守护进程 ==========
echo ""
echo "启动语音输入守护进程..."
pkill -f daemon.py 2>/dev/null || true
sleep 1
nohup "$DAEMON_SCRIPT" > /dev/null 2>&1 &
sleep 2

# 检查是否运行
if pgrep -f daemon.py > /dev/null; then
    echo "✓ 守护进程已启动"
else
    echo "✗ 守护进程启动失败"
    exit 1
fi

echo ""
echo "============================================"
echo "  安装完成！"
echo "============================================"
echo ""
echo "使用方法："
echo "  按 Ctrl+Q 开始录音"
echo "  再按 Ctrl+Q 停止，文字自动填入"
echo ""
echo "Wayland 用户注意："
echo "  如果热键不工作，请运行: ydotoold &"
echo "  或者设置 /dev/uinput 权限: sudo chmod 666 /dev/uinput"
echo ""
echo "重启后自动生效。"
