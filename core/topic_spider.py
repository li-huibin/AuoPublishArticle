# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime

class TopicSpider:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.google.com/"
        }
        # 兜底热点数据（当网络抓取失败时使用）- 扩充到35条支持分页轮换
        self.backup_topics = [
            "2026年政府工作报告释放哪些信号",
            "新能源汽车销量突破1600万辆",
            "年轻人就业观念变化引热议",
            "AI大模型应用场景持续扩展",
            "房价走势成民生关注焦点",
            "延迟退休政策实施效果观察",
            "短视频平台监管趋严",
            "医疗改革新进展引关注",
            "研究生报考人数创新高",
            "国货品牌崛起现象分析",
            "直播电商乱象整治",
            "碳中和目标下的产业转型",
            "家庭教育支出负担引讨论",
            "数字经济与实体经济融合",
            "养老产业发展机遇与挑战",
            "5G技术商用化加速推进",
            "芯片自主研发取得新突破",
            "元宇宙概念持续升温",
            "电商直播带货新规出台",
            "新冠疫苗研发最新进展",
            "高考改革方案引发讨论",
            "城市更新改造政策解读",
            "网络安全法律体系完善",
            "文化创意产业蓬勃发展",
            "智能家居市场规模扩大",
            "绿色出行理念深入人心",
            "职业教育改革持续深化",
            "远程办公模式成新常态",
            "消费升级趋势日益明显",
            "乡村振兴战略全面推进",
            "科技创新驱动发展战略",
            "金融科技监管政策调整",
            "体育产业市场潜力巨大",
            "影视行业复苏迹象显现",
            "快递物流行业提质增效"
        ]

    def search_topics(self, keyword: str, limit: int = 10):
        """
        真正的主题搜索 - 多平台级联搜索
        
        :param keyword: 搜索关键词
        :param limit: 返回数量
        :return: list of dicts with 'title' and 'heat' keys
        """
        import urllib.parse
        encoded_kw = urllib.parse.quote(keyword)
        print(f"[*] 开始多平台搜索主题: {keyword}")

        # 按优先级依次尝试各平台
        search_methods = [
            ("百度新闻", lambda: self._search_baidu_news(keyword, encoded_kw, limit)),
            ("微信搜狗", lambda: self._search_weixin_sogou(keyword, encoded_kw, limit)),
            ("今日头条", lambda: self._search_toutiao_search(keyword, encoded_kw, limit)),
            ("知乎",     lambda: self._search_zhihu_search(keyword, encoded_kw, limit)),
            ("百度通用", lambda: self._search_baidu_general(keyword, encoded_kw, limit)),
        ]

        for platform, method in search_methods:
            try:
                results = method()
                if results:
                    print(f"[OK] {platform}搜索成功，返回 {len(results)} 条结果")
                    return results
                print(f"[--] {platform}未返回结果，尝试下一平台...")
            except Exception as e:
                print(f"[!!] {platform}搜索异常: {e}，尝试下一平台...")
                continue

        print(f"[!] 所有平台均未找到「{keyword}」相关内容")
        return [{"title": f"暂时无法搜索到关于「{keyword}」的相关内容，请稍后重试或换个关键词", "heat": 0}]

    def _search_baidu_news(self, keyword: str, encoded_kw: str, limit: int):
        """百度新闻搜索"""
        url = f"https://news.baidu.com/ns?word={encoded_kw}&tn=news&cl=2&rn=20&ie=utf-8"
        print(f"[*] 百度新闻搜索: {keyword}")
        headers = self.headers.copy()
        headers["Referer"] = "https://news.baidu.com/"
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        # 百度新闻结果列表
        for item in soup.select("div.result"):
            title_tag = item.select_one("h3 a") or item.select_one(".news-title")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not title:
                continue
            # 来源和时间作为辅助信息
            source_tag = item.select_one(".c-color-gray") or item.select_one(".source")
            source = source_tag.get_text(strip=True) if source_tag else ""
            display = f"{title}（{source}）" if source else title
            results.append({
                "title": display[:80],
                "heat": random.randint(10000, 500000)
            })
            if len(results) >= limit:
                break
        return results

    def _search_weixin_sogou(self, keyword: str, encoded_kw: str, limit: int):
        """搜狗微信公众号文章搜索"""
        url = f"https://weixin.sogou.com/weixin?type=2&s_from=input&query={encoded_kw}&ie=utf8&_sug_=n&_sug_type_="
        print(f"[*] 搜狗微信搜索: {keyword}")
        headers = self.headers.copy()
        headers["Referer"] = "https://weixin.sogou.com/"
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for item in soup.select("li.news-box, .news-list li"):
            title_tag = item.select_one("h3 a") or item.select_one("a.news")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not title or keyword not in title and len(title) < 3:
                continue
            # 公众号名称
            account_tag = item.select_one(".account") or item.select_one("span.s2")
            account = account_tag.get_text(strip=True) if account_tag else ""
            display = f"{title}【{account}】" if account else title
            results.append({
                "title": display[:80],
                "heat": random.randint(5000, 200000)
            })
            if len(results) >= limit:
                break
        return results

    def _search_toutiao_search(self, keyword: str, encoded_kw: str, limit: int):
        """今日头条搜索"""
        url = f"https://www.toutiao.com/search/?keyword={encoded_kw}"
        print(f"[*] 今日头条搜索: {keyword}")
        headers = self.headers.copy()
        headers["Referer"] = "https://www.toutiao.com/"
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        # 尝试从页面内嵌JSON提取数据
        import re, json
        pattern = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', resp.text, re.S)
        if pattern:
            try:
                data = json.loads(pattern.group(1))
                # 深度查找列表
                feed_list = (data.get("search", {}).get("feedList") or
                             data.get("list") or [])
                for item in feed_list:
                    title = (item.get("title") or item.get("abstract") or "").strip()
                    if title:
                        results.append({
                            "title": title[:80],
                            "heat": item.get("hotValue", random.randint(5000, 300000))
                        })
                    if len(results) >= limit:
                        break
            except Exception:
                pass

        # JSON解析失败，尝试HTML解析
        if not results:
            for item in soup.select(".result-content, .search-result-item"):
                title_tag = item.select_one("h3, h4, .title, a")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                if title:
                    results.append({
                        "title": title[:80],
                        "heat": random.randint(5000, 300000)
                    })
                if len(results) >= limit:
                    break
        return results

    def _search_zhihu_search(self, keyword: str, encoded_kw: str, limit: int):
        """知乎搜索（问题+文章）"""
        url = f"https://www.zhihu.com/search?type=content&q={encoded_kw}"
        print(f"[*] 知乎搜索: {keyword}")
        headers = self.headers.copy()
        headers["Referer"] = "https://www.zhihu.com/"
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        import re, json
        # 尝试从内嵌JSON提取
        pattern = re.search(r'<script id="js-initialData"[^>]*>(.*?)</script>', resp.text, re.S)
        if pattern:
            try:
                data = json.loads(pattern.group(1))
                search_result = (data.get("initialState", {})
                                    .get("entities", {})
                                    .get("questions", {}))
                if search_result:
                    for qid, qdata in search_result.items():
                        title = qdata.get("title", "").strip()
                        if title:
                            results.append({
                                "title": title[:80],
                                "heat": qdata.get("followerCount", random.randint(1000, 100000))
                            })
                        if len(results) >= limit:
                            break
            except Exception:
                pass

        # HTML兜底解析
        if not results:
            for item in soup.select(".List-item, .SearchResult-item"):
                title_tag = item.select_one("h2, .QuestionItem-title, .ContentItem-title")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                if title:
                    results.append({
                        "title": title[:80],
                        "heat": random.randint(1000, 100000)
                    })
                if len(results) >= limit:
                    break
        return results

    def _search_baidu_general(self, keyword: str, encoded_kw: str, limit: int):
        """百度通用搜索（最终兜底）"""
        url = f"https://www.baidu.com/s?wd={encoded_kw}&rn=20"
        print(f"[*] 百度通用搜索: {keyword}")
        headers = self.headers.copy()
        headers["Referer"] = "https://www.baidu.com/"
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        # 百度搜索结果的标题通常在 h3 下的 a 标签
        for h3 in soup.select("h3.t, h3.c-title"):
            a_tag = h3.select_one("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            if title and len(title) > 3:
                results.append({
                    "title": title[:80],
                    "heat": random.randint(1000, 50000)
                })
            if len(results) >= limit:
                break
        return results

    def get_hot_topics(self, source="toutiao", limit=5):
        """
        获取热点话题
        :param source: toutiao | zhihu | weibo
        :param limit: 返回数量
        :return: list of dicts with 'title' and 'heat' keys
        """
        topics = []
        if source == "zhihu":
            topics = self._get_zhihu_hot(limit)
        elif source == "weibo":
            topics = self._get_weibo_hot(limit)
        elif source == "toutiao":
            topics = self._get_toutiao_hot(limit)

        # 如果指定源失败，尝试自动切换到今日头条（最稳）
        if not topics and source != "toutiao":
            print(f"[!] {source} 抓取失败，自动切换到今日头条热榜...")
            topics = self._get_toutiao_hot(limit)

        # 如果所有网络抓取都失败，使用兜底数据
        if not topics:
            print("[*] 网络抓取失败，使用本地热点库...")
            # 随机选择，每次不一样
            shuffled = self.backup_topics.copy()
            random.shuffle(shuffled)
            # 返回字典格式，包含随机热度值
            topics = [
                {
                    "title": title,
                    "heat": random.randint(50000, 999999)  # 5万到99.9万之间的随机热度
                }
                for title in shuffled[:limit]
            ]
            print(f"[*] 已加载 {len(topics)} 个备选热点")

        return topics

    def _get_toutiao_hot(self, limit):
        """
        抓取今日头条热榜 (JSON 接口，最稳)
        返回包含标题和热度的字典列表
        """
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        print("[*] 正在抓取今日头条热榜...")
        try:
            resp = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
            resp.raise_for_status()
            data = resp.json()

            hot_list = []
            if "data" in data:
                for item in data["data"]:
                    if "Title" in item:
                        topic_data = {
                            "title": item["Title"],
                            "heat": item.get("HotValue", 0)  # 获取热度值
                        }
                        hot_list.append(topic_data)

            return hot_list[:limit]
        except requests.exceptions.Timeout:
            print("[!] 抓取今日头条超时")
            return []
        except requests.exceptions.ConnectionError:
            print("[!] 无法连接到今日头条（可能是防火墙/代理问题）")
            return []
        except Exception as e:
            print(f"[!] 抓取今日头条失败: {e}")
            return []

    def _get_zhihu_hot(self, limit):
        """
        抓取知乎热榜
        返回包含标题和热度的字典列表
        """
        url = "https://www.zhihu.com/billboard"
        print("[*] 正在抓取知乎热榜...")
        try:
            # 知乎对 Referer 和 Cookie 检查较严
            headers = self.headers.copy()
            headers["Referer"] = "https://www.zhihu.com/"
            resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 知乎热榜的结构通常是 script 里的 JSON 或者特定的 class
            # 简单解析 dom
            hot_list = []
            # 查找热榜标题容器 (class 可能会变，这里尝试找包含 text 的链接)
            # 目前知乎热榜的每一项都在 HotList-item 里
            items = soup.select(".HotList-item")

            for item in items:
                title_tag = item.select_one(".HotList-itemTitle")
                metrics_tag = item.select_one(".HotList-itemMetrics")
                if title_tag:
                    title = title_tag.get_text().strip()
                    # 尝试提取热度值（知乎显示为"XX万热度"）
                    heat = 0
                    if metrics_tag:
                        metrics_text = metrics_tag.get_text().strip()
                        # 解析类似"100万热度"的文本
                        import re
                        match = re.search(r'(\d+(?:\.\d+)?)\s*万', metrics_text)
                        if match:
                            heat = int(float(match.group(1)) * 10000)
                    
                    hot_list.append({
                        "title": title,
                        "heat": heat if heat > 0 else random.randint(50000, 500000)
                    })

            # 如果解析失败（页面结构变了），尝试另一种通用方式
            if not hot_list:
                 # 兜底：直接找 title 属性或者特定的 meta
                 print("[!] 知乎页面结构可能已更新，尝试备用解析...")

            return hot_list[:limit]
        except requests.exceptions.Timeout:
            print("[!] 抓取知乎超时")
            return []
        except requests.exceptions.ConnectionError:
            print("[!] 无法连接到知乎（可能是防火墙/代理问题）")
            return []
        except Exception as e:
            print(f"[!] 抓取知乎失败: {e}")
            return []

    def _get_weibo_hot(self, limit):
        """
        抓取微博热搜
        返回包含标题和热度的字典列表
        """
        url = "https://s.weibo.com/top/summary"
        print("[*] 正在抓取微博热搜...")
        try:
            # 微博需要 Cookie 吗？通常不需要
            resp = requests.get(url, headers=self.headers, timeout=10, allow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            hot_list = []
            # 微博热搜在 td.td-02 > a
            rows = soup.select("tr")
            for row in rows:
                link = row.select_one("td.td-02 > a")
                num_tag = row.select_one("td.td-02 > span")
                
                if link:
                    text = link.get_text().strip()
                    # 排除置顶广告
                    href = link.get("href", "")
                    if "javascript:void(0)" in href:
                        continue
                    
                    # 提取热度值
                    heat = 0
                    if num_tag:
                        heat_text = num_tag.get_text().strip()
                        # 微博热度通常直接是数字
                        try:
                            heat = int(heat_text)
                        except:
                            heat = random.randint(50000, 999999)
                    
                    hot_list.append({
                        "title": text,
                        "heat": heat if heat > 0 else random.randint(50000, 999999)
                    })

            return hot_list[:limit]
        except requests.exceptions.Timeout:
            print("[!] 抓取微博超时")
            return []
        except requests.exceptions.ConnectionError:
            print("[!] 无法连接到微博（可能是防火墙/代理问题）")
            return []
        except Exception as e:
            print(f"[!] 抓取微博失败: {e}")
            return []

if __name__ == "__main__":
    # 测试
    spider = TopicSpider()
    topics = spider.get_hot_topics("zhihu")
    print("知乎热榜:", topics)
    topics = spider.get_hot_topics("weibo")
    print("微博热搜:", topics)
