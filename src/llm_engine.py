import os
import json
import re
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
            你叫 VoxForge, 是一个拥有系统控制权限的桌面 AI 助手。
            
            【核心规则】
            1. 正常聊天时, 请用简短、幽默的口语回答 (50字以内) 。
            2. 当用户要求【创建文件/写代码/保存文本】时：
               不要直接输出代码！不要说话！
               必须严格且只输出以下 JSON 格式：
               
               {
                   "action": "create_file",
                   "filename": "文件名(含后缀)",
                   "content": "文件完整内容"
               }
            
            3. 只能输出纯 JSON, 不要包含 Markdown 代码块（如 ```json ... ```）。
            4. 语气要像钢铁侠的 Jarvis 一样专业、冷静但幽默。
            """
        }
        
        # 简单的对话历史 (短期记忆)，重启后丢失
        self.history = [self.system_prompt]

    def chat(self, user_input):
        """
        发送文本给 LLM 并获取回复
        """
        if not self.client: return "请先配置 API Key。"

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
                temperature=0.7, # 0.7 比较均衡，既有创造性又不太疯
                max_tokens=2000   # 限制回答长度，防止废话太多
            )
            
            reply_content = response.choices[0].message.content.strip()
            
            # === 智能解析逻辑 ===

            # 尝试寻找 JSON 格式的命令
            json_match = re.search(r'\{.*"action":\s*"create_file".*\}', reply_content, re.DOTALL)

            if json_match:
                # 提取 JSON 字符串
                json_str = json_match.group(0)
                try:
                    command = json.loads(json_str)
                    # 返回一个特殊的字典，告诉 actions.py 这不是普通对话，是指令
                    return {
                        "type": "command",
                        "data": command, 
                    }
                except json.JSONDecodeError:
                    print("AI 返回了类似 JSON 但格式错误的内容")

            # 如果没找到 JSON，就当普通聊天处理
            self.history.append({"role": "assistant", "content": reply_content})
            return {
                "type": "text",
                "data": reply_content
            }

        except Exception as e:
            print(f"LLM 错误: {e}")
            return {"type": "text", "data": "大脑掉线了。"}

# 测试代码
if __name__ == "__main__":
    bot = LLMEngine()
    print(bot.chat("你是谁？"))