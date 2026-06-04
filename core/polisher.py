# -*- coding: utf-8 -*-

import re
from prompts.anti_ai_rules import FORBIDDEN_WORDS, STYLE_GUIDE

class Polisher:
    """
    润色模块：负责检查和修改 AI 生成的内容，去除 'AI 味'。
    包含基于规则的过滤和基于 LLM 的重写。
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def basic_check(self, text):
        """
        基于规则的基础检查。
        返回包含的禁止词列表。
        """
        found_issues = []
        for word in FORBIDDEN_WORDS:
            if word in text:
                found_issues.append(word)
        return found_issues

    def polish(self, text):
        """
        使用 LLM 进行润色。
        """
        issues = self.basic_check(text)

        prompt = f"""
        任务：请润色以下文本，使其读起来更像人写的。

        原文存在的问题（包含以下禁止词）：{', '.join(issues) if issues else '暂无明显禁止词，但仍需优化'}

        风格指南：
        {STYLE_GUIDE}

        【重要内容标注要求】
        如果文中有重要内容（数据、关键观点、重点事件等），可以用 <strong> 标签包裹来加粗强调！
        例如：<strong>87.3%</strong>、<strong>2.54亿</strong>、<strong>2026年</strong>、<strong>2000条</strong>
        注意：只给真正重要的内容加粗，不要滥用！

        原文：
        {text}

        请直接输出润色后的文本：
        """

        messages = [
            {"role": "system", "content": "你是一位严格的文字编辑，痛恨陈词滥调和机器味。"},
            {"role": "user", "content": prompt}
        ]

        return self.llm.chat(messages, temperature=0.3)
