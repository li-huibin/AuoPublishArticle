# -*- coding: utf-8 -*-

"""
人设模板库 - 动态加载版
支持从 PersonaManager 动态加载不同人设
"""

from typing import Optional
from prompts.common_structure import (
    build_thinking_prompt,
    build_writing_prompt,
    build_revision_prompt_1,
    build_revision_prompt_2,
    build_title_prompt
)
from prompts.persona_manager import get_persona_manager

# ==================== 人设配置定义 ====================

# 1. 人设基本信息 - 角色定位和背景
PERSONA_PROFILE = """
你是一位热点事件观察者，专注于用平实的语言讲清楚正在发生的事。

定位：
- 理性、客观、接地气
- 帮读者看懂事件的来龙去脉
- 提供多角度思考，而非单一立场
- 关注事实本身，而非情绪宣泄
"""

# 2. 人设风格指南 - 核心差异化特征
PERSONA_STYLE_GUIDE = """
说话风格（严格执行）：
- 短句为主，每段2-4句话，避免大段堆砌
- 口语化但不过度：比如说、其实、简单来说、换句话说
- 避免情绪化词汇，保持中性客观的表达
- 适度疑问引导思考：值得注意的是、有意思的是、问题在于

排版节奏感：
- 开头2-3个短段直击核心事实（每段1-2句）
- 中间段落2-4句为一组，逻辑清晰
- 关键转折、重要观点可单独成段
- 结尾引发思考，最后一句单独成段
"""

# 3. 人设写作规则 - 内容要求
PERSONA_WRITING_RULES = """
写作规则（必须全部遵守）：
1. 开头直接说事实：谁、做了什么、关键数字/细节，分成2-3个短段
2. 用生活化比喻解释复杂概念，避免专业术语堆砌
3. 提供事件背景和多角度分析，帮助读者理解全貌
4. 客观呈现不同观点，不强行站队或制造对立
5. 结尾引发思考或总结启示（最后一句单独成段）
6. 禁止抒情散文，禁止个人日记式写作
7. 只写资料里有的内容，不编造、不脑补、不过度延伸
8. 语言平实自然，像跟朋友聊天一样讲清楚事情
9. 【排版铁律】每段不超过80字，重要观点单独成段，避免连续长段落
"""

# 4. 完整人设提示词 - 用于主要生成阶段（思考、写作）
PERSONA_FULL_PROMPT = f"""
{PERSONA_PROFILE}

{PERSONA_STYLE_GUIDE}

{PERSONA_WRITING_RULES}
"""

# 5. 润色指南 - 用于修改阶段的语言风格强化
PERSONA_POLISH_GUIDE = """
保持平实自然的表达：
- 适度口语化：比如说、其实、简单来说、换句话说
- 引导思考：值得注意的是、有意思的是、问题在于
- 避免情绪化词汇，保持客观中性
"""

# ==================== 组装完整提示词（动态版） ====================

def get_thinking_prompt(topic: str, resources_text: str, persona_id: Optional[str] = None) -> str:
    """
    获取思考提示词
    
    Args:
        topic: 主题
        resources_text: 资源文本
        persona_id: 人设ID，如果为None则使用当前人设
    """
    manager = get_persona_manager()
    persona_prompts = manager.get_persona_prompt(persona_id)
    
    return build_thinking_prompt(
        topic=topic,
        resources_text=resources_text,
        persona_style=persona_prompts["profile"]  # 带入人设背景
    )

def get_writing_prompt(topic: str, thinking_text: str, resources_text: str, persona_id: Optional[str] = None) -> str:
    """
    获取写作提示词
    
    Args:
        topic: 主题
        thinking_text: 思考文本
        resources_text: 资源文本
        persona_id: 人设ID，如果为None则使用当前人设
    """
    manager = get_persona_manager()
    persona_prompts = manager.get_persona_prompt(persona_id)
    
    return build_writing_prompt(
        topic=topic,
        thinking_text=thinking_text,
        resources_text=resources_text,
        persona_rules=persona_prompts["full_prompt"]  # 完整人设规则
    )

def get_revision_prompt_1(article_text: str, persona_id: Optional[str] = None) -> str:
    """
    获取第一轮修改提示词
    
    Args:
        article_text: 文章文本
        persona_id: 人设ID，如果为None则使用当前人设
    """
    manager = get_persona_manager()
    persona_prompts = manager.get_persona_prompt(persona_id)
    
    return build_revision_prompt_1(
        article_text=article_text,
        persona_style=persona_prompts["polish_guide"]  # 强化语言风格
    )

def get_revision_prompt_2(article_text: str, persona_id: Optional[str] = None) -> str:
    """
    获取第二轮修改提示词
    
    Args:
        article_text: 文章文本
        persona_id: 人设ID，如果为None则使用当前人设
    """
    manager = get_persona_manager()
    persona_prompts = manager.get_persona_prompt(persona_id)
    
    return build_revision_prompt_2(
        article_text=article_text,
        persona_style=persona_prompts["polish_guide"]  # 强化语言风格
    )

def get_title_prompt(article_text: str, persona_id: Optional[str] = None) -> str:
    """
    获取标题生成提示词
    
    Args:
        article_text: 文章文本
        persona_id: 人设ID（标题生成通常不需要特别强调人设）
    """
    return build_title_prompt(
        article_text=article_text,
        persona_style=""  # 标题生成不需要特别强调人设
    )
