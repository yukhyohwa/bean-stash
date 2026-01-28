import requests
import os
import hashlib
from urllib.parse import urlparse

def download_cover(url, save_dir="data/covers", identifier=None):
    """
    下载封面图并返回本地相对路径。
    优先使用 identifier (如 ISBN/IMDb ID) 作为文件名，
    如果没有 identifier，则使用 URL 的哈希值。
    """
    if not url or not url.startswith("http"):
        return None
        
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    try:
        # 确定文件名
        ext = os.path.splitext(urlparse(url).path)[-1]
        if not ext or len(ext) > 5: ext = ".jpg" # 处理异常后缀
        
        if identifier:
            filename = f"{identifier}{ext}"
        else:
            filename = hashlib.md5(url.encode()).hexdigest() + ext
            
        local_path = os.path.join(save_dir, filename)
        
        # 如果文件已存在则直接返回
        if os.path.exists(local_path):
            return local_path
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douban.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return local_path
        return None
    except Exception as e:
        print(f"下载封面失败: {e}")
        return None

