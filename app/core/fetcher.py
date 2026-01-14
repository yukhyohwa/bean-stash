import requests
from bs4 import BeautifulSoup
import re
import json

class DoubanFetcher:
    """负责从豆瓣抓取资讯的类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douban.com/'
        }

    def search(self, query, category="movie"):
        """搜索条目并返回候选列表"""
        # 注意：真实生产环境建议使用已有的 API 封装，这里展示基础爬取逻辑
        search_url = f"https://www.douban.com/search?cat=1002&q={query}" # 1002 为电影
        if category == "book":
            search_url = f"https://www.douban.com/search?cat=1001&q={query}"
        elif category == "music":
            search_url = f"https://www.douban.com/search?cat=1003&q={query}"
            
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 解析搜索结果 (简化版)
            items = soup.select('.result')[:5]
            for item in items:
                title_tag = item.select_one('.title a')
                if title_tag:
                    results.append({
                        'title': title_tag.get_text(strip=True),
                        'url': title_tag['href'],
                        'sid': re.search(r'sid/(\d+)', title_tag['href']).group(1) if 'sid/' in title_tag['href'] else ""
                    })
            return results
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def fetch_detail(self, url):
        """抓取详情页详细信息"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            data = {}
            # 通用标题
            data['title'] = soup.select_one('h1 span[property="v:itemreviewed"]').get_text(strip=True) if soup.select_one('h1 span[property="v:itemreviewed"]') else ""
            
            # 封面图
            cover_tag = soup.select_one('#mainpic img')
            data['cover_url'] = cover_tag['src'] if cover_tag else ""

            # 评分
            rating_tag = soup.select_one('.ll.rating_num')
            data['rating_douban'] = float(rating_tag.get_text()) if rating_tag and rating_tag.get_text() else None

            info_text = soup.select_one('#info').get_text() if soup.select_one('#info') else ""
            
            # 根据 URL 判断类型
            if "movie.douban.com" in url:
                data['media_type'] = "movie"
                data['director'] = soup.select_one('span:contains("导演") .attrs').get_text(strip=True) if soup.select_one('span:contains("导演") .attrs') else ""
                
                # 主演 (取前3个)
                casts = [a.get_text() for a in soup.select('span.actor .attrs a')[:5]]
                data['cast'] = " / ".join(casts)
                
                # 年份
                year_tag = soup.select_one('.year')
                if year_tag:
                    year_match = re.search(r'(\d{4})', year_tag.get_text())
                    data['year'] = year_match.group(1) if year_match else None
                
                # 剧情简介
                summary_tag = soup.select_one('span[property="v:summary"]')
                data['summary'] = summary_tag.get_text(strip=True) if summary_tag else ""

                # IMDb 链接提取
                imdb_match = re.search(r'IMDb:.*?(\w+)', info_text)
                data['imdb_id'] = imdb_match.group(1) if imdb_match else None

                # 制片国家
                country_match = re.search(r'制片国家/地区: (.*)', info_text)
                data['country'] = country_match.group(1).split('\n')[0].strip() if country_match else ""
                
                # 类型
                genres = [span.get_text() for span in soup.select('span[property="v:genre"]')]
                data['genres'] = " / ".join(genres)
            
            elif "book.douban.com" in url:
                data['media_type'] = "book"
                author_tag = soup.select_one('span:contains("作者")')
                data['author'] = author_tag.find_next_sibling('a').get_text(strip=True) if author_tag and author_tag.find_next_sibling('a') else ""
                
                # ISBN
                isbn_match = re.search(r'ISBN: (\d+)', info_text)
                data['isbn'] = isbn_match.group(1) if isbn_match else ""
                
                # 出版社
                pub_match = re.search(r'出版社: (.*)', info_text)
                data['publisher'] = pub_match.group(1).strip() if pub_match else ""

                # 简介
                summary_node = soup.select_one('.intro p')
                data['summary'] = summary_node.get_text(strip=True) if summary_node else ""
                
            return data
        except Exception as e:
            print(f"抓取详情失败: {e}")
            return None

    def search_imdb(self, query):
        """IMDb 搜索占位 (建议使用专门的库如 imdbpy 或公开 API)"""
        # 这里仅为逻辑展示，实际可通过类似 https://www.imdb.com/find?q=... 爬取
        return []

    def search_goodreads(self, query):
        """Goodreads 搜索占位"""
        return []

if __name__ == "__main__":
    fetcher = DoubanFetcher()
    print("测试获取详情...")
    # 测试肖申克的救赎
    detail = fetcher.fetch_detail("https://movie.douban.com/subject/1292052/")
    print(json.dumps(detail, indent=2, ensure_ascii=False))
