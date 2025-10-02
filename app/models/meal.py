from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class Meal(Base):
    """급식 메뉴 정보"""
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, comment="식당 ID")
    date = Column(Date, nullable=False, index=True, comment="날짜")
    day_of_week = Column(String(10), comment="요일")
    meal_type = Column(String(10), nullable=False, comment="식사 종류 (조식, 중식, 석식)")
    
    # 메뉴 정보 (JSON으로 리스트 저장)
    korean_name = Column(JSON, nullable=False, comment="한국어 메뉴명 (리스트)")
    tags = Column(JSON, comment="태그 (리스트, 예: [중식A], [특식])")
    price = Column(String(20), comment="가격")
    image_url = Column(String(500), comment="이미지 URL")
    
    # 관계
    restaurant = relationship("Restaurant", back_populates="meals")
    ratings = relationship("Rating", back_populates="meal", cascade="all, delete-orphan")
    keyword_reviews = relationship("MealKeywordReview", back_populates="meal", cascade="all, delete-orphan")
    
    # 인덱스: 식당 + 날짜 + 식사종류 조합으로 빠른 조회
    __table_args__ = (
        UniqueConstraint('restaurant_id', 'date', 'meal_type', 'korean_name', name='unique_meal'),
        Index('idx_restaurant_date', 'restaurant_id', 'date'),
    )

