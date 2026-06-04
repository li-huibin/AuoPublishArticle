# -*- coding: utf-8 -*-
"""
图片管理器 - 负责搜索、下载、上传图片
支持 Unsplash、Pexels、Pixabay 等免费图库 API
"""
import os
import requests
import time
import random
import hashlib
from typing import Optional, List, Dict, Tuple


class ImageManager:
    """图片管理器类"""

    # 中英文关键词映射表 - 用于将中文主题翻译成英文搜索关键词
    KEYWORD_TRANSLATIONS = {
        # 科技类
        "人工智能": ["artificial intelligence", "AI", "machine learning", "neural network", "robotics"],
        "AI": ["artificial intelligence", "AI", "machine learning", "robot"],
        "机器人": ["robot", "robotics", "automation", "android"],
        "无人驾驶": ["autonomous vehicle", "self-driving car", "driverless car", "automotive"],
        "自动驾驶": ["self-driving", "autonomous driving", "driverless"],
        "区块链": ["blockchain", "cryptocurrency", "bitcoin", "digital currency"],
        "大数据": ["big data", "data science", "analytics", "database"],
        "云计算": ["cloud computing", "cloud", "server", "data center"],
        "5G": ["5G", "network", "telecommunication", "wireless"],
        "元宇宙": ["metaverse", "virtual reality", "VR", "augmented reality", "digital world"],
        "算法": ["algorithm", "code", "programming", "software"],
        "芯片": ["chip", "semiconductor", "processor", "electronics"],
        "手机": ["smartphone", "mobile phone", "iphone", "android"],
        "电脑": ["computer", "laptop", "pc", "desktop"],
        "互联网": ["internet", "web", "digital", "online"],
        "科技": ["technology", "tech", "innovation", "digital"],

        # 商业/经济类
        "经济": ["economy", "finance", "business", "market"],
        "金融": ["finance", "banking", "investment", "stock market"],
        "股市": ["stock market", "trading", "investment", "finance"],
        "创业": ["startup", "entrepreneur", "business", "innovation"],
        "公司": ["company", "corporation", "business", "office"],
        "企业": ["enterprise", "business", "corporation", "company"],
        "市场": ["market", "shopping", "commerce", "retail"],
        "投资": ["investment", "finance", "stock", "trading"],
        "货币": ["money", "currency", "cash", "finance"],
        "银行": ["bank", "banking", "finance", "money"],

        # 社会/热点类
        "事件": ["event", "incident", "happening", "news"],
        "新闻": ["news", "journalism", "media", "newspaper"],
        "社会": ["society", "social", "community", "people"],
        "城市": ["city", "urban", "skyline", "metropolis"],
        "生活": ["life", "lifestyle", "living", "everyday"],
        "家庭": ["family", "home", "domestic", "household"],
        "教育": ["education", "school", "university", "learning"],
        "医疗": ["healthcare", "hospital", "medical", "health"],
        "健康": ["health", "wellness", "fitness", "medical"],
        "环境": ["environment", "nature", "eco", "sustainability"],
        "气候": ["climate", "weather", "environment", "global warming"],
        "政策": ["policy", "government", "politics", "law"],
        "法律": ["law", "legal", "justice", "court"],
        "安全": ["security", "safety", "protection", "secure"],

        # 文化/娱乐类
        "电影": ["movie", "film", "cinema", "theater"],
        "音乐": ["music", "concert", "musician", "audio"],
        "游戏": ["game", "gaming", "play", "esports"],
        "体育": ["sports", "athletics", "game", "competition"],
        "艺术": ["art", "artist", "creative", "gallery"],
        "文化": ["culture", "heritage", "tradition", "arts"],
        "旅游": ["travel", "tourism", "journey", "trip"],
        "美食": ["food", "cuisine", "restaurant", "delicious"],
        "时尚": ["fashion", "style", "trend", "clothing"],

        # 通用概念
        "未来": ["future", "tomorrow", "vision", "forward"],
        "历史": ["history", "past", "historical", "ancient"],
        "时间": ["time", "clock", "hour", "moment"],
        "空间": ["space", "universe", "cosmos", "astronomy"],
        "问题": ["problem", "challenge", "issue", "question"],
        "解决": ["solution", "solve", "answer", "resolve"],
        "变化": ["change", "transform", "transition", "evolution"],
        "发展": ["development", "growth", "progress", "evolution"],
        "创新": ["innovation", "creative", "invention", "new"],
        "挑战": ["challenge", "obstacle", "difficulty", "struggle"],
        "机遇": ["opportunity", "chance", "possibility", "fortune"],
        "矛盾": ["conflict", "contradiction", "tension", "debate"],
        "观点": ["opinion", "perspective", "viewpoint", "idea"],
        "分析": ["analysis", "analyze", "study", "research"],
        "背景": ["background", "context", "foundation", "basis"],
        "启示": ["insight", "inspiration", "lesson", "wisdom"],
        "建议": ["suggestion", "advice", "recommendation", "tip"],
    }

    # 兜底通用关键词（当所有特定关键词都找不到图片时使用）
    FALLBACK_KEYWORDS = [
        "technology", "business", "abstract", "concept", "modern",
        "digital", "future", "innovation", "connection", "network",
        "city", "people", "office", "work", "data", "chart",
        "communication", "information", "knowledge", "wisdom"
    ]

    # 章节类型关键词 - 为不同类型的章节提供多样化的关键词
    SECTION_TYPE_KEYWORDS = {
        # 事件/故事类章节 - 更具体、场景化
        "事件": ["accident", "incident", "scene", "moment", "street", "road", "city life", "news event"],
        "事儿": ["story", "scene", "moment", "daily life", "urban", "street", "city"],
        "背景": ["history", "background", "context", "timeline", "evolution", "past", "retro"],
        "数据": ["data", "statistics", "chart", "graph", "dashboard", "analytics", "numbers", "report"],
        "分析": ["analysis", "thinking", "brainstorm", "mind map", "strategy", "planning", "deep thought"],
        "观点": ["opinion", "debate", "discussion", "conversation", "meeting", "forum", "different views"],
        "矛盾": ["conflict", "tension", "balance", "scale", "dilemma", "challenge", "opposite"],
        "问题": ["problem", "challenge", "puzzle", "question mark", "thinking", "solution"],
        "本质": ["essence", "core", "center", "focus", "depth", "deep", "fundamental"],
        "启示": ["insight", "inspiration", "lightbulb", "idea", "epiphany", "wisdom", "learning"],
        "建议": ["advice", "guidance", "direction", "path", "roadmap", "plan", "next step"],
        "未来": ["future", "vision", "tomorrow", "forward", "horizon", "predict", "forecast"],
        "怎么办": ["solution", "action", "step", "path", "forward", "progress", "way forward"],
    }

    # 视觉多样性关键词 - 用于增加图片视觉风格的多样性
    VISUAL_VARIETY_KEYWORDS = [
        ["close up", "detail", "macro"],
        ["wide shot", "panoramic", "landscape"],
        ["aerial view", "from above", "bird's eye"],
        ["night", "evening", "dark"],
        ["sunset", "sunrise", "golden hour"],
        ["blur", "bokeh", "shallow depth of field"],
        ["black and white", "monochrome"],
        ["vintage", "retro", "old style"],
        ["minimal", "simple", "clean"],
        ["busy", "crowded", "complex"],
    ]

    def __init__(self, cache_dir: str = "data/images", wechat_client=None):
        """
        初始化图片管理器

        Args:
            cache_dir: 图片缓存目录
            wechat_client: 微信客户端实例（用于上传图片）
        """
        self.cache_dir = cache_dir
        self.wechat_client = wechat_client

        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)

        # 加载 API 配置
        self.unsplash_access_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY", "")
        self.pixabay_api_key = os.environ.get("PIXABAY_API_KEY", "")

        # 默认图片源
        self.default_source = os.environ.get("IMAGE_DEFAULT_SOURCE", "unsplash")

        # 请求超时设置
        self.timeout = 30

        # 调试模式（输出更详细的日志）
        self.debug = True

        # 记录已使用的图片ID，避免重复
        self.used_image_ids = set()

        # 章节计数器，用于增加关键词多样性
        self.section_count = 0

    def search_images(self, keyword: str, count: int = 1, source: str = None) -> List[Dict]:
        """
        搜索相关图片

        Args:
            keyword: 搜索关键词
            count: 需要的图片数量
            source: 图片源 (unsplash/pexels/pixabay)，None 则自动选择

        Returns:
            图片信息列表，每个包含 url、thumbnail、author 等字段
        """
        if not source:
            source = self._get_available_source()

        if not source:
            print("[!] 没有可用的图片 API 源")
            return []

        print(f"[*] 正在从 {source} 搜索图片: '{keyword}'")

        try:
            if source == "unsplash":
                return self._search_unsplash(keyword, count)
            elif source == "pexels":
                return self._search_pexels(keyword, count)
            elif source == "pixabay":
                return self._search_pixabay(keyword, count)
            else:
                print(f"[!] 不支持的图片源: {source}")
                return []
        except Exception as e:
            print(f"[!] 搜索图片失败: {e}")
            return []

    def _get_available_source(self) -> Optional[str]:
        """获取可用的图片源"""
        if self.unsplash_access_key:
            return "unsplash"
        if self.pexels_api_key:
            return "pexels"
        if self.pixabay_api_key:
            return "pixabay"
        return None

    def _search_unsplash(self, keyword: str, count: int) -> List[Dict]:
        """从 Unsplash 搜索图片"""
        if not self.unsplash_access_key:
            print("[!] 未配置 UNSPLASH_ACCESS_KEY")
            return []

        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": keyword,
            "per_page": min(count * 5, 50),  # 获取更多结果以便筛选
            "client_id": self.unsplash_access_key
        }

        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "id": item["id"],
                "url": item["urls"]["small"],  # 使用 small 尺寸而不是 regular，文件更小
                "thumbnail": item["urls"]["thumb"],
                "author": item["user"]["name"],
                "link": item["links"]["html"],
                "source": "unsplash",
                "description": item.get("description", "") or item.get("alt_description", "")
            })

        if self.debug:
            print(f"[*] Unsplash 返回了 {len(results)} 张图片")

        # 如果有结果，进行简单的相关性筛选，而不是随机选择
        if len(results) > count:
            results = self._rank_and_select_images(results, keyword, count)
        else:
            results = results[:count]

        if self.debug and results:
            print(f"[+] 最终选择了 {len(results)} 张图片")

        return results

    def _search_pexels(self, keyword: str, count: int) -> List[Dict]:
        """从 Pexels 搜索图片"""
        if not self.pexels_api_key:
            print("[!] 未配置 PEXELS_API_KEY")
            return []

        url = "https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": keyword,
            "per_page": min(count * 5, 80)  # 获取更多结果以便筛选
        }

        resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("photos", []):
            results.append({
                "id": str(item["id"]),
                "url": item["src"]["medium"],  # 使用 medium 尺寸，文件更小
                "thumbnail": item["src"]["small"],
                "author": item["photographer"],
                "link": item["url"],
                "source": "pexels",
                "description": item.get("alt", "")
            })

        if self.debug:
            print(f"[*] Pexels 返回了 {len(results)} 张图片")

        # 如果有结果，进行简单的相关性筛选
        if len(results) > count:
            results = self._rank_and_select_images(results, keyword, count)
        else:
            results = results[:count]

        return results

    def _search_pixabay(self, keyword: str, count: int) -> List[Dict]:
        """从 Pixabay 搜索图片"""
        if not self.pixabay_api_key:
            print("[!] 未配置 PIXABAY_API_KEY")
            return []

        url = "https://pixabay.com/api/"
        params = {
            "key": self.pixabay_api_key,
            "q": keyword,
            "per_page": min(count * 5, 200),  # 获取更多结果以便筛选
            "image_type": "photo",
            "safesearch": "true"
        }

        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("hits", []):
            results.append({
                "id": str(item["id"]),
                "url": item["webformatURL"],  # 使用 webformat 而不是 largeImageURL，文件更小
                "thumbnail": item["previewURL"],
                "author": item["user"],
                "link": item["pageURL"],
                "source": "pixabay",
                "description": item.get("tags", "")
            })

        if self.debug:
            print(f"[*] Pixabay 返回了 {len(results)} 张图片")

        # 如果有结果，进行简单的相关性筛选
        if len(results) > count:
            results = self._rank_and_select_images(results, keyword, count)
        else:
            results = results[:count]

        return results

    def _rank_and_select_images(self, images: List[Dict], keyword: str, count: int) -> List[Dict]:
        """
        根据关键词对图片进行简单的相关性评分并选择最好的
        会跳过已使用的图片，避免重复

        Args:
            images: 图片列表
            keyword: 搜索关键词
            count: 需要选择的数量

        Returns:
            选择后的图片列表
        """
        keyword_lower = keyword.lower()
        keyword_words = set(keyword_lower.split())

        scored_images = []
        for img in images:
            # 跳过已使用的图片
            img_id = img.get("id")
            if img_id and img_id in self.used_image_ids:
                if self.debug:
                    print(f"[*] 跳过已使用图片: {img_id}")
                continue

            score = 0
            desc = img.get("description", "").lower()

            # 简单评分：描述中包含关键词的得分更高
            for word in keyword_words:
                if word and len(word) > 2:  # 只考虑较长的词
                    if word in desc:
                        score += 10

            # 随机加分，增加多样性
            score += random.randint(0, 10)

            scored_images.append((score, img))

        # 按分数排序，选择分数最高的
        scored_images.sort(key=lambda x: x[0], reverse=True)
        selected = [img for (score, img) in scored_images[:count]]

        # 记录已使用的图片
        for img in selected:
            img_id = img.get("id")
            if img_id:
                self.used_image_ids.add(img_id)
                if self.debug:
                    print(f"[*] 记录已使用图片: {img_id}")

        if self.debug and scored_images:
            available = len(scored_images)
            top_score = scored_images[0][0] if scored_images else 0
            print(f"[*] 最高相关性分数: {top_score}, 可选图片: {available}")

        return selected

    def reset_used_images(self):
        """重置已使用图片记录，用于新文章"""
        self.used_image_ids = set()
        self.section_count = 0
        if self.debug:
            print(f"[*] 已重置已使用图片记录和章节计数器")

    def _get_section_type_keywords(self, clean_section: str) -> List[str]:
        """
        根据章节标题获取章节类型关键词，增加多样性

        Args:
            clean_section: 清理后的章节标题

        Returns:
            章节类型关键词列表
        """
        type_keywords = []

        # 匹配章节类型
        for type_name, keywords in self.SECTION_TYPE_KEYWORDS.items():
            if type_name in clean_section:
                type_keywords.extend(keywords)
                break

        # 如果没有匹配到，根据章节序号返回通用多样性关键词
        if not type_keywords:
            # 根据章节序号选择不同的视觉风格关键词
            idx = self.section_count % len(self.VISUAL_VARIETY_KEYWORDS)
            type_keywords.extend(self.VISUAL_VARIETY_KEYWORDS[idx])

        return type_keywords

    def download_image(self, url: str, save_path: str = None) -> Optional[str]:
        """
        下载图片到本地

        Args:
            url: 图片 URL
            save_path: 保存路径，None 则自动生成

        Returns:
            保存的文件路径，失败返回 None
        """
        if not save_path:
            # 基于 URL 哈希生成文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            ext = self._get_extension_from_url(url)
            save_path = os.path.join(self.cache_dir, f"img_{url_hash}{ext}")

        # 如果已缓存，直接返回
        if os.path.exists(save_path):
            if self.debug:
                print(f"[*] 使用缓存图片: {os.path.basename(save_path)}")
            return save_path

        try:
            print(f"[*] 正在下载图片: {url[:60]}...")
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()

            with open(save_path, "wb") as f:
                f.write(resp.content)

            print(f"[+] 图片已保存: {save_path}")
            return save_path
        except Exception as e:
            print(f"[!] 下载图片失败: {e}")
            return None

    def _get_extension_from_url(self, url: str) -> str:
        """从 URL 提取文件扩展名"""
        url_lower = url.lower()
        if ".jpg" in url_lower or ".jpeg" in url_lower:
            return ".jpg"
        elif ".png" in url_lower:
            return ".png"
        elif ".gif" in url_lower:
            return ".gif"
        elif ".webp" in url_lower:
            return ".webp"
        return ".jpg"  # 默认

    def upload_to_wechat(self, image_path: str) -> Optional[str]:
        """
        上传图片到微信素材库

        Args:
            image_path: 本地图片路径

        Returns:
            微信 media_id，失败返回 None
        """
        if not self.wechat_client:
            print("[!] 未配置微信客户端，无法上传图片")
            return None

        try:
            print(f"[*] 正在上传图片到微信: {os.path.basename(image_path)}")
            media_id = self.wechat_client.upload_image(image_path)
            if media_id:
                print(f"[+] 上传成功，Media ID: {media_id}")
            return media_id
        except Exception as e:
            print(f"[!] 上传到微信失败: {e}")
            return None

    def get_related_image(self, topic: str, section_title: str = "",
                         images_per_section: int = 1, source: str = None,
                         upload_to_wechat: bool = False) -> List[Dict]:
        """
        获取某个章节的相关图片（完整流程：搜索 -> 下载 -> 上传）

        Args:
            topic: 文章主题
            section_title: 章节标题
            images_per_section: 每节图片数量
            source: 图片源
            upload_to_wechat: 是否上传到微信

        Returns:
            图片信息列表，每个包含 local_path、media_id（如果上传了）、url 等
        """
        # 增加章节计数器
        self.section_count += 1

        # 生成搜索关键词
        keywords = self._generate_search_keywords(topic, section_title)

        if self.debug:
            print(f"\n[*] 图片搜索关键词列表:")
            for i, kw in enumerate(keywords[:5], 1):  # 只显示前5个
                print(f"  {i}. {kw}")
            if len(keywords) > 5:
                print(f"  ... 还有 {len(keywords) - 5} 个")

        images = []
        for keyword in keywords:
            if len(images) >= images_per_section:
                break

            # 搜索图片
            image_infos = self.search_images(keyword, count=images_per_section - len(images), source=source)
            if not image_infos:
                continue

            for image_info in image_infos:
                if len(images) >= images_per_section:
                    break

                # 下载图片
                local_path = self.download_image(image_info["url"])
                if not local_path:
                    continue

                result = {
                    "local_path": local_path,
                    "image_url": image_info["url"],
                    "thumbnail": image_info["thumbnail"],
                    "author": image_info["author"],
                    "link": image_info["link"],
                    "source": image_info["source"],
                    "keyword": keyword
                }

                # 上传到微信
                if upload_to_wechat:
                    media_id = self.upload_to_wechat(local_path)
                    if media_id:
                        result["media_id"] = media_id

                images.append(result)
                if self.debug:
                    print(f"[+] 已获取图片 (关键词: {keyword})")

        if self.debug and images:
            print(f"[*] 共获取 {len(images)} 张图片")

        return images

    def _generate_search_keywords(self, topic: str, section_title: str) -> List[str]:
        """
        生成搜索关键词列表（按优先级排序）
        优先使用英文关键词，因为图库主要是英文内容
        会结合章节标题生成更具体的关键词，并增加多样性

        Args:
            topic: 文章主题
            section_title: 章节标题

        Returns:
            关键词列表
        """
        keywords = []

        # 1. 清理章节标题
        clean_section = ""
        if section_title:
            clean_section = self._clean_section_title(section_title)

        # 2. 生成英文关键词（优先）
        topic_english = self._translate_to_english(topic)

        # 3. 获取章节类型关键词（用于增加多样性）
        section_type_keywords = self._get_section_type_keywords(clean_section or "通用")

        if self.debug:
            print(f"[*] 章节 {self.section_count} - 类型关键词: {section_type_keywords[:3]}")

        # 4. 生成多样化的关键词组合
        if clean_section:
            section_english = self._translate_to_english(clean_section)

            # 组合1：章节类型 + 主题（高优先级，增加多样性）
            for stk in section_type_keywords[:3]:
                for tk in topic_english[:2]:
                    keywords.append(f"{stk} {tk}")
                    keywords.append(f"{tk} {stk}")

            # 组合2：章节 + 主题（具体）
            for sk in section_english[:2]:
                for tk in topic_english[:2]:
                    if sk != tk:
                        keywords.append(f"{sk} {tk}")
                        keywords.append(f"{tk} {sk}")

            # 单独章节关键词
            keywords.extend(section_english)
        else:
            # 没有章节标题时，用章节类型 + 主题
            for stk in section_type_keywords[:4]:
                for tk in topic_english[:2]:
                    keywords.append(f"{stk} {tk}")

        # 5. 章节类型关键词单独使用
        keywords.extend(section_type_keywords)

        # 6. 主题关键词
        keywords.extend(topic_english)

        # 7. 保留原始中文作为 fallback（某些图库可能支持中文）
        if clean_section:
            keywords.append(f"{topic} {clean_section}")
            keywords.append(clean_section)
        keywords.append(topic)

        # 8. 添加兜底通用关键词
        keywords.extend(self.FALLBACK_KEYWORDS)

        # 去重并返回
        result = list(dict.fromkeys(keywords))

        if self.debug:
            print(f"[*] 从主题 '{topic}' + 章节 '{clean_section}' (第{self.section_count}章) 生成了 {len(result)} 个搜索关键词")

        return result

    def _translate_to_english(self, chinese_text: str) -> List[str]:
        """
        将中文文本翻译成英文搜索关键词（使用预定义的映射表）

        Args:
            chinese_text: 中文文本

        Returns:
            英文关键词列表
        """
        results = []

        # 首先尝试精确匹配整个文本
        text_clean = chinese_text.strip()
        if text_clean in self.KEYWORD_TRANSLATIONS:
            results.extend(self.KEYWORD_TRANSLATIONS[text_clean])

        # 然后尝试匹配子字符串
        for cn_word, en_words in self.KEYWORD_TRANSLATIONS.items():
            if cn_word in chinese_text and cn_word != text_clean:
                results.extend(en_words)

        # 如果没有找到任何匹配，尝试一些简单的通用词
        if not results:
            # 提取文本中的核心概念（这里做简单处理）
            if "AI" in chinese_text or "智能" in chinese_text:
                results.extend(["artificial intelligence", "AI", "technology"])
            elif "科技" in chinese_text:
                results.extend(["technology", "tech", "innovation"])
            elif "经济" in chinese_text or "金融" in chinese_text:
                results.extend(["economy", "finance", "business"])
            elif "社会" in chinese_text:
                results.extend(["society", "people", "community"])
            else:
                # 最兜底的：使用一些通用科技/商业词汇
                results.extend(["technology", "business", "abstract", "concept"])

        # 去重并返回
        return list(dict.fromkeys(results))

    def _clean_section_title(self, title: str) -> str:
        """清理章节标题，移除编号等"""
        import re
        # 移除 "01 标题" 格式中的数字编号
        cleaned = re.sub(r'^\d+\s*', '', title.strip())
        # 移除常见的章节词
        for word in ["事件", "背景", "分析", "观点", "建议", "解读", "洞察", "启示"]:
            if cleaned == word:
                return ""
        return cleaned

    def get_image_html(self, image_info: Dict, caption: str = "", use_media_id: bool = False) -> str:
        """
        生成图片 HTML

        Args:
            image_info: 图片信息
            caption: 图片说明文字
            use_media_id: 是否使用微信 media_id（True=微信发布用，False=本地预览用）

        Returns:
            HTML 字符串
        """
        # 选择图片源
        img_src = None

        if use_media_id:
            # 微信发布模式：优先使用 media_id
            if "media_id" in image_info and image_info["media_id"]:
                img_src = image_info["media_id"]
                if self.debug:
                    print(f"[*] 使用微信 media_id: {img_src[:20]}...")
            elif "image_url" in image_info:
                # 降级：如果没有 media_id，使用 URL
                img_src = image_info["image_url"]
                if self.debug:
                    print(f"[*] media_id 不可用，降级使用 URL")
        else:
            # 本地预览模式：强制使用 image_url
            if "image_url" in image_info:
                img_src = image_info["image_url"]
                if self.debug:
                    print(f"[*] 本地预览模式，使用图片 URL")
            elif "media_id" in image_info:
                # 本地预览时，如果只有 media_id，警告并返回空
                print(f"[!] 警告：本地预览模式下，只有 media_id 没有 image_url，跳过该图片")
                return ""

        if not img_src:
            print(f"[!] 警告：没有可用的图片源，跳过该图片")
            return ""

        # 图片样式：固定高度 + object-fit 确保所有图片显示尺寸一致
        style = "width: 100%; max-width: 800px; height: 450px; object-fit: cover; border-radius: 8px; margin: 15px auto; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"

        html_parts = [f'<img src="{img_src}" style="{style}">']

        # 图片说明（可选）
        if caption:
            caption_style = "text-align: center; color: #999; font-size: 14px; margin-bottom: 20px;"
            html_parts.append(f'<p style="{caption_style}">{caption}</p>')

        return "\n".join(html_parts)

    def cleanup_old_images(self, max_age_hours: int = 24):
        """
        清理旧的缓存图片

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        if not os.path.exists(self.cache_dir):
            return

        now = time.time()
        max_age_seconds = max_age_hours * 3600

        cleaned_count = 0
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                age = now - os.path.getmtime(filepath)
                if age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        cleaned_count += 1
                    except Exception as e:
                        print(f"[!] 无法删除 {filename}: {e}")

        if cleaned_count > 0:
            print(f"[*] 已清理 {cleaned_count} 个旧图片文件")
