from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class Position(Base, BaseModel):
    """Модель должности в организационной структуре"""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    division_id = Column(Integer, ForeignKey("division.id"), nullable=True)
    section_id = Column(Integer, ForeignKey("section.id"), nullable=True)
    attribute = Column(String(50), nullable=True)  # Уровень должности (Директор, Руководитель и т.д.)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    division = relationship("Division", back_populates="positions")
    section = relationship("Section", back_populates="positions")
    staff_positions = relationship("StaffPosition", back_populates="position")
    functional_assignments = relationship("FunctionalAssignment", back_populates="position")
    functional_relations_source = relationship(
        "FunctionalRelation", 
        foreign_keys="FunctionalRelation.source_id",
        back_populates="source"
    )
    functional_relations_target = relationship(
        "FunctionalRelation", 
        foreign_keys="FunctionalRelation.target_id",
        back_populates="target"
    )
    
    __tablename__ = "position"
    
    __table_args__ = (
        # Уникальный код в пределах подразделения
        UniqueConstraint('code', 'division_id', name='uix_position_code_division'),
    ) 