import os
import sys
import queue
import sounddevice as sd    # 比 pyaudio 更简单
import vosk
import json

# =================配置区域=================
# 获取当前脚本所在目录 (src)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 模型路径 (就是你放 model 文件夹的地方)
MODEL_PATH = os.path.join(current_dir, "..", "resources", "model")
# 采样率 (Vosk 模型通常需要 16000Hz)
SAMPLE_RATE = 16000 
# =========================================

# 检查模型是否连接
if not os.path.exists(MODEL_PATH):
    print(f"错误：找不到模型路径 '{MODEL_PATH}'")
    print("请确保你下载了 Vosk 模型并解压重命名 'model' 放在项目根目录下")
    sys.exit(1)

print("正在加载语音模型, 请稍后...")
try:
    # 加载模型
    model = vosk.Model(MODEL_PATH)
    print("模型加载成功！")
except Exception as e:
    print(f"模型加载失败: {e}")
    sys.exit(1)

# 创建识别器
# 这里 device=None 表示使用默认麦克风
rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)

# 创建一个队列来存放音频数据
q = queue.Queue()

# 定义一个回调函数: 当麦克风有数据的时候, sounddevice 会自动调用这个函数
def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # 将音频数据放入队列 (bytes格式)
    q.put(bytes(indata))

print("\n" + "="*40)
print("🎤 现在的你可以开始说话了 (按 Ctrl+C 退出)...")
print("="*40 + "\n")

try:
    # 打开麦克风流
    # samplerate: 采样率
    # blocksize: 缓冲区大小
    # dtype: 数据类型 (int16是标准音频格式)
    # channels: 通道数 (1=单声道)
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, device=None, 
                           dtype='int16', channels=1, callback=callback):
        
        # 这是一个死循环, 程序会一直运行直到强制退出
        while True:
            # 从队列里获取音频数据
            data = q.get()

            # 让 Vosk 识别这段数据
            if rec.AcceptWaveform(data):
                # 如果一句话说完了 (检测到停顿), 会进入这里
                result = json.loads(rec.Result())
                text = result['text']
                # 只有识别出文字才打印
                if text.strip() != "":
                    print(f"最终识别: [{text}]")
                if "再见" in text or "结束" in text:
                    print("识别已结束，再见！")
                    break

            else:
                # 如果正在说话中 (连续流), 会进入到这里
                # PartialResult 会返回实时的 "正在说..." 的内容
                partial = json.loads(rec.PartialResult())
                # 我们这里可以不打印 partial, 也可以打印出来看看效果
                print(f"Listening... {partial['partial']}", end='\r')
                pass


except KeyboardInterrupt:
    print("\n\n程序已停止")
except Exception as e:
    print(f"\n发生错误: {e}")