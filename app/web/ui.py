import streamlit as st
from app.core.models import init_db, get_session, CollectionItem, MediaType, CollectionStatus
from app.core.fetcher import DoubanFetcher
from app.utils.downloader import download_cover
import pandas as pd
from datetime import datetime
import os

# --- 页面配置 ---
st.set_page_config(
    page_title="BeanStash | 个人私藏馆",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 数据库初始化 ---
engine = init_db()
session = get_session(engine)

# --- PREMIUM UI 样式定制 (日系简约风格) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Zen+Maru+Gothic:wght@400;500&display=swap');

* { font-family: 'Zen Maru Gothic', sans-serif; }
h1, h2, h3 { font-family: 'Noto Serif SC', serif; font-weight: 700; color: #2c3e50; }

/* 日系和色背景：胡桃色/白练 */
.stApp { 
    background-color: #fcfaf2;
    background-image: radial-gradient(#e0e0e0 0.5px, transparent 0.5px);
    background-size: 20px 20px;
}

#MainMenu, footer, header { visibility: hidden; }

/* 侧边栏：和纸质感增强 */
section[data-testid="stSidebar"] { 
    background-color: #f8f4ed !important; /* 象牙/白练色 */
    background-image: 
        linear-gradient(90deg, rgba(200,0,0,.02) 50%, transparent 50%),
        linear-gradient(rgba(200,0,0,.02) 50%, transparent 50%);
    background-size: 4px 4px; /* 模拟极细的和纸纹理 */
    border-right: 2px solid #e0dcd3;
}

/* 侧边栏标题 */
div[data-testid="stSidebar"] h2 {
    color: #5d513c !important; /* 锖青磁/深橄榄色 */
    border-bottom: 2px solid #5d513c;
    padding-bottom: 10px;
    letter-spacing: 2px;
}

/* 菜单按钮自定义 - 更加精美的和风标签 */
div[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] {
    font-weight: 600;
    color: #7a6e5d;
    margin-top: 20px;
    letter-spacing: 1px;
}

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
    padding: 12px 15px !important;
    border-radius: 0px !important; /* 日系正式风格多用直角 */
    background-color: #fff !important;
    border: 1px solid #dcd6c8 !important;
    border-left: 5px solid #dcd6c8 !important; /* 模拟竹简/册页边 */
    margin-bottom: 10px !important;
    transition: all 0.3s ease !important;
    color: #5d513c !important;
}

div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
    border-left-color: #e67e22 !important; /* 柿色激活 */
    background-color: #fdfaf5 !important;
    transform: translateX(3px);
}

/* 选中的按钮状态 (Streamlit 特有 CSS 选择器) */
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] input:checked + div {
    border-left: 5px solid #e67e22 !important;
}

/* 侧边栏统计卡片：和风小报风格 */
.stats-card {
    background-color: #ffffff !important;
    border: 1px double #dcd6c8;
    padding: 20px;
    margin-top: 20px;
    position: relative;
}
.stats-card::before {
    content: "";
    position: absolute;
    top: 5px; right: 5px; bottom: 5px; left: 5px;
    border: 1px solid #f8f4ed; /* 内边框 */
    pointer-events: none;
}

/* 电影卡片：和风简约 */
.movie-card {
    background: #ffffff !important;
    border-radius: 4px;
    padding: 0px;
    margin-bottom: 25px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    overflow: hidden;
}

.movie-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    border-color: #bdc3c7;
}

.cover-img { 
    width: 100%; 
    height: 240px; 
    object-fit: cover; 
    filter: sepia(10%) contrast(95%); /* 微微的怀旧感 */
}

.info-container { 
    padding: 15px; 
    background: #fff;
}

.title-text {
    font-size: 1.05rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 6px;
    line-height: 1.4;
}

.meta-text { 
    font-size: 0.85rem; 
    color: #95a5a6; 
    letter-spacing: 0.05em;
}

.rating-pill {
    position: absolute;
    top: 12px;
    right: 12px;
    background: #e67e22; /* 柿色 */
    color: white;
    padding: 2px 10px;
    border-radius: 2px;
    font-size: 12px;
    font-weight: bold;
}

.status-badge {
    display: inline-block;
    margin-top: 10px;
    padding: 2px 10px;
    border-radius: 2px;
    font-size: 0.75rem;
    border: 1px solid #ddd;
}

