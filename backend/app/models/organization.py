from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class Organization(Base, BaseModel):
    """Модель организации"""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    org_type = Column(String(50), nullable=False)  # 'HOLDING', 'LEGAL_ENTITY', etc.
    parent_id = Column(Integer, ForeignKey("organization.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    parent = relationship("Organization", remote_side=[id], backref="children")
    divisions = relationship("Division", back_populates="organization")
    
    __tablename__ = "organization"  # Явно указываем имя таблицы 