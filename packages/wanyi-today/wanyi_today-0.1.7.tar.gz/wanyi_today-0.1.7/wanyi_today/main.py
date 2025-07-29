"""
Wanyi Today - 一个基于 FastMCP 的演示服务器。

该服务器提供数字相加工具和答案之书功能。
"""

import random
from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP("Wanyi Today")


def detect_answer_book_trigger(text: str) -> bool:
    """检测用户输入是否包含答案之书触发词
    
    Args:
        text: 用户输入的文本
        
    Returns:
        如果包含触发词则返回True，否则返回False
    """
    if not text:
        return False
    
    # 定义触发词列表
    triggers = ["/答案之书", "答案之书"]
    
    # 转换为小写进行不区分大小写的匹配
    text_lower = text.lower()
    
    # 检查是否包含任何触发词
    return any(trigger.lower() in text_lower for trigger in triggers)


def generate_mysterious_answer() -> str:
    """生成神秘的答案之书回答
    
    Returns:
        随机选择的神秘回答
    """
    # 预定义的神秘回答列表，风格模棱两可且简短
    mysterious_answers = [
        "时机未到",
        "答案就在你心中",
        "或许是，或许不是",
        "静待花开",
        "一切皆有可能",
        "顺其自然",
        "缘分自有安排",
        "耐心等待",
        "相信直觉",
        "命运自有定数",
        "不必强求",
        "水到渠成",
        "心诚则灵",
        "随遇而安",
        "天时地利人和",
        "机会总会来临",
        "保持初心",
        "万事皆空",
        "因果循环",
        "道法自然"
    ]
    
    # 随机选择一个回答
    return random.choice(mysterious_answers)


@mcp.tool()
def add(a: int, b: int) -> int:
    """将两个数字相加
    
    Args:
        a: 第一个数字
        b: 第二个数字
        
    Returns:
        两个数字的和
    """
    return a + b


@mcp.tool()
def answer_book(user_input: str) -> str:
    """答案之书 - 为你的问题提供神秘的回答
    
    当用户输入包含"/答案之书"或"答案之书"关键词时，
    将返回一个简短且模棱两可的神秘回答。
    
    Args:
        user_input: 用户的输入文本
        
    Returns:
        神秘的回答或使用提示
    """
    try:
        # 输入验证
        if not user_input or not isinstance(user_input, str):
            return "请提供有效的文本输入。"
        
        # 去除首尾空白字符
        user_input = user_input.strip()
        
        if not user_input:
            return "请输入一些文字来咨询答案之书。"
        
        # 检测是否包含触发关键词
        if detect_answer_book_trigger(user_input):
            # 生成神秘回答
            return generate_mysterious_answer()
        else:
            # 提供使用提示
            return "请在你的问题中包含'答案之书'或使用'/答案之书'指令来获得神秘的回答。"
    
    except Exception as e:
        # 错误处理，返回默认神秘回答
        return "命运之轮正在转动..."



def main():
    """服务器的主入口点"""
    # 根据 FastMCP 文档，使用 run 方法启动服务器
    mcp.run()


if __name__ == "__main__":
    main()