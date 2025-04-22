from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class Section(Base, BaseModel):
    """Модель отдела, который входит в подразделение"""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    division_id = Column(Integer, ForeignKey("division.id"), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    division = relationship("Division", back_populates="sections")
    positions = relationship("Position", back_populates="section")
    functions = relationship("Function", back_populates="section")
    
    __tablename__ = "section"
    
    __table_args__ = (
        # Уникальный код в пределах подразделения
        UniqueConstraint('code', 'division_id', name='uix_section_code_division'),
    ) 