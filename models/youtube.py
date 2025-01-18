import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from models.db import db

class YoutubeVideo(db.Model):
    __tablename__ = 'youtube_videos'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    channel_title: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_id: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f'<Video {self.title}>' 

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'video_id': self.video_id,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'channel_title': self.channel_title,
            'channel_id': self.channel_id,
            'thumbnail_url': self.thumbnail_url,
            'url': self.url
        }

class YoutubeChannel(db.Model):
    __tablename__ = 'youtube_channels'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    thumbnail_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<YoutubeChannel {self.title}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'title': self.title,
            'description': self.description,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'thumbnail_url': self.thumbnail_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
