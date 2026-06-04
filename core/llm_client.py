# -*- coding: utf-8 -*-

import os
import json
import time

class LLMClient:
    """
    LLM 客户端封装。
    支持 'mock' 模式和 'openai' 模式。
    使用 OpenAI 官方客户端，确保与智谱AI等兼容API的完全兼容性。
    """

    def __init__(self, provider=None, api_key=None, base_url=None, model=None):
        # 优先使用传入参数，否则读取环境变量
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        # 如果指定了 provider，则使用指定的
        if provider:
            self.provider = provider
        # 否则，如果有 key，自动切到 openai 模式
        elif self.api_key:
            self.provider = "openai"
        else:
            self.provider = "mock"

        if self.provider == "openai" and not self.api_key:
            print("[!] 警告: 设置为 OpenAI 模式但未找到 API Key，将回退到 Mock 模式。")
            self.provider = "mock"
        
        # 初始化 OpenAI 客户端（仅在 openai 模式下）
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                print("[!] 警告: 未安装 openai 库，将回退到 Mock 模式。")
                print("[!] 请运行: pip install openai")
                self.provider = "mock"

    def chat(self, messages, temperature=0.7):
        """
        发送聊天请求。
        :param messages: 消息列表 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        :param temperature: 温度参数
        :return: LLM 的回复文本
        """
        if self.provider == "mock":
            return self._mock_response(messages)
        elif self.provider == "openai":
            return self._openai_request(messages, temperature)
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented yet.")

    def _openai_request(self, messages, temperature):
        """
        使用 OpenAI 官方客户端发送请求，包含自动重试机制
        """
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                if attempt == 0:
                    print(f"[*] 正在请求 API (可能需要几十秒，请耐心等待)...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    timeout=120.0  # 设置120秒超时
                )
                
                return response.choices[0].message.content
            
            except Exception as e:
                error_msg = str(e)
                
                # 检查是否是速率限制或服务器错误，这些情况下应重试
                should_retry = (
                    "rate_limit" in error_msg.lower() or
                    "429" in error_msg or
                    "500" in error_msg or
                    "502" in error_msg or
                    "503" in error_msg or
                    "504" in error_msg or
                    "timeout" in error_msg.lower()
                )
                
                if should_retry and attempt < max_retries - 1:
                    print(f"[!] 遇到可重试错误，正在等待 {retry_delay} 秒后重试 (第 {attempt + 1} 次)...")
                    print(f"[!] 错误信息: {error_msg}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                
                # 不可重试的错误或重试耗尽
                print(f"[!] API 请求失败: {error_msg}")
                return f"Error: API request failed - {error_msg}"
                
        return "Error: Maximum retries exceeded"

    def _mock_response(self, messages):
        """
        模拟 LLM 的回复，用于测试流程。
        """
        time.sleep(1) # 模拟网络延迟
        last_user_msg = messages[-1]["content"]

        print(f"[*] [Mock] 收到请求: {last_user_msg[:30]}...")

        # 简单的逻辑判断来返回不同的模拟数据
        if "JSON格式的大纲" in last_user_msg or "JSON 格式的大纲" in last_user_msg:
            return json.dumps({
                "title": "为什么我不建议你现在学 Python",
                "angle": "从市场供需失衡的角度，反直觉地劝退新手。",
                "sections": [
                    "事儿是这样的",
                    "数据不说谎",
                    "为什么现在",
                    "本质问题",
                    "启示"
                ]
            }, ensure_ascii=False)
        
        elif "你正在写一篇文章" in last_user_msg or "你正在为\"小苏的热事笔记\"" in last_user_msg:
            # 模拟段落生成（带有深度解读的示例）
            return """昨天下午，办公室的空调坏了，面试者汗流浃背地坐在我对面。
我看了一眼他的简历，精通 Django、Flask、Pandas... 写得很漂亮。

但当我问他列表和元组的区别时，他卡住了。
这本身没什么，谁都会有紧张的时候。但你想过没有——
为什么一个培训班出来的孩子，简历上写满了框架，但连最基础的概念都不懂？

这说明现在的培训行业已经走偏了。
他们不是在教编程，而是在教"怎么通过面试"。
结合另一条资料说的"培训班就业率造假"，
我们可以得出一个结论：这是一个典型的"逆向选择"市场。"""
        
        elif "深度阅读者" in last_user_msg or "深度分析" in last_user_msg:
            # 模拟深度分析结果（三层深度结构）
            return json.dumps({
                "第一层：事实层": {
                    "关键事实梳理": [
                        "这是一条模拟的关键事实",
                        "这是另一条模拟的关键事实",
                        "这是第三条模拟的关键事实"
                    ],
                    "时间线梳理": ["事件按时间顺序发展的模拟梳理"],
                    "各方观点汇总": {
                        "支持方观点": ["支持方的模拟观点"],
                        "反对方观点": ["反对方的模拟观点"],
                        "中立/其他观点": ["中立的模拟观点"]
                    },
                    "数据整理": ["模拟数据（来源：模拟资料）"],
                    "资料可信度评估": ["模拟的可信度评估"]
                },
                "第二层：解读层": {
                    "资料之间的联系": {
                        "互相印证的资料": ["资料X和资料Y都提到了..."],
                        "有矛盾的资料": ["资料X说...，但资料Y说...，可能的原因是..."],
                        "组合得出的新结论": ["把资料A和资料B放在一起看，得出的新结论"]
                    },
                    "原因深度分析": {
                        "为什么是现在发生": "模拟的时间点原因分析",
                        "表层导火索": "模拟的直接触发原因",
                        "深层驱动因素": "模拟的深层根本原因"
                    },
                    "矛盾与争议点": ["资料中体现的核心矛盾是什么"]
                },
                "第三层：洞察层": {
                    "本质洞察": {
                        "抛开表面看本质": "这件事的本质到底是什么",
                        "一句话说透": "用最精炼的语言概括这件事的核心"
                    },
                    "历史对比": {
                        "类似历史事件": "历史上类似的事件",
                        "当时的发展和结果": "当时的发展和结果",
                        "这次的不同之处": "这次和历史上的事件有什么不一样"
                    },
                    "趋势研判": {
                        "短期影响": "短期（1-3个月）会带来什么影响",
                        "长期影响": "长期（1年以上）会带来什么改变",
                        "对普通人的启示": "对普通人有什么启示"
                    }
                },
                "视角锚点与逻辑链条": {
                    "最佳切入视角": "从矛盾切入（模拟视角）",
                    "视角选择理由": "为什么选这个视角的理由",
                    "核心逻辑链条": [
                        "起点：最核心的事实是什么",
                        "追问1：这个事实的直接原因是什么",
                        "追问2：这个原因背后的深层原因是什么",
                        "追问3：这会导致什么结果",
                        "追问4：这个结果又会引发什么",
                        "终点：读者应该记住什么核心洞察"
                    ]
                },
                "写作思路建议": {
                    "最有冲击力的事实": "模拟的最有冲击力的事实",
                    "可以展开的争议点": "模拟的争议点",
                    "标题建议": ["模拟标题1", "模拟标题2"]
                }
            }, ensure_ascii=False)

        elif "润色" in last_user_msg:
            # 模拟润色，简单返回原文本加标记，防止死循环
            # 从 user message 中提取原文
            original_text = last_user_msg.split("原文：")[1].split("请直接输出")[0].strip() if "原文：" in last_user_msg else "模拟内容"
            return f"{original_text} [已润色]"

        else:
            return "这是 LLM 的模拟回复。"
