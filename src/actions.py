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
import requests
import pyperclip

# 定义一个动作执行器类
class ActionEngine:
    def __init__(self):
        print("动作引擎已经就绪")

        # 多轮对话状态机
        self.pending_confirmation = None    # 存字符串，例如 "read_clipboard"
        self.pending_data = None    # 存数据

        pass

    def execute(self, text):
        """
        根据传入的文本 text, 判断意图并执行动作
        """
        # 保留原始文本
        raw_text = text

        # 去除所有空格，不区分大小写
        cmd = text.replace(" ", "").lower()

        print(f"解析: 原始[{raw_text}] | 清洗[{cmd}]")

        # === 优先处理：多轮对话的回复 ===
        # 只有在有等待任务时，才拦截 "是的/确定"
        if self.pending_confirmation:
            if "是的" in cmd or "确定" in cmd or "读吧" in cmd or "ok" in cmd:
                self.confirm_action()
                return # 拦截成功，结束
            
            if "不用" in cmd or "取消" in cmd or "算" in cmd:
                self.cancel_action()
                return # 拦截成功，结束
            
            # 💡 关键策略：
            # 如果用户在等待确认期间，说了一个完全不相关的指令（比如“打开百度”），
            # 我们应该认为是“隐式取消”，直接执行新指令。
            # 所以这里不需要 else return，直接让它往下走，
            # 但为了严谨，最好先重置状态
            self.reset_state() 


        # === 智能搜索逻辑 ===
        # 识别模式： "百度搜索" + 内容
        if "百度搜索" in cmd:
            # 策略：从原始文本里找 "搜索" 两个字，取它后面的所有内容
            # 因为 Vosk 可能会把 "百度 搜索 Python" 识别成不同分词
            # 我们用简单的逻辑：把 "百度" 和 "搜索" 替换为空，剩下的就是内容
            keyword = cmd.replace("百度", "").replace("搜索", "")
            
            if keyword:
                self.speak(f"正在百度搜索 {keyword}")
                webbrowser.open(f"https://www.baidu.com/s?wd={keyword}")
            else:
                self.speak("你要搜什么？请说：百度搜索某某某")
            return

        # === 天气查询逻辑 ===
        if "天气" in cmd:
            # 简单版：只查默认城市
            # 进阶版：提取城市名 (比如 "查询上海天气")
            city = "Beijing" # 默认
            
            if "上海" in cmd: city = "Shanghai"
            elif "广州" in cmd: city = "Guangzhou"
            elif "深圳" in cmd: city = "Shenzhen"
            # ... 可以加更多
            
            self.check_weather(city)
            return

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
        
        if "朗读剪贴板"  in cmd or "读一下" in cmd:
            self.read_clipboard()
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

    # === 查询天气 ===
    def check_weather(self, city="Beijing"):
        # 默认查背景，后面我们可以支持其他城市
        self.speak(f"正在查询{city}的天气...")

        try:
            # format=3 表示简短格式：地区: 天气图标 温度
            # lang=zh 表示中文
            url = f"https://wttr.in/{city}?format=3&lang=zh"
            
            # 发送请求，超时设置为5秒，防止卡死
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                weather_info = response.text.strip()
                # wttr.in 有时返回格式会带一点杂质，我们直接读出来通常没问题
                print(f"天气数据: {weather_info}")
                
                # 语音播报
                # 比如返回的是 "Beijing: ⛅️ +20°C"
                # 我们稍微处理一下，让读起来自然点
                self.speak(f"查询到了：{weather_info}")
            else:
                self.speak("天气服务暂时不可用。")
                
        except Exception as e:
            print(f"天气查询失败: {e}")
            self.speak("网络连接似乎有问题，无法查询天气。")

    # === 智能搜索 (参数提取) ===
    def smart_search(self, command):
        # 假设指令是 "百度搜索 Python 教程"
        # 我们需要把 "百度搜索" 去掉，提取后面的 "Python 教程"
        
        target = ""
        
        if "百度搜索" in command:
            # 简单粗暴的字符串切分
            # command 是去除了空格的，比如 "百度搜索python教程"
            # 这种切分稍微有点难，因为我们之前在 main.py 把空格全删了...
            # 💡 这是一个坑！还记得吗？
            pass

    # === 技能: 智能剪贴板朗读 ===
    def read_clipboard(self):
        text = pyperclip.paste().strip()
        
        if not text:
            self.speak("剪贴板是空的。")
            return

        if len(text) <= 50:
            # 短文本，直接读
            self.speak(f"剪贴板内容是：{text}")
        else:
            # 长文本，进入【确认态】
            self.pending_data = text
            self.pending_confirmation = "read_clipboard"
            
            # 提示用户
            snippet = text[:20].replace("\n", " ") # 取前20个字预览
            self.speak(f"剪贴板内容较长，共有{len(text)}个字。开头是：{snippet}... 确定要朗读全文吗？")

    # === 核心: 处理确认指令 ===
    def confirm_action(self):
        """当用户说'是的/确定'时调用"""
        if self.pending_confirmation == "read_clipboard":
            self.speak("好的，开始朗读...")
            # 这里读全文
            self.speak(self.pending_data)
            # 读完重置状态
            self.reset_state()
        else:
            # 如果当前没有在等确认，用户却说了“是的”，可以忽略或回一句
            self.speak("我不明白你要确认什么。")

    def cancel_action(self):
        """当用户说'不用了/取消'时调用"""
        if self.pending_confirmation:
            self.speak("好的，已取消。")
            self.reset_state()
    
    def reset_state(self):
        self.pending_confirmation = None
        self.pending_data = None



# 单独测试代码
if __name__ == "__main__":
    engine = ActionEngine()
    engine.execute("打开记事本")