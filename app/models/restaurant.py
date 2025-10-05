from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base


class Restaurant(Base):
    """식당 정보"""
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True, comment="식당 코드 (re11, re12 등)")
    name = Column(String(100), nullable=False, comment="식당 이름")
    
    # 위치 정보
    address = Column(String(200), comment="주소")
    building = Column(String(50), comment="건물명")
    floor = Column(String(20), comment="층수")
    latitude = Column(String(20), comment="위도")
    longitude = Column(String(20), comment="경도")
    description = Column(String(500), comment="위치 설명")
    
    # 관계
    meals = relationship("Meal", back_populates="restaurant", cascade="all, delete-orphan")

