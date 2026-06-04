# -*- coding: utf-8 -*-

"""
简单质量检查器
仅做基础的 AI 味和真实感检测，不做自适应学习
"""

import re
from prompts.anti_ai_rules import DETECTION_CONFIG


class QualityChecker:
    """
    简单质量检查器
    """

    def __init__(self):
        # 加载检测配置
        self.forbidden_symbols = DETECTION_CONFIG["forbidden_symbols"]
        self.forbidden_words = DETECTION_CONFIG["forbidden_words"]
        self.max_fake_names = DETECTION_CONFIG.get("max_fake_names", 1)
        self.max_repeated_questions = DETECTION_CONFIG.get("max_repeated_questions", 1)

    def check(self, text):
        """
        执行质量检查

        Args:
            text: 文章内容

        Returns:
            检查结果字典
        """
        # AI 味检测
        ai_issues, ai_score = self._check_ai_flavor(text)

        # 真实感检测
        reality_details, reality_score = self._check_reality(text)

        # 综合得分
        total_score = (ai_score + reality_score) / 2

        return {
            "ai_score": ai_score,
            "ai_issues": ai_issues,
            "reality_score": reality_score,
            "reality_details": reality_details,
            "total_score": total_score
        }

    def _check_ai_flavor(self, text):
        """
        检测 AI 味

        Args:
            text: 文章内容

        Returns:
            (问题列表, 得分)
        """
        issues = []
        score = 100

        # 1. 检测禁用符号
        for symbol in self.forbidden_symbols:
            count = text.count(symbol)
            if count > 0:
                issues.append(f"发现禁用符号 '{symbol}'（出现 {count} 次）")
                score -= count * 20

        # 2. 检测禁用词汇
        for word in self.forbidden_words:
            if word in text:
                count = text.count(word)
                issues.append(f"发现禁用词汇 '{word}'（出现 {count} 次）")
                score -= count * 5

        # 3. 检测假名
        fake_names = ["小张", "小李", "小王", "小刘", "老张", "老李", "老王"]
        fake_count = sum(text.count(name) for name in fake_names)
        if fake_count > self.max_fake_names:
            excess = fake_count - self.max_fake_names
            issues.append(f"假名使用过多（{fake_count} 个）")
            score -= excess * 10

        # 4. 检测重复疑问句
        repeated_questions = [
            "看出差别了吗", "明白了吗", "懂了吗",
            "理解了吗", "清楚了吗", "发现了吗"
        ]
        for question in repeated_questions:
            count = text.count(question)
            if count > self.max_repeated_questions:
                excess = count - self.max_repeated_questions
                issues.append(f"重复疑问句 '{question}'（出现 {count} 次）")
                score -= excess * 10

        # 5. 检测禁用句式
        forbidden_patterns = [
            r"不是[^，。]{1,10}，更是",
            r"不仅[^，。]{1,10}，而是",
            r"从[^，。]{1,10}到[^，。]{1,10}，从",
        ]
        for pattern in forbidden_patterns:
            matches = re.findall(pattern, text)
            if matches:
                issues.append(f"发现禁用句式（出现 {len(matches)} 次）")
                score -= len(matches) * 8

        # 6. 检测教学结构
        if "错误示范" in text or "正确示范" in text:
            issues.append("发现教学式结构（错误示范/正确示范）")
            score -= 15

        score = max(0, score)
        return issues, score

    def _check_reality(self, text):
        """
        检测真实感

        Args:
            text: 文章内容

        Returns:
            (详情列表, 得分)
        """
        details = []
        score = 100

        # 1. 检查是否有具体公司名
        company_names = ["字节跳动", "腾讯", "阿里巴巴", "百度", "美团", "京东",
                        "拼多多", "网易", "小米", "华为", "阿里", "B站", "微博",
                        "知乎", "微信", "QQ", "淘宝", "天猫", "抖音", "快手"]
        has_company = any(name in text for name in company_names)
        if not has_company:
            details.append("⚠️ 缺少具体公司名称")
            score -= 15

        # 2. 检查是否有具体数据
        number_pattern = r'\d{1,3}%|\d{1,4}亿|\d{1,3}万|\d{4}年|\d{1,2}月|\d{1,2}日'
        has_numbers = bool(re.search(number_pattern, text))
        if not has_numbers:
            details.append("⚠️ 缺少具体数据（百分比、金额、时间等）")
            score -= 15

        # 3. 检查是否有第一人称表达
        first_person = ["我", "我觉得", "我认为", "在我看来", "依我看", "我的观点"]
        has_first_person = any(p in text for p in first_person)
        if not has_first_person:
            details.append("💡 建议增加第一人称表达，增强个人观点")
            score -= 10

        # 4. 检查细节丰富度
        if len(text) < 500:
            details.append("💡 文章较短，建议增加更多细节描述")
            score -= 10

        # 正面检查
        if has_company:
            details.append("✅ 包含具体公司名称")
        if has_numbers:
            details.append("✅ 包含具体数据")
        if has_first_person:
            details.append("✅ 包含第一人称表达")

        score = max(0, score)
        return details, score
