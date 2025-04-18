from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, Date, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional

from app.db.base import Base, BaseModel

class Staff(Base, BaseModel):
    """Модель сотрудника"""
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    middle_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    hire_date = Column(Date, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    photo_path = Column(String(255), nullable=True)
    document_paths = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="staff")
    staff_positions = relationship("StaffPosition", back_populates="staff")
    
    __tablename__ = "staff"
    
    def full_name(self) -> str:
        """Возвращает полное имя сотрудника"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}" 