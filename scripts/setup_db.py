"""
데이터베이스 초기화 스크립트
테이블 생성 및 기본 데이터 삽입
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models import Restaurant, Meal, Rating, Keyword, MealKeywordReview
from app.core.config import settings


def init_database():
    """데이터베이스 초기화 (테이블 생성 + 기본 데이터)"""
    print("=" * 60)
    print("🔧 한양대 급식 API - 데이터베이스 초기화")
    print("=" * 60)
    print()
    
    try:
        # 데이터베이스 연결
        print("1️⃣  데이터베이스 연결 중...")
        engine = create_engine(settings.DATABASE_URL)
        print("   ✓ 연결 성공")
        print()
        
        # 테이블 생성
        print("2️⃣  테이블 생성 중...")
        Base.metadata.create_all(bind=engine)
        print("   ✓ 모든 테이블 생성 완료")
        print()
        
        # 세션 생성
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # 기본 데이터 삽입
            print("3️⃣  기본 데이터 삽입 중...")
            
            # 1. 식당 데이터
            restaurants_data = [
                ('re11', '교직원식당'),
                ('re12', '학생식당'),
                ('re13', '창의인재원식당'),
                ('re15', '창업보육센터'),
            ]
            
            for code, name in restaurants_data:
                existing = db.query(Restaurant).filter(Restaurant.code == code).first()
                if not existing:
                    restaurant = Restaurant(code=code, name=name)
                    db.add(restaurant)
            
            db.commit()
            print(f"   ✓ {len(restaurants_data)}개 식당 데이터 삽입")
            
            # 2. 키워드 데이터
            keywords_data = [
                ('맛있어요', '긍정', 1),
                ('양이 많아요', '긍정', 2),
                ('가성비 좋아요', '긍정', 3),
                ('신선해요', '긍정', 4),
                ('따뜻해요', '긍정', 5),
                ('식감이 좋아요', '긍정', 6),
                ('건강해요', '긍정', 7),
                ('담백해요', '긍정', 8),
                ('재방문 의사 있어요', '긍정', 9),
                ('추천해요', '긍정', 10),
                ('푸짐해요', '긍정', 11),
                ('깔끔해요', '긍정', 12),
                ('부드러워요', '긍정', 13),
                ('향이 좋아요', '긍정', 14),
                ('만족해요', '긍정', 15),
                ('별로예요', '부정', 16),
                ('양이 적어요', '부정', 17),
                ('비싸요', '부정', 18),
                ('차가워요', '부정', 19),
                ('식감이 별로예요', '부정', 20),
                ('기름져요', '부정', 21),
                ('비추천', '부정', 22),
                ('짜요', '부정', 23),
                ('싱거워요', '부정', 24),
                ('매워요', '부정', 25),
                ('달아요', '부정', 26),
                ('냄새가 나요', '부정', 27),
                ('딱딱해요', '부정', 28),
                ('질겨요', '부정', 29),
                ('아쉬워요', '부정', 30),
            ]
            
            for name, category, order in keywords_data:
                existing = db.query(Keyword).filter(Keyword.name == name).first()
                if not existing:
                    keyword = Keyword(name=name, category=category, display_order=order)
                    db.add(keyword)
            
            db.commit()
            print(f"   ✓ {len(keywords_data)}개 키워드 데이터 삽입")
            print()
            
            # 4. 확인
            print("4️⃣  생성된 데이터 확인...")
            restaurant_count = db.query(Restaurant).count()
            keyword_count = db.query(Keyword).count()
            print(f"   ✓ restaurants: {restaurant_count}개")
            print(f"   ✓ keywords: {keyword_count}개")
            print()
            
        finally:
            db.close()
        
        print("=" * 60)
        print("🎉 데이터베이스 초기화 완료!")
        print("=" * 60)
        print()
        print("다음 단계:")
        print("1. 서버 실행:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 5401")
        print()
        print("2. 급식 데이터 수집 (관리자 API 키 필요):")
        print("   curl -X POST http://localhost:5401/api/v1/meals/fetch \\")
        print('     -H "X-API-Key: your_api_key"')
        print()
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    init_database()
