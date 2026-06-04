# AI 文章生成器 - 小苏的热事笔记

这是一个专注于生成**高质量、去 AI 味、适合新媒体传播**的文章生成器。
特别针对**微信公众号热点解读号**进行了优化，支持**自动抓取热点、自动写作、自动排版、自动发布**一条龙服务。

## 🎯 "小苏的热事笔记" 账号定位

**账号名称**: 小苏的热事笔记  
**功能介绍**: 记录全网热门事件，分享深度思考与多角度解读

**核心优势**（发挥AI创作者的独特价值）：
- ⚡ **快速响应**: 热点出现3小时内给出深度解读
- 🔄 **高频更新**: 每日早晚双更，持续输出优质内容
- 🎯 **信息密集**: 用最短时间讲清热点本质和背后逻辑
- 🌐 **跨领域覆盖**: 从科技到娱乐，从财经到社会，全方位热点追踪

**内容风格**：
- 信息密集、逻辑清晰、观点鲜明
- 多角度解读（当事人/围观者/专家/历史对比）
- 避免情绪化站队，注重客观分析
- 结构："事件回顾 → 背景分析 → 多角度解读 → 趋势预测"

---

## 🌟 核心特性

### 🔍 多源资料收集器（核心模块）
- **百度搜索集成**: 自动搜索相关网页，提取标题、摘要和原文链接
- **智能全文抓取**: 自动跳转搜索结果链接，抓取完整文章内容（反反爬优化）
- **多轮解析策略**: 优先提取正文容器，降级收集所有有效段落
- **资料质量检测**: 自动评估收集到的资料质量（全文数量、内容长度、可信度）
- **智能格式化**: 将收集的资料整理为 AI 友好的格式，包含引用规则

### 📰 热点自动抓取
- 支持今日头条、知乎、微博热榜
- 配有本地兜底热点库，网络异常时也能正常运行

### ✍️ 智能解读生成
- 基于"事件回顾-背景分析-多角度解读-趋势预测"结构
- 3分钟讲清热点本质

### 🎨 自动排版引擎
- 生成的文章自带公众号风格排版（CSS）
- 使用 HTML `<strong>` 标签实现加粗，微信完美兼容

### 📱 微信全自动接入
- 一键上传至**公众号草稿箱**
- 支持**自动发布**（生成永久链接）
- 支持**定时自动化**（每日早晚双更）

### 🖼️ 智能配图
- **多图库支持**: Unsplash、Pexels、Pixabay 三大免费图库
- **智能关键词**: 自动中英文翻译，结合章节类型生成多样化搜索词
- **统一显示**: 固定高度 450px + object-fit 裁剪，所有图片显示一致
- **去重机制**: 自动跳过已使用图片，确保每张图都是唯一的

### 🤖 去 AI 味
- 拒绝"综上所述"、"赋能"等机器味
- 主打信息密集、逻辑清晰、观点鲜明

### 🚀 DeepSeek 驱动
- 默认针对 DeepSeek 模型优化，性价比极高

---

## 🛠️ 安装与使用

### 1. 安装依赖
请确保安装了必要的 Python 库：
```bash
pip install -r requirements.txt
```

### 2. 配置环境 (.env)
在项目根目录创建 `.env` 文件，填入以下配置：

```properties
# LLM 配置 (推荐使用 DeepSeek)
OPENAI_API_KEY=sk-xxxxxx
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat

# 微信公众号配置 (发布功能必须)
WECHAT_APP_ID=wxxxxxxxxxx
WECHAT_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
# (可选) 默认封面图 Media ID
WECHAT_COVER_ID=...

# 图片 API 配置 (任选一个或多个，用于智能配图)
# Unsplash: https://unsplash.com/developers
UNSPLASH_ACCESS_KEY=your_unsplash_access_key
# Pexels: https://www.pexels.com/api/
PEXELS_API_KEY=your_pexels_api_key
# Pixabay: https://pixabay.com/api/docs/
PIXABAY_API_KEY=your_pixabay_api_key

# 图片默认配置
IMAGE_DEFAULT_SOURCE=unsplash
IMAGE_CACHE_DIR=data/images
```

### 3. 获取图片 API Key（可选，用于智能配图）

你只需要配置**任意一个**图库即可使用智能配图功能。

#### 方案一：Unsplash（推荐，图片质量最高）

1. 访问 https://unsplash.com/developers
2. 注册/登录账号
3. 创建应用（New Application）
   - 应用名称：AI Article Generator
   - 描述：用于为文章生成相关图片
