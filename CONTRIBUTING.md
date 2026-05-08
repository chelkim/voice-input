# Contributing Guide / 贡献指南

[English](#english) | [中文](#中文)

---

## English

Thank you for your interest in contributing to Voice Input! We welcome all forms of contributions.

### How to Contribute

#### Reporting Issues

If you find a bug or have a feature request:

1. Search existing issues to avoid duplicates
2. Create a new issue including:
   - Clear title and description
   - Steps to reproduce
   - System environment info (Linux distro, session type X11/Wayland)

#### Submitting Code

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Develop and test
4. Ensure code follows project style
5. Commit and push
6. Create a Pull Request

#### Code Style

- Python code follows PEP 8
- Use meaningful variable and function names
- Add comments and docstrings for new features
- Add appropriate error handling

### Project Structure

```
voice-input/
├── src/
│   ├── daemon.py           # Main entry point
│   ├── config.py           # Configuration management
│   ├── platform/           # Platform abstraction
│   │   └── base.py
│   ├── keyboard/          # Keyboard capture
│   │   ├── base.py
│   │   ├── x11.py         # pynput implementation
│   │   └── wayland.py     # evdev implementation
│   ├── audio/             # Audio recording
│   │   └── recorder.py
│   ├── recognition/       # Speech recognition
│   │   └── sensevoice.py
│   └── ui/                # User interface
│       └── overlay.py
├── tests/                  # Tests
├── scripts/                # Setup scripts
└── voice-input.desktop     # GNOME autostart config
```

### Testing

Run tests:

```bash
./venv-voice/bin/python3 tests/test_config.py
```

### Adding New Features

If you want to add new features:

1. Consider compatibility with existing architecture
2. Add appropriate configuration options (don't hardcode)
3. Update README documentation
4. Add tests

### License

By submitting code, you agree that your contribution will be licensed under the project's license.

---

## 中文

感谢您对 Voice Input 项目的兴趣！我们欢迎各种形式的贡献。

### 如何贡献

#### 报告问题

如果您发现 bug 或有功能建议：

1. 搜索现有 issue 确保没有重复
2. 创建新的 issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 系统环境信息（Linux 发行版、会话类型 X11/Wayland）

#### 提交代码

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature-name`
3. 进行开发并测试
4. 确保代码符合项目风格
5. 提交并 push
6. 创建 Pull Request

#### 代码风格

- Python 代码遵循 PEP 8
- 使用有意义的变量和函数名
- 为新功能添加注释和文档字符串
- 添加适当的错误处理

### 项目结构

```
voice-input/
├── src/
│   ├── daemon.py           # 主入口
│   ├── config.py           # 配置管理
│   ├── platform/           # 平台抽象层
│   │   └── base.py
│   ├── keyboard/          # 键盘捕获
│   │   ├── base.py
│   │   ├── x11.py         # pynput 实现
│   │   └── wayland.py     # evdev 实现
│   ├── audio/             # 音频录制
│   │   └── recorder.py
│   ├── recognition/       # 语音识别
│   │   └── sensevoice.py
│   └── ui/                # 界面
│       └── overlay.py
├── tests/                  # 测试
├── scripts/                # 安装脚本
└── voice-input.desktop     # GNOME 自启配置
```

### 测试

运行测试：

```bash
./venv-voice/bin/python3 tests/test_config.py
```

### 添加新功能

如果您想添加新功能：

1. 考虑与现有架构的兼容性
2. 添加适当的配置选项（不要硬编码）
3. 更新 README 文档
4. 添加测试

### 许可证

通过提交代码，您同意您的贡献将按照项目许可证进行许可。
