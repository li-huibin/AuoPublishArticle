# -*- coding: utf-8 -*-

import re

class ArticleFormatter:
    """
    文章排版优化模块
    负责：
    1. 智能分段 - 按语义和长度自动分段
    2. 添加小标题 - 为关键段落生成小标题
    3. 优化阅读体验 - 控制段落长度，增加可读性
    """

    def __init__(self, llm_client):
        self.llm = llm_client

    def format_article(self, article_text, add_subtitles=False, paragraph_length=60, ultra_mode=False):
        """
        综合排版优化
        
        Args:
            article_text: 原始文章文本
            add_subtitles: 是否添加小标题
            paragraph_length: 建议的段落长度（字数，默认60字更适合手机阅读）
            ultra_mode: 是否启用超级碎片化模式（40-50字/段，适合地铁、马桶等场景）
            
        Returns:
            格式化后的文章
        """
        print(f"\n{'='*50}")
        print(f"【排版优化】")
        print(f"{'='*50}")
        print(f"[*] 原文长度: {len(article_text)}字")
        print(f"[*] 添加小标题: {'是' if add_subtitles else '否'}")
        print(f"[*] 目标段落长度: {paragraph_length}字")
        print(f"[*] 碎片化模式: {'开启' if ultra_mode else '关闭'}")
        
        # 第一步：智能分段
        if ultra_mode:
            # 超级碎片化模式：40-50字/段
            formatted_text = self.auto_paragraph(article_text, 45)
        else:
            formatted_text = self.auto_paragraph(article_text, paragraph_length)
        
        # 第二步：如果需要，添加小标题
        if add_subtitles:
            formatted_text = self.add_subtitles(formatted_text)
        
        print(f"[+] 排版完成")
        return formatted_text

    def auto_paragraph(self, text, target_length=60):
        """
        智能分段 - 针对手机阅读优化（更激进的策略）
        
        策略：
        1. 使用LLM识别文章的逻辑结构
        2. 在合适的位置分段
        3. 控制段落长度，确保手机阅读体验
        4. 优先在疑问句、转折词、强调句后分段
        """
        # 计算合理的段落长度范围（手机阅读场景）
        min_length = int(target_length * 0.5)  # 最短50%（更激进）
        max_length = int(target_length * 1.2)  # 最长120%（更严格）
        
        prompt = f"""
请对下面这篇文章进行智能分段，让它更适合手机阅读。这次要分得更细，让读者读起来更轻松。

【核心目标】
让读者在手机上阅读时，每个段落都能一眼扫完，有明显的呼吸感和节奏感。

【分段原则（更激进的策略）】
1. **段落长度**：每段控制在 {min_length}-{max_length} 字（目标 {target_length} 字）
   - 手机屏幕有限，宁可段落多一点，也不要让读者看得累
   - 一般1-2个完整的句子就可以考虑分段
   - 特别短的金句（如"太他妈对了"、"说白了"等）可以单独成段

2. **强制分段点**（遇到这些必须分段）：
   🔴 疑问句结尾（"？"后立即分段）
   🔴 转折词开头（"但是"、"可是"、"不过"、"然而"开头的句子独立成段）
   🔴 强调词开头（"你想啊"、"说白了"、"我就直说了"开头的句子独立成段）
   🔴 对话或引用（带引号的内容独立成段）
   🔴 数据或案例（具体数字、百分比独立成段）
   🔴 情绪转折（从支持到反对，从乐观到悲观，立即分段）

3. **优先分段点**（这些地方优先考虑分段）：
   ⚠️ 观点表达完整后
   ⚠️ 例子举完后
   ⚠️ 话题切换时
   ⚠️ 总结陈词前
   ⚠️ 设问、反问后

4. **阅读体验**：
   - 每段要有明确的"一个点"，不要贪多
   - 重要观点、金句必须单独成段，让它更突出
   - 对比、反转要分开成两段，制造冲击感
   - 宁可多分，不要少分

5. **禁止事项**：
   ❌ 不要在句子中间断开
   ❌ 不要修改或删减原文任何内容
   ❌ 不要添加小标题或其他内容

【优化示例】

❌ 优化前（段落太长）：
你想啊，无线耳机，AirPods那种，刚出来的时候多酷啊。没有线，往耳朵里一塞，科技感拉满。我也跟风买过。可这东西，你得当个祖宗供着。你得记得给它充电。放那个小盒子里，忘了，第二天出门，好嘛，没电了。

✅ 优化后（节奏明快）：
你想啊，无线耳机，AirPods那种，刚出来的时候多酷啊。

没有线，往耳朵里一塞，科技感拉满。我也跟风买过。

可这东西，你得当个祖宗供着。

你得记得给它充电。放那个小盒子里，忘了，第二天出门，好嘛，没电了。

---

❌ 优化前：
最戳我的，是看到有网友说那句话："有些消费升级走到后面，用户开始不想再伺候它了。"太他妈对了。

✅ 优化后：
最戳我的，是看到有网友说那句话：

"有些消费升级走到后面，用户开始不想再伺候它了。"

太他妈对了。

【原文】
{text}

【要求】
1. 直接输出分段后的文章，不要加任何说明或前言
2. 段落之间用一个空行分隔
3. 严格保持原文所有内容不变
4. 大胆分段，让每个段落都短小精悍，有节奏感
5. 遇到强制分段点必须分段，不要犹豫
"""

        try:
            formatted = self.llm.chat([
                {"role": "system", "content": "你是专业的手机端内容编辑，深谙移动阅读的节奏和体验。你的使命是让读者在地铁上、马桶上都能轻松看完文章。"},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            print(f"[+] 自动分段完成")
            return formatted
            
        except Exception as e:
            print(f"[!] 自动分段失败: {e}")
            # 降级方案：智能的按语义分段
            return self._simple_paragraph(text, target_length)

    def _simple_paragraph(self, text, target_length=60):
        """
        智能降级分段方案（更激进的策略）
        按语义和句子结构切分，优化手机阅读体验
        """
        print("[*] 使用智能降级分段方案（激进模式）")
        
        # 移除现有的多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        # 智能分句：处理各种复杂标点
        # 匹配句子结束标点：。！？，同时考虑引号、括号、省略号
        sentence_pattern = r'([^。！？]*[。！？…]["』」\)]?)'
        sentences = re.findall(sentence_pattern, text)
        
        # 过滤空句子并清理
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text
        
        paragraphs = []
        current_paragraph = ""
        min_paragraph_length = int(target_length * 0.5)  # 最小约30字（更激进）
        max_paragraph_length = int(target_length * 1.2)  # 最大约72字（更严格）
        
        # 语义分段关键词（用于识别自然的分段点）- 扩充列表
        transition_words = ['但是', '不过', '然而', '所以', '因此', '那么', '你想啊', '说白了', '问题是', 
                          '可是', '我就直说了', '你看', '哎', '嘿', '好嘛', '说实话']
        # 强调词（这些开头的句子倾向于独立成段）
        emphasis_words = ['太', '真', '就是', '关键', '最', '特别']
        
        for i, sentence in enumerate(sentences):
            # 如果当前段落为空，直接添加
            if not current_paragraph:
                current_paragraph = sentence
                continue
            
            # 预测添加这句话后的长度
            predicted_length = len(current_paragraph) + len(sentence)
            
            # 检查句子特征
            is_transition = any(sentence.strip().startswith(word) for word in transition_words)
            is_question = sentence.strip().endswith('？')
            is_emphasis = any(sentence.strip().startswith(word) for word in emphasis_words)
            is_quote = '"' in sentence or '"' in sentence or '"' in sentence
            is_short_punch = len(sentence) < 15  # 短句（可能是金句）
            
            # 决策逻辑（更激进的分段策略）：
            
            # 1. 强制分段点：疑问句、引用、转折词开头
            if is_question or is_quote or (is_transition and len(current_paragraph) >= 10):
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
                
            # 2. 金句处理：特别短的句子（可能是强调、感叹）
            elif is_short_punch and len(current_paragraph) >= min_paragraph_length * 0.7:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
                
            # 3. 强调句开头：优先独立成段
            elif is_emphasis and len(current_paragraph) >= min_paragraph_length * 0.6:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
                
            # 4. 当前段落太短（< 50%目标），继续添加
            elif len(current_paragraph) < min_paragraph_length:
                current_paragraph += sentence
                
            # 5. 添加后会超过最大长度，分段
            elif predicted_length > max_paragraph_length:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
                
            # 6. 当前段落接近目标长度（> 80%），考虑分段
            elif len(current_paragraph) >= target_length * 0.8:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
                
            # 7. 否则继续添加
            else:
                current_paragraph += sentence
        
        # 添加最后一段
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
        
        # 后处理：如果某段过长，尝试进一步拆分
        final_paragraphs = []
        for para in paragraphs:
            if len(para) > max_paragraph_length * 1.8:
                # 找中间位置的句号拆分
                mid_point = len(para) // 2
                split_point = -1
                
                # 在中点前后寻找最佳拆分点
                for offset in range(0, len(para) // 2):
                    if mid_point + offset < len(para) and para[mid_point + offset] in '。！？':
                        split_point = mid_point + offset + 1
                        break
                    if mid_point - offset >= 0 and para[mid_point - offset] in '。！？':
                        split_point = mid_point - offset + 1
                        break
                
                if split_point > 0:
                    final_paragraphs.append(para[:split_point].strip())
                    final_paragraphs.append(para[split_point:].strip())
                else:
                    final_paragraphs.append(para)
            else:
                final_paragraphs.append(para)
        
        result = '\n\n'.join(final_paragraphs)
        print(f"[+] 智能降级分段完成，共 {len(final_paragraphs)} 段，平均每段 {len(result)//len(final_paragraphs) if final_paragraphs else 0} 字")
        return result

    def add_subtitles(self, text):
        """
        为文章添加小标题
        
        策略：
        1. 识别文章的主要段落
        2. 为关键段落生成简洁的小标题
        3. 小标题要能概括段落核心
        """
        # 根据文章长度自适应小标题数量
        article_length = len(text)
        if article_length < 500:
            subtitle_count = "1-2个"
        elif article_length < 1000:
            subtitle_count = "2-3个"
        else:
            subtitle_count = "3-4个"
        
        prompt = f"""
请为下面这篇文章的关键段落添加小标题。小标题必须从文章的具体内容中提炼，不能使用通用的空话。

【核心要求】
⚠️ 小标题必须直接提炼该段落的核心观点、具体事实或关键论点
⚠️ 严禁使用"我的看法"、"说实话"、"关键在这儿"等空洞表述
⚠️ 必须让读者一看标题就知道这段讲什么具体内容

【小标题原则】
1. **数量**：建议添加 {subtitle_count} 个小标题（不是每段都要）
2. **长度**：5-10个字
3. **格式**：## 标题内容（Markdown二级标题）
4. **位置**：在文章关键转折点添加
   - 引出核心矛盾或现象时
   - 观点发生转折时
   - 揭示问题本质时
   - 总结升华时

【小标题类型（从段落内容中提炼）】

**类型一：提炼具体现象/事实**
例如文中讲"有线耳机销量涨了20%，年轻人在买"：
✅ "20块耳机重回C位"
✅ "有线耳机销量暴涨"
❌ "新趋势来了"（太空泛）
❌ "市场变化"（没有信息量）

**类型二：提炼核心矛盾/反差**
例如文中讲"以前拼命想摆脱的土东西，现在成了潮流"：
✅ "被淘汰的土玩意儿成了香饽饽"
✅ "无线变累赘，有线成救星"
❌ "形势逆转"（说了等于没说）
❌ "意外的变化"（太模糊）

**类型三：提炼观点态度**
例如文中讲"年轻人不想再伺候无线耳机了"：
✅ "不想当无线耳机的保姆"
✅ "伺候不动这些聪明设备了"
❌ "年轻人的选择"（没有态度）
❌ "新的想法"（没有信息）

**类型四：提炼痛点/问题**
例如文中讲"充电、配对、怕丢，烦不胜烦"：
✅ "三大痛点让人崩溃"
✅ "天天惦记充电和配对"
❌ "使用体验"（太宽泛）
❌ "一些问题"（没有具体性）

【反面案例（禁止使用的通用标题）】
❌ "我的看法"、"说实话"、"问题来了"
❌ "关键在这儿"、"重点是"、"核心问题"
❌ "深入分析"、"具体来说"、"总结一下"
❌ "年轻人怎么想"、"市场变化"、"新趋势"

这些标题太空泛，必须具体化：
- "我的看法" → 根据文中具体观点改为"别被无线自由忽悠了"
- "年轻人怎么想" → 根据具体内容改为"不想天天伺候电子产品"
- "问题来了" → 根据具体问题改为"手机都没耳机孔了咋办"

【操作步骤】
1. 先通读全文，找出3-4个关键转折点或核心段落
2. 对每个关键段落，用一句话概括它的核心内容（具体的事实、观点或现象）
3. 把这句话精炼成5-10个字的小标题
4. 检查：标题是否包含具体信息？如果去掉上下文，读者能否理解标题说的是什么？
5. 在对应段落前添加小标题（格式：## 标题）

【原文】
{text}

【输出要求】
1. 直接输出添加了小标题的文章，不要加任何说明
2. 严格保持原文内容不变（一个字都不改）
3. 保持原有的段落分隔（空行）
4. 小标题使用 ## 格式，小标题后空一行再接正文
5. 小标题必须具体、有信息量，能独立理解
"""

        try:
            result = self.llm.chat([
                {"role": "system", "content": "你是专业的文章编辑，擅长为文章添加画龙点睛的小标题。"},
                {"role": "user", "content": prompt}
            ], temperature=0.5)
            
            print(f"[+] 小标题添加完成")
            return result
            
        except Exception as e:
            print(f"[!] 小标题添加失败: {e}")
            return text

    def optimize_readability(self, text):
        """
        优化可读性
        包括：
        1. 确保段落间有空行
        2. 清理多余的空行
        3. 确保标题格式正确
        """
        # 清理多余的空行（超过2个连续换行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 确保标题前后有空行
        text = re.sub(r'([^\n])\n(##\s)', r'\1\n\n\2', text)
        text = re.sub(r'(##\s[^\n]+)\n([^\n])', r'\1\n\n\2', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
