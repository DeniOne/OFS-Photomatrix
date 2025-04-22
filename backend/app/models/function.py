from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseModel

class Function(Base, BaseModel):
    __tablename__ = "function"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    section_id = Column(Integer, ForeignKey("section.id"), nullable=False, index=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связи
    section = relationship("Section", back_populates="functions")
    functional_assignments = relationship("FunctionalAssignment", back_populates="function")

    # Уникальность кода (если нужно, но обычно код глобально уникален)
    # __table_args__ = (UniqueConstraint('code', name='uix_function_code'),)

    def __repr__(self):
        return f"<Function(name='{self.name}', code='{self.code}')>" 