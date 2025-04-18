from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class FunctionalRelation(Base, BaseModel):
    """Модель для функциональных отношений между должностями"""
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    relation_type = Column(String(50), nullable=False)  # Тип отношения (руководство, наставничество, координация)
    weight = Column(Float, default=1.0, nullable=False)  # Вес связи для визуализации и расчетов
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    source = relationship("Position", foreign_keys=[source_id], back_populates="functional_relations_source")
    target = relationship("Position", foreign_keys=[target_id], back_populates="functional_relations_target")
    
    __tablename__ = "functional_relation" 