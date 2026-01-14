from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class CollectionStatus(enum.Enum):
    WISH = "想看/想听/想读"
    DOING = "在看/在听/在读"
    DONE = "看过/听过/读过"

class MediaType(enum.Enum):
    MOVIE = "movie"
    BOOK = "book"
    MUSIC = "music"

class CollectionItem(Base):
    __tablename__ = 'collection_items'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    original_title = Column(String(255))
    media_type = Column(Enum(MediaType), nullable=False)
    
    # 外部链接
    douban_id = Column(String(50), unique=True)
    douban_url = Column(String(512))
    imdb_id = Column(String(50))
    goodreads_id = Column(String(50))
    
    # 图片
    cover_url = Column(String(512))
    local_cover_path = Column(String(512))
    
    # 用户评价
    my_rating = Column(Float)  # 1-5 星
    my_status = Column(Enum(CollectionStatus), default=CollectionStatus.WISH)
    my_comment = Column(Text)
    my_tags = Column(String(255))  # 以逗号分隔
    
    # 统计
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime)
    
    # 详细信息 (通用)
    year = Column(Integer)
    summary = Column(Text)
    rating_douban = Column(Float)
    rating_imdb = Column(Float)

    # 电影特有
    director = Column(String(255))
    cast = Column(Text)
    country = Column(String(100))
    duration = Column(String(50))
    genres = Column(String(255)) # 新增流派

    # 书籍特有
    author = Column(String(255))
    publisher = Column(String(255))
    pub_year = Column(String(50))
    isbn = Column(String(50))
    pages = Column(Integer)
    translator = Column(String(255)) # 新增翻译

    # 音乐特有
    performer = Column(String(255))
    genre = Column(String(100))
    media_format = Column(String(50))

def init_db(db_path="sqlite:///data/collection.db"):
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
