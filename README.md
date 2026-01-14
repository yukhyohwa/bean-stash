# BeanStash | 豆蔵 🍃

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&color=4A596D)

A personal library manager for books, movies, and music powered by Python + SQLite. Inspired by Douban's collection experience, it offers a private, elegant, and secure space with a **Minimalist** visual design and local storage.

## 🌟 Key Features

1.  **Elegant Interface**: Custom minimalist UI based on Streamlit, utilizing Noto Serif SC elegant fonts and refined color palettes.
2.  **Multi-dimensional Collection**: Supports Movies, Books, and Music, with optimized layouts for each media type.
3.  **Automatic Metadata Retrieval**: Supports auto-completion of metadata like directors, authors, summaries, and ratings via Douban search.
4.  **Offline Cover Caching**: Automatically saves cover images locally to prevent broken links.
5.  **Visualized Footprints**: Built-in data analysis page to review your collection trends and preferences through statistical charts.

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Custom CSS with Minimalist Style)
- **Backend**: Python 3.10+
- **Database**: SQLAlchemy + SQLite
- **Crawler**: BeautifulSoup4 + Requests

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Web Version
```bash
python -m streamlit run app/web/ui.py
```

### 3. Run CLI Version (Optional)
```bash
python main.py
```

## 📅 Recent Updates
- [x] **UI 2.0**: Fully upgraded to minimalist style.
- [x] **Sidebar Enhancement**: Integrated real-time data statistics.
- [x] **No Cover Optimization**: Auto-generated text placeholder covers.

---
*Created with ❤️ by Antigravity*
