# BeanStash 🍃

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&color=4A596D)

A personal library manager for books, movies, and music powered by Python + SQLite. Inspired by Douban's collection experience, it offers a private, elegant, and secure space with a **Minimalist** visual design and local storage.

## 🌟 Key Features

1. **Elegant Interface**: Custom minimalist UI based on Streamlit, utilizing Noto Serif SC elegant fonts and refined color palettes.
2. **Smart Matching System**: Uses **ISBN** for books and **IMDb ID** for movies as unique identifiers, ensuring precision and easy cover matching.
3. **Automatic Metadata Retrieval**: Supports auto-completion of metadata like directors, authors, summaries, and ratings via Douban search.
4. **Local ID-Based Storage**: Covers are saved based on unique IDs (ISBN/IMDb), making it easy to manually sync higher-quality posters.
5. **Dual View Mode**:
   - **🗂️ Grid View**: Clean and beautiful poster wall for daily browsing.
   - **📑 Table View**: High-capacity database view with pagination (100 items/page) for bulk editing and note reviewing.
6. **Visualized Footprints**: Comprehensive analytics dashboard showing media types, reading status, and collection years.

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

### 2. Run Application

```bash
python main.py web
```

## 📂 Folder Structure & Cover Syncing

Save your custom covers to `data/covers/` using the following naming convention:

- **Books**: `[ISBN].jpg` (e.g., `9787111213826.jpg`)
- **Movies**: `[IMDb_ID].jpg` (e.g., `tt0111161.jpg`)
- **Douban**: `[Douban_ID].jpg` (e.g., `1292052.jpg`)

## 📅 Recent Updates

- [X] **Database Optimization**: Refactored edit logic to prevent SQLite locking.
- [X] **Enhanced Table View**: Added pagination (100 items) and expanded height (600px).
- [X] **ID-Based Cover Management**: Support for ISBN/IMDb/Douban ID matching.
- [X] **Analytics Dashboard**: Detailed charts for media status and years.

---

*Created with ❤️ by Antigravity*
