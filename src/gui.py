"""
专门管理界面逻辑
"""

import eel
import threading

class GUI:
    def __init__(self):
        # 初始化 Eel, 指定 web 文件夹路径
        eel.init('web')

    def start(self):
        """启动 GUI 窗口 (阻塞式，要在主线程运行)"""
        try:
            eel.start('index.html', size=(600, 600), port=0)
        except (SystemExit, MemoryError, KeyboardInterrupt):
            # 处理窗口关闭时的清理工作
            print("GUI 窗口已关闭")

    # === 封装发送给前端的方法 ===
    def update_status(self, text, state="idle"):
        """
        state: idle(空闲), listening(红灯), processing(蓝灯)
        """
        # eel.js_function_name(args)
        eel.update_status(text, state)

    def add_user_message(self, text):
        eel.add_message(text, "user")

    def add_bot_message(self, text):
        eel.add_message(text, "bot")

    def close(self):
        eel.close_window()