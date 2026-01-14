# BeanStash | 豆蔵 🍃

![GitHub License](https://img.shields.io/github/license/yukhyohwa/bean-stash?style=flat-square&color=A8D8B9)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&color=4A596D)

这是一个基于 Python + SQLite 的个人书影音收藏管理工具。它不仅模仿了豆瓣的收藏体验，更通过**日系极简主义（Japanese Minimalist）**的视觉设计和本地化存储，为你打造一个私密、优雅、安全的精神角落。

## 🌟 核心特性

1.  **和风美学界面**：基于 Streamlit 定制的日系简约 UI，支持 Noto Serif SC 优雅字体与和色调色盘。
2.  **多维度收藏**：支持电影、书籍、音乐三大类别，界面针对各类媒体进行了排版优化。
3.  **自动资讯获取**：支持通过豆瓣搜索自动补全导演、作者、简介、评分等元数据。
4.  **数据无缝迁移**：预置 Goodreads CSV 导入支持，轻松同步海外阅读记录。
5.  **离线封面缓存**：自动本地化存储封面图，无惧链接失效。
6.  **可视化足迹**：内置数据分析页面，通过统计图表回顾你的收藏趋势与喜好。

## 🛠️ 技术栈

- **前端**: Streamlit (Custom CSS with Japanese Aesthetics)
- **后端**: Python 3.10+
- **数据库**: SQLAlchemy + SQLite
- **爬虫**: BeautifulSoup4 + Requests

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行网页版本
```bash
python -m streamlit run app/web/ui.py
```

### 3. 数据导入 (Goodreads)
将你的 Goodreads 导出文件命名为 `goodreads_library_export.csv` 放入根目录，执行：
```bash
python import_goodreads.py
```

## 📅 最近更新
- [x] **UI 2.0**: 全面升级为日系简约风格。
- [x] **侧边栏增强**: 集成实时数据统计。
- [x] **无封面优化**: 文字占位封面自动生成。
- [x] **CSV 导入**: 支持 Goodreads 全量数据同步。

---
*Created with ❤️ by Antigravity*
