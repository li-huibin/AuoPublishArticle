# 开发者指南 - AI 文章生成器

> 本文档面向开发者，提供项目架构、技术实现和开发指南。

## 项目概述

这是一个**去 AI 味的微信公众号文章自动生成系统**，专注于生成高质量、具有人格化风格的热点解读文章。

**核心特性：**
- 自动抓取全网热点（今日头条/知乎/微博）
- 多阶段生成流程，强化去 AI 味
- 自适应质量检测与优化
- 微信公众号自动发布
- Web 界面 + 命令行双模式

## 技术栈

| 类别 | 技术选型 | 用途 |
|------|----------|------|
| **后端框架** | FastAPI | Web API 服务 |
| **LLM** | OpenAI API 兼容 | 文章生成（推荐 DeepSeek） |
| **爬虫** | Requests + BeautifulSoup | 热点数据抓取 |
| **文本处理** | Markdown, SnowNLP | 格式转换与情感分析 |
| **发布平台** | 微信公众号 API | 文章发布 |
| **前端** | Vanilla JavaScript | Web 界面 |

## 项目架构

### 目录结构

```
content/
├── main.py                    # 命令行入口
├── web_app.py                 # Web 服务入口（FastAPI）
├── auto_publish_daily.py      # 定时发布脚本
├── upload_cover.py            # 封面图上传工具
├── requirements.txt           # Python 依赖
├── .env                       # 环境配置（敏感信息）
├── README.md                  # 用户手册
├── DEVELOPMENT.md             # 本文档
│
├── api/                       # Web API 路由
│   ├── __init__.py
│   ├── generate.py           # 文章生成 API（SSE 流式输出）
│   └── hot_topics.py         # 热点话题 API
│
├── core/                      # 核心业务模块
│   ├── generator.py          # 文章生成器（主逻辑）
│   ├── llm_client.py         # LLM 客户端封装
│   ├── topic_spider.py       # 热点爬虫
│   ├── wechat_client.py      # 微信 API 客户端
│   ├── polisher.py           # 文章润色模块
│   ├── quality_checker.py    # 自适应质量检测
│   ├── resource_collector.py # 资源收集器
│   └── image_manager.py      # 图片管理
│
├── prompts/                   # 提示词库
│   ├── templates.py          # 文章生成模板
│   └── anti_ai_rules.py      # 去 AI 味规则
│
├── static/                    # 前端静态文件
│   └── index.html            # Web 界面（单页应用）
│
└── data/                      # 数据存储
    ├── images/               # 图片缓存
    └── resources_*.json      # 资源缓存
```

### 核心模块说明

#### 1. main.py - 命令行入口

**主要功能：**
- 解析命令行参数
- 协调文章生成流程
- 质量控制与重试机制（最多 3 次）
- 保存文章并记录数据

**关键流程：**（main.py:124-318）
```python
# 1. 生成文章（带自动重试）
article = generator.generate_article(topic, resources)

# 2. 保存文章到本地
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(article['content'])

# 3. 发布到微信（可选）
if publish:
    wechat.upload_draft(title, content, cover_id)
```

#### 2. web_app.py - Web 服务入口

**技术实现：**
- FastAPI 框架
- SSE (Server-Sent Events) 流式输出
- CORS 跨域支持

**核心路由：**
- `GET /` - 返回 Web 界面
- `GET /api/hot-topics` - 获取热点列表
- `POST /api/generate` - 生成文章（SSE 流式）

#### 3. core/generator.py - 文章生成核心

**多阶段生成流程（去 AI 味策略）：**

```python
class ArticleGenerator:
    def generate_article(self, topic, resources):
        # 阶段 1: 风格定义 (Persona)
        self.set_persona(name, style)
        
        # 阶段 2: 大纲与观点先行
        outline = self._generate_outline(topic)
        
        # 阶段 3: 分段扩写与注入细节
        content = self._expand_sections(outline, resources)
        
        # 阶段 4: 反 AI 润色
        polished = self.polisher.polish(content)
        
        return polished
```

