# -*- coding: utf-8 -*-
"""
文章生成API路由
使用SSE(Server-Sent Events)实现流式输出
重构版：复用generator.generate_article()方法
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
import queue
import threading
import sys
import os

from core.image_manager import ImageManager

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.generator import ArticleGenerator
from core.wechat_client import WeChatClient
from core.llm_client import LLMClient

router = APIRouter()

# 懒加载的 LLM 客户端（避免启动时阻塞）
_llm_client = None

def get_llm_client():
    """获取 LLM 客户端实例（懒加载）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(
            provider="openai",  # 使用OpenAI兼容的API
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("OPENAI_MODEL", "deepseek-chat")
        )
    return _llm_client

# 进度步骤映射：后端步骤名 -> 前端格式
PROGRESS_MAPPING = {
    "start": {
        "step": 0,
        "name": "准备中...",
        "detail": "初始化生成流程",
        "status": "running"
    },
    "collecting": {
        "step": 1,
        "name": "资料收集中...",
        "detail": "正在收集相关资料",
        "status": "running"
    },
    "collected": {
        "step": 1,
        "name": "资料收集完成",
        "detail": "已收集相关资料",
        "status": "completed"
    },
    "thinking": {
        "step": 2,
        "name": "深度思考中...",
        "detail": "正在分析热点背后的本质问题",
        "status": "running"
    },
    "thought": {
        "step": 2,
        "name": "深度思考完成",
        "detail": "已完成思考分析",
        "status": "completed"
    },
    "writing": {
        "step": 3,
        "name": "初稿写作中...",
        "detail": "基于思考生成文章框架",
        "status": "running"
    },
    "drafted": {
        "step": 3,
        "name": "初稿写作完成",
        "detail": "已生成文章初稿",
        "status": "completed"
    },
    "revising_1": {
        "step": 4,
        "name": "第一轮润色中...",
        "detail": "优化语言表达和逻辑",
        "status": "running"
    },
    "revised_1": {
        "step": 4,
        "name": "第一轮润色完成",
        "detail": "已完成第一轮优化",
        "status": "completed"
    },
    "revising_2": {
        "step": 5,
        "name": "第二轮润色中...",
        "detail": "增强可读性和感染力",
        "status": "running"
    },
    "revised_2": {
        "step": 5,
        "name": "第二轮润色完成",
        "detail": "已完成第二轮优化",
        "status": "completed"
    },
    "formatting": {
        "step": 6,
        "name": "排版优化中...",
        "detail": "正在智能分段和优化排版",
        "status": "running"
    },
    "formatted": {
        "step": 6,
        "name": "排版优化完成",
        "detail": "已完成排版优化",
        "status": "completed"
    },
    "generating_title": {
        "step": 7,
        "name": "生成标题中...",
        "detail": "提炼核心观点",
        "status": "running"
    },
    "title_generated": {
        "step": 7,
        "name": "生成标题完成",
        "detail": "已生成文章标题",
        "status": "completed"
    },
    "checking": {
        "step": 8,
        "name": "质量检查中...",
        "detail": "正在检查文章质量",
        "status": "running"
    },
    "checked": {
        "step": 8,
        "name": "质量检查完成",
        "detail": "已完成质量检查",
        "status": "completed"
    },
    "completed": {
        "step": 8,
        "name": "生成完成",
        "detail": "文章已全部生成完成",
        "status": "completed"
    },
    "error": {
        "step": -1,
        "name": "生成失败",
        "detail": "生成过程出现错误",
        "status": "error"
    }
}

class PublishRequest(BaseModel):
    """发布请求模型"""
    title: str
    content: str
    images: Optional[List[str]] = []

