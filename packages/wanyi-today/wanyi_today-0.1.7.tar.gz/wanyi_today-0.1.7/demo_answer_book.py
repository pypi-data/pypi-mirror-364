#!/usr/bin/env python3
"""
答案之书功能演示脚本
"""

from wanyi_today.main import answer_book

def demo_answer_book():
    """演示答案之书功能"""
    print("=== 答案之书功能演示 ===\n")
    
    # 测试用例
    test_cases = [
        "/答案之书",
        "我想问答案之书一个问题",
        "答案之书，今天运势如何？",
        "普通问题，不包含关键词",
        "",
        "   ",
        "答案之书能告诉我未来吗？"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"测试 {i}: '{test_input}'")
        result = answer_book(test_input)
        print(f"回答: {result}")
        print("-" * 50)

if __name__ == "__main__":
    demo_answer_book()