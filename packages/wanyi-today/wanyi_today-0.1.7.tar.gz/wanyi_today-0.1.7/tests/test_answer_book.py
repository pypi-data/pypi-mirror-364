"""
答案之书功能的测试用例
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from wanyi_today.main import detect_answer_book_trigger, generate_mysterious_answer, answer_book


class TestAnswerBook(unittest.TestCase):
    """答案之书功能测试类"""
    
    def test_detect_answer_book_trigger_with_slash_command(self):
        """测试检测/答案之书指令"""
        self.assertTrue(detect_answer_book_trigger("/答案之书"))
        self.assertTrue(detect_answer_book_trigger("我想使用/答案之书"))
        self.assertTrue(detect_answer_book_trigger("请帮我/答案之书一下"))
    
    def test_detect_answer_book_trigger_with_keyword(self):
        """测试检测答案之书关键词"""
        self.assertTrue(detect_answer_book_trigger("答案之书"))
        self.assertTrue(detect_answer_book_trigger("我想咨询答案之书"))
        self.assertTrue(detect_answer_book_trigger("请问答案之书有什么建议"))
    
    def test_detect_answer_book_trigger_case_insensitive(self):
        """测试不区分大小写的检测"""
        self.assertTrue(detect_answer_book_trigger("答案之书"))
        self.assertTrue(detect_answer_book_trigger("答案之书"))
        self.assertTrue(detect_answer_book_trigger("答案之书"))
    
    def test_detect_answer_book_trigger_negative_cases(self):
        """测试不应该触发的情况"""
        self.assertFalse(detect_answer_book_trigger("普通的问题"))
        self.assertFalse(detect_answer_book_trigger("今天天气怎么样"))
        self.assertFalse(detect_answer_book_trigger(""))
        self.assertFalse(detect_answer_book_trigger(None))
    
    def test_generate_mysterious_answer(self):
        """测试神秘回答生成"""
        # 生成多个回答，确保都是字符串且不为空
        for _ in range(10):
            answer = generate_mysterious_answer()
            self.assertIsInstance(answer, str)
            self.assertGreater(len(answer), 0)
            self.assertLess(len(answer), 20)  # 确保回答简短
    
    def test_answer_book_tool_with_trigger(self):
        """测试答案之书工具触发情况"""
        result = answer_book("/答案之书")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        # 确保不是提示信息
        self.assertNotIn("请在你的问题中包含", result)
    
    def test_answer_book_tool_without_trigger(self):
        """测试答案之书工具未触发情况"""
        result = answer_book("普通问题")
        self.assertIn("请在你的问题中包含", result)
    
    def test_answer_book_tool_input_validation(self):
        """测试输入验证"""
        # 测试空输入
        result = answer_book("")
        self.assertTrue("请提供有效的文本输入" in result or "请输入一些文字" in result)
        
        # 测试空白字符输入
        result = answer_book("   ")
        self.assertIn("请输入一些文字", result)
    
    def test_answer_book_tool_various_inputs(self):
        """测试各种输入情况"""
        test_cases = [
            ("我想问答案之书一个问题", True),
            ("/答案之书 今天运势如何", True),
            ("答案之书，我应该做什么", True),
            ("今天天气不错", False),
            ("普通的聊天内容", False)
        ]
        
        for input_text, should_trigger in test_cases:
            result = answer_book(input_text)
            if should_trigger:
                self.assertNotIn("请在你的问题中包含", result)
            else:
                self.assertIn("请在你的问题中包含", result)


if __name__ == '__main__':
    unittest.main()