@router.get("/generate")
async def generate_article(
    topic: str,
    auto_format: bool = True,
    add_subtitles: bool = False,
    paragraph_length: int = 60,
    persona_id: Optional[str] = None
):
    """
    生成文章（SSE流式输出）
    复用generator.generate_article()方法
    
    Args:
        topic: 话题标题
        auto_format: 是否自动排版（默认True）
        add_subtitles: 是否添加小标题（默认False，按心情开启）
        paragraph_length: 目标段落字数（默认60，更适合手机阅读）
        persona_id: 可选的人设ID，不指定则使用当前人设
        
    Returns:
        SSE流，包含生成进度和最终结果
    """
    async def event_generator():
        """SSE事件生成器"""
        try:
            # 创建队列用于线程间通信
            progress_queue = queue.Queue()
            result_container = {"result": None, "error": None}
            
            # 定义进度回调函数
            def progress_callback(step, data):
                """进度回调，将进度信息放入队列并转换为前端格式"""
                # 获取映射配置
                mapping = PROGRESS_MAPPING.get(step, {
                    "step": 0,
                    "name": "处理中...",
                    "detail": str(data),
                    "status": "running"
                })
                
                # 合并数据
                progress_data = {
                    "step": mapping["step"],
                    "name": mapping["name"],
                    "detail": mapping["detail"],
                    "status": mapping["status"]
                }
                
                # 如果data中有额外信息，添加到detail中
                if isinstance(data, dict):
                    if "title" in data:
                        progress_data["detail"] = f"标题：{data['title']}"
                    elif "count" in data:
                        progress_data["detail"] = f"已收集 {data['count']} 条资料"
                    elif "length" in data:
                        progress_data["detail"] = f"已生成 {data['length']} 字"
                
                progress_queue.put(progress_data)
            
            # 在独立线程中运行generate_article（因为它是同步的）
            def run_generation():
                try:
                    # 懒加载 LLM 客户端
                    llm_client = get_llm_client()
                    generator = ArticleGenerator(llm_client=llm_client, image_manager=ImageManager())
                    result = generator.generate_article(
                        topic=topic,
                        collect_resources=True,
                        max_resources=5,
                        progress_callback=progress_callback,
                        auto_format=True,  # 始终启用自动排版
                        add_subtitles=add_subtitles,
                        paragraph_length=paragraph_length,
                        persona_id=persona_id
                    )
                    result_container["result"] = result
                except Exception as e:
                    result_container["error"] = str(e)
                finally:
                    # 发送结束信号
                    progress_queue.put(None)
            
            # 启动生成线程
            generation_thread = threading.Thread(target=run_generation)
            generation_thread.start()
            
            # 持续从队列中读取进度并通过SSE发送
            while True:
                try:
                    # 非阻塞地获取进度，超时0.1秒
                    progress_item = progress_queue.get(timeout=0.1)
                    
                    if progress_item is None:
                        # 收到结束信号
                        break
                    
                    # 发送进度事件（progress_item已经是转换后的格式）
                    yield _create_sse_event("progress", progress_item)
                    
                    # 让出控制权
                    await asyncio.sleep(0)
                    
                except queue.Empty:
                    # 队列为空，继续等待
                    await asyncio.sleep(0.1)
                    continue
            
            # 等待线程完成
            generation_thread.join()
            
            # 检查是否有错误
            if result_container["error"]:
                yield _create_sse_event("error", {
                    "message": f"生成失败: {result_container['error']}"
                })
                return
            
            # 发送最终结果
            result = result_container["result"]
            if result:
                yield _create_sse_event("complete", {
                    "title": result["title"],
                    "content": result["article"],
                    "images": []  # 暂时不包含图片
                })
            else:
                yield _create_sse_event("error", {
                    "message": "生成失败: 未返回结果"
                })
                
        except Exception as e:
            yield _create_sse_event("error", {
                "message": f"生成失败: {str(e)}"
            })
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/publish")
async def publish_article(request: PublishRequest):
    """
    发布文章到微信公众号
    
    Args:
        request: 发布请求，包含标题、正文和配图
        
    Returns:
        发布结果
    """
    try:
        print(f"[API] 收到发布请求，标题: {request.title}")
        print(f"[API] 内容长度: {len(request.content)} 字符")
        print(f"[API] 配图数量: {len(request.images)}")
        
        wechat = WeChatClient()
        print("[API] WeChatClient 初始化成功")
        
        result = wechat.publish(
            title=request.title,
            content=request.content,
            images=request.images
        )
        
        print(f"[API] 发布结果: {result}")
        
        if result.get("success"):
            return {
                "success": True,
                "message": "发布成功",
                "data": result
            }
        else:
            return {
                "success": False,
                "message": result.get("error", "发布失败")
            }
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"[API ERROR] 发布失败:")
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"发布失败: {str(e)}")

def _create_sse_event(event_type: str, data: dict) -> str:
    """
    创建SSE事件字符串
    
    Args:
        event_type: 事件类型 (progress/complete/error)
        data: 事件数据
        
    Returns:
        格式化的SSE事件字符串
    """
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