**关键方法：**
- `set_persona()` - 设置作者人设
- `generate_article()` - 生成完整文章
- `record_published_article()` - 记录发布数据

#### 4. core/topic_spider.py - 热点爬虫

**支持的数据源：**

| 平台 | API/URL | 数据格式 |
|------|---------|----------|
| 今日头条 | `https://www.toutiao.com/hot-event/hot-board/` | JSON |
| 知乎 | `https://www.zhihu.com/api/v4/creators/rank/hot` | JSON |
| 微博 | `https://s.weibo.com/top/summary` | HTML 解析 |

**实现示例：**
```python
def fetch_toutiao_hot():
    resp = requests.get('https://www.toutiao.com/hot-event/hot-board/')
    data = resp.json()
    return [{'title': item['Title'], 'hot': item['HotValue']} 
            for item in data['data']]
```

#### 5. core/wechat_client.py - 微信 API 客户端

**核心功能：**
- 获取 Access Token（自动刷新）
- 上传草稿到草稿箱
- 发布草稿为永久链接
- Markdown 转微信公众号 HTML

**关键实现：**
```python
class WeChatClient:
    def publish(self, title, content, cover_url=None):
        # 1. 清理内容（移除标题行、核心视角引用块、提取摘要）
        cleaned_content = self._clean_content(content)
        
        # 2. 转换为微信 HTML 格式
        html_content = self._markdown_to_wechat_html(cleaned_content)
        
        # 3. 处理封面图
        thumb_media_id = cover_url or os.environ.get("WECHAT_COVER_ID")
        
        # 4. 上传草稿
        draft_id = self.upload_draft(title, html_content, thumb_media_id)
        
        # 5. 发布为永久链接
        article_id = self.publish_draft(draft_id)
        
        return article_id
```

#### 6. core/quality_checker.py - 质量检测

**自适应评分系统：**

```python
def check_quality(article):
    scores = {
        'authenticity': check_authenticity(article),  # 真实感
        'ai_detection': detect_ai_content(article),   # AI 味检测
        'emotion': analyze_emotion(article),          # 情感分析
        'structure': check_structure(article)         # 结构合理性
    }
    
    # 综合评分
    total_score = sum(scores.values()) / len(scores)
    return total_score, scores
```

#### 7. prompts/templates.py - 提示词模板

**人设定义：**
```python
PERSONA = {
    "name": "小苏的热事笔记",
    "style": "犀利、有脾气、爱吐槽，不装理中客",
    "tone": "直率、幽默、接地气",
    "perspective": "独立思考，敢于质疑主流观点"
}
```

**文章结构模板：**
```python
ARTICLE_STRUCTURE = """
1. 事件回顾（简要概述，不要流水账）
2. 背景分析（挖掘深层原因）
3. 多角度解读（至少 3 个独特观点）
4. 趋势预测（基于逻辑推理）
"""
```

#### 8. prompts/anti_ai_rules.py - 去 AI 味规则

**禁用词汇列表：**
```python
FORBIDDEN_WORDS = [
    "综上所述", "总而言之", "首先、其次、最后",
    "宏大的画卷", "织就", "交响曲",
    "不仅...而且...", "一方面...另一方面..."
]
```

**风格约束：**
```python
STYLE_RULES = [
    "禁止使用标准三段式结构",
    "每段必须包含具体例子或数据",
    "句式长短交替，避免过度整齐",
    "适当使用口语化表达和网络用语"
]
```

## 核心技术实现

### 1. 去 AI 味策略（Humanize Strategy）

**多阶段生成流程：**

1. **风格定义（Style Definition）**
   - 不直接生成文章，先设定具体的"人类画像"（Persona）
   - 示例："你是一个科技行业老兵，说话直率，喜欢用比喻"

2. **大纲与观点先行（Outline & Opinion First）**
   - 强制 AI 通过"头脑风暴"产生独特观点
   - 禁止标准三段式结构

3. **分段扩写与注入细节（Drafting with Details）**
   - 依据大纲分段生成
   - **Show, Don't Tell** - 每段必须包含具体例子

