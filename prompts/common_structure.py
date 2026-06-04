# -*- coding: utf-8 -*-

"""
通用写作结构库 (Common Writing Structure Library)
适用于所有人设的通用写作框架、思考模式和修改逻辑
"""

# 通用思考框架 - 适用于任何热点文章
COMMON_THINKING_FRAMEWORK = """
热点主题：{topic}

【资料】
{resources_text}

先别写文章，用清晰的语言快速回答6个问题，每点1-2句：

1. 核心事实一句话总结：谁、做了什么、关键数字或细节？
2. 最值得关注的细节是什么？为什么重要？
3. 事件中的主要矛盾或问题是什么？
4. 事件背后的深层原因是什么？（制度、利益、观念等）
5. 用一个生活化的比喻帮助理解这件事
6. 读者最关心什么？文章应该重点解答哪些疑问？

只回答问题，不写文章。
"""

# 通用文章结构规范
COMMON_ARTICLE_STRUCTURE = """
文章结构要求（1200–1500字）：

【开头（前150字）】
直接抛核心事实：谁、事件、数字/关键细节
不许铺垫、不许抒情、不许绕弯
开头必须分成2-3个短段，每段1-2句话，给读者视觉冲击

【主体】
- 清晰呈现：事件的来龙去脉和关键信息
- 分析矛盾：事件中各方的观点和立场
- 插入1个生活化比喻，帮助读者理解
- 提供背景：相关的制度、历史或社会因素
- 【可选】根据内容复杂度，插入1-2个小标题（如"事情经过"、"背后原因"、"多方观点"），但不强制

【结尾】
引发思考或提供启示：
提问 / 总结 / 呼吁关注 / 提供建议
结尾最后一句单独成段，增强印象
"""

# 通用语言要求
COMMON_LANGUAGE_RULES = """
语言要求：
- 短句为主，口语化表达，通俗易懂
- 表达清晰直接，避免抽象空话
- 禁止官话套话，禁止无意义总结
- 根据人设选择合适的表达视角

【段落排版规则（严格执行）】
1. 每段控制在2-4句话，约60-80字（移动端阅读最佳）
2. 重要观点、转折、金句要单独成段（1句话1段）
3. 避免连续3段以上的长段落，要有节奏变化
4. 多用换行，给读者视觉呼吸空间
5. 禁止大段文字堆砌（超过100字的段落必须拆分）
"""

# 第一轮修改 - 通用优化逻辑
COMMON_REVISION_1 = """
文章：
{article_text}

只改这4点，不动其他内容：
1. 开头强化：如果前150字信息不够充实，重写开头，确保包含人物+事件+关键数字/细节
2. 观点明确：如果表达模糊，补充清晰的分析和观点
3. 细节补充：如果缺少关键信息，从资料中补充最重要的细节
4. 语言优化：删掉书面语，换成口语化、通俗易懂的表达

改完直接输出全文。
"""

# 第二轮修改 - 通用润色逻辑
COMMON_REVISION_2 = """
文章：
{article_text}

微调优化：
1. 结尾强化：确保结尾有引发思考或行动的元素
2. 句式优化：拆分过长的句子，保持短句节奏
3. 语言润色：增加1-2处口语化表达，更自然易读
4. 真实感增强：适当加入个人观点或不确定性表达，避免过于绝对
5. 【重点】检查段落长度，超过80字的段落必须拆分成2-3段
6. 【重点】重要观点、转折句、金句要单独成段，增强视觉冲击
7. 如内容较长且复杂，可考虑加1-2个小标题（如"事情经过"、"背后原因"），但保持克制

只微调，不改结构，改完直接输出。
"""

# 标题冲突词库（常量定义）
CONFLICT_WORDS = "离谱、傻眼、绝了、吓人、扯淡、打脸、反转、刚刚、突然、紧急、终于"

# 通用标题生成规则
COMMON_TITLE_RULES = f"""
标题生成要求：

生成5个爆款标题，15–25字，按吸引力从高到低排列。

必须满足：
1. 含至少1个冲突词：{CONFLICT_WORDS}
2. 带具体信息：人物/机构/数字/时间
3. 用问号或冒号制造悬念/反差
4. 不抽象、不文艺、不官方

冲突词库：{CONFLICT_WORDS}

禁止：深度解读、一些思考、值得关注、无信息空话

直接输出5个标题，每行一个，不加序号。
"""

# 组装函数 - 将人设和通用结构组合
def build_thinking_prompt(topic: str, resources_text: str, persona_style: str = "") -> str:
    """
    构建思考提示词
    
    Args:
        topic: 热点主题
        resources_text: 资料文本
        persona_style: 人设风格补充（可选）
    """
    base = COMMON_THINKING_FRAMEWORK.format(
        topic=topic,
        resources_text=resources_text
    )
    if persona_style:
        return f"{persona_style}\n\n{base}"
    return base

def build_writing_prompt(topic: str, thinking_text: str, resources_text: str, 
                        persona_rules: str = "") -> str:
    """
    构建写作提示词
    
    Args:
        topic: 热点主题
        thinking_text: 思考文本
        resources_text: 资料文本
        persona_rules: 人设特有规则（可选）
    """
    structure = COMMON_ARTICLE_STRUCTURE
    language = COMMON_LANGUAGE_RULES
    
    prompt = f"""热点主题：{topic}

【你的思考】
{thinking_text}

【资料】
{resources_text}

现在写一篇完整热点文章，严格按结构来：

{structure}

{language}"""
    
    if persona_rules:
        prompt = f"{persona_rules}\n\n{prompt}"
    
    prompt += "\n\n直接开始写，不要任何前缀。"
    return prompt

def build_revision_prompt_1(article_text: str, persona_style: str = "") -> str:
    """构建第一轮修改提示词"""
    base = COMMON_REVISION_1.format(article_text=article_text)
    if persona_style:
        return f"{persona_style}\n\n{base}"
    return base

def build_revision_prompt_2(article_text: str, persona_style: str = "") -> str:
    """构建第二轮修改提示词"""
    base = COMMON_REVISION_2.format(article_text=article_text)
    if persona_style:
        return f"{persona_style}\n\n{base}"
    return base

def build_title_prompt(article_text: str, persona_style: str = "") -> str:
    """构建标题生成提示词"""
    prompt = f"""文章：
{article_text}

{COMMON_TITLE_RULES}"""
    
    if persona_style:
        prompt = f"{persona_style}\n\n{prompt}"
    return prompt
