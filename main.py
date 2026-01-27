import os
import sys
import subprocess
from app.core.models import init_db, get_session, CollectionItem, MediaType, CollectionStatus
from app.core.fetcher import DoubanFetcher

def run_web():
    """启动 Streamlit 页面"""
    print("🚀 正在启动 Web 界面...")
    # 动态获取当前脚本所在目录的 app/web/ui.py 路径
    ui_path = os.path.join(os.path.dirname(__file__), "app", "web", "ui.py")
    # 使用 sys.executable 确保使用当前环境的 Python 运行 Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", ui_path])

def main():
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        run_web()
        return

    print("=== 欢迎使用 Douban-Collect (个人书影音收藏库) ===")
    
    # 1. 初始化数据库
    if not os.path.exists("data"):
        os.makedirs("data")
    engine = init_db()
    session = get_session(engine)
    
    # ... 其余 CLI 代码保持不变 ...
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
            try:
                if idx == 'q': continue
                selected = results[int(idx)]
                print(f"正在获取 '{selected['title']}' 的详细信息...")
                # 提示：完整信息获取逻辑建议在 Web 端操作，或在此补充 fetch_detail
                new_item = CollectionItem(
                    title=selected['title'],
                    douban_url=selected['url'],
                    media_type=MediaType.MOVIE, # 暂时默认电影
                    my_status=CollectionStatus.WISH
                )
                session.add(new_item)
                session.commit()
                print("✅ 录入成功！")
            except (ValueError, IndexError):
                print("❌ 输入无效。")
            
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
