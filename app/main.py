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
    
    # 스케줄러 시작 (파일 락으로 첫 번째 프로세스에서만)
    try:
        import os
        import fcntl
        import tempfile
        
        # 스케줄러 락 파일 경로
        lock_file_path = "/tmp/ricerica_scheduler.lock"
        
        try:
            # 락 파일 열기
            lock_file = open(lock_file_path, 'w')
            
            # 논블로킹 락 시도
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # 락 획득 성공 - 이 프로세스가 스케줄러를 담당
            pid = os.getpid()
            lock_file.write(str(pid))
            lock_file.flush()
            
            start_scheduler()
            logger.info(f"스케줄러 시작 완료 (마스터 프로세스 - PID: {pid})")
            
            # 락 파일은 프로세스 종료까지 유지 (자동으로 해제됨)
            
        except (IOError, OSError) as e:
            # 락 획득 실패 - 다른 프로세스가 이미 스케줄러를 담당 중
            logger.info(f"스케줄러 시작 건너뜀 (워커 프로세스 - PID: {os.getpid()})")
            if 'lock_file' in locals():
                lock_file.close()
                
    except Exception as e:
        logger.error(f"스케줄러 시작 실패: {e}")
    
    yield
    
    # 종료 시
    logger.info("애플리케이션 종료")
    try:
        import os
        is_master = os.environ.get("MASTER_PROCESS", "false").lower() == "true"
        
        if is_master:
            stop_scheduler()
            logger.info("스케줄러 중지 완료 (마스터 프로세스)")
        else:
            logger.info("스케줄러 중지 건너뜀 (워커 프로세스)")
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

# frontend 셋팅
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", tags=["root"])
async def root():
    """메인 페이지"""
    return FileResponse("index.html")

@app.get("/sw.js")
async def get_sw_js():
    """Service Worker 파일"""
    return FileResponse("app/static/sw.js")

@app.get("manifest.json")
async def get_manifest_json():
    """Manifest 파일"""
    return FileResponse("app/static/manifest.json")

@app.get("/static/{file_name}")
async def get_file(file_name: str):
    """정적 파일 서빙"""
    return FileResponse(f"app/static/{file_name}")

@app.get("/health", tags=["health"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5401)

