from sqlalchemy import Integer, String, DateTime, Text, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from models.db import db

class Artefact(db.Model):
    __tablename__ = 'artefacts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_text: Mapped[str] = mapped_column(Text)
    used: Mapped[int] = mapped_column(SmallInteger, default=0)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Artefact {self.title}>'

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'source_id': self.source_id,
            'full_text': self.full_text,
            'used': self.used,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }