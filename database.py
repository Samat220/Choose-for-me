import json

from sqlalchemy import TIMESTAMP, Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./media_picker.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MediaItem(Base):
    __tablename__ = "media_items"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # 'game' or 'movie'
    title = Column(String, nullable=False)
    platform = Column(String, nullable=True)
    cover_url = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string
    status = Column(String, default="active")  # 'active', 'done', 'archived'
    added_at = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "platform": self.platform,
            "coverUrl": self.cover_url,
            "tags": json.loads(self.tags) if self.tags else [],
            "status": self.status,
            "addedAt": self.added_at,
        }


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
