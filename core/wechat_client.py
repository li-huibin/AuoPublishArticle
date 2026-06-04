# -*- coding: utf-8 -*-
import requests
import json
import time
import os
import markdown
import re

class WeChatClient:
    def __init__(self, app_id=None, app_secret=None):
        self.app_id = app_id or os.environ.get("WECHAT_APP_ID")
        self.app_secret = app_secret or os.environ.get("WECHAT_APP_SECRET")
        self.access_token = None
        self.token_expires_at = 0

        if not self.app_id or not self.app_secret:
            raise ValueError("缺少 WECHAT_APP_ID 或 WECHAT_APP_SECRET 配置。请在 .env 文件中设置或通过参数传入。")

    def _get_access_token(self):
        """
        获取微信 Access Token，带简单的本地缓存
        """
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }

        print(f"[*] 正在请求微信 Access Token...")
        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"微信 API 错误: {data.get('errmsg')} (code: {data.get('errcode')})")

            self.access_token = data["access_token"]
            # 提前 5 分钟过期，确保安全
            self.token_expires_at = time.time() + data["expires_in"] - 300
            print(f"[+] 获取 Access Token 成功")
            return self.access_token
        except Exception as e:
            print(f"[!] 获取 Access Token 失败: {e}")
            raise

    def upload_draft(self, title, content, author="小苏的热事笔记", digest="", cover_url=None):
        """
        上传文章到草稿箱
        :param title: 标题
        :param content: 内容 (HTML 格式)
        :param author: 作者
        :param digest: 摘要
        :param cover_url: 封面图片的 media_id (如果需要)
        :return: media_id
        """
        token = self._get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        # 简单的 Markdown 转 HTML 处理 (如果输入是 Markdown)
        # 实际生产中建议使用 markdown2 或 mistune 库，这里做简易处理
        html_content = content
        if not content.strip().startswith("<"):
            html_content = self._simple_markdown_to_html(content)

        # 封面图逻辑比较复杂，这里暂时不强制要求，如果没传 cover_url，可能会报错
        # 微信接口要求必须有 thumb_media_id。
        # 为了简化流程，如果没有提供 thumb_media_id，我们可能需要先上传一张默认图片或者提示用户
        # 目前版本我们先假定用户只是测试，如果没有 media_id 可能会失败，
        # 但我们先尝试构建请求，看 API 是否允许空 thumb_media_id (通常不允许)
        
        # 如果没有封面，从环境变量读取默认封面
        thumb_media_id = cover_url or os.environ.get("WECHAT_COVER_ID")
        if not thumb_media_id:
             print("[!] 警告: 未提供封面图 (thumb_media_id)，且未配置 WECHAT_COVER_ID 环境变量。")
             print("[!] 微信草稿箱接口通常要求必须有封面图，请在 .env 文件中配置 WECHAT_COVER_ID。")
             # 如果没有配置，可能会上传失败

        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": html_content,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }

        payload = {
            "articles": [article]
        }

        print(f"[*] 正在上传草稿到微信公众号: {title}")
        try:
            # ensure_ascii=False 很重要，否则中文会乱码
            resp = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            resp.raise_for_status()
            data = resp.json()

            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"微信 API 错误: {data.get('errmsg')} (code: {data.get('errcode')})")

            print(f"[+] 上传成功! Media ID: {data.get('media_id')}")
            return data.get('media_id')
        except Exception as e:
            print(f"[!] 上传草稿失败: {e}")
            return None

    def _simple_markdown_to_html(self, text):
        """
        使用 Markdown 库转 HTML，并注入微信公众号适配的内联样式
        """
        # 1. Markdown 转基础 HTML
        # extensions: nl2br (换行转br), extra (支持更多语法)
        html = markdown.markdown(text, extensions=['nl2br', 'extra'])
        
        # 2. 注入内联样式 (CSS Inlining)
        # 定义样式
        styles = {
            'h1': 'font-size: 22px; font-weight: bold; margin-top: 30px; margin-bottom: 20px; color: #1a1a1a;',
            'h2': 'font-size: 18px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; color: #ff8800; border-bottom: 1px solid #eaeaea; padding-bottom: 10px;',
            'h3': 'font-size: 16px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #ff8800;',
            'p': 'font-size: 16px; line-height: 1.8; margin-bottom: 20px; color: #333; text-align: justify;',
            'blockquote': 'border-left: 4px solid #07c160; padding: 10px 15px; margin: 20px 0; color: #666; font-size: 15px; background: #f9f9f9; border-radius: 4px;',
            'ul': 'margin-bottom: 20px; padding-left: 20px;',
            'ol': 'margin-bottom: 20px; padding-left: 20px;',
            'li': 'margin-bottom: 8px; font-size: 16px; line-height: 1.8; color: #333;',
            'strong': 'font-weight: bold;', # 重点文字加粗，颜色继承父元素
            'em': 'color: #666; font-style: italic;',
        }

        # 使用正则进行简单替换 (Simple CSS Injection)
        # 注意：这种方式比较粗糙，但对于生成的标准 Markdown HTML 足够用了
        for tag, style in styles.items():
            # 替换开始标签 <tag> 为 <tag style="...">
            # 使用非贪婪匹配，防止破坏已有属性（虽然 markdown 库生成的通常很干净）
            pattern = re.compile(f'<{tag}(?![^>]*style=)([^>]*)>', re.IGNORECASE)
            replacement = f'<{tag} style="{style}"\\1>'
            html = pattern.sub(replacement, html)

        # 3. 包裹一层容器
        wrapper = f'<section style="font-family: -apple-system, BlinkMacSystemFont, \'Helvetica Neue\', \'PingFang SC\', \'Microsoft YaHei\', sans-serif;">{html}</section>'
        
        return wrapper

    def publish_draft(self, media_id):
        """
        发布草稿 (Publish)
        注意：这会将草稿发布为正式文章，生成永久链接，但不会推送到粉丝聊天列表（除非手动群发）。
        发布成功后，文章会出现在公众号主页。
        """
        token = self._get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"
        
        payload = {
            "media_id": media_id
        }
        
        print(f"[*] 正在自动发布文章 (Media ID: {media_id})...")
        try:
            resp = requests.post(url, data=json.dumps(payload))
            resp.raise_for_status()
            data = resp.json()
            
            if "errcode" in data and data["errcode"] != 0:
                if data["errcode"] == 48001:
                    raise Exception(f"发布失败 (48001): 您的公众号账号类型（可能是未认证的个人订阅号）没有权限调用此接口。请尝试只使用 --publish 上传到草稿箱，然后手动发布。")
                raise Exception(f"发布失败: {data.get('errmsg')} (code: {data.get('errcode')})")
            
            # 发布是异步的，会返回 publish_id
            print(f"[+] 发布任务提交成功！Publish ID: {data.get('publish_id')}")
            print(f"[*] 注意：文章已发布到公众号主页，但可能不会推送到粉丝手机（取决于微信规则）。建议进后台确认。")
            return data.get('publish_id')
        except Exception as e:
            print(f"[!] 发布请求失败: {e}")
            return None

    def get_published_articles(self, offset=0, count=20):
        """
        获取已发布的文章列表
        :param offset: 从第几篇开始获取，默认从 0 开始
        :param count: 获取的文章数量，默认 20 篇（最大支持 20）
        :return: 文章列表
        """
        token = self._get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/batchget?access_token={token}"
        
        payload = {
            "offset": offset,
            "count": count,
            "no_content": 0  # 0 表示返回内容，1 表示不返回内容
        }
        
        print(f"[*] 正在获取已发布文章列表 (offset={offset}, count={count})...")
        try:
            resp = requests.post(url, data=json.dumps(payload))
            resp.raise_for_status()
            data = resp.json()
            
            if "errcode" in data and data["errcode"] != 0:
                # 48001 表示接口未授权（通常是未认证的订阅号）
                if data["errcode"] == 48001:
                    print(f"[!] 接口权限不足 (code: 48001)")
                    print(f"[!] 此接口需要【已认证的服务号】权限")
                    print(f"[!] 未认证的订阅号无法使用此功能")
                    print(f"[!] 提示：你仍然可以使用 --publish 上传草稿，但无法自动获取阅读数据")
                    return None
                raise Exception(f"获取文章列表失败: {data.get('errmsg')} (code: {data.get('errcode')})")
            
            articles = data.get('item', [])
            total_count = data.get('total_count', 0)
            print(f"[+] 成功获取 {len(articles)} 篇文章，总共 {total_count} 篇")
            return {
                'articles': articles,
                'total_count': total_count
            }
        except Exception as e:
            print(f"[!] 获取文章列表失败: {e}")
            return None

    def get_article_statistics(self, begin_date, end_date):
        """
        获取图文统计数据（阅读数、分享数等）
        注意：此接口仅支持认证后的公众号，且数据有延迟（通常延迟1-3天）
        :param begin_date: 开始日期，格式 YYYY-MM-DD
        :param end_date: 结束日期，格式 YYYY-MM-DD（最大跨度为1天）
        :return: 统计数据列表
        """
        token = self._get_access_token()
        url = f"https://api.weixin.qq.com/datacube/getarticlesummary?access_token={token}"
        
        payload = {
            "begin_date": begin_date,
            "end_date": end_date
        }
        
        print(f"[*] 正在获取文章统计数据 ({begin_date} ~ {end_date})...")
        try:
            resp = requests.post(url, data=json.dumps(payload))
            resp.raise_for_status()
            data = resp.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"获取统计数据失败: {data.get('errmsg')} (code: {data.get('errcode')})")
            
            stats = data.get('list', [])
            print(f"[+] 成功获取 {len(stats)} 条统计数据")
            return stats
        except Exception as e:
            print(f"[!] 获取统计数据失败: {e}")
            return None

    def get_article_detail_statistics(self, article_id):
        """
        获取单篇文章的详细统计数据
        注意：这需要组合使用多个接口，且数据可能有延迟
        :param article_id: 文章ID（通常是 article_id 或 idx）
        :return: 详细统计数据
        """
        # 微信API中，单篇文章的详细数据获取比较复杂
        # 通常需要通过 getarticletotal 等接口获取
        # 这里提供一个简化版本，实际使用时可能需要根据具体需求调整
        token = self._get_access_token()
        url = f"https://api.weixin.qq.com/datacube/getarticletotal?access_token={token}"

        # 获取最近7天的数据
        from datetime import datetime, timedelta
        end_date = datetime.now()
        begin_date = end_date - timedelta(days=7)

        payload = {
            "begin_date": begin_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        print(f"[*] 正在获取文章详细统计数据...")
        try:
            resp = requests.post(url, data=json.dumps(payload))
            resp.raise_for_status()
            data = resp.json()

            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"获取详细统计数据失败: {data.get('errmsg')} (code: {data.get('errcode')})")

            stats = data.get('list', [])
            print(f"[+] 成功获取详细统计数据")
            return stats
        except Exception as e:
            print(f"[!] 获取详细统计数据失败: {e}")
            return None

    def upload_image(self, image_path):
        """
        上传图片到微信永久素材库
        :param image_path: 本地图片路径
        :return: media_id
        """
        token = self._get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"

        print(f"[*] 正在上传图片到微信素材库: {os.path.basename(image_path)}")
        try:
            with open(image_path, "rb") as f:
                files = {'media': f}
                resp = requests.post(url, files=files, timeout=60)
                data = resp.json()

                if "errcode" in data and data["errcode"] != 0:
                    raise Exception(f"微信 API 错误: {data.get('errmsg')} (code: {data.get('errcode')})")

                if "media_id" in data:
                    print(f"[+] 图片上传成功! Media ID: {data['media_id']}")
                    return data["media_id"]
                else:
                    raise Exception(f"上传响应异常: {data}")
        except Exception as e:
            print(f"[!] 上传图片失败: {e}")
            return None

    def format_image_html(self, media_id, caption=""):
        """
        生成微信公众号图片 HTML
        :param media_id: 微信图片 media_id
        :param caption: 图片说明文字（可选）
        :return: HTML 字符串
        """
        style = "width: 100%; border-radius: 8px; margin: 15px 0; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"

        html_parts = [f'<img src="{media_id}" style="{style}">']

        if caption:
            caption_style = "text-align: center; color: #999; font-size: 14px; margin-bottom: 20px;"
            html_parts.append(f'<p style="{caption_style}">{caption}</p>')

        return "\n".join(html_parts)

    def publish(self, title, content, images=None):
        """
        一键发布文章到微信公众号（上传草稿 + 自动发布）
        :param title: 文章标题
        :param content: 文章内容（支持 Markdown 或 HTML）
        :param images: 图片列表（可选，暂未实现）
        :return: 发布结果
        """
        try:
            print(f"[*] 开始发布文章: {title}")
            
            # 清理文章内容（参考 main.py 的处理逻辑）
            lines = content.split('\n')
            clean_lines = []
            
            # 1. 移除标题行（如果第一行是 # 开头的标题）
            if lines and lines[0].strip().startswith('# '):
                lines = lines[1:]
            
            # 2. 移除"核心视角"引用块，并去除开头的空行
            for line in lines:
                stripped = line.strip()
                # 跳过核心视角/核心观点的引用块
                if stripped.startswith('>'):
                    if "核心视角" in stripped or "核心观点" in stripped:
                        continue
                # 跳过开头的空行
                if not clean_lines and not stripped:
                    continue
                clean_lines.append(line)
            
            clean_content = '\n'.join(clean_lines)
            
            # 3. 提取摘要（从清理后的内容中提取第一个非标题、非引用、非列表的段落）
            digest = ""
            for line in clean_lines:
                stripped = line.strip()
                if stripped and not stripped.startswith(('#', '>', '-')):
                    digest = stripped[:54] + "..." if len(stripped) > 54 else stripped
                    break
            
            # 4. 获取封面图 media_id（从环境变量读取）
            cover_id = os.environ.get("WECHAT_COVER_ID")
            
            # 第一步：上传草稿
            media_id = self.upload_draft(
                title=title,
                content=clean_content,
                author="小苏的热事笔记",
                digest=digest,
                cover_url=cover_id
            )
            
            if not media_id:
                return {
                    "success": False,
                    "error": "上传草稿失败"
                }
            
            # 第二步：自动发布（如果账号有权限）
            publish_id = self.publish_draft(media_id)
            
            if publish_id:
                return {
                    "success": True,
                    "media_id": media_id,
                    "publish_id": publish_id,
                    "message": "文章已成功发布到公众号"
                }
            else:
                # 如果发布失败（可能是权限问题），但草稿上传成功
                return {
                    "success": True,
                    "media_id": media_id,
                    "message": "文章已上传到草稿箱，请手动发布（可能因账号类型限制无法自动发布）"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
