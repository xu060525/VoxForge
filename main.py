"""
主程序（大脑），负责调度耳朵和手
"""

import sys
import os
import threading
import time
import eel

# 导入模块
from src.voice_engine import VoiceEngine
from src.actions import ActionEngine
from src.gui import GUI

# 全局变量
global_voice_engine = None

# 暴露给JS的函数
@eel.expose
def set_listening_state(state):
    # state 是 JS 传过来的 true/false
    global global_voice_engine
    if global_voice_engine:
        if state:
            global_voice_engine.resume()
        else:
            global_voice_engine.pause()

def main():
    # 引用全局变量
    global global_voice_engine

    # 1. 实例化三大模块
    gui = GUI()
    action_engine = ActionEngine()
    voice_engine = VoiceEngine()

    # 把实例化的对象赋给全局变量
    global_voice_engine = voice_engine

    # 2. 定义核心逻辑 (这是在子线程里跑的)
    def voice_thread_logic():
        # 等待 GUI 先启动一小会儿，避免JS还没加载好就发消息
        time.sleep(2) 
        
        gui.update_status("正在监听环境音...", "listening")
        gui.add_bot_message("系统已启动，请下达指令。")

        # 定义当听到声音时的回调
        def on_hear(text):
            # A. 更新界面：显示用户说了啥
            gui.update_status("正在分析...", "processing")
            gui.add_user_message(text)
            
            # B. 执行动作
            action_engine.execute(text)
            
            # C. 动作执行完，恢复监听状态
            gui.add_bot_message(f"已执行: {text}") # 简单回显
            gui.update_status("继续监听中...", "listening")

        # 启动语音引擎的监听循环
        voice_engine.listen_loop(on_hear)

    # 3. 创建并启动子线程
    # daemon=True 表示如果你关掉主窗口，这个子线程也会自动随之关闭，不会残留后台
    t = threading.Thread(target=voice_thread_logic, daemon=True)
    t.start()

    # 4. 启动 GUI (必须在主线程，且必须放在最后，因为它会阻塞)
    print("启动图形界面...")
    gui.start()

if __name__ == "__main__":
    main()