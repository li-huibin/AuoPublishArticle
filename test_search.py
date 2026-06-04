#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试新的主题搜索功能"""

from core.topic_spider import TopicSpider

def test_search():
    spider = TopicSpider()
    
    # 测试多个关键词
    keywords = ["职场", "裁员", "AI", "新能源"]
    
    for keyword in keywords:
        print(f"\n{'='*60}")
        print(f"搜索关键词: {keyword}")
        print('='*60)
        
        results = spider.search_topics(keyword, limit=5)
        
        print(f"\n找到 {len(results)} 条结果：")
        for i, item in enumerate(results, 1):
            print(f"{i}. {item['title']}")
            print(f"   热度: {item['heat']}")

if __name__ == "__main__":
    test_search()
