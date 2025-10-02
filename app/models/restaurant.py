from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class Restaurant(Base):
    """식당 정보"""
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True, comment="식당 코드 (re11, re12 등)")
    name = Column(String(100), nullable=False, comment="식당 이름")
    
    # 관계
    meals = relationship("Meal", back_populates="restaurant", cascade="all, delete-orphan")

