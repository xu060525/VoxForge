import os

class ToolBox:
    def __init__(self):
        # 获取桌面路径
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    def create_file(self, filename, content):
        """
        在桌面创建文件
        """
        try:
            full_path = os.path.join(self.desktop_path, filename)
            
            # 写入文件
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return True, f"文件已成功创建在桌面: {full_path}"
        except Exception as e:
            return False, f"创建文件失败: {e}"

# 单独测试
if __name__ == "__main__":
    tools = ToolBox()
    tools.create_file("test_agent.txt", "这是 AI 自动创建的文件！")
    print("测试完成，请检查桌面。")