4. **反 AI 润色（Anti-AI Polishing）**
   - 专门的编辑 Agent 检查并修改草稿
   - **负面约束** - 明确禁止列表（如"综上所述"）

### 2. SSE 流式输出实现

**后端（api/generate.py）：**
```python
@router.post("/generate")
async def generate_article(request: Request):
    async def event_stream():
        # 流式输出进度
        yield f"data: {json.dumps({'status': 'progress', 'message': '正在生成...'})}\n\n"
        
        # 生成完成
        yield f"data: {json.dumps({'status': 'complete', 'data': article})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

**前端（static/index.html）：**
```javascript
const eventSource = new EventSource('/api/generate');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status === 'complete') {
        displayArticle(data.data);
        eventSource.close();
    }
};
```

### 3. 微信公众号 HTML 转换

**Markdown → 微信公众号样式：**
```python
def _markdown_to_wechat_html(self, content):
    # 1. 转换 Markdown
    html = markdown.markdown(content)
    
    # 2. 添加微信公众号样式
    styled_html = f"""
    <section style="font-size: 16px; line-height: 1.8;">
        {html}
    </section>
    """
    
    return styled_html
```

## 开发指南

### 环境配置

**1. 安装依赖：**
```bash
pip install -r requirements.txt
```

**2. 配置环境变量（.env）：**
```properties
# LLM 配置
OPENAI_API_KEY=sk-xxxxxx
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat

# 微信公众号配置
WECHAT_APP_ID=wxxxxxxxxxx
WECHAT_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
WECHAT_COVER_ID=xxxxxx  # 可选，默认封面图 Media ID
```

### 本地开发

**运行 Web 服务：**
```bash
python web_app.py
# 访问 http://localhost:8000
```

**命令行测试：**
```bash
# 模拟模式（不消耗 API 额度）
python main.py --hot --mock

# 降低质量要求快速测试
python main.py --hot --min-score 60
```

### 代码规范

1. **编码风格**
   - 遵循 PEP 8 规范
   - 使用 UTF-8 编码
   - 中文注释和文档字符串

2. **命名约定**
   - 类名：大驼峰（ArticleGenerator）
   - 函数/变量：小写下划线（generate_article）
   - 常量：全大写下划线（FORBIDDEN_WORDS）

3. **注释规范**
   ```python
   def generate_article(self, topic: str, resources: list) -> dict:
       """生成文章
       
       Args:
           topic: 文章主题
           resources: 参考资源列表
           
       Returns:
           包含 title、content 等字段的字典
       """
   ```

### 测试建议

**单元测试：**
```python
# 测试热点爬虫
python -m pytest tests/test_topic_spider.py

# 测试文章生成
python -m pytest tests/test_generator.py
```

**集成测试：**
```bash
# 端到端测试（模拟模式）
python main.py --hot --mock --min-score 60
```

## 常见开发任务

### 1. 修改文章风格

**步骤：**
1. 编辑 `prompts/templates.py` 中的 `PERSONA` 和 `ARTICLE_STRUCTURE`
2. 调整 `prompts/anti_ai_rules.py` 中的禁用词列表
3. 测试生成效果：`python main.py --hot --mock`

### 2. 添加新的热点源

**在 core/topic_spider.py 中添加：**
```python
def fetch_custom_hot(self):
    """抓取自定义热点源"""
    resp = requests.get('https://example.com/api/hot')
    data = resp.json()
    
    topics = []
    for item in data['list']:
        topics.append({
            'title': item['title'],
            'hot_value': item['views'],
            'url': item['link']
        })
    
    return topics
```

### 3. 调整质量检测规则

**修改 core/quality_checker.py：**
```python
def check_authenticity(self, article):
    """真实感检测"""
    score = 100
    
    # 自定义检测规则
    if "综上所述" in article:
        score -= 20
    
    if not self._has_specific_examples(article):
        score -= 30
    
    return max(0, score)
```

### 4. 扩展 Web API

**在 api/ 目录下新建路由文件：**
```python
# api/analytics.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/stats")
async def get_stats():
    """获取文章统计数据"""
    return {"total": 100, "published": 80}
