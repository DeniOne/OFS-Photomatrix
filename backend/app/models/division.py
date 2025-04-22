from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, func, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime
import enum

# Определение перечисления для типов подразделений
class DivisionType(str, enum.Enum):
    DEPARTMENT = "DEPARTMENT"  # Департамент (верхний уровень)
    DIVISION = "DIVISION"      # Отдел (дочерний уровень)

class Division(Base):
    __tablename__ = "division"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Связь с организацией
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    organization = relationship("Organization", back_populates="divisions")
    
    # Самоссылка на родительское подразделение
    parent_id = Column(Integer, ForeignKey("division.id"), nullable=True)
    parent = relationship("Division", remote_side=[id], back_populates="children")
    children = relationship("Division", back_populates="parent")
    
    # Тип подразделения
    type = Column(Enum(DivisionType), default=DivisionType.DEPARTMENT, nullable=False)
    
    # Отношение с отделами (sections)
    sections = relationship("Section", back_populates="division")
    
    # Отношение с должностями (positions)
    positions = relationship("Position", back_populates="division")
    
    # Статус активности
    is_active = Column(Boolean, default=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<Division id={self.id} name={self.name} code={self.code}>" 