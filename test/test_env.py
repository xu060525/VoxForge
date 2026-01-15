import sys
import speech_recognition as sr
import pyttsx3
import pyautogui
import eel
import psutil

# 打印欢迎语, 测试Python环境
print(f"Python 版本: {sys.version}")
print("正在初始化 VoxForge 环境监测...")

# 测试 TTS (Text To Speech)
try:
    engine = pyttsx3.init()
    print("语音合成引擎 (pyttsx3): 正常")
except Exception as e:
    print(f"语音合成引擎错误: {e}")

# 测试麦克风环境
try:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("麦克风检测 (PyAudio): 驱动正常")
except Exception as e:
    print(f"麦克风/PyAudio 错误: {e}")
    print("请检查 PyAudio 是否安装成功, 以及是否有麦克风设备")

# 测试自动化库
try:
    size = pyautogui.size()
    print(f"屏幕自动化 (PyAutoGUI): 正常 (分辨率: {size})")
except Exception as e:
    print(f"自动化库错误: {e}")

# 测试 GUI 库
print(f"GUI 框架 (Eel): 正常")

print("\n 检测已完成")