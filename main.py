"""
主程序（大脑），负责调度耳朵和手
"""

import sys
import os

# 将 src 目录添加到 Python 搜索路径，否则找不到模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from voice_engine import VoiceEngine
from actions import ActionEngine

def main():
    print("VoxForge 启动中...")

    # 初始化动作引擎
    action_engine = ActionEngine()

    # 初始化语音引擎
    voice_engine = VoiceEngine()

    # 定义一个处理函数：链接 耳朵->手
    # 当耳朵听到东西是，出发这个逻辑
    def on_command_received(text):
        # 把听到的命令交给动作引擎去处理
        action_engine.execute(text)

    # 启动监听循环，并将处理函数传进去
    try:
        voice_engine.listen_loop(on_command_received)
    except KeyboardInterrupt:
        print("程序已退出，再见！")

if __name__ == "__main__":
    main()