from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Keyword(Base):
    """키워드 마스터 (미리 정의된 키워드)"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="키워드 이름")
    category = Column(String(20), comment="키워드 카테고리 (맛, 양, 서비스 등)")
    display_order = Column(Integer, default=0, comment="표시 순서")
    
    # 관계
    meal_reviews = relationship("MealKeywordReview", back_populates="keyword")


class MealKeywordReview(Base):
    """메뉴별 키워드 리뷰"""
    __tablename__ = "meal_keyword_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False, index=True, comment="메뉴 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, index=True, comment="키워드 ID")
    user_id = Column(String(100), nullable=False, index=True, comment="사용자 ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    
    # 관계
    meal = relationship("Meal", back_populates="keyword_reviews")
    keyword = relationship("Keyword", back_populates="meal_reviews")
    
    # 제약조건: 한 사용자는 한 메뉴에 같은 키워드를 중복으로 선택할 수 없음
    __table_args__ = (
        UniqueConstraint('meal_id', 'keyword_id', 'user_id', name='unique_user_meal_keyword'),
        Index('idx_meal_keyword', 'meal_id', 'keyword_id'),
    )

