import streamlit as st
from app.core.models import init_db, get_session, CollectionItem, MediaType, CollectionStatus
from app.core.fetcher import DoubanFetcher
from app.utils.downloader import download_cover
import pandas as pd
from datetime import datetime
import os

# --- 页面配置 ---
st.set_page_config(
    page_title="BeanStash | 个人收藏馆",
    page_icon="🍃",
    layout="wide"
)

# --- 标准化样式 (统一封面比例) ---
st.markdown("""
<style>
    /* 强制图片保持书籍比例，防止过窄 */
    div[data-testid="stImage"] img {
        height: 320px !important;
        width: 100% !important;
        object-fit: cover !important;
        border-radius: 4px 12px 12px 4px; /* 模拟书脊效果 */
        border-left: 3px solid rgba(0,0,0,0.1);
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    div[data-testid="stImage"] img:hover {
        transform: translateY(-5px);
    }
    /* 统一文字容器高度，防止书名过长导致错位 */
    .stMarkdown p {
        margin-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 数据库初始化 ---
engine = init_db()
session = get_session(engine)

# --- 侧边栏：导航与统计 ---
with st.sidebar:
    st.title("🍃 BeanStash")
    
    total_count = session.query(CollectionItem).count()
    st.write(f"📊 当前总藏品：**{total_count}**")
    
    menu = st.radio(
        "导航", 
        ["🏛️ 我的私藏", "✨ 发现与录入", "📈 数据分析"], 
        index=0
    )
    
    st.divider()
    
    # 始终在侧边栏底部显示一个“管理”占位符
    if 'editing_item_id' in st.session_state:
        st.subheader("⚙️ 藏品管理")
        item_id = st.session_state['editing_item_id']
        item_to_edit = session.query(CollectionItem).filter(CollectionItem.id == item_id).first()
        
        if item_to_edit:
            st.info(f"正在编辑：《{item_to_edit.title}》")

            # 状态编辑
            status_map = ["想看/想听/想读", "在看/在听/在读", "看过/听过/读过"]
            try:
                current_idx = status_map.index(item_to_edit.my_status.value)
            except:
                current_idx = 0
                
            new_status = st.selectbox("收藏状态", status_map, index=current_idx)
            
            # --- 辅助 ID 编辑 (低频) ---
            st.write("") # 增加一点空隙
            with st.expander("🆔 标识编码 (用于匹配封面)", expanded=False):
                if item_to_edit.media_type == MediaType.BOOK:
                    temp_isbn = st.text_input("ISBN (书号)", value=item_to_edit.isbn or "")
                else:
                    temp_isbn = item_to_edit.isbn
                    
                if item_to_edit.media_type == MediaType.MOVIE:
                    temp_imdb = st.text_input("IMDb ID", value=item_to_edit.imdb_id or "")
                else:
                    temp_imdb = item_to_edit.imdb_id
                
                temp_douban = st.text_input("豆瓣 ID", value=item_to_edit.douban_id or "")
                st.caption("注：修改后需点击上方“保存修改”以生效")

            # 评分
            new_rating = st.slider("我的评分", 0.0, 5.0, float(item_to_edit.my_rating or 0.0), 0.5)
            
            # 标签
            new_tags = st.text_input("标签 (逗号分隔)", value=item_to_edit.my_tags or "")
            
            # --- 评论功能 (核心) ---
            new_comment = st.text_area("短评 & 个人笔记", value=item_to_edit.my_comment or "", height=200)
            
            col_save, col_del = st.columns(2)
            with col_save:
                if st.button("💾 保存修改", use_container_width=True, type="primary"):
                    map_rev = {
                        "想看/想听/想读": CollectionStatus.WISH,
                        "在看/在听/在读": CollectionStatus.DOING,
                        "看过/听过/读过": CollectionStatus.DONE
                    }
                    # 统一在此处提交修改
                    item_to_edit.isbn = temp_isbn
                    item_to_edit.imdb_id = temp_imdb
                    item_to_edit.douban_id = temp_douban
                    
                    item_to_edit.my_status = map_rev[new_status]
                    item_to_edit.my_rating = new_rating
                    item_to_edit.my_tags = new_tags
                    item_to_edit.my_comment = new_comment
                    item_to_edit.updated_at = datetime.now()
                    
                    # 重新匹配封面逻辑
                    if not item_to_edit.local_cover_path or not os.path.exists(item_to_edit.local_cover_path):
                        identifier = item_to_edit.isbn or item_to_edit.imdb_id or item_to_edit.douban_id
                        if identifier:
                            potential_path = f"data/covers/{identifier}.jpg"
                            if os.path.exists(potential_path):
                                item_to_edit.local_cover_path = potential_path

                    session.commit()
                    st.success("已保存！")
                    st.rerun()
            
            with col_del:
                if st.button("🗑️ 删除", use_container_width=True):
                    session.delete(item_to_edit)
                    session.commit()
                    del st.session_state['editing_item_id']
                    st.rerun()
            
            if st.button("关闭管理", use_container_width=True):
                del st.session_state['editing_item_id']
                st.rerun()


        else:
            del st.session_state['editing_item_id']

# --- 主页面内容 ---
if menu == "🏛️ 我的私藏":
    st.header("我的书影音库")
    
    # 筛选与视图切换
    col_f1, col_f2, col_v = st.columns([1, 1, 1])
    with col_f1:
        type_filter = st.selectbox("类型", ["全部", "电影", "书籍", "音乐"])
    with col_f2:
        status_filter = st.selectbox("状态", ["全部", "想看/想听/想读", "在看/在听/在读", "看过/听过/读过"])
    with col_v:
        view_mode = st.radio("视图模式", ["🗂️ 封面网格", "📑 数据库表格"], horizontal=True)
    
    # 查询
    query = session.query(CollectionItem)
    if type_filter != "全部":
        type_map = {"电影": MediaType.MOVIE, "书籍": MediaType.BOOK, "音乐": MediaType.MUSIC}
        query = query.filter(CollectionItem.media_type == type_map[type_filter])
    if status_filter != "全部":
        status_map_rev = {"想看/想听/想读": CollectionStatus.WISH, "在看/在听/在读": CollectionStatus.DOING, "看过/听过/读过": CollectionStatus.DONE}
        query = query.filter(CollectionItem.my_status == status_map_rev[status_filter])
    
    items = query.order_by(CollectionItem.created_at.desc()).all()
    
    if not items:
        st.info("库中还没有藏品，请先去录入吧！")
    elif view_mode == "📑 数据库表格":
        # 数据表视图
        data = []
        for item in items:
            data.append({
                "ID": item.id,
                "标题": item.title,
                "类型": item.media_type.value,
                "书号/IMDb": item.isbn or item.imdb_id or "-",
                "豆瓣ID": item.douban_id or "-",
                "我的评分": item.my_rating,
                "状态": item.my_status.value,
                "笔记/评价": item.my_comment or "",
                "更新时间": item.updated_at.strftime("%Y-%m-%d")
            })
        
        df = pd.DataFrame(data)
        
        # 分页逻辑
        items_per_page = 100
        total_items = len(df)
        total_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
        
        col_p1, col_p2 = st.columns([1, 4])
        with col_p1:
            page_num = st.number_input("页码", min_value=1, max_value=total_pages, step=1)
        with col_p2:
            st.write(f"📊 共 **{total_items}** 条记录 | 第 {page_num}/{total_pages} 页")
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        # 展示表格，增加高度
        st.dataframe(
            df.iloc[start_idx:end_idx], 
            use_container_width=True, 
            hide_index=True,
            height=600 # 显式设置高度，让表格变大
        )
        st.caption("💡 提示：点击列头可以排序。如需修改，请切换回“封面网格”并点击“管理”。")

    else:
        # 网格视图
        cols = st.columns(4)
        DEFAULT_COVER = "config/default_cover.png"
        
        for i, item in enumerate(items):
            with cols[i % 4]:
                # 封面展示逻辑
                cover_path = None
                
                # 1. 优先使用数据库记录的本地路径
                if item.local_cover_path and os.path.exists(item.local_cover_path):
                    cover_path = item.local_cover_path
                
                # 2. 如果数据库路径失效，尝试根据 ID 自动猜测是否存在本地文件
                if not cover_path:
                    identifier = item.isbn or item.imdb_id or item.douban_id
                    if identifier:
                        potential_path = f"data/covers/{identifier}.jpg"
                        if os.path.exists(potential_path):
                            cover_path = potential_path
                
                # 3. 尝试使用远程 URL
                if not cover_path and item.cover_url and item.cover_url.startswith("http") and item.cover_url != "https://via.placeholder.com/300x450":
                    cover_path = item.cover_url
                
                # 4. 最后回退到默认封面
                if not cover_path:
                    cover_path = DEFAULT_COVER if os.path.exists(DEFAULT_COVER) else "https://via.placeholder.com/300x450?text=BeanStash"

                st.image(cover_path, use_container_width=True)
                
                # 文字信息
                st.markdown(f"**{item.title}**")
                
                # 显示书号/ID
                identifier_display = item.isbn or item.imdb_id or item.douban_id or "未知 ID"
                st.caption(f"🆔 {identifier_display}")
                
                # 显示年份和类型
                st.caption(f"{item.year or ''} | {item.media_type.value}")
                
                # 管理按钮
                if st.button("管理", key=f"btn_{item.id}", use_container_width=True):

                    st.session_state['editing_item_id'] = item.id
                    st.rerun()

elif menu == "✨ 发现与录入":
    st.header("添加新藏品")
    category = st.selectbox("选择分类", ["movie", "book", "music"])
    keyword = st.text_input("输入关键词搜索...")
    
    if keyword:
        with st.spinner("正在搜索..."):
            fetcher = DoubanFetcher()
            results = fetcher.search(keyword, category=category)
        
        if not results:
            st.warning("未找到结果")
        else:
            for idx, res in enumerate(results):
                col_res1, col_res2 = st.columns([4, 1])
                with col_res1:
                    st.write(f"**{res['title']}**")
                    st.caption(res['url'])
                with col_res2:
                    if st.button("入库", key=f"add_{idx}"):
                        detail = fetcher.fetch_detail(res['url'])
                        if detail:
                            # 确定唯一标识符用于封面命名
                            cover_id = detail.get('isbn') or detail.get('imdb_id') or res.get('sid')
                            
                            local_path = download_cover(detail['cover_url'], identifier=cover_id)
                            new_item = CollectionItem(
                                title=detail['title'],
                                media_type=MediaType(detail['media_type']),
                                cover_url=detail['cover_url'],
                                local_cover_path=local_path,
                                douban_id=res.get('sid'),
                                douban_url=res['url'],
                                isbn=detail.get('isbn'),
                                imdb_id=detail.get('imdb_id'),
                                my_status=CollectionStatus.WISH,
                                year=int(detail['year']) if str(detail.get('year', '')).isdigit() else None,
                                author=detail.get('author'),
                                director=detail.get('director')
                            )
                            session.add(new_item)
                            session.commit()
                            st.success(f"《{detail['title']}》已加入我的私藏")


elif menu == "📈 数据分析":
    st.header("统计分析")
    df = pd.read_sql(session.query(CollectionItem).statement, engine)
    
    if df.empty:
        st.info("暂无数据，请先录入一些藏品吧！")
    else:
        # 顶部总览卡片
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("总藏品", len(df))
        with col_m2:
            st.metric("平均评分", round(df['my_rating'].mean(), 1) if not df['my_rating'].isnull().all() else "-")
        with col_m3:
            st.metric("已完成", len(df[df['my_status'] == CollectionStatus.DONE]))

        st.divider()

        # 第一排：分类与状态
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📁 类型分布")
            type_counts = df['media_type'].apply(lambda x: x.value).value_counts()
            st.bar_chart(type_counts)
        
        with col_c2:
            st.subheader("🎏 状态分布")
            status_counts = df['my_status'].apply(lambda x: x.value).value_counts()
            st.bar_chart(status_counts)

        st.divider()

        # 第二排：年份分布
        st.subheader("📅 年份分布")
        # 过滤掉空的年份
        year_df = df[df['year'].notnull()].copy()
        if not year_df.empty:
            year_counts = year_df['year'].value_counts().sort_index()
            st.bar_chart(year_counts)
        else:
            st.caption("暂无年份信息")

        # 最近录入
        st.divider()
        st.subheader("🕒 最近录入")
        recent_df = df.sort_values(by="created_at", ascending=False).head(5)
        st.table(recent_df[['title', 'media_type', 'my_status']].assign(
            media_type=recent_df['media_type'].apply(lambda x: x.value),
            my_status=recent_df['my_status'].apply(lambda x: x.value)
        ))

