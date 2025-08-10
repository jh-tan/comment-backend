from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base


class CommentHistory(Base):
    __tablename__ = "comment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    old_value = Column(String)
    new_value = Column(String, nullable=False)
    
    comment = relationship("Comment", back_populates="history_entries")