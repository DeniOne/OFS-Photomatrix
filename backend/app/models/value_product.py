from sqlalchemy import Boolean, Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class ValueProduct(Base, BaseModel):
    """Модель ЦКП (Ценный Конечный Продукт)"""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Связь с организацией
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    
    # Возможная связь с родительским ЦКП (для иерархии)
    parent_id = Column(Integer, ForeignKey("value_product.id"), nullable=True)
    
    # Вес влияния на родительский ЦКП
    weight = Column(Float, default=1.0, nullable=False)
    
    # Метрики выполнения (в JSON формате)
    completion_metrics = Column(JSON, default={}, nullable=False)
    
    # Статус ЦКП
    status = Column(String(50), default="active", nullable=False)
    
    # Флаг активности
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Отношения
    organization = relationship("Organization")
    parent = relationship("ValueProduct", remote_side=[id], backref="children")
    
    __tablename__ = "value_product"
    
    __table_args__ = (
        # Уникальный код в пределах организации
        UniqueConstraint('code', 'organization_id', name='uix_value_product_code_organization'),
    ) 