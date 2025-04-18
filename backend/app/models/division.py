from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class Division(Base, BaseModel):
    """Модель подразделения организации (департамент)"""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("division.id"), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    organization = relationship("Organization", back_populates="divisions")
    parent = relationship("Division", remote_side=[id], backref="children")
    sections = relationship("Section", back_populates="division")
    positions = relationship("Position", back_populates="division")
    
    __tablename__ = "division"
    
    __table_args__ = (
        # Уникальный код в пределах организации
        UniqueConstraint('code', 'organization_id', name='uix_division_code_organization'),
    ) 