```

**注册路由（web_app.py）：**
```python
from api import analytics
app.include_router(analytics.router)
```

## 部署指南

### 本地部署

```bash
# 1. 克隆项目
git clone https://gitee.com/sub_callow/AuoPublishArticle.git
cd AuoPublishArticle

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 运行服务
python web_app.py
```

### 服务器部署

**使用 Supervisor 管理进程：**
```ini
[program:article-generator]
command=/usr/bin/python3 /path/to/web_app.py
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/article-generator.err.log
stdout_logfile=/var/log/article-generator.out.log
```

### 定时任务配置

**Linux Crontab：**
```bash
# 每天 8:00 发布早班文章
0 8 * * * cd /path/to/project && python auto_publish_daily.py morning

# 每天 20:00 发布晚班文章
0 20 * * * cd /path/to/project && python auto_publish_daily.py evening
```

**Windows 任务计划程序：**
- 创建基本任务
- 触发器：每天 8:00 / 20:00
- 操作：启动程序 `python.exe`
- 参数：`auto_publish_daily.py morning`

## 故障排查

### 常见问题

**1. API 调用失败**
```python
# 检查环境变量
import os
print(os.environ.get('OPENAI_API_KEY'))
print(os.environ.get('OPENAI_BASE_URL'))

# 测试连接
python -c "from core.llm_client import LLMClient; client = LLMClient(); print(client.test_connection())"
```

**2. 微信发布失败**
- 检查 IP 白名单配置
- 验证 AppID 和 AppSecret
- 确认封面图 Media ID 有效

**3. 热点爬取失败**
- 检查网络连接
- 验证 API 地址是否变更
- 查看 User-Agent 是否被封禁

### 日志调试

**启用详细日志：**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**查看 Web 服务日志：**
```bash
# 运行时输出到控制台
python web_app.py

# 重定向到文件
python web_app.py > app.log 2>&1
```

## 性能优化

### 1. LLM 调用优化

```python
# 使用缓存避免重复调用
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_outline(topic):
    return llm_client.generate(prompt)
```

### 2. 热点数据缓存

```python
# 缓存热点数据 5 分钟
import time

cache = {'data': None, 'timestamp': 0}

def fetch_hot_with_cache():
    if time.time() - cache['timestamp'] < 300:
        return cache['data']
    
    data = fetch_toutiao_hot()
    cache['data'] = data
    cache['timestamp'] = time.time()
    return data
```

## 扩展方向

### 1. Few-Shot Learning
- 支持用户上传参考范文
- 通过风格模仿提升生成质量

### 2. 多模型支持
- 接入 Claude、文心一言等多个 LLM
- 实现模型性能对比

### 3. 内容审核
- 集成敏感词过滤
- 添加事实核查机制

### 4. 数据分析
- 记录文章阅读数据
- 分析热点趋势

## 贡献指南

### 提交代码

1. Fork 项目到个人仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -m "添加新功能"`
4. 推送到分支：`git push origin feature/new-feature`
5. 提交 Pull Request

### 代码审查要点

- 代码风格是否符合规范
- 是否添加必要的注释
- 是否包含测试用例
- 是否更新相关文档

## 安全注意事项

1. **敏感信息保护**
   - `.env` 文件不提交到 Git
   - API Key 使用环境变量
   - 定期轮换密钥

2. **API 额度管理**
   - 开发时使用 `--mock` 模式
   - 设置调用频率限制
   - 监控 API 消耗情况

3. **微信 IP 白名单**
   - 及时更新服务器 IP
   - 使用固定 IP 或域名
   - 定期检查白名单状态

## 相关资源

- **微信公众平台开发文档**: https://developers.weixin.qq.com/doc/
- **OpenAI API 文档**: https://platform.openai.com/docs/
- **DeepSeek API 文档**: https://api-docs.deepseek.com/
- **FastAPI 官方文档**: https://fastapi.tiangolo.com/

---

*最后更新: 2026-04-02*
