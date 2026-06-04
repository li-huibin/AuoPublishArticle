# -*- coding: utf-8 -*-
from prompts.templates import (
    PERSONA_SYSTEM_PROMPT,
    get_thinking_prompt,
    get_writing_prompt,
    get_revision_prompt_1,
    get_revision_prompt_2,
    get_title_prompt,
)

print("[OK] 提示词导入成功")
print(f"人设长度: {len(PERSONA_SYSTEM_PROMPT)}")

thinking = get_thinking_prompt(topic="测试主题", resources_text="无")
print(f"思考提示词长度: {len(thinking)}")

writing = get_writing_prompt(topic="测试主题", thinking_text="无", resources_text="无")
print(f"写作提示词长度: {len(writing)}")

rev1 = get_revision_prompt_1(article_text="测试文章")
print(f"修改提示词1长度: {len(rev1)}")

rev2 = get_revision_prompt_2(article_text="测试文章")
print(f"修改提示词2长度: {len(rev2)}")

title = get_title_prompt(article_text="测试文章")
print(f"标题提示词长度: {len(title)}")

print("[OK] 所有函数接口测试通过")
