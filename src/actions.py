"""
这是 VoxForge 的动作引擎 (手)，负责具体的系统操作
"""

import os
import webbrowser
import platform
import pyautogui
import pyttsx3
import threading
import datetime
import time

# 定义一个动作执行器类
class ActionEngine:
    def __init__(self):
        print("动作引擎已经就绪")
        pass

    def execute(self, text):
        """
        根据传入的文本 text, 判断意图并执行动作
        """
        # 统一转换成小写，方便匹配
        # cmd = text.lower()
        # 去除所有空格，不区分大小写
        cmd = text.replace(" ", "").lower()

        print(f"正在解析指令: {cmd}")

        # === 优先处理：时间查询 ===
        if "几点了" in cmd or "时间" in cmd:
            self.report_time()
            return
        
        if "日期" in cmd or "几号" in cmd or "星期几" in cmd:
            self.report_date()
            return

        # === 优先处理：截图 ===
        if "截图" in cmd or "截屏" in cmd:
            self.take_screenshot()
            return

        # === 优先处理：音量控制 ===
        if "音量" in cmd or "声音" in cmd or "静音" in cmd:
            self.control_media(cmd)
            return

        # === 网页浏览 ===
        if "打开百度" in cmd:
            self.speak("正在为您打开百度")
            webbrowser.open("https://www.baidu.com")
            return
        
        if "打开谷歌" in cmd:
            self.speak("Opening Google")
            webbrowser.open("https://www.google.com")
            return
        
        if "打开哔哩哔哩" in cmd or "打开b站" in cmd:
            self.speak("好的, 打开B站")
            webbrowser.open("https://www.bilibili.com")
            return
        
        # === 系统应用（Windows）===
        # 注意：os.system 或 os.startfile 仅限 Windows 比较好用
        if "打开记事本" in cmd:
            self.speak("启动记事本")
            os.system("start notepad")
            return

        if "打开计算器" in cmd:
            self.speak("启动计算器")
            os.system("start calc")
            return

        if "打开画图" in cmd:
            self.speak("启动画图板")
            os.system("start mspaint")
            return
        
        if "显示桌面" in cmd:
            self.speak("回到桌面")
            pyautogui.hotkey('win', 'd')
            return
        
        if "老板来了" in cmd:
            pyautogui.hotkey('win', 'd')
            pyautogui.press('volumemute')
            webbrowser.open("https://github.com")
            return

        # === 兜底回复 ===
        # 如果什么都没匹配到
        print(f"未知指令: {cmd}")

    def speak(self, text):
        """
        接入 TTS 语音合成，让电脑说话
        """
        # 先在终端打印，方便调试
        print(f"助手回复: {text}")

        # 定义一个内部函数，专门负责说话
        # pyttsx3 在多线程环境下，最好是“谁用谁初始化”，防止线程冲突 crash
        def _speak_thread():
            try:
                engine = pyttsx3.init()
                # 调整语速
                rate = engine.getProperty('rate')
                engine.setProperty('rate', rate - 20)

                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"语音合成出错: {e}")

        # 启动一个临时线程去执行
        t = threading.Thread(target=_speak_thread)
        t.start()

    # === 时间感知 ===
    def report_time(self):
        now = datetime.datetime.now()
        # 格式化时间
        time_str = now.strftime("%H点%M分")
        self.speak(f"现在是 {time_str}")

    def report_date(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        self.speak(f"今天是 {date_str}")

    # === 媒体控制 ===
    def control_media(self, cmd):
        if "大点声" in cmd:
            for _ in range(5):
                pyautogui.press('volumeup')
            self.speak("音量已调大")

        elif "小点声" in cmd:
            for _ in range(5):
                pyautogui.press('volumedown')
            self.speak("音量已调大")

        elif "静音" in cmd:
            pyautogui.press('volumemute')
            self.speak("已静音")

     # === 屏幕截图 ===
    def take_screenshot(self):
        self.speak("正在截图...")
        
        # 1. 生成文件名 (按时间戳，防止重名)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        
        # 2. 计算保存路径 (动态路径)
        # 获取项目根目录 (假设 actions.py 在 src 下，回退一级是根目录)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, "..") 
        save_path = os.path.join(project_root, "captures", filename)
        
        try:
            # 3. 截图并保存
            pyautogui.screenshot(save_path)
            self.speak("截图已保存")
            
            # (可选) 截图后自动打开该图片查看
            os.startfile(save_path) 
        except Exception as e:
            print(f"截图失败: {e}")
            self.speak("截图失败，请检查日志")

# 单独测试代码
if __name__ == "__main__":
    engine = ActionEngine()
    engine.execute("打开记事本")