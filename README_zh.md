# 语音输入 / Voice Input

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform-Ubuntu](https://img.shields.io/badge/Platform-Ubuntu-orange.svg)](https://ubuntu.com/)
[![Tested_on-Ubuntu_24.04](https://img.shields.io/badge/Tested_on-Ubuntu_24.04-24.04-orange.svg)](https://ubuntu.com/)

[English](README.md) | [中文](README_zh.md) | [한국어](README_ko.md)

---

语音输入是一款基于全局热键的语音听写工具，专为 Linux 系统设计。只需按 `Ctrl+Q` 即可开始录音，系统会自动将语音转写为文字并粘贴到当前焦点输入框。支持中文、英文、日文、韩文、粤语等多种语言，其中中文识别率最高。UI 语言会根据你的使用习惯自动适应。完美支持 X11 和 Wayland 桌面会话，开机自动启动，无需网络，离线运行。

## 功能特性

- **全局热键** - 按 `Ctrl+Q` 开始/停止录音（可自定义）
- **多语言支持** - 中文、英文、日文、韩文、粤语自动识别
- **智能 UI 语言** - UI 自动切换到匹配你的说话习惯
- **双平台支持** - 完美支持 X11 和 Wayland 会话
- **实时音量显示** - 录音时显示音量波形动画
- **自动粘贴** - 识别完成后自动将文字粘贴到焦点窗口
- **开机自启** - 配置后开机自动启动守护进程
- **离线运行** - 无需网络，本地完成语音识别

## 系统要求

- **操作系统**: Ubuntu 24.04 LTS（已测试）
  - 其他 Ubuntu 版本可能可用，但未经过官方测试
  - **macOS 和 Windows 未测试** - 无法保证功能正常
- **桌面环境**: GNOME（支持开机自启）
- **会话类型**: X11 或 Wayland
- **硬件**: 需要麦克风进行语音输入
- **Python**: 3.8 或更高版本

### 必需依赖

本程序需要以下工具：

| 工具 | 用途 | 安装命令 |
|------|------|---------|
| xdotool | 窗口焦点检测、键盘模拟 | `sudo apt install xdotool` |
| xsel | 剪贴板操作 | `sudo apt install xsel` |
| xprop | 窗口类检测 | `sudo apt install x11-utils` |

Wayland 额外需要：

| 工具 | 用途 | 安装命令 |
|------|------|---------|
| ydotoold | Wayland 键盘模拟 | `sudo apt install ydotool` |
| wl-copy | Wayland 剪贴板 | `sudo apt install wl-clipboard` |

### 窗口兼容性

程序会自动检测窗口类型并选择合适的粘贴方式：

**终端窗口**（使用 `Ctrl+Shift+V` 粘贴）：
- GNOME Terminal
- Konsole
- xterm、uxterm
- Terminator
- Alacritty
- Kitty
- Tilix
- Terminology
- LilyTerm
- Termite

**GUI 应用程序**（使用 `Ctrl+V` 粘贴）：
- 所有图形化应用程序（gedit、VS Code、Chrome、Firefox 等）
- Electron 应用
- Qt 应用程序
- GTK 应用程序

这种自动检测确保语音输入在终端和图形环境中都能正常工作。

## 快速开始

### 安装

```bash
git clone https://github.com/chelkim/voice-input.git ~/.voice-input
cd ~/.voice-input
./setup.sh
```

### 使用方法

1. 确保守护进程在运行（开机后自动启动）
2. 鼠标点击目标输入框
3. 按 `Ctrl+Q` 开始录音
4. 说话
5. 再按 `Ctrl+Q` 停止录音
6. 文字自动填入输入框

## 配置

配置文件位于 `~/.config/voice-input/config`

```ini
[hotkey]
# 修饰键+主键，修饰键包括 ctrl, alt, shift, meta
key = Ctrl+Q

[recognition]
# 识别语言: auto (自动检测), zh (中文), en (英文), ja (日语), ko (韩语), yue (粤语)
# 注意：中文识别率最高，其他语言识别率相对较低
language = auto

[ui]
# UI 显示语言: auto (根据使用习惯自动检测), zh, en, ja, ko, yue
# 设置为 auto 时，系统会学习你的语言习惯并自动切换 UI 语言
language = auto
```

**语言识别准确率说明：**

SenseVoice 模型支持 6 种语言，但识别准确率不同：
- **中文 (zh)** - 准确率最高，训练数据最多
- **英文 (en)** - 准确率较好
- **日语 (ja)、韩语 (ko)、粤语 (yue)** - 准确率较低，可能偶尔与中文混淆

建议保持 `language = auto` 以获得最佳效果。如果你主要说中文，模型会自动优先识别中文。

**智能 UI 语言功能：**
- 当 `[ui] language = auto` 时，系统会自动检测你的说话习惯
- 连续 2 次同一语言的转写后，UI 语言会自动更新
- 例如：连续 2 次说中文，UI 会切换为中文显示
- 语言统计数据会持久保存，重启后不丢失

修改配置后需要重启服务生效。

## 常用命令

```bash
# 重启服务
pkill -f daemon.py && sleep 1 && ~/.voice-input/venv-voice/bin/python3 ~/.voice-input/src/daemon.py &

# 检查服务状态
pgrep -f daemon.py

# 查看日志
tail -f ~/.voice-input/voice.log
```

## 开发

### 项目架构

本项目采用模块化架构，便于维护和扩展：

- **src/config.py** - 配置管理
- **src/platform/** - 平台抽象层
- **src/keyboard/** - 键盘捕获
- **src/audio/** - 音频录制
- **src/recognition/** - 语音识别
- **src/ui/** - 用户界面

### 运行测试

```bash
./venv-voice/bin/python3 tests/test_config.py
```

## Wayland 额外配置

```bash
# 安装 ydotoold
sudo apt-get install ydotoold

# 设置 /dev/uinput 权限
sudo chmod 666 /dev/uinput

# 启动 ydotoold
ydotoold &
```

## 故障排除

### 守护进程没有响应

```bash
pgrep -f daemon.py  # 检查是否运行
~/.voice-input/venv-voice/bin/python3 ~/.voice-input/src/daemon.py &  # 手动启动
```

### Wayland 下 ydotool 不工作

1. 确保 ydotoold 服务正在运行：`ps aux | grep ydotoold`
2. 检查 /dev/uinput 权限：`ls -la /dev/uinput`

### 无法粘贴到终端

终端使用 `Ctrl+Shift+V` 粘贴

## 贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与开发。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。
