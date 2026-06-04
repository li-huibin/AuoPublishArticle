# -*- coding: utf-8 -*-
"""
FastAPI Web服务主入口
提供Web界面和API接口
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI

# 加载环境变量（必须在导入其他模块之前）
load_dotenv()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# 导入API路由
from api import hot_topics, generate, persona

# 创建FastAPI应用
app = FastAPI(
    title="AI文章生成工作台",
    description="选热点 → 流式生成 → 编辑成品 → 发布到微信",
    version="1.0.0"
)

# 配置CORS（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册API路由
app.include_router(hot_topics.router, prefix="/api", tags=["热点"])
app.include_router(generate.router, prefix="/api", tags=["生成"])
app.include_router(persona.router, prefix="/api", tags=["人设"])

# 根路径重定向到静态页面
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页面"""
    static_path = os.path.join("static", "index.html")
    with open(static_path, "r", encoding="utf-8") as f:
        return f.read()

# 应用启动时的预热操作
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    print("🔥 预热LLM客户端...")
    try:
        # 预先初始化LLM客户端，避免首次请求时卡顿
        from api.generate import get_llm_client
        get_llm_client()
        print("✅ LLM客户端预热完成")
    except Exception as e:
        print(f"⚠️  LLM客户端预热失败: {e}")
        print("   首次生成文章时可能会有延迟")

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动AI文章生成工作台...")
    print("📝 访问地址: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
