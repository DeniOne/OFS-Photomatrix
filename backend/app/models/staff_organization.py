from sqlalchemy import Boolean, Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class StaffOrganization(Base, BaseModel):
    """Модель связи сотрудника с организацией"""
    
    __tablename__ = "staff_organization"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    is_primary = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    staff = relationship("Staff", foreign_keys=[staff_id], backref="staff_organizations")
    organization = relationship("Organization", foreign_keys=[organization_id]) 