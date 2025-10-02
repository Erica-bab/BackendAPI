from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1.api import api_router
from app.services.scheduler import start_scheduler, stop_scheduler
from app.db.session import engine

# 모든 모델을 import하여 테이블 생성이 가능하도록 함
from app.models.restaurant import Restaurant
from app.models.meal import Meal
from app.models.rating import Rating
from app.models.keyword import Keyword, MealKeywordReview

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 로직"""
    # 시작 시
    logger.info("애플리케이션 시작")
    
    # 데이터베이스 테이블 생성 (개발용 - 프로덕션에서는 Alembic 사용)
    try:
        from app.db.base import Base
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"데이터베이스 테이블 생성 실패: {e}")
    
    # 스케줄러 시작
    try:
        start_scheduler()
        logger.info("스케줄러 시작 완료")
    except Exception as e:
        logger.error(f"스케줄러 시작 실패: {e}")
    
    yield
    
    # 종료 시
    logger.info("애플리케이션 종료")
    try:
        stop_scheduler()
        logger.info("스케줄러 중지 완료")
    except Exception as e:
        logger.error(f"스케줄러 중지 실패: {e}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "한양대학교 급식 API",
        "version": settings.VERSION,
        "description": "급식 정보 조회 및 평점/리뷰 기능",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5401)