4. 获取 Access Key，填入 `.env` 的 `UNSPLASH_ACCESS_KEY`

**API 限制**：每小时 50 次请求

#### 方案二：Pixabay（申请最简单）

1. 访问 https://pixabay.com/
2. 注册账号
3. 访问 https://pixabay.com/api/docs/ 获取 API Key
4. 填入 `.env` 的 `PIXABAY_API_KEY`

**API 限制**：每分钟 100 次请求，无每日限制

#### 方案三：Pexels

1. 访问 https://www.pexels.com/api/
2. 注册账号并申请 API Key
3. 填入 `.env` 的 `PEXELS_API_KEY`

**API 限制**：每小时 200 次请求

### 4. 获取封面图 ID (Media ID)
微信接口要求发布文章必须带封面图。你可以使用自带的小工具一键获取：

```bash
# 找一张图片放在项目目录，例如 cover.jpg
python upload_cover.py cover.jpg

# 运行后会显示 Media ID，请复制它
```

---

## 📖 使用方式

### 方式一：命令行模式

#### 🎯 场景一：自动抓取热点 + 发布（推荐用于日常养号）
程序会自动从今日头条抓取热榜第一条，生成深度解读文章，并发布到公众号。
```bash
# 抓取热点 + 上传草稿箱
python main.py --publish --cover-id "你的MediaID"

# 抓取热点 + 自动发布（生成链接）
python main.py --publish --auto-publish --cover-id "你的MediaID"
```

#### 🔍 场景二：指定热点源
默认抓取今日头条，也可以指定其他平台：
```bash
# 从知乎热榜抓取
python main.py --source zhihu --publish --cover-id "你的MediaID"

# 从微博热搜抓取
python main.py --source weibo --publish --cover-id "你的MediaID"
```

#### ✍️ 场景三：手动指定话题
不使用爬虫，手动指定要写的话题：
```bash
python main.py "如何看待2026年春节档电影票价争议" --publish --cover-id "你的MediaID"
```

#### 💾 场景四：仅生成文件（本地测试）
不发公众号，只生成 Markdown 文件到本地。
```bash
python main.py --source toutiao
```

#### 🖼️ 场景五：智能配图（推荐）
为文章自动添加相关图片，支持 Unsplash、Pexels、Pixabay 三大图库：
```bash
# 基础配图（使用默认图库 unsplash）
python main.py "如何看待人工智能发展" --with-images

# 指定图片来源
python main.py --hot --with-images --image-source pexels

# 每章节多张图片（默认每节1张）
python main.py "无人驾驶" --with-images --images-per-section 2

# 完整流程：抓取热点 + 配图 + 发布
python main.py --hot --with-images --publish --cover-id "你的MediaID"
```

---

### 方式二：Web 界面模式

#### 启动 Web 服务

```bash
python web_app.py
```

启动成功后，访问：**http://localhost:8000**

#### 使用界面

1. **选择热点**：在左侧选择今日热点话题，或输入自定义话题
2. **生成文章**：点击"开始生成"按钮，观察AI工作台的实时进度
3. **编辑文章**：生成完成后，可编辑标题、正文和管理配图
4. **预览发布**：点击"微信预览"查看效果，确认后发布到微信公众号

#### Web 模式特点

- ✅ 可视化的热点选择
- ✅ 实时的生成进度（SSE流式输出）
- ✅ 灵活的编辑功能
- ✅ 便捷的发布流程
- ✅ 现代化的用户界面（Tailwind CSS）

---

## ⏰ 定时自动化发布（每日养号）

使用内置的 `auto_publish_daily.py` 脚本实现每日自动更新。

### 脚本功能
- **早班模式**（morning）：早8点发布"热点速递"
- **晚班模式**（evening）：晚8点发布"深度解读"
- **自动日志**：记录每次发布情况到 `publish_log.txt`

### Windows 计划任务配置

**第一步：测试脚本是否正常运行**
```bash
# 测试早班发布
python auto_publish_daily.py morning

# 测试晚班发布
python auto_publish_daily.py evening
```

**第二步：创建批处理文件**

在项目目录创建 `morning_publish.bat`：
```batch
@echo off
cd /d D:\study\content
python auto_publish_daily.py morning
```

在项目目录创建 `evening_publish.bat`：
```batch
@echo off
cd /d D:\study\content
python auto_publish_daily.py evening
```

**第三步：配置 Windows 计划任务**

1. 按 `Win + R`，输入 `taskschd.msc`，打开"任务计划程序"
2. 点击右侧"创建基本任务"

