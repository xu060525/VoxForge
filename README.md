# 🎙️ VoxForge - 你的可视化桌面语音助手

<p align="center">
  <img src="resources/icon.ico" width="128" height="128" />
</p>

> 让每个人都拥有自己的离线版“贾维斯”。
> Build your own "Jarvis" with Python, Privacy-first & Offline-ready.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-orange)

## 📖 项目简介

VoxForge 是一个基于 Python 开发的桌面语音助手。与 Siri 或小爱同学不同，VoxForge 专注于**桌面自动化**与**隐私安全**。
它完全运行在本地（Offline），不需要联网上传你的语音数据，支持通过语音指令控制电脑、打开应用、查询信息等。

## ✨ 核心功能

- **👂 离线语音识别**: 基于 Vosk 模型，无需联网，隐私 100% 安全。
- **🗣️ 语音反馈**: 内置 TTS (Text-to-Speech)，能开口与你对话。
- **🖥️ 可视化界面**: 极客风的 Web UI (Eel 框架)，实时显示系统状态。
- **⚡ 自动化控制**:
  - 打开应用/网页 ("打开百度", "启动记事本")
  - 系统控制 ("音量大点", "静音", "截图")
  - 剪贴板朗读 ("读一下")
  - 摸鱼模式 ("老板来了" -> 一键回到桌面并静音)
- **🧠 多轮对话**: 支持简单的上下文确认 ("内容太长，确定要读吗？" -> "是的")。

## 🛠️ 技术栈

*   **后端**: Python 3.11
*   **前端**: HTML5 / CSS3 / JavaScript (Eel Framework)
*   **语音识别**: Vosk + SoundDevice
*   **语音合成**: pyttsx3
*   **自动化**: PyAutoGUI / Webbrowser / Pyperclip
*   **打包**: PyInstaller

## 🚀 快速开始

### 方式一：直接运行 (Windows)
1. 在 [Releases](https://github.com/你的用户名/VoxForge/releases) 页面下载最新的 `VoxForge.zip`。
2. 解压后，确保 `resources` 文件夹与 `.exe` 在同一目录。
3. 双击 `VoxForge.exe` 即可启动。

### 方式二：源码运行
```bash
# 1. 克隆项目
git clone https://github.com/你的用户名/VoxForge.git
cd VoxForge

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 下载模型
# 请去 https://alphacephei.com/vosk/models 下载 vosk-model-small-cn
# 解压并重命名为 model，放入 resources 目录

# 5. 运行
python main.py