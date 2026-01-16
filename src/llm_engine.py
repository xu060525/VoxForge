import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 中的环境变量
load_dotenv()

class LLMEngine:
    def __init__(self):
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.model = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")

        if not self.api_key:
            print("警告: 未找到 SILICONFLOW_API_KEY, AI 功能将不可用。")
            self.client = None
        else:
            print(f"LLM 引擎已就绪 (模型: {self.model})")
            # 初始化客户端，指向硅基流动的地址
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.siliconflow.cn/v1"
            )

        # 定义系统人设 (Prompt Engineering)
        # 这决定了你的助手说话的风格
        self.system_prompt = {
            "role": "system",
            "content": """
            你叫 VoxForge, 是一个运行在用户电脑上的桌面语音助手。
            1. 回复必须简洁、口语化，适合 TTS (语音合成) 朗读。
            2. 尽量控制在 50 字以内，除非用户要求详细解释。
            3. 不要使用 Markdown 格式（如 **加粗**），直接输出纯文本。
            4. 语气要像钢铁侠的 Jarvis 一样专业、冷静但幽默。
            """
        }
        
        # 简单的对话历史 (短期记忆)，重启后丢失
        self.history = [self.system_prompt]

    def chat(self, user_input):
        """
        发送文本给 LLM 并获取回复
        """
        if not self.client:
            return "请先配置 API Key。"

        # 将用户输入加入历史
        self.history.append({"role": "user", "content": user_input})
        
        # 保持历史记录不无限增长 (只保留最近 10 轮)
        if len(self.history) > 10:
            # 保留 system prompt (index 0)，删除最早的对话
            self.history = [self.history[0]] + self.history[-9:]

        try:
            print("AI 正在思考...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                temperature=1, # 0.7 比较均衡，既有创造性又不太疯
                max_tokens=200   # 限制回答长度，防止废话太多
            )
            
            reply = response.choices[0].message.content
            
            # 将 AI 回复也加入历史
            self.history.append({"role": "assistant", "content": reply})
            
            return reply

        except Exception as e:
            print(f"LLM 请求失败: {e}")
            return "连接云端大脑失败，请检查网络。"

# 测试代码
if __name__ == "__main__":
    bot = LLMEngine()
    print(bot.chat("你是谁？"))