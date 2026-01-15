"""
语音引擎（耳朵），把识别到的文字传递出去，而不是自己打印。
"""

import os
import sys
import queue
import sounddevice as sd    # 比 pyaudio 更简单
import vosk
import json

class VoiceEngine:
    def __init__(self):
        # 动态获取模型路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "..", "resources", "model")
        
        if not os.path.exists(self.model_path):
            print(f"错误：找不到模型路径 {self.model_path}")
            sys.exit(1)
            
        try:
            print("正在初始化语音模型...")
            self.model = vosk.Model(self.model_path)
            self.q = queue.Queue()
            print("语音引擎初始化完成")
        except Exception as e:
            print(f"模型加载失败: {e}")
            sys.exit(1)

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
        
        print("\n 监听已启动，请说话...")
        
        # 打开麦克风流
        with sd.RawInputStream(samplerate=16000, blocksize=8000, device=None,
                               dtype='int16', channels=1, callback=self._callback):
            while True:
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