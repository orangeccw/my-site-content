import requests
import json
import os
import urllib3
from datetime import datetime, timedelta

# 环境配置
os.environ['no_proxy'] = '*'
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def cleanup_by_filename(repo_name, github_token, days_to_keep=30):
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0"
    }
    
    # 计算 30 天前的截止日期
    threshold_date = datetime.now() - timedelta(days=days_to_keep)
    print(f"📅 正在清理 {threshold_date.strftime('%Y-%m-%d')} 之前的文件...")

    # 1. 获取仓库文件列表
    url = f"https://api.github.com/repos/{repo_name}/contents/"
    try:
        res = requests.get(url, headers=headers, verify=False, timeout=20)
        if res.status_code != 200:
            print(f"❌ 无法读取目录: {res.text}")
            return
        
        items = res.json()
        for item in items:
            name = item['name']
            
            # 排除 index.html 和非 html 文件
            if name == "index.html" or not name.endswith(".html"):
                continue
            
            try:
                # 假设格式是 2026-02-03-xxxx.html 或 2026-02-03.html
                # 提取前 10 位日期字符
                date_str = name[:10] 
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < threshold_date:
                    # 2. 执行删除
                    print(f"🗑️ 检测到过期文件: {name}，准备删除...")
                    del_url = f"https://api.github.com/repos/{repo_name}/contents/{name}"
                    del_data = {
                        "message": f"Auto-cleanup: delete old file {name}",
                        "sha": item['sha']  # 必须提供 sha 才能删除
                    }
                    del_res = requests.delete(del_url, headers=headers, data=json.dumps(del_data), verify=False)
                    
                    if del_res.status_code in [200, 204]:
                        print(f"✅ 已成功删除 {name}")
                    else:
                        print(f"❌ 删除 {name} 失败: {del_res.text}")
            
            except ValueError:
                # 如果文件名不是日期开头，跳过
                print(f"⏩ 跳过非日期命名文件: {name}")
                continue

    except Exception as e:
        print(f"❌ 运行报错: {e}")

# --- 配置 ---
MY_TOKEN = os.getenv("MY_GITHUB_TOKEN") 
MY_REPO = os.getenv("GITHUB_REPOSITORY")

cleanup_by_filename(MY_REPO, MY_TOKEN)
