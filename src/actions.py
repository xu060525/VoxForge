"""
这是 VoxForge 的动作引擎 (手)，负责具体的系统操作
"""

import os
import webbrowser
import platform
import pyautogui

# 定义一个动作执行器类
class ActionEngine:
    def __init__(self):
        print("动作引擎已经就绪")

    def execute(self, text):
        """
        根据传入的文本 text, 判断意图并执行动作
        """
        # 统一转换成小写，方便匹配
        # cmd = text.lower()
        # 去除所有空格，并不区分大小写
        cmd = text.replace(" ", "").lower()

        print(f"正在解析指令: {cmd}")

        # === 规则1：网页浏览 ===
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
        
        # === 规则2：系统应用（Windows）===
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
        
        if "显示桌面" in cmd or "老板来了" in cmd:
            self.speak("回到桌面")
            pyautogui.hotkey('win', 'd')
            return
        
        # === 规则 3: 兜底回复 ===
        # 如果什么都没匹配到
        print(f"未知指令: {cmd}")

    def speak(self, response):
        """
        (预留接口) 以后这里会接入 TTS 语音合成，让电脑说话
        目前先用 print 代替
        """
        print(f"助手回复: {response}")

# 单独测试代码
if __name__ == "__main__":
    engine = ActionEngine()
    engine.execute("打开记事本")