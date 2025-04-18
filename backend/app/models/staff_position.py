from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class StaffPosition(Base, BaseModel):
    """Модель для связи сотрудников с должностями (многие ко многим)"""
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("position.id"), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    staff = relationship("Staff", back_populates="staff_positions")
    position = relationship("Position", back_populates="staff_positions")
    
    __tablename__ = "staff_position"
    
    __table_args__ = (
        # Уникальное сочетание сотрудника и должности
        UniqueConstraint('staff_id', 'position_id', name='uix_staff_position'),
    ) 