**配置早班任务（每天早8点）**：
- 名称：`小苏的热事笔记-早班发布`
- 触发器：每天，时间 `08:00:00`
- 操作：启动程序，浏览选择 `D:\study\content\morning_publish.bat`
- 完成后勾选"属性对话框"

在属性中：
- 勾选"不管用户是否登录都要运行"
- 勾选"使用最高权限运行"
- 起始位置填：`D:\study\content`

**配置晚班任务（每天晚8点）**：
- 名称：`小苏的热事笔记-晚班发布`
- 触发器：每天，时间 `20:00:00`
- 操作：启动程序，浏览选择 `D:\study\content\evening_publish.bat`
- 其他配置同上

**第四步：测试计划任务**
- 右键任务，点击"运行"
- 检查 `publish_log.txt` 文件查看执行情况

### Linux/Mac Cron 配置

编辑 crontab：
```bash
crontab -e
```

添加以下内容：
```bash
# 每天早8点发布
0 8 * * * cd /path/to/content && /usr/bin/python3 auto_publish_daily.py morning >> publish_log.txt 2>&1

# 每天晚8点发布
0 20 * * * cd /path/to/content && /usr/bin/python3 auto_publish_daily.py evening >> publish_log.txt 2>&1
```

---

## 📂 项目结构

```
D:/study/content/
├── README.md              # 📘 本文档（用户手册）
├── DEVELOPMENT.md         # 📗 开发者指南
├── LICENSE                
├── .env                   # 环境配置
├── requirements.txt       # 依赖列表
├── adaptive_config.json   # 自适应配置
├── main.py               # 命令行入口
├── web_app.py            # Web服务入口
├── auto_publish_daily.py # 定时发布脚本
├── upload_cover.py       # 封面上传工具
├── morning_publish.bat   # 定时任务模板
├── publish_log.txt       # 发布日志
├── api/                  # API路由模块
│   ├── __init__.py
│   ├── hot_topics.py    # 热点获取API
│   └── generate.py      # 文章生成API（SSE流式输出）
├── core/                 # 核心业务逻辑
│   ├── generator.py     # 文章生成器
│   ├── resource_collector.py  # 资源收集器（核心）
│   ├── image_manager.py # 图片管理器
│   ├── topic_spider.py  # 热点爬虫
│   ├── wechat_client.py # 微信客户端
│   ├── llm_client.py    # LLM客户端封装
│   ├── polisher.py      # 润色模块
│   └── quality_checker.py # 质量检测
├── prompts/              # 提示词模板
│   ├── templates.py     # 文章生成模板
│   └── anti_ai_rules.py # 去AI味规则
├── static/               # Web界面
│   └── index.html
└── data/
    ├── images/          # 图片缓存
    └── .gitkeep
```

---

## 🚀 后续功能开发

项目将持续迭代优化，以下是规划中的重要功能：

### 1. SEO优化模块
为生成的文章提供全面的SEO优化支持，提升搜索引擎可见度和流量获取能力。

**核心功能**：
- 🔍 **智能关键词提取**：基于TF-IDF算法或LLM自动提取文章核心关键词
- 📊 **关键词密度分析**：确保关键词密度在2%-5%的最佳范围内
- 🏷️ **标签自动生成**：为文章生成3-5个相关标签
- 📝 **多版本摘要**：自动生成50字/100字/200字等不同长度的文章摘要
- 📈 **可读性分析**：评估文章可读性得分，提供改进建议
- 🔗 **内链建议**：推荐相关文章的内链插入位置
- 📋 **SEO综合报告**：生成完整的SEO优化报告和改进建议

**技术栈**：
- jieba分词（中文分词）
- scikit-learn（TF-IDF算法）
- LLM辅助分析

**开发进度**：规划中（详见 `core/seo_optimizer.py`）

### 2. 多平台发布
支持将同一篇文章根据不同平台特性自动调整风格后，一键发布到多个自媒体平台。

**目标平台**：
- 📱 微信公众号（已支持）
- 🎬 今日头条
- 📖 知乎
- 🐦 微博
- 📝 掘金
- 🌐 更多平台...

**核心挑战**：
- 不同平台的文章风格差异较大，需要针对性调整
- 各平台API接口和发布流程不同
- 图片格式和尺寸要求各异

**技术方案**：
- 建立平台特性配置文件
- 为每个平台创建独立的风格适配器
- 统一的发布接口封装
- 智能的内容格式转换

