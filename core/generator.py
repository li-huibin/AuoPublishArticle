# -*- coding: utf-8 -*-

import json
import os
from typing import Optional, Dict, Any, Callable
from prompts.templates import (
    PERSONA_FULL_PROMPT,
    get_thinking_prompt,
    get_writing_prompt,
    get_revision_prompt_1,
    get_revision_prompt_2,
    get_title_prompt
)
from core.llm_client import LLMClient
from core.quality_checker import QualityChecker
from core.resource_collector import ResourceCollector
from core.formatter import ArticleFormatter


class ArticleGenerator:
    """
    核心生成器类（V4.0 - 真人化版）

    新流程：
    1. 收集资料
    2. 深度思考（不写文章，只回答问题）
    3. 一次性写作（基于思考，全文生成）
    4. 两轮修改
    5. 生成标题
    """

    # 温度配置 - 控制各阶段的创造性程度
    TEMPERATURE_CONFIG = {
        'thinking': 0.8,   # 思考阶段：更发散，鼓励多角度思考
        'writing': 0.7,    # 写作阶段：平衡创造性和连贯性
        'revision': 0.5,   # 修改阶段：更严谨，保持稳定输出
        'title': 0.8       # 标题生成：更创新，吸引眼球
    }

    def __init__(self, llm_client=None, provider=None, api_key=None, base_url=None, model=None,
                 with_images=False, image_source=None, images_per_section=1,
                 image_manager=None, wechat_client=None):
        if llm_client:
            self.llm = llm_client
        else:
            self.llm = LLMClient(provider=provider, api_key=api_key, base_url=base_url, model=model)

        self.checker = QualityChecker()

        # 初始化资料收集器
        self.resource_collector = ResourceCollector()
        
        # 初始化排版优化器
        self.formatter = ArticleFormatter(self.llm)

        # 图片相关配置（暂时保留，但不强制使用）
        self.with_images = with_images
        self.image_source = image_source
        self.images_per_section = images_per_section
        self.wechat_client = wechat_client
        self.image_manager = None

        if self.with_images:
            from core.image_manager import ImageManager
            if image_manager:
                self.image_manager = image_manager
            else:
                self.image_manager = ImageManager(
                    cache_dir=os.environ.get("IMAGE_CACHE_DIR", "data/images"),
                    wechat_client=wechat_client
                )

    def _emit_progress(self, step: str, data: Dict[str, Any]) -> None:
        """
        发送进度更新（如果设置了回调函数）
        
        Args:
            step: 进度步骤标识
            data: 进度数据
        """
        if self.progress_callback:
            try:
                self.progress_callback(step, data)
            except Exception as e:
                print(f"[!] 进度回调失败: {e}")

    def generate_article(self, topic: str, collect_resources: bool = True, max_resources: int = 5, 
                        progress_callback: Optional[Callable] = None,
                        auto_format: bool = True, add_subtitles: bool = False, 
                        paragraph_length: int = 60, persona_id: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        生成文章（新流程：思考-写作-修改-排版）

        Args:
            topic: 文章主题
            collect_resources: 是否收集网络资料
            max_resources: 每个来源最多收集的资料数
            progress_callback: 可选的进度回调函数，接收(step, data)参数
            auto_format: 是否启用自动排版优化（默认True）
            add_subtitles: 是否添加小标题（默认False，可按心情开启）
            paragraph_length: 段落建议长度（默认60字，更适合手机阅读）
            persona_id: 可选的人设ID，不指定则使用当前人设
            
        Returns:
            包含 'article' 和 'title' 的字典，失败时返回 None
        """
        # 保存回调函数引用
        self.progress_callback = progress_callback
        
        # 发送开始信号
        self._emit_progress("start", {"message": "开始生成文章", "topic": topic})
        # 重置图片管理器
        if self.image_manager:
            if hasattr(self.image_manager, 'reset_used_images'):
                self.image_manager.reset_used_images()

        # === 第一步：收集资料 ===
        self._emit_progress("collecting", {"message": "正在收集网络资料..."})
        resources_text = ""
        resources = None

        if collect_resources:
            try:
                print(f"\n{'='*50}")
                print(f"【第一步：资料收集】")
                print(f"{'='*50}")
                resources = self.resource_collector.collect_resources(topic, max_results=max_resources)
                resources_text = self.resource_collector.format_resources_for_prompt(resources)

                # 保存资料
                self.resource_collector.save_resources(resources, topic)
                
                self._emit_progress("collected", {
                    "message": "资料收集完成",
                    "count": len(resources) if resources else 0
                })

                # 检查资料质量
                print(f"\n{'='*50}")
                print(f"【资料质量检查】")
                print(f"{'='*50}")
                quality_check = self.resource_collector.check_resource_quality(resources)
                print(f"📊 质量评分: {quality_check['quality_score']}/100")

                if not quality_check['has_valid_data']:
                    print(f"\n❌ 资料质量太差，无法生成有意义的文章")
                    return None

                print(f"\n✅ 资料质量检查通过")

            except Exception as e:
                print(f"[!] 资料收集失败: {e}")
                resources_text = ""
                resources = None

        # === 第二步：深度思考 ===
        self._emit_progress("thinking", {"message": "正在深度思考..."})
        print(f"\n{'='*50}")
        print(f"【第二步：深度思考】")
        print(f"{'='*50}")
        print("[*] 正在思考这个话题...")

        thinking_text = self._deep_think(topic, resources_text, persona_id)
        if not thinking_text:
            print("[!] 思考失败，使用简化模式...")
            thinking_text = "直接开始写吧。"
        
        self._emit_progress("thought", {
            "message": "思考完成",
            "preview": thinking_text[:200] if thinking_text else ""
        })

        # === 第三步：一次性写作 ===
        self._emit_progress("writing", {"message": "正在撰写初稿..."})
        print(f"\n{'='*50}")
        print(f"【第三步：写初稿】")
        print(f"{'='*50}")
        print("[*] 正在写初稿...")

        article_text = self._write_draft(topic, thinking_text, resources_text, persona_id)
        if not article_text:
            print("[!] 写作失败")
            self._emit_progress("error", {"message": "写作失败"})
            return None
        
        self._emit_progress("drafted", {
            "message": "初稿完成",
            "length": len(article_text)
        })

        # === 第四步：第一轮修改（加细节） ===
        self._emit_progress("revising_1", {"message": "第一轮修改：加细节..."})
        print(f"\n{'='*50}")
        print(f"【第四步：修改 - 加细节】")
        print(f"{'='*50}")
        print("[*] 正在修改（第一轮）...")

        article_text = self._revise_1(article_text, persona_id)
        
        self._emit_progress("revised_1", {"message": "第一轮修改完成"})

        # === 第五步：第二轮修改（去AI味） ===
        self._emit_progress("revising_2", {"message": "第二轮修改：去AI味..."})
        print(f"\n{'='*50}")
        print(f"【第五步：修改 - 去AI味】")
        print(f"{'='*50}")
        print("[*] 正在修改（第二轮）...")

        article_text = self._revise_2(article_text, persona_id)
        
        self._emit_progress("revised_2", {"message": "第二轮修改完成"})

        # === 第六步：排版优化 ===
        if auto_format:
            self._emit_progress("formatting", {"message": "正在优化排版..."})
            article_text = self.formatter.format_article(
                article_text,
                add_subtitles=add_subtitles,
                paragraph_length=paragraph_length
            )
            self._emit_progress("formatted", {"message": "排版优化完成"})

        # === 第七步：生成标题 ===
        self._emit_progress("generating_title", {"message": "正在生成标题..."})
        print(f"\n{'='*50}")
        print(f"【第六步：起标题】")
        print(f"{'='*50}")
        print("[*] 正在起标题...")

        title = self._generate_title(article_text, persona_id)
        
        self._emit_progress("title_generated", {
            "message": "标题生成完成",
            "title": title
        })

        # === 第八步：质量检查（仅报告，不重试） ===
        self._emit_progress("checking", {"message": "正在进行质量检查..."})
        print(f"\n{'='*50}")
        print(f"【质量检查】")
        print(f"{'='*50}")

        check_result = self.checker.check(article_text)
        print(f"\n🤖 AI味检测得分: {check_result['ai_score']}/100")
        print(f"✨ 真实感检测得分: {check_result['reality_score']}/100")
        print(f"📊 综合得分: {check_result['total_score']:.1f}/100")
        
        self._emit_progress("checked", {
            "message": "质量检查完成",
            "scores": check_result
        })

        # 组装最终文章
        final_article = f"# {title}\n\n"
        final_article += article_text
        
        self._emit_progress("completed", {
            "message": "文章生成完成",
            "title": title,
            "article": final_article,
            "length": len(final_article)
        })

        return {
            "article": final_article,
            "title": title
        }

    def _deep_think(self, topic: str, resources_text: str, persona_id: Optional[str] = None) -> Optional[str]:
        """
        深度思考阶段
        
        Args:
            topic: 文章主题
            resources_text: 格式化后的资料文本
            persona_id: 可选的人设ID
            
        Returns:
            思考结果文本，失败时返回 None
        """
        prompt = get_thinking_prompt(
            topic=topic,
            resources_text=resources_text or "暂时没有资料，凭你的理解来想。",
            persona_id=persona_id
        )

        try:
            # 动态获取人设提示词
            from prompts.persona_manager import get_persona_manager
            manager = get_persona_manager()
            persona_prompts = manager.get_persona_prompt(persona_id)
            
            thinking_result = self.llm.chat([
                {"role": "system", "content": persona_prompts["full_prompt"]},
                {"role": "user", "content": prompt}
            ], temperature=self.TEMPERATURE_CONFIG['thinking'])

            print(f"\n[+] 思考完成：")
            print("-" * 50)
            print(thinking_result)
            print("-" * 50)

            return thinking_result

        except Exception as e:
            print(f"[!] 思考失败: {e}")
            return None

    def _write_draft(self, topic: str, thinking_text: str, resources_text: str, persona_id: Optional[str] = None) -> Optional[str]:
        """
        写初稿阶段：一次性全文生成
        
        Args:
            topic: 文章主题
            thinking_text: 思考阶段的输出
            resources_text: 格式化后的资料文本
            persona_id: 可选的人设ID
            
        Returns:
            初稿文本，失败时返回 None
        """
        prompt = get_writing_prompt(
            topic=topic,
            thinking_text=thinking_text,
            resources_text=resources_text or "没有收集到资料，基于常识来写，但别编太离谱的。",
            persona_id=persona_id
        )

        try:
            # 动态获取人设提示词
            from prompts.persona_manager import get_persona_manager
            manager = get_persona_manager()
            persona_prompts = manager.get_persona_prompt(persona_id)
            
            draft = self.llm.chat([
                {"role": "system", "content": persona_prompts["full_prompt"]},
                {"role": "user", "content": prompt}
            ], temperature=self.TEMPERATURE_CONFIG['writing'])

            print(f"\n[+] 初稿完成（{len(draft)}字）")
            return draft

        except Exception as e:
            print(f"[!] 写作失败: {e}")
            return None

    def _revise_1(self, article_text: str, persona_id: Optional[str] = None) -> str:
        """
        第一轮修改：加细节
        
        Args:
            article_text: 初稿文本
            persona_id: 可选的人设ID
            
        Returns:
            修改后的文本，失败时返回原文本
        """
        prompt = get_revision_prompt_1(article_text=article_text, persona_id=persona_id)

        try:
            # 动态获取人设提示词
            from prompts.persona_manager import get_persona_manager
            manager = get_persona_manager()
            persona_prompts = manager.get_persona_prompt(persona_id)
            
            revised = self.llm.chat([
                {"role": "system", "content": persona_prompts["full_prompt"]},
                {"role": "user", "content": prompt}
            ], temperature=self.TEMPERATURE_CONFIG['revision'])

            print("[+] 第一轮修改完成")
            return revised if revised else article_text

        except Exception as e:
            print(f"[!] 第一轮修改失败: {e}")
            return article_text

    def _revise_2(self, article_text: str, persona_id: Optional[str] = None) -> str:
        """
        第二轮修改：去AI味
        
        Args:
            article_text: 第一轮修改后的文本
            persona_id: 可选的人设ID
            
        Returns:
            修改后的文本，失败时返回原文本
        """
        prompt = get_revision_prompt_2(article_text=article_text, persona_id=persona_id)

        try:
            # 动态获取人设提示词
            from prompts.persona_manager import get_persona_manager
            manager = get_persona_manager()
            persona_prompts = manager.get_persona_prompt(persona_id)
            
            revised = self.llm.chat([
                {"role": "system", "content": persona_prompts["full_prompt"]},
                {"role": "user", "content": prompt}
            ], temperature=self.TEMPERATURE_CONFIG['revision'])

            print("[+] 第二轮修改完成")
            return revised if revised else article_text

        except Exception as e:
            print(f"[!] 第二轮修改失败: {e}")
            return article_text

    def _generate_title(self, article_text: str, persona_id: Optional[str] = None) -> str:
        """
        生成标题
        
        Args:
            article_text: 文章正文
            persona_id: 可选的人设ID
            
        Returns:
            生成的标题，失败时返回默认标题
        """
        prompt = get_title_prompt(article_text=article_text, persona_id=persona_id)

        try:
            # 动态获取人设提示词
            from prompts.persona_manager import get_persona_manager
            manager = get_persona_manager()
            persona_prompts = manager.get_persona_prompt(persona_id)
            
            result = self.llm.chat([
                {"role": "system", "content": persona_prompts["full_prompt"]},
                {"role": "user", "content": prompt}
            ], temperature=self.TEMPERATURE_CONFIG['title'])

            # 尝试提取第一个标题
            lines = result.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('1.') and not line.startswith('2.') and not line.startswith('3.'):
                    print(f"[+] 标题：{line}")
                    return line
                if line.startswith('1.'):
                    title = line[2:].strip()
                    print(f"[+] 标题：{title}")
                    return title

            # 保底
            print(f"[+] 标题：{lines[0] if lines else '热点解读'}")
            return lines[0] if lines else "热点解读"

        except Exception as e:
            print(f"[!] 标题生成失败: {e}")
            return "热点解读"

    def record_published_article(self, topic: str, title: str, url: str, 
                                article_data: Dict[str, Any]) -> None:
        """
        记录发布的文章（保留兼容性）
        
        Args:
            topic: 文章主题
            title: 文章标题
            url: 发布URL
            article_data: 文章相关数据
        """
        try:
            record_file = "data/published_articles.json"
            os.makedirs(os.path.dirname(record_file), exist_ok=True)

            record = {
                "topic": topic,
                "title": title,
                "url": url,
                "timestamp": article_data.get("timestamp"),
                "quality_score": article_data.get("quality_score"),
                "article_length": article_data.get("article_length")
            }

            records = []
            if os.path.exists(record_file):
                with open(record_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)

            records.append(record)

            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[! 记录发布文章失败: {e}")
