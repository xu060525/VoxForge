"""
语音引擎（耳朵），把识别到的文字传递出去，而不是自己打印。
"""

import os
import sys
import queue
import sounddevice as sd    # 比 pyaudio 更简单
import vosk
import json
import time

def get_resource_path(relative_path):
    """获取资源绝对路径 (兼容开发环境和打包环境)"""
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后运行，基准路径是临时目录
        base_path = sys._MEIPASS
    else:
        # 如果是源代码运行，基准路径是项目根目录
        # (假设当前 voice_engine.py 在 src 下，根目录是上一级)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

class VoiceEngine:
    def __init__(self):
        # 动态获取模型路径
        # 策略：模型在 exe 旁边的 resources/model 里
        # 注意：这里如果是外部资源，就不能用 _MEIPASS 了，而是用 sys.executable
        
        if hasattr(sys, 'frozen'):
            # 打包后：exe 所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发中：项目根目录
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.model_path = os.path.join(base_dir, "resources", "model")

        if not os.path.exists(self.model_path):
            print(f"错误：找不到模型路径 {self.model_path}")
            sys.exit(1)
            
        try:
            print("正在初始化语音模型...")
            self.model = vosk.Model(self.model_path)
            self.q = queue.Queue()
            # 定义暂停标志位
            self.is_paused = False
            print("语音引擎初始化完成")
        except Exception as e:
            print(f"模型加载失败: {e}")
            sys.exit(1)

    def close(self):
        print("正在释放语音引擎资源...")
        # 显式删除对象，触发 __del__
        # 在程序彻底退出前手动删，此时 C 库肯定还在
        if hasattr(self, 'model'):
            del self.model 
        if hasattr(self, 'rec'): # 如果你把 rec 保存为 self.rec 的话
            del self.rec

    # 新增两个控制方法
    def pause(self):
        self.is_paused = True
        print("语音监听已暂停")

    def resume(self):
        self.is_paused = False
        print("语音监听已恢复")

    def _callback(self, indata, frames, time, status):
        """麦克风回调函数 (内部使用)"""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def listen_loop(self, handler_function):
        """
        核心监听循环
        :param handler_function: 一个函数，当识别到文本时，会调用这个函数把文本传出去
        """
        rec = vosk.KaldiRecognizer(self.model, 16000)
        
        print("\n监听已启动, 请说话...")
        
        # 打开麦克风流
        with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None,
                               dtype='int16', channels=1, callback=self._callback):
            while True:
                # 核心逻辑：如果暂停了，就不从队列读取数据
                # if self.is_paused:
                #     time.sleep(0.5) # 休息0.5秒，避免占用CPu
                #     continue    # 不执行下面的识别逻辑
                # 现在换成软开关：关闭时识别到“开始识别”就开始

                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result['text'].strip()
                    
                    if text:
                        # === 关键点：这里调用传入的函数 ===
                        print(f"听到: {text}")
                        handler_function(text)
                        
                        if "退出" in text or "再见" in text:
                            print("正在停止监听...")
                            break