.status-wish { background-color: #fff; color: #7f8c8d; border-color: #bdc3c7; }
.status-done { background-color: #f7f1e3; color: #d35400; border-color: #f39c12; }

/* 搜索框风格 */
.stTextInput input {
    border-radius: 2px !important;
    border: 1px solid #ddd !important;
    background-color: #fff !important;
}
</style>
""", unsafe_allow_html=True)

# --- Helper functions ---
def get_display_image(item):
    if item.local_cover_path and os.path.exists(item.local_cover_path):
        return item.local_cover_path
    return item.cover_url if item.cover_url else "https://via.placeholder.com/300x450"

# --- 侧边栏导航 ---
with st.sidebar:
    st.markdown("<h2 style='color: #2e7d32; margin-bottom: 25px;'>🍃 BeanStash</h2>", unsafe_allow_html=True)
    
    # 算一下统计数据
    total_count = session.query(CollectionItem).count()
    movie_count = session.query(CollectionItem).filter(CollectionItem.media_type == MediaType.MOVIE).count()
    book_count = session.query(CollectionItem).filter(CollectionItem.media_type == MediaType.BOOK).count()
    music_count = session.query(CollectionItem).filter(CollectionItem.media_type == MediaType.MUSIC).count()

    # 初始化变量以防作用域错误
    type_filter = "全部"
    status_filter = "全部"

    menu = st.radio(
        "导航菜单", 
        ["🏛️ 我的私藏", "✨ 发现与录入", "📈 数据分析"], 
        index=0
    )
    
    st.markdown("---")
    
    # 侧边栏统计：日系小报风格卡片
    st.markdown("### 📊 本地藏品统计")
    st.markdown(f"""
    <div class="stats-card">
        <div style="font-size: 0.85rem; color: #7a6e5d; margin-bottom: 5px;">蔵書総数</div>
        <div style="font-size: 2rem; font-weight: bold; color: #d35400; margin-bottom: 15px;">{total_count}</div>
        <div style="display: flex; gap: 15px; font-size: 0.9rem; color: #5d513c; border-top: 1px dashed #dcd6c8; padding-top: 10px;">
            <span>🎬 {movie_count}</span>
            <span>📚 {book_count}</span>
            <span>🎵 {music_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("🍃 BeanStash v1.1 | 个人私藏馆")
    st.caption("© 2024 Design by Antigravity")

# --- 路由逻辑 ---
if menu == "🏛️ 我的私藏":
    st.markdown("<h1 style='font-weight: 600;'>我的书影音库</h1>", unsafe_allow_html=True)
    
    # 筛选器移动至主页面
    col_f1, col_f2, col_f3 = st.columns([2, 3, 4])
    with col_f1:
        type_filter = st.selectbox("媒体类型", ["全部", "电影", "书籍", "音乐"], label_visibility="visible")
    with col_f2:
        status_filter = st.selectbox("收藏状态", ["全部", "想看/想听/想读", "在看/在听/在读", "看过/听过/读过"], label_visibility="visible")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 构造查询
    query = session.query(CollectionItem)
    
    # 应用类型筛选
    if type_filter != "全部":
        map_type = {"电影": MediaType.MOVIE, "书籍": MediaType.BOOK, "音乐": MediaType.MUSIC}
        query = query.filter(CollectionItem.media_type == map_type[type_filter])
    
    # 应用状态筛选
    if status_filter != "全部":
        map_status = {
            "想看/想听/想读": CollectionStatus.WISH,
            "在看/在听/在读": CollectionStatus.DOING,
            "看过/听过/读过": CollectionStatus.DONE
        }
        query = query.filter(CollectionItem.my_status == map_status[status_filter])
    
    items = query.order_by(CollectionItem.created_at.desc()).all()
    
    if not items:
        st.info("目前库中还没有东西，点击左侧 '发现与录入' 开始吧！")
    else:
        cols = st.columns(5)
        for i, item in enumerate(items):
            with cols[i % 5]:
                status_class = "status-wish" if "想" in item.my_status.value else "status-done"
                # 特色图标显示：如果有 IMDb 则显示
                imdb_icon = f"🍿 IMDb: {item.imdb_id}" if item.imdb_id else ""
                
                # --- 封面渲染逻辑 ---
                has_cover = item.local_cover_path and os.path.exists(item.local_cover_path)
                if not has_cover and item.cover_url and item.cover_url != "https://via.placeholder.com/300x450":
                    has_cover = True
                    cover_display = item.cover_url
                elif has_cover:
                    cover_display = item.local_cover_path
                else:
                    cover_display = None

                # 构造封面 HTML
                if cover_display:
                    cover_html = f'<img src="{cover_display}" class="cover-img" style="height: 100%; transition: transform 0.3s ease;">'
                else:
                    # 日系风格的文字封面占位
                    cover_html = f'<div style="height: 100%; display: flex; align-items: center; justify-content: center; background-color: #f1f2f6; color: #7f8c8d; padding: 20px; text-align: center; border-bottom: 1px solid #eee;"><div style="font-family: \'Noto Serif SC\', serif; font-size: 1.1rem; line-height: 1.4;">{item.title}</div></div>'

                st.markdown(f"""
                <div class="movie-card">
                    {f'<div class="rating-pill">⭐ {item.rating_douban}</div>' if item.rating_douban else ''}
                    <div style="height: 240px; background: #eee; overflow: hidden;">{cover_html}</div>
                    <div class="info-container" style="background: white; min-height: 100px; border-top: 1px solid #f0f0f0;">
                        <div class="title-text" style="color: #333; font-weight: bold; margin-bottom: 4px;" title="{item.title}">{item.title}</div>
                        <div class="meta-text" style="font-size: 0.75rem;">{item.year if item.year else 'N/A'} · {item.media_type.value.upper()}</div>
                        <div style="font-size: 0.65rem; color: #999; margin-bottom: 8px; height: 15px;">{imdb_icon}</div>
                        <span class="status-badge {status_class}" style="font-size: 0.65rem;">{item.my_status.value}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif menu == "✨ 发现与录入":
    st.markdown("<h1 style='font-weight: 600;'>发现新灵感</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔍 豆瓣搜索", "📦 外部来源 (IMDb/Goodreads)"])
    
    with tab1:
        c1, c2 = st.columns([1, 4])
        with c1:
            category = st.selectbox("分类", ["movie", "book", "music"], label_visibility="collapsed")
        with c2:
            search_query = st.text_input("输入关键词搜索 (如: 肖申克的救赎)...", label_visibility="collapsed")
        
        if search_query:
            with st.spinner("正在探寻豆瓣的海量数据..."):
                fetcher = DoubanFetcher()
                results = fetcher.search(search_query, category=category)
            
            if not results:
                st.warning("未找到匹配内容")
            else:
                for idx, res in enumerate(results):
                    with st.container():
                        sc1, sc2, sc3 = st.columns([1, 6, 2])
                        with sc1:
                            st.image("https://img3.doubanio.com/f/movie/30c3501750d990425e40da1fff96738092a06511/pics/movie/movie_default_small.png", width=60)
                        with sc2:
                            st.markdown(f"**{res['title']}**")
                            st.caption(f"豆瓣链接: {res['url']}")
                        with sc3:
                            if st.button("加入私藏", key=f"add_{idx}"):
                                detail = fetcher.fetch_detail(res['url'])
                                if detail:
                                    # --- 封面本地化 ---
                                    local_path = download_cover(detail['cover_url'])
                                    
                                    new_item = CollectionItem(
                                        title=detail['title'],
                                        media_type=MediaType(detail['media_type']),
                                        cover_url=detail['cover_url'],
                                        local_cover_path=local_path,
                                        douban_url=res['url'],
                                        imdb_id=detail.get('imdb_id'),
                                        my_status=CollectionStatus.WISH,
                                        year=int(detail['year']) if str(detail.get('year', '')).isdigit() else None,
                                        rating_douban=detail.get('rating_douban'),
                                        director=detail.get('director'),
                                        cast=detail.get('cast'),
                                        genres=detail.get('genres'),
                                        summary=detail.get('summary'),
                                        isbn=detail.get('isbn'),
                                        publisher=detail.get('publisher'),
                                        author=detail.get('author')
                                    )
                                    session.add(new_item)
                                    session.commit()
                                    st.success(f"《{detail['title']}》 已成功入库并完成封面本地化！")
                                    st.balloons()
    with tab2:
        st.info("IMDb 与 Goodreads 直接搜索功能对接中... 目前推荐使用豆瓣搜索（已支持自动提取 IMDb ID）")

elif menu == "📈 数据分析":
    st.markdown("<h1 style='font-weight: 600;'>我的时光足迹</h1>", unsafe_allow_html=True)
    
    # 获取统计数据
    df = pd.read_sql(session.query(CollectionItem).statement, engine)
    
    if df.empty:
        st.info("暂无数据，快去录入一些收藏吧！")
    else:
        # 顶层指标
        m1, m2, m3 = st.columns(3)
        m1.metric("总收藏数", len(df))
        m2.metric("电影数量", len(df[df['media_type'] == MediaType.MOVIE]))
        m3.metric("书籍数量", len(df[df['media_type'] == MediaType.BOOK]))
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎬 媒体类型分布")
            # 转换成 DataFrame 以便绘图
            type_counts = df['media_type'].apply(lambda x: x.value if hasattr(x, 'value') else str(x)).value_counts()
            st.bar_chart(type_counts)
            
        with c2:
            st.subheader("📅 年度收藏趋势")
            df['year_created'] = pd.to_datetime(df['created_at']).dt.year
            year_trend = df['year_created'].value_counts().sort_index()
            st.line_chart(year_trend)
            
        st.subheader("🌟 评分解析")
        if not df['my_rating'].isnull().all():
            st.line_chart(df['my_rating'].dropna())
        else:
            st.caption("由于你还没给收藏评分，暂时无法生成评分分析图表。")
