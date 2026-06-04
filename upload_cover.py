# -*- coding: utf-8 -*-
"""
辅助脚本：上传图片到微信公众号并获取 Media ID
使用方法：python upload_cover.py <图片路径>
"""
import sys
import os
import requests

# 尝试加载 .env 中的配置
def load_env():
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k and v:
                        os.environ[k] = v.strip().strip("'").strip('"')

def main():
    if len(sys.argv) < 2:
        print("用法: python upload_cover.py <图片路径>")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        return

    load_env()
    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")

    if not app_id or not app_secret:
        print("错误: 请先在 .env 文件中配置 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        return

    # 1. 获取 Access Token
    print("[*] 正在获取 Access Token...")
    token_url = "https://api.weixin.qq.com/cgi-bin/token"
    resp = requests.get(token_url, params={
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret
    })
    token_data = resp.json()
    if "access_token" not in token_data:
        print(f"错误: 获取 Token 失败: {token_data}")
        return
    token = token_data["access_token"]

    # 2. 上传图片 (永久素材)
    print(f"[*] 正在上传图片: {file_path}")
    upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    
    try:
        with open(file_path, "rb") as f:
            files = {'media': f}
            resp = requests.post(upload_url, files=files)
            data = resp.json()
            
            if "media_id" in data:
                print("-" * 50)
                print(f"[+] 上传成功！")
                print(f"[+] Media ID: {data['media_id']}")
                print("-" * 50)
                print(f"提示：请将上面的 Media ID 填入 .env 文件的 WECHAT_COVER_ID 字段，或者在运行 main.py 时使用 --cover-id 参数。")
            else:
                print(f"[-] 上传失败: {data}")
    except Exception as e:
        print(f"[-] 发生错误: {e}")

if __name__ == "__main__":
    main()
