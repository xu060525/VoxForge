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
global_system_active = True # 默认是活跃状态
global_gui = None   # 方便我们在 set_listening_state 里通知前端更新UI

# 暴露给JS的函数
@eel.expose
def set_listening_state(state):
    # state 是 JS 传过来的 true/false
    global global_system_active
    global_system_active = state
    # 这里不需要去控制 voice_engine 了，知识改变一个布尔值变量
    print(f"状态切换: {'活跃' if state else '静默'}")

def main():
    # 引用全局变量
    global global_gui

    # 实例化三大模块
    gui = GUI()
    action_engine = ActionEngine()
    voice_engine = VoiceEngine()

    # 保存引用
    global_gui = gui

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
            global global_system_active
            
            # 清洗文本
            cmd = text.replace(" ", "").lower()
            
            # === 无论当前是什么状态，都要检查“唤醒/休眠”指令 ===
            
            if "开始识别" in cmd or "恢复监听" in cmd:
                if not global_system_active:
                    global_system_active = True
                    action_engine.speak("好的，我回来了")
                    # 通知前端更新按钮状态 (这一步很重要，保持界面同步)
                    # 我们需要去 script.js 里写一个 updateToggleBtnState 函数
                    eel.js_update_toggle_btn(True) 
                    gui.update_status("正在监听...", "listening")
                return

            if "停止识别" in cmd or "暂停监听" in cmd:
                if global_system_active:
                    global_system_active = False
                    action_engine.speak("好的，进入静默模式")
                    eel.js_update_toggle_btn(False)
                    gui.update_status("已暂停 (仅响应'开始识别')", "idle")
                return
            
            if "退出" in cmd or "再见" in cmd or "exit" in cmd:
                # 1. 礼貌道别
                # 注意：这里不能用 action_engine.speak() 异步线程
                # 因为如果主程序退太快，声音还没发出来就被掐断了
                # 但为了简单，我们先发指令，稍等一下再关
                action_engine.speak("好的，期待下次为您服务。")
                
                # 2. 更新界面状态
                gui.add_bot_message("系统正在关闭...")
                
                # 3. 定义一个延时关闭函数
                def shutdown_sequence():
                    time.sleep(2) # 等2秒，让 TTS 把话说完
                    # 调用前端关闭窗口，这会触发 main.py 最底部的异常捕获，从而结束程序
                    eel.close_window()
                    # 双重保险：如果前端没关掉，后端强制退出
                    # time.sleep(1)
                    # os._exit(0) 

                # 启动关闭线程
                threading.Thread(target=shutdown_sequence).start()
                return


            # === 只有在活跃状态下，才执行普通指令 ===
            if global_system_active:
                gui.update_status("正在分析...", "processing")
                gui.add_user_message(text)
                
                action_engine.execute(text)
                
                gui.add_bot_message(f"已执行: {text}")
                gui.update_status("继续监听中...", "listening")
            else:
                # 静默状态下，听到普通话语，直接忽略，不打印也不执行
                print(f"静默中，忽略指令: {text}")

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