# -*- coding: utf-8 -*-
"""
热点话题API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.topic_spider import TopicSpider

router = APIRouter()

@router.get("/search")
async def search_topics(keyword: str, limit: int = 10) -> List[Dict]:
    """
    搜索热点话题
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量（默认10）
    
    Returns:
        搜索到的话题列表
    """
    try:
        # 创建话题爬虫
        spider = TopicSpider()
        
        # 搜索热点话题
        topics = spider.search_topics(keyword=keyword, limit=limit)
        
        # 转换为前端需要的格式
        result = []
        for idx, topic_data in enumerate(topics):
            title = topic_data.get("title", "")
            heat_value = topic_data.get("heat", 0)
            
            result.append({
                "id": idx + 1,
                "title": title,
                "icon": _get_topic_icon(title, idx),
                "heat": _format_heat_value(heat_value),
                "source": "搜索结果"
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/hot")
async def get_hot_topics(offset: int = 0, limit: int = 10) -> List[Dict]:
    """
    获取今日热点话题列表
    
    Args:
        offset: 偏移量，用于分页（默认0）
        limit: 每页数量（默认10）
    
    Returns:
        热点话题列表，每个话题包含：
        - id: 话题ID
        - title: 话题标题
        - icon: 图标emoji
        - heat: 热度值
        - source: 来源
    """
    try:
        # 创建话题爬虫
        spider = TopicSpider()
        
        # 获取更多热点话题以支持分页轮换（获取30条）
        all_topics = spider.get_hot_topics(source="toutiao", limit=30)
        
        # 根据offset和limit返回对应批次
        topics = all_topics[offset:offset + limit]
        
        # 转换为前端需要的格式
        result = []
        for idx, topic_data in enumerate(topics):
            # 兼容新旧格式
            if isinstance(topic_data, dict):
                title = topic_data.get("title", "")
                heat_value = topic_data.get("heat", 0)
            else:
                title = topic_data
                heat_value = 0
            
            result.append({
                "id": idx + 1,
                "title": title,
                "icon": _get_topic_icon(title, idx),
                "heat": _format_heat_value(heat_value),
                "source": "今日头条"
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热点失败: {str(e)}")

def _format_heat_value(heat) -> str:
    """
    格式化热度值，类似抖音显示方式
    
    Args:
        heat: 热度数值（int或str）
    
    Returns:
        格式化后的热度字符串（如：100万、50.5万、9999）
    """
    # 确保heat是整数类型
    try:
        heat_int = int(heat) if heat else 0
    except (ValueError, TypeError):
        heat_int = 0
    
    if heat_int >= 10000:
        # 大于1万，显示为"XX万"或"XX.X万"
        wan_value = heat_int / 10000
        if wan_value >= 100:
            return f"{int(wan_value)}万"
        else:
            return f"{wan_value:.1f}万"
    else:
        # 小于1万，直接显示数字
        return str(heat_int)

def _get_topic_icon(title: str, index: int = 0) -> str:
    """
    根据话题标题返回合适的图标（支持20+分类智能匹配）
    
    Args:
        title: 话题标题
        index: 话题索引（用于生成多样化的默认图标）
    
    Returns:
        emoji图标
    """
    # 关键词图标映射表（20+个分类）
    keyword_icons = {
        '💻': ["科技", "AI", "人工智能", "芯片", "手机", "电脑", "网络", "互联网", "软件", "硬件"],
        '💰': ["经济", "股市", "金融", "投资", "货币", "贸易", "商业", "企业"],
        '🎬': ["娱乐", "明星", "电影", "音乐", "综艺", "演员", "歌手"],
        '⚽': ["体育", "足球", "篮球", "奥运", "比赛", "运动", "球员", "冠军"],
        '🏛️': ["政治", "政府", "外交", "选举", "国际"],
        '👥': ["社会", "民生", "教育", "就业", "养老"],
        '🎖️': ["军事", "国防", "武器", "战争"],
        '🌍': ["环境", "气候", "环保", "污染", "生态"],
        '🏥': ["健康", "医学", "疾病", "药物", "医疗", "疫情"],
        '✈️': ["旅游", "景点", "假期", "出行"],
        '🍜': ["美食", "餐饮", "食品", "厨艺"],
        '🎮': ["游戏", "电竞", "玩家"],
        '🚗': ["汽车", "交通", "车辆", "驾驶"],
        '🏠': ["房产", "建筑", "地产", "楼市"],
        '🎨': ["文化", "艺术", "展览", "博物馆"],
        '🔬': ["科学", "研究", "发现", "实验"],
        '🚀': ["太空", "航天", "火箭", "卫星"],
        '🐾': ["动物", "宠物", "萌宠"],
        '⛈️': ["天气", "灾害", "地震", "台风"],
        '⚖️': ["法律", "犯罪", "案件", "法院"],
        '📚': ["学习", "考试", "学校", "大学", "高考"],
        '💼': ["职场", "工作", "招聘", "求职"]
    }
    
    # 遍历关键词匹配
    for icon, keywords in keyword_icons.items():
        if any(keyword in title for keyword in keywords):
            return icon
    
    # 如果没有匹配到关键词，使用多样化的默认图标池（基于索引循环）
    default_icons = ['📰', '📌', '💡', '🔔', '⭐', '🎯', '📣', '🌟', '💬', '🎪', '🎭', '🎨', '🎬', '📸', '🎵']
    return default_icons[index % len(default_icons)]
