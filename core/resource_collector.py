"""
资料收集模块（增强版 V2.0）
从多个来源收集与主题相关的真实资料，支持多搜索引擎、多关键词、全文爬取
"""
import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict
import json
import re
import os
import sys
import io
from urllib.parse import urljoin, urlparse, quote

# 设置标准输出为 UTF-8 编码（解决 Windows GBK 编码问题）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ResourceCollector:
    """多源资料收集器（增强版 V2.0）"""

    def __init__(self):
        # 多个User-Agent轮换
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        ]
        self.headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 全局去重集合（跨来源去重）
        self._seen_titles = set()
        self._seen_content_hashes = set()

    def collect_resources(self, topic: str, max_results: int = 8, fetch_full_text: bool = True) -> Dict[str, List[Dict]]:
        """
        收集指定主题的资料（增强版 V2.0）
        - 多搜索引擎：百度 + 必应(Bing)
        - 多关键词：自动生成搜索词变体，扩大覆盖面
        - 知乎内容：通过百度 site:zhihu.com 稳定获取
        - 全局去重：跨来源智能去重

        Args:
            topic: 主题关键词
            max_results: 每个来源最多收集的结果数（默认提升到8）
            fetch_full_text: 是否尝试抓取全文内容

        Returns:
            包含各来源资料的字典
        """
        print(f"\n[INFO] 开始收集主题资料: {topic}")

        # 重置全局去重集合
        self._seen_titles = set()
        self._seen_content_hashes = set()

        resources = {
            'search_results': [],
            'zhihu_discussions': [],
            'weibo_posts': [],
            'summary': ''
        }

        # 生成多个搜索关键词变体
        search_variants = self._generate_search_variants(topic)
        print(f"[INFO] 搜索词变体: {search_variants}")

        # 1. 百度搜索（原始关键词）
        print("[SEARCH] 正在搜索百度...")
        baidu_results = self._search_baidu(topic, max_results, fetch_full_text)
        resources['search_results'].extend(baidu_results)
        time.sleep(random.uniform(0.8, 1.5))

        # 2. 必应搜索（补充来源，链接直接指向目标，抓取成功率更高）
        print("[SEARCH] 正在搜索必应(Bing)...")
        bing_query = search_variants[1] if len(search_variants) > 1 else topic
        bing_results = self._search_bing(bing_query, max_results, fetch_full_text)
        for item in bing_results:
            if not self._is_duplicate(item):
                resources['search_results'].append(item)
        time.sleep(random.uniform(0.8, 1.5))

        # 3. 如果总结果不足5条，用第三个搜索词变体补充搜索
        if len(resources['search_results']) < 5 and len(search_variants) > 2:
            print(f"[SEARCH] 补充搜索: {search_variants[2]}...")
            extra_results = self._search_baidu(search_variants[2], max_results // 2, fetch_full_text)
            for item in extra_results:
                if not self._is_duplicate(item):
                    resources['search_results'].append(item)
            time.sleep(random.uniform(0.5, 1.0))

        # 4. 知乎内容（通过百度 site:zhihu.com 搜索，比直接访问知乎更稳定）
        print("[SEARCH] 正在搜索知乎内容...")
        resources['zhihu_discussions'] = self._search_zhihu(topic, max_results // 2)
        time.sleep(random.uniform(0.5, 1.0))

        # 5. 生成资料摘要
        resources['summary'] = self._generate_resource_summary(resources)

        # 统计收集结果
        total = sum(len(v) for k, v in resources.items() if k != 'summary')
        full_text_count = sum(
            1 for item in resources['search_results']
            if item.get('full_text') and len(item['full_text']) > 100
        )
        print(f"\n[OK] 资料收集完成，共获取 {total} 条资料（{full_text_count} 条有全文）")

        return resources

    def _generate_search_variants(self, topic: str) -> List[str]:
        """
        生成多个搜索关键词变体，扩大信息覆盖面
        适用于任意话题（科技、社会、娱乐、生活等）
        """
        variants = [topic]

        if len(topic) <= 8:
            # 短话题：添加补充词扩展搜索
            variants.append(f"{topic} 是什么 原因")
            variants.append(f"{topic} 最新 分析")
        else:
            # 长话题：提取核心关键词
            core = topic
            for prefix in ['关于', '有关', '最新', '最近', '据说', '传说']:
                core = core.replace(prefix, '').strip()

            # 用前半段作为精简版关键词
            short_version = topic.split('，')[0] if '，' in topic else topic.split(' ')[0]
            if short_version and short_version != topic and len(short_version) >= 4:
                variants.append(short_version)

            if core and core != topic:
                variants.append(core)

        # 去重并限制最多3个变体
        seen = set()
        result = []
        for v in variants:
            v = v.strip()
            if v and v not in seen:
                seen.add(v)
                result.append(v)

        return result[:3]

    def _is_duplicate(self, item: Dict) -> bool:
        """
        跨来源智能去重：检查标题和内容是否与已有结果重复
        """
        title = item.get('title', '')
        content = item.get('content', '') or item.get('full_text', '')

        # 标题去重
        if title and title in self._seen_titles:
            return True

        # 内容哈希去重
        if content and len(content) > 20:
            content_hash = hash(content[:100])
            if content_hash in self._seen_content_hashes:
                return True
            self._seen_content_hashes.add(content_hash)

        if title:
            self._seen_titles.add(title)

        return False

    def _search_baidu(self, keyword: str, max_results: int, fetch_full_text: bool = True) -> List[Dict]:
        """搜索百度获取相关网页"""
        results = []
        seen_titles = set()
        seen_content_hashes = set()
        try:
            self.session.headers['User-Agent'] = random.choice(self.user_agents)

            # rn=20 请求更多结果
            url = f"https://www.baidu.com/s?wd={quote(keyword)}&rn=20"
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            containers = []
            containers += soup.select('.result.c-container')
            containers += soup.select('.result-op.c-container')
            if not containers:
                print("    - 未找到标准容器，使用降级方案")
                containers = soup.find_all('h3')

            print(f"    - 找到 {len(containers)} 个搜索结果容器")

            for container in containers[:max_results + 20]:
                try:
                    h3 = None
                    if container.name == 'h3':
                        h3 = container
                    else:
                        h3 = container.find('h3')

                    if not h3:
                        continue

                    title = h3.get_text(strip=True)
                    title = re.sub(r'[\uE000-\uF8FF]', '', title).strip()

                    if not title or len(title) < 5:
                        continue

                    skip_keywords = ['百度百科', '百度视频', '百度图片', '百度知道', '百度贴吧',
                                     '视频大全', '图片大全', '龙头股', '股票频道', '官方网站',
                                     '高清在线观看', '股吧', '行情中心', '证券之星', '百度文库',
                                     '好看视频', '百度网盘', '百度APP', '下载百度']
                    if any(kw in title for kw in skip_keywords):
                        continue

                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    self._seen_titles.add(title)

                    link = ''
                    a_elem = h3.find('a')
                    if a_elem:
                        link = a_elem.get('href', '')

                    abstract = ''
                    if container.name != 'h3':
                        abstract_elem = container.select_one('.c-abstract')
                        if abstract_elem:
                            abstract = abstract_elem.get_text(strip=True)

                        if not abstract or len(abstract) < 50:
                            for sel in ['.c-span-last', '.content-right', '[class*="content"]']:
                                elem = container.select_one(sel)
                                if elem:
                                    text = elem.get_text(strip=True)
                                    if text and len(text) > len(abstract):
                                        abstract = text

                    if not abstract or len(abstract) < 30:
                        parent = h3.parent
                        for _ in range(5):
                            if not parent:
                                break
                            for sel in ['.c-abstract', '.c-summary', '.summary']:
                                elem = parent.select_one(sel)
                                if elem:
                                    text = elem.get_text(strip=True)
                                    if text and len(text) > 20:
                                        abstract = text
                                        break
                            if abstract and len(abstract) > 50:
                                break
                            parent = parent.parent

                    if not abstract or len(abstract) < 10:
                        abstract = title

                    content_hash = hash(abstract[:80]) if len(abstract) > 80 else hash(abstract)
                    if content_hash in seen_content_hashes:
                        continue
                    seen_content_hashes.add(content_hash)

                    full_text = ''
                    if fetch_full_text and link:
                        time.sleep(random.uniform(0.3, 0.8))
                        print(f"    [FETCH] 尝试抓取: {title[:18]}...")
                        full_text = self._fetch_full_text(link)
                        if full_text:
                            print(f"    [OK] 抓取成功 ({len(full_text)}字)")
                        else:
                            print(f"    [SKIP] 抓取失败，使用摘要")

                    if not full_text or len(full_text) < 80:
                        if abstract and len(abstract) > 60:
                            full_text = abstract

                    if full_text:
                        full_text = self._clean_content(full_text)

                    content = abstract[:400] + "..." if len(abstract) > 400 else abstract

                    results.append({
                        'source': '百度搜索',
                        'title': title,
                        'content': content,
                        'url': link,
                        'full_text': full_text
                    })

                    if len(results) >= max_results:
                        break

                except Exception:
                    continue

            full_count = sum(1 for r in results if r.get('full_text') and len(r['full_text']) > 100)
            print(f"  [OK] 百度搜索获取 {len(results)} 条结果 (其中 {full_count} 条有全文)")
        except Exception as e:
            print(f"  [ERROR] 百度搜索失败: {str(e)}")

        return results

    def _search_bing(self, keyword: str, max_results: int, fetch_full_text: bool = True) -> List[Dict]:
        """
        搜索必应(Bing)获取相关网页
        优势：链接直接指向目标页面（无跳转），全文抓取成功率更高
        """
        results = []
        try:
            self.session.headers.update({
                'User-Agent': random.choice(self.user_agents),
                'Referer': 'https://cn.bing.com/',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            })

            url = f"https://cn.bing.com/search?q={quote(keyword)}&count=20&setlang=zh-hans&cc=CN"
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 必应搜索结果容器
            containers = soup.select('li.b_algo')
            if not containers:
                containers = soup.select('div.b_algo')

            print(f"    - 必应找到 {len(containers)} 个搜索结果")

            for container in containers[:max_results + 10]:
                try:
                    h2 = container.find('h2')
                    if not h2:
                        continue

                    a_elem = h2.find('a')
                    if not a_elem:
                        continue

                    title = h2.get_text(strip=True)
                    link = a_elem.get('href', '')

                    if not title or len(title) < 5:
                        continue

                    # 跳过微软/必应自家链接
                    skip_domains = ['microsoft.com', 'bing.com', 'msn.com', 'live.com']
                    if any(d in link for d in skip_domains):
                        continue

                    # 提取摘要
                    abstract = ''
                    caption = container.select_one('.b_caption')
                    if caption:
                        p = caption.find('p')
                        if p:
                            abstract = p.get_text(strip=True)

                    if not abstract:
                        for sel in ['.b_descript', 'p.b_lineclamp2', 'p.b_lineclamp3', '.b_snippet']:
                            elem = container.select_one(sel)
                            if elem:
                                abstract = elem.get_text(strip=True)
                                break

                    if not abstract or len(abstract) < 10:
                        abstract = title

                    # 必应链接是直接链接，抓取成功率比百度更高
                    full_text = ''
                    if fetch_full_text and link and link.startswith('http'):
                        time.sleep(random.uniform(0.3, 0.8))
                        print(f"    [FETCH] 必应抓取: {title[:18]}...")
                        full_text = self._fetch_full_text(link, from_bing=True)
                        if full_text:
                            print(f"    [OK] 必应抓取成功 ({len(full_text)}字)")
                        else:
                            print(f"    [SKIP] 必应抓取失败，使用摘要")

                    if not full_text or len(full_text) < 80:
                        if abstract and len(abstract) > 60:
                            full_text = abstract

                    if full_text:
                        full_text = self._clean_content(full_text)

                    results.append({
                        'source': '必应搜索',
                        'title': title,
                        'content': abstract[:400],
                        'url': link,
                        'full_text': full_text
                    })

                    if len(results) >= max_results:
                        break

                except Exception:
                    continue

            full_count = sum(1 for r in results if r.get('full_text') and len(r['full_text']) > 100)
            print(f"  [OK] 必应搜索获取 {len(results)} 条结果 (其中 {full_count} 条有全文)")
        except Exception as e:
            print(f"  [ERROR] 必应搜索失败: {str(e)}")

        return results

    def _fetch_full_text(self, url: str, max_length: int = 5000, from_bing: bool = False) -> str:
        """
        尝试抓取网页全文内容（增强版）
        - 改进百度跳转处理
        - 更多通用内容选择器
        - 更好的编码检测
        """
        try:
            if not url.startswith('http'):
                return ''

            real_url = url
            # 处理百度跳转链接
            if 'baidu.com/link' in url:
                try:
                    resp = self.session.get(url, timeout=10, allow_redirects=True)
                    real_url = resp.url
                    # 如果跳转后还在百度域名，说明跳转被拦截了
                    if 'baidu.com' in real_url:
                        return ''
                except Exception:
                    return ''

            # 跳过已知难爬的域名
            skip_domains = ['t.cn', 'wenku.baidu.com', 'baike.baidu.com',
                            'weibo.com', 'passport.baidu.com',
                            'wappass.baidu.com', 'captcha', 'login',
                            'zhihu.com']  # 知乎单独通过 site: 搜索获取
            if any(domain in real_url for domain in skip_domains):
                return ''

            # 根据来源设置不同的 Referer
            referer = 'https://cn.bing.com/' if from_bing else 'https://www.baidu.com/'
            self.session.headers.update({
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': referer,
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Cache-Control': 'no-cache',
            })

            response = self.session.get(real_url, timeout=12)

            # 自动检测编码
            encoding = self._detect_encoding(response)
            try:
                response.encoding = encoding
                html = response.text
            except Exception:
                html = response.content.decode('utf-8', errors='ignore')

            soup = BeautifulSoup(html, 'html.parser')

            # 移除不需要的标签
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside',
                             'iframe', 'noscript', 'form', 'svg', 'canvas', 'figure']):
                tag.decompose()

            # 内容选择器（覆盖更多网站布局）
            content_selectors = [
                # 新闻网站专用
                'div#article_content', 'div.article_content',
                'div#article_body', 'div.article-body', 'div.articleBody',
                'div#content_body', 'div.content-detail', 'div#main_content',
                # 通用文章容器
                'article', 'main article', '.article-wrap', '#article-content',
                '.post-content', '.entry-content', '.post-body', '.post-text',
                # 中文媒体常用
                '.news-content', '.news-text', '.news_cont', '.news_article',
                '.detail-content', '.text-content', '#main_text',
                '.article-detail', '.content-article', '.WB_text',
                # 通用内容区域
                'div.content', '#content', '.main-content', 'div#main',
                '.page-content', '#page-content',
                # 模糊匹配（覆盖更多网站）
                '[id*="article"]', '[class*="article"]',
                '[id*="content"]', '[class*="content"]',
                '[id*="detail"]', '[class*="detail"]',
                'div.text', '#text', '.text-body', '.rich_media_content',
            ]

            main_content = None
            best_score = 0

            for selector in content_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        for elem in elements:
                            p_count = len(elem.find_all('p'))
                            text_length = len(elem.get_text(strip=True))
                            # 综合评分：p标签数量权重更高
                            score = p_count * 10 + text_length / 10
                            if score > best_score and p_count >= 2 and text_length >= 150:
                                best_score = score
                                main_content = elem.get_text(separator='\n', strip=True)
                except Exception:
                    continue

            # 降级方案：收集页面所有 <p> 标签
            if not main_content or len(main_content) < 200:
                paragraphs = soup.find_all('p')
                if paragraphs:
                    valid_ps = [p.get_text(strip=True) for p in paragraphs
                                if len(p.get_text(strip=True)) >= 20]
                    if valid_ps:
                        candidate = '\n'.join(valid_ps[:40])
                        if len(candidate) > len(main_content or ''):
                            main_content = candidate

            if main_content:
                main_content = self._clean_content(main_content)
                if len(main_content) < 150:
                    return ''
                return main_content[:max_length]

        except Exception:
            pass

        return ''

    def _detect_encoding(self, response) -> str:
        """自动检测响应编码"""
        if response.encoding and response.encoding.upper() not in ('ISO-8859-1', 'WINDOWS-1252'):
            return response.encoding

        meta_charset = re.search(r'<meta[^>]*charset=["\']?([^"\'>\s]+)', response.text, re.I)
        if meta_charset:
            return meta_charset.group(1)

        for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
            try:
                response.content.decode(enc)
                return enc
            except Exception:
                continue

        return 'utf-8'

    def _clean_content(self, text: str) -> str:
        """清理文本内容，去除导航栏、广告等垃圾信息"""
        garbage_keywords = [
            '扫一扫', '手机打开', '版权所有', '备案号', '网站首页',
            '关于我们', '联系我们', '设为首页', '加入收藏',
            '用户登录', '免费注册', '忘记密码', '验证码',
            '微信公众号', '扫码关注', '播报', '暂停',
            '展开全部', '收起', '上一篇', '下一篇',
            '分享到', '打印', '责任编辑', '编辑：',
            '责编：', '浏览次数', '本文地址',
            '未经授权', '不得转载', '点击查看', '查看全文',
            '广告', '推广', '赞助', '商业合作',
            '', '', '>>', '<<',
        ]
        for kw in garbage_keywords:
            text = text.replace(kw, '')

        # 清理多余空白
        text = re.sub(r'[ \t\xa0]+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        text = text.strip()

        return text

    def _search_zhihu(self, keyword: str, max_results: int) -> List[Dict]:
        """
        通过百度 site:zhihu.com 搜索知乎内容
        比直接访问知乎更稳定（无需登录、无验证码）
        """
        results = []
        try:
            self.session.headers['User-Agent'] = random.choice(self.user_agents)

            # 通过百度的 site: 搜索获取知乎相关内容
            zhihu_query = f"site:zhihu.com {keyword}"
            url = f"https://www.baidu.com/s?wd={quote(zhihu_query)}&rn=10"

            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            containers = soup.select('.result.c-container') + soup.select('.result-op.c-container')

            count = 0
            for container in containers[:max_results + 10]:
                try:
                    h3 = container.find('h3')
                    if not h3:
                        continue

                    title = h3.get_text(strip=True)
                    title = re.sub(r'[\uE000-\uF8FF]', '', title).strip()

                    if not title or len(title) < 5:
                        continue

                    a_elem = h3.find('a')
                    link = a_elem.get('href', '') if a_elem else ''

                    # 提取摘要
                    abstract = ''
                    abstract_elem = container.select_one('.c-abstract')
                    if abstract_elem:
                        abstract = abstract_elem.get_text(strip=True)

                    if not abstract or len(abstract) < 20:
                        for sel in ['.c-span-last', '[class*="content"]']:
                            elem = container.select_one(sel)
                            if elem:
                                t = elem.get_text(strip=True)
                                if t and len(t) > len(abstract):
                                    abstract = t

                    if not abstract:
                        abstract = title

                    results.append({
                        'source': '知乎',
                        'title': title,
                        'content': abstract[:400],
                        'url': link,
                        'meta': '知乎讨论'
                    })
                    count += 1

                    if count >= max_results:
                        break

                except Exception:
                    continue

            print(f"  [OK] 知乎搜索获取 {len(results)} 条结果")
        except Exception as e:
            print(f"  [ERROR] 知乎搜索失败: {str(e)}")

        return results

    def _search_weibo(self, keyword: str, max_results: int) -> List[Dict]:
        """微博搜索（反爬严格，暂时跳过）"""
        results = []
        print(f"  - 微博搜索已跳过（反爬限制）")
        return results

    def _generate_resource_summary(self, resources: Dict) -> str:
        """生成资料摘要，帮助AI快速理解收集到的信息"""
        summary_parts = []

        all_titles = []
        all_contents = []

        for category, items in resources.items():
            if category == 'summary' or not items:
                continue
            for item in items:
                if 'title' in item:
                    all_titles.append(item['title'])
                content = item.get('full_text', '') or item.get('content', '')
                if content:
                    all_contents.append(content[:200])

        if all_titles:
            summary_parts.append("【关键标题汇总】")
            summary_parts.extend([f"- {t}" for t in all_titles[:12]])

        if all_contents:
            combined = ' '.join(all_contents[:6])
            summary_parts.append("\n【内容摘要】")
            summary_parts.append(combined[:700] + "..." if len(combined) > 700 else combined)

        return '\n'.join(summary_parts)

    def format_resources_for_prompt(self, resources: Dict[str, List[Dict]]) -> str:
        """
        将收集的资料格式化为适合放入提示词的文本（增强版）
        - 展示更多内容（600字/条）
        - 标注来源（百度/必应/知乎）
        """
        formatted_text = "=" * 60 + "\n"
        formatted_text += "📚 【已收集的真实资料 - 写作时必须参考】\n"
        formatted_text += "=" * 60 + "\n\n"

        if resources.get('summary'):
            formatted_text += "【资料摘要】\n"
            formatted_text += resources['summary']
            formatted_text += "\n\n"

        # 搜索引擎结果（百度 + 必应）
        if resources.get('search_results'):
            formatted_text += "【搜索引擎结果】\n"
            for idx, item in enumerate(resources['search_results'][:8], 1):
                source = item.get('source', '搜索')
                formatted_text += f"\n{idx}. [{source}] {item['title']}\n"
                content = item.get('full_text', '') or item.get('content', '')
                if content:
                    # 提升展示长度到600字
                    formatted_text += f"   {content[:600]}...\n" if len(content) > 600 else f"   {content}\n"

        # 知乎社区讨论
        if resources.get('zhihu_discussions'):
            formatted_text += "\n【知乎社区讨论】\n"
            for idx, item in enumerate(resources['zhihu_discussions'][:4], 1):
                formatted_text += f"\n{idx}. {item['title']}\n"
                formatted_text += f"   {item['content'][:300]}\n"

        formatted_text += "\n" + "=" * 60 + "\n"
        formatted_text += "【资料使用规则 - 违反视为不合格】\n"
        formatted_text += "1. 必须引用至少2-3条资料中的事实、数据或观点\n"
        formatted_text += "2. 用自己的话重新表达，不要直接复制粘贴\n"
        formatted_text += "3. 可以说\"根据公开信息\"、\"网友讨论显示\"等标注来源\n"
        formatted_text += "4. 禁止编造资料中没有的事实或数据\n"
        formatted_text += "5. 资料不足时宁可写短，也不要瞎编\n"
        formatted_text += "=" * 60 + "\n"

        return formatted_text

    def check_resource_quality(self, resources: Dict) -> Dict:
        """
        检查收集到的资料质量

        Returns:
            {
                'has_valid_data': bool,
                'full_text_count': int,
                'total_count': int,
                'avg_content_length': int,
                'issues': List[str],
                'quality_score': int  # 0-100
            }
        """
        issues = []
        total_count = 0
        full_text_count = 0
        total_length = 0

        search_results = resources.get('search_results', [])
        for item in search_results:
            total_count += 1
            content = item.get('full_text', '') or item.get('content', '')
            total_length += len(content)
            if item.get('full_text') and len(item['full_text']) > 100:
                full_text_count += 1

        for key in ['zhihu_discussions', 'weibo_posts']:
            items = resources.get(key, [])
            for item in items:
                total_count += 1
                content = item.get('content', '')
                total_length += len(content)

        if total_count == 0:
            issues.append('没有收集到任何资料')
        elif full_text_count == 0:
            issues.append('没有抓取到任何全文内容，只有摘要')

        avg_length = total_length // total_count if total_count > 0 else 0
        if avg_length < 80:
            issues.append('资料内容过短，可能没有实质信息')

        score = 0
        if total_count > 0:
            score += 30
            score += min(full_text_count * 12, 45)
            if avg_length >= 150:
                score += 20
            elif avg_length >= 80:
                score += 10
            if total_count >= 5:
                score += 10
            elif total_count >= 3:
                score += 5

        score = min(score, 100)

        return {
            'has_valid_data': score >= 25,
            'full_text_count': full_text_count,
            'total_count': total_count,
            'avg_content_length': avg_length,
            'issues': issues,
            'quality_score': score
        }

    def save_resources(self, resources: Dict, topic: str):
        """保存资料到本地文件"""
        try:
            os.makedirs('data', exist_ok=True)
            safe_topic = re.sub(r'[\\/:*?"<>|]', '_', topic[:20])
            filename = f"data/resources_{safe_topic}_{int(time.time())}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(resources, f, ensure_ascii=False, indent=2)
            print(f"[SAVE] 资料已保存到: {filename}")
        except Exception as e:
            print(f"[WARN] 资料保存失败: {str(e)}")


if __name__ == "__main__":
    # 测试代码
    collector = ResourceCollector()
    resources = collector.collect_resources("人工智能", max_results=8)

    print("\n" + "=" * 60)
    print("格式化后的资料:")
    print("=" * 60)
    print(collector.format_resources_for_prompt(resources))

    collector.save_resources(resources, "人工智能")
