from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from app.db.session import SessionLocal
from app.services.meal_fetcher import meal_fetcher
from app.core.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def scheduled_meal_fetch():
    """스케줄된 급식 정보 수집 작업"""
    logger.info("스케줄된 급식 정보 수집 시작")
    db = SessionLocal()
    try:
        meal_fetcher.fetch_and_store_meals(db)
    except Exception as e:
        logger.error(f"스케줄된 급식 정보 수집 실패: {e}")
    finally:
        db.close()


def start_scheduler():
    """스케줄러 시작"""
    # Cron 표현식 파싱 (예: "0 2 * * *" = 매일 새벽 2시)
    cron_parts = settings.MEAL_FETCH_SCHEDULE.split()
    
    if len(cron_parts) == 5:
        minute, hour, day, month, day_of_week = cron_parts
        
        scheduler.add_job(
            scheduled_meal_fetch,
            CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week
            ),
            id="meal_fetch_job",
            replace_existing=True
        )
        
        logger.info(f"스케줄러 시작: {settings.MEAL_FETCH_SCHEDULE}")
        scheduler.start()
    else:
        logger.error(f"잘못된 cron 표현식: {settings.MEAL_FETCH_SCHEDULE}")


def stop_scheduler():
    """스케줄러 중지"""
    scheduler.shutdown()
    logger.info("스케줄러 중지")

