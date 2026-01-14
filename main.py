from app.core.models import init_db, get_session, CollectionItem, MediaType, CollectionStatus
from app.core.fetcher import DoubanFetcher
import os

def main():
    print("=== 欢迎使用 Douban-Collect (个人书影音收藏库) ===")
    
    # 1. 初始化数据库
    if not os.path.exists("data"):
        os.makedirs("data")
    engine = init_db()
    session = get_session(engine)
    
    while True:
        print("\n[1] 录入新收藏  [2] 查看我的库  [3] 退出")
        choice = input("请选择操作: ")
        
        if choice == "1":
            keyword = input("请输入要搜索的名称: ")
            print("正在搜索...")
            fetcher = DoubanFetcher()
            results = fetcher.search(keyword)
            
            if not results:
                print("未找到结果。")
                continue
                
            for i, res in enumerate(results):
                print(f"[{i}] {res['title']} ({res['url']})")
                
            idx = input("请选择序号 (或输入 q 取消): ")
            if idx == 'q': continue
            
            selected = results[int(idx)]
            print(f"正在获取 '{selected['title']}' 的详细信息...")
            # 这里简化一下，直接存入
            # 真实逻辑应该调用 fetch_detail 获取更多信息
            
            new_item = CollectionItem(
                title=selected['title'],
                douban_url=selected['url'],
                media_type=MediaType.MOVIE, # 暂时默认电影
                my_status=CollectionStatus.WISH
            )
            session.add(new_item)
            session.commit()
            print("✅ 录入成功！")
            
        elif choice == "2":
            items = session.query(CollectionItem).all()
            if not items:
                print("库中空空如也。")
            else:
                for item in items:
                    print(f"[{item.media_type.value}] {item.title} - 状态: {item.my_status.value}")
        
        elif choice == "3":
            break

if __name__ == "__main__":
    main()