**开发进度**：规划中（需求分析阶段）

---

**注意**：以上功能目前暂不开发，优先保证核心功能的稳定性和质量。功能开发的优先级将根据用户反馈和实际需求动态调整。

---

## ⚠️ 常见问题

### 1. 报错 `invalid ip ... not in whitelist`
- **原因**：你的 IP 没在公众号白名单里
- **解决**：去微信公众平台 → 设置与开发 → 基本配置 → IP白名单，把报错里的 IP 加进去

### 2. 爬虫抓取失败怎么办？
- 今日头条最稳定（推荐），知乎和微博偶尔会反爬
- 如果抓取失败，程序会自动使用**本地兜底热点库**（内置15个近期热点话题，随机选择）
- 也可以手动指定话题：`python main.py "具体热点话题"`
- 或者切换到其他热点源：`--source zhihu` 或 `--source weibo`

### 3. 遇到 WinError 10013 错误？
- 这是 Windows 网络套接字权限问题，可能是防火墙/杀毒软件/代理阻止了连接
- **解决方法**：
  - 检查防火墙设置，允许 Python 访问网络
  - 尝试关闭代理/VPN 后重试
  - 程序会自动使用本地兜底热点库，不影响使用

### 4. 生成的文章不够"热点解读"风格？
- 检查 `prompts/templates.py` 中的人设定义是否正确
- 确认使用的是最新版本的提示词模板
- 可以在 `main.py` 中调整 `--style` 参数来微调风格

### 5. 定时任务没有执行？
- Windows：检查任务计划程序中任务状态，查看"上次运行结果"
- 查看 `publish_log.txt` 文件，里面有详细的执行日志
- 确保批处理文件路径正确，Python 环境变量配置正确

### 6. 发布后格式乱了？
- 程序内置了自动排版（Markdown 转 HTML + CSS），通常直接发就很漂亮
- 现在使用 `<strong>` 标签而非 `**` 来加粗，微信公众号兼容性更好
- 如果需要微调，建议先发到草稿箱，在后台调整

### 7. 能不能自动推送到粉丝手机？
- 目前脚本只支持"上传草稿"和"发布（生成链接）"
- 自动"群发"（推送给粉丝）接口风险较大且每天次数有限，建议人工在后台操作

### 8. 图片功能怎么用？
- 先在 .env 配置图片 API Key（推荐 Unsplash，免费且图片质量高）
- 使用 `--with-images` 参数启用配图
- 可选：`--image-source` 指定图库（unsplash/pexels/pixabay）
- 可选：`--images-per-section` 设置每章节图片数量

### 9. 图片与内容不匹配怎么办？
- 系统已内置中英文关键词映射，会自动将中文主题翻译成英文搜索
- 不同章节会使用不同类型关键词（场景/鸟瞰/夜景/日落等）增加多样性
- 如果仍不满意，可以手动修改生成的 Markdown 文件中的图片

### 10. 图片尺寸不一致？
- 已统一设置 `height: 450px` + `object-fit: cover`
- 所有图片都会裁剪填充到相同高度显示
- 如需要调整，可修改 `core/image_manager.py` 中的 `height` 值

### 11. Web服务端口冲突？
- 修改 `web_app.py` 中的端口号：
  ```python
  uvicorn.run(app, host="0.0.0.0", port=8000)  # 改为其他端口
  ```

### 12. 热点加载失败怎么办？
- 检查网络连接是否正常
- 检查 `core/topic_spider.py` 中的热点源是否可访问
- 查看控制台错误信息

---

## 📝 养号建议

### 初期（1-2周）
- 先手动发布几篇，测试文章质量和用户反馈
- 根据反馈调整提示词和风格参数
- 观察不同热点源的内容质量，选择最合适的

### 稳定期（第3周起）
- 启用定时任务，实现每日早晚双更
- 保持内容的稳定输出，建立用户阅读习惯
- 定期查看 `publish_log.txt`，确保自动化正常运行

### 优化技巧
- 早班（8点）适合发"热点速递"，快速响应昨晚到今晨的热点
- 晚班（20点）适合发"深度解读"，对当天热点进行深入分析
- 建议保留草稿箱发布方式，人工审核后再群发，确保内容质量

---

## 📚 更多信息

- 开发者指南：请查看 [DEVELOPMENT.md](./DEVELOPMENT.md)
- 问题反馈：请提交 GitHub Issue
- 技术支持：详见开发者文档

---

**祝你使用愉快！开始创作高质量的热点解读文章吧！** 🎉
