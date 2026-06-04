# -*- coding: utf-8 -*-
"""
今日热观察 - 自动化发布脚本
用于定时任务，每日自动抓取热点并发布到公众号

使用方法：
1. Windows计划任务：
   - 打开"任务计划程序"
   - 创建基本任务，名称"今日热观察早班"
   - 触发器：每天早上8:00
   - 操作：启动程序 python，参数：D:/study/content/auto_publish_daily.py morning
   - 同理创建"今日热观察晚班"，时间改为晚上8:00，参数改为 evening

2. Linux/Mac Cron：
   - 编辑 crontab: crontab -e
   - 添加：0 8 * * * cd /path/to/content && python auto_publish_daily.py morning
   - 添加：0 20 * * * cd /path/to/content && python auto_publish_daily.py evening
"""

import sys
import os
import subprocess
from datetime import datetime

# 确保在正确的目录下运行
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # 写入日志文件
    with open("publish_log.txt", "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def run_morning_publish():
    """早班发布：热点速递（简短版）"""
    log("=" * 60)
    log("开始执行早班任务：今日热点速递")
    
    try:
        # 抓取今日头条热榜前5条，生成速递文章并上传到草稿箱
        cmd = [
            "python", "main.py",
            "--hot",
            "--source", "toutiao",
            "--publish"
        ]
        
        # 如果配置了封面ID，加上
        cover_id = os.environ.get("WECHAT_COVER_ID")
        if cover_id:
            cmd.extend(["--cover-id", cover_id])
        
        log(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        log("STDOUT:")
        log(result.stdout)
        
        if result.returncode == 0:
            log("✓ 早班任务执行成功！")
        else:
            log(f"✗ 早班任务执行失败，返回码：{result.returncode}")
            log("STDERR:")
            log(result.stderr)
            
    except Exception as e:
        log(f"✗ 早班任务异常：{e}")
    
    log("=" * 60)

def run_evening_publish():
    """晚班发布：深度解读（完整版）"""
    log("=" * 60)
    log("开始执行晚班任务：热点深度解读")
    
    try:
        # 抓取当日最热话题，生成深度解读并上传到草稿箱
        cmd = [
            "python", "main.py",
            "--hot",
            "--source", "toutiao",
            "--publish"
        ]
        
        # 如果配置了封面ID，加上
        cover_id = os.environ.get("WECHAT_COVER_ID")
        if cover_id:
            cmd.extend(["--cover-id", cover_id])
        
        log(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        log("STDOUT:")
        log(result.stdout)
        
        if result.returncode == 0:
            log("✓ 晚班任务执行成功！")
        else:
            log(f"✗ 晚班任务执行失败，返回码：{result.returncode}")
            log("STDERR:")
            log(result.stderr)
            
    except Exception as e:
        log(f"✗ 晚班任务异常：{e}")
    
    log("=" * 60)

def main():
    if len(sys.argv) < 2:
        print("用法: python auto_publish_daily.py [morning|evening]")
        print("  morning: 早班发布（热点速递）")
        print("  evening: 晚班发布（深度解读）")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "morning":
        run_morning_publish()
    elif mode == "evening":
        run_evening_publish()
    else:
        print(f"未知模式: {mode}")
        print("请使用 morning 或 evening")

if __name__ == "__main__":
    main()
