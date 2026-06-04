# -*- coding: utf-8 -*-

import argparse
import sys
import os
import io

# 解决 Windows 终端中文乱码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from core.generator import ArticleGenerator
from core.wechat_client import WeChatClient
from core.topic_spider import TopicSpider

def load_env():
    """
    手动加载 .env 文件，避免依赖 python-dotenv。
    仅支持简单的 KEY=VALUE 格式。
    """
    env_path = ".env"
    if not os.path.exists(env_path):
        return

    print(f"[*] 发现 .env 文件，正在加载环境变量...")
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # 去除可能的引号
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

                    if key and value:
                        os.environ[key] = value
    except Exception as e:
        print(f"[!] 加载 .env 文件失败: {e}")

def main():
    # 优先加载 .env
    load_env()

    parser = argparse.ArgumentParser(description="AI 文章生成器 - 新媒体特别版")
    parser.add_argument("topic", nargs="*", help="文章主题 (如果使用 --hot 可选)")
    parser.add_argument("--name", default="小苏的热事笔记", help="作者名字")
    parser.add_argument("--background", default="热点观察员，记录全网热门事件，分享深度思考与多角度解读", help="作者背景")
    parser.add_argument("--style", default="犀利、有脾气、爱吐槽，不装理中客。看到不爽的直接骂，看到佩服的真心夸。喜欢用短句，像跟朋友聊天一样。", help="作者风格")
    parser.add_argument("--output", "-o", default="output_article.md", help="输出文件名")

    # 新增 OpenAI 相关参数
    parser.add_argument("--api-key", help="OpenAI API Key (可选，也可以通过环境变量 OPENAI_API_KEY 设置)")
    parser.add_argument("--base-url", help="OpenAI Base URL (可选，默认为官方接口，DeepSeek 请填 https://api.deepseek.com)")
    parser.add_argument("--model", help="使用的模型 (可选，默认从环境变量读取)", default=None)
    parser.add_argument("--mock", action="store_true", help="强制使用模拟模式 (不消耗 API 额度)")

    # 微信发布相关参数
    parser.add_argument("--publish", action="store_true", help="生成后自动上传至微信公众号草稿箱")
    parser.add_argument("--auto-publish", action="store_true", help="上传草稿后自动发布 (注意：这是发布为永久链接，不占用群发次数，但可能不会推送到粉丝手机)")
    parser.add_argument("--cover-id", help="微信封面图 Media ID (发布时必须)")

    # 热点抓取相关参数
    parser.add_argument("--hot", action="store_true", help="自动抓取全网热点作为主题")
    parser.add_argument("--source", default="toutiao", choices=["zhihu", "weibo", "toutiao"], help="热点来源 (toutiao/zhihu/weibo，默认toutiao最稳定)")

    # 资料收集相关参数
    parser.add_argument("--no-collect", action="store_true", help="禁用网络资料收集，纯AI生成")
    parser.add_argument("--max-resources", type=int, default=5, help="每个来源最多收集的资料数 (默认5)")
    parser.add_argument("--cleanup", action="store_true", help="生成完成后清空 data 目录")

    # 图片相关参数
    parser.add_argument("--with-images", action="store_true", help="为文章添加相关图片")
    parser.add_argument("--image-source", choices=["unsplash", "pexels", "pixabay"], help="图片来源 (unsplash/pexels/pixabay)")
    parser.add_argument("--images-per-section", type=int, default=1, help="每个章节的图片数量 (默认1)")
    parser.add_argument("--image-api-key", help="图片 API Key (也可以通过环境变量设置)")

    args = parser.parse_args()

    # 将可能被拆分的主题列表合并为一个字符串
    topic_str = " ".join(args.topic)

    # 处理热点逻辑
    if args.hot:
        print("-" * 50)
        spider = TopicSpider()
        hot_list = spider.get_hot_topics(source=args.source, limit=10)

        if hot_list:
            print(f"[*] 成功抓取到 {len(hot_list)} 个热点:")
            for i, h in enumerate(hot_list):
                print(f"  {i+1}. {h}")

            # 从前10个热点中随机选择一个
            import random
            import time
            # 使用当前时间戳和进程ID作为随机种子，确保真正的随机性
            random.seed(time.time() + os.getpid())
            topic_str = random.choice(hot_list)
            print(f"\n[*] 随机选定热点话题: 【{topic_str}】")
        else:
            print("[!] 抓取热点失败，请手动指定主题。")
            if not topic_str:
                return

    if not topic_str and not args.hot:
        print("错误: 必须指定文章主题，或者使用 --hot 参数。")
        parser.print_help()
        return

    # 设置图片 API Key（如果提供）
    if args.image_api_key:
        if args.image_source == "unsplash":
            os.environ["UNSPLASH_ACCESS_KEY"] = args.image_api_key
        elif args.image_source == "pexels":
            os.environ["PEXELS_API_KEY"] = args.image_api_key
        elif args.image_source == "pixabay":
            os.environ["PIXABAY_API_KEY"] = args.image_api_key

    print("-" * 50)
    print("[*] 启动 AI 文章生成器")
    print(f"[*] 主题: {topic_str}")
    print(f"[*] 作者: {args.name}")
    if args.mock:
        print("[*] 模式: 强制模拟 (Mock)")
    if args.with_images:
        print("[*] 图片: 已启用")
    print("-" * 50)

    # 初始化微信客户端（如果需要发布或需要上传图片）
    wechat_client = None
    if args.publish or args.with_images:
        try:
            from core.wechat_client import WeChatClient
            wechat_client = WeChatClient()
            if args.with_images:
                print("[*] 微信客户端已初始化（用于图片上传）")
        except Exception as e:
            if args.publish:
                raise
            else:
                print(f"[!] 微信客户端初始化失败: {e}")
                print(f"[!] 图片功能将不会上传到微信，仅保存到本地")

    # 传递 OpenAI 参数给 Generator
    generator = ArticleGenerator(
        provider="mock" if args.mock else None,
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        with_images=args.with_images,
        image_source=args.image_source,
        images_per_section=args.images_per_section,
        wechat_client=wechat_client
    )
    generator.set_persona(args.name, args.background, args.style)

    # ============================================
    # 完整工作流程
    # ============================================

    # 步骤1：生成文章
    print("\n" + "=" * 50)
    print("✍️  步骤1/3：生成文章")
    print("=" * 50)

    result = generator.generate_article(
        topic_str,
        collect_resources=not args.no_collect,
        max_resources=args.max_resources
    )

    if not result:
        print(f"[!] 文章生成失败")
        return

    article = result["article"]
    title = result["title"]

    # 步骤2：保存文章
    print("\n" + "=" * 50)
    print("💾 步骤2/3：保存文章")
    print("=" * 50)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"[+] 文章已保存至: {args.output}")

    # 步骤3：发布到微信（如果指定）
    article_id = None
    if args.publish:
        print("\n" + "=" * 50)
        print("🚀 步骤3/3：发布到微信公众号")
        print("=" * 50)

        # 微信发布逻辑
        if args.publish:
            print("-" * 50)
            print("[*] 正在尝试发布至微信公众号草稿箱...")

            # 智能提取标题和清洗内容
            lines = article.strip().split('\n')
            clean_lines = []

            # 1. 移除标题行（已从 result 中获取标题）
            if lines and lines[0].startswith('# '):
                lines = lines[1:]

            # 2. 移除 "核心视角" 引用块和空行
            skip_next = False
            for line in lines:
                stripped = line.strip()
                # 如果是引用块且包含"核心视角"，跳过
                if stripped.startswith('>'):
                    if "核心视角" in stripped or "核心观点" in stripped:
                        continue

                # 移除开头多余的空行
                if not clean_lines and not stripped:
                    continue

                clean_lines.append(line)

            clean_article = "\n".join(clean_lines)

            # 3. 提取摘要 (使用清洗后的第一段非空内容)
            digest = ""
            for line in clean_lines:
                if line.strip() and not line.strip().startswith(('#', '>', '-')):
                    digest = line.strip()[:54] + "..." # 微信摘要限制54字
                    break
            if not digest:
                digest = clean_article[:54] + "..."

            try:
                client = WeChatClient()
                # 检查是否有 cover-id，如果没有，尝试从 env 获取，再没有则传 None (并在 Client 内部警告)
                cover_id = args.cover_id or os.environ.get("WECHAT_COVER_ID")

                media_id = client.upload_draft(
                    title=title,
                    content=clean_article, # 使用清洗后的内容
                    author=args.name,
                    digest=digest,
                    cover_url=cover_id
                )

                if media_id:
                    print(f"[+] 成功发布到草稿箱！Media ID: {media_id}")

                    if args.auto_publish:
                        article_id = client.publish_draft(media_id)
                    else:
                        print(f"[*] 请登录微信公众平台查看并手动群发")
                else:
                    print("[-] 发布到草稿箱失败，请检查错误日志")
            except ValueError as ve:
                print(f"[!] 配置错误: {ve}")
                print("[!] 请确保在 .env 中配置了 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
            except Exception as e:
                print(f"[!] 发布过程中发生错误: {e}")

    # 完成提示
    print("\n" + "=" * 50)
    print("✅ 所有步骤完成！")
    print("=" * 50)
    if args.publish:
        print("\n💡 提示：")
        print("  - 文章已成功发布到微信公众号")
        print("  - 使用 --auto-publish 参数可自动发布为永久链接")
    else:
        print("\n💡 提示：使用 --publish 参数可自动发布到微信公众号")

    # 清理 data 目录（如果指定了 --cleanup）
    if args.cleanup:
        print("\n" + "=" * 50)
        print("🧹 正在清理 data 目录...")
        print("=" * 50)
        try:
            import shutil
            if os.path.exists('data'):
                shutil.rmtree('data')
                print("✅ data 目录已清理")
            else:
                print("  - data 目录不存在，无需清理")
        except Exception as e:
            print(f"⚠️ 清理 data 目录失败: {e}")

if __name__ == "__main__":
    main()
