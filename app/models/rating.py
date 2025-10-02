from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Rating(Base):
    """메뉴 평점"""
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False, index=True, comment="메뉴 ID")
    user_id = Column(String(100), nullable=False, index=True, comment="사용자 ID (익명 또는 UUID)")
    rating = Column(Float, nullable=False, comment="평점 (1.0 ~ 5.0)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간")
    
    # 관계
    meal = relationship("Meal", back_populates="ratings")
    
    # 제약조건: 한 사용자는 한 메뉴에 하나의 평점만 가능
    __table_args__ = (
        UniqueConstraint('meal_id', 'user_id', name='unique_user_meal_rating'),
    )

