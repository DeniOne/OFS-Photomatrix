from sqlalchemy import Boolean, Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class FunctionalAssignment(Base, BaseModel):
    """Модель для назначения функций на должности"""
    
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    function_id = Column(Integer, ForeignKey("function.id"), nullable=False)
    percentage = Column(Integer, default=100, nullable=False)  # Процент загрузки
    is_primary = Column(Boolean, default=False, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    position = relationship("Position", back_populates="functional_assignments")
    function = relationship("Function", back_populates="functional_assignments")
    
    __tablename__ = "functional_assignment"
    
    __table_args__ = (
        # Уникальное сочетание должности и функции
        UniqueConstraint('position_id', 'function_id', name='uix_position_function'),
    ) 