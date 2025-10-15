"""
식당 오픈시간 체크 유틸리티

식사 종류별 오픈시간에만 리뷰 작성이 가능하도록 체크하는 함수들
"""
from datetime import datetime, time, date
from typing import Tuple


# 식사 종류별 오픈시간 정의
MEAL_OPEN_TIMES = {
    "조식": {
        "start": time(7, 40),   # 07:40
        "end": time(9, 0)      # 09:00
    },
    "중식": {
        "start": time(11, 30), # 11:30
        "end": time(13, 30)    # 13:30
    },
    "석식": {
        "start": time(17, 30), # 17:30
        "end": time(19, 0)     # 19:00
    }
}


def is_meal_time_open(meal_type: str, current_time: datetime = None) -> bool:
    """
    특정 식사 종류의 오픈시간인지 확인
    
    Args:
        meal_type: 식사 종류 ("조식", "중식", "석식")
        current_time: 현재 시간 (기본값: 현재 시간)
    
    Returns:
        bool: 오픈시간이면 True, 아니면 False
    """
    if meal_type not in MEAL_OPEN_TIMES:
        return False
    
    if current_time is None:
        current_time = datetime.now()
    
    current_time_only = current_time.time()
    open_times = MEAL_OPEN_TIMES[meal_type]
    
    return open_times["start"] <= current_time_only <= open_times["end"]


def get_meal_open_time_range(meal_type: str) -> Tuple[time, time]:
    """
    특정 식사 종류의 오픈시간 범위 반환
    
    Args:
        meal_type: 식사 종류 ("조식", "중식", "석식")
    
    Returns:
        Tuple[time, time]: (시작시간, 종료시간)
    """
    if meal_type not in MEAL_OPEN_TIMES:
        raise ValueError(f"잘못된 식사 종류: {meal_type}")
    
    open_times = MEAL_OPEN_TIMES[meal_type]
    return open_times["start"], open_times["end"]


def get_meal_open_time_string(meal_type: str) -> str:
    """
    특정 식사 종류의 오픈시간을 문자열로 반환
    
    Args:
        meal_type: 식사 종류 ("조식", "중식", "석식")
    
    Returns:
        str: "07:40 ~ 09:00" 형식의 문자열
    """
    if meal_type not in MEAL_OPEN_TIMES:
        return "정보 없음"
    
    start_time, end_time = get_meal_open_time_range(meal_type)
    return f"{start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}"


def check_review_permission(meal_type: str, meal_date: date, current_time: datetime = None) -> dict:
    """
    리뷰 작성 권한 확인
    
    Args:
        meal_type: 식사 종류 ("조식", "중식", "석식")
        meal_date: 급식 날짜
        current_time: 현재 시간 (기본값: 현재 시간)
    
    Returns:
        dict: {
            "allowed": bool,
            "reason": str,
            "open_time": str,
            "current_time": str
        }
    """
    if current_time is None:
        current_time = datetime.now()
    
    current_date = current_time.date()
    current_time_only = current_time.time()
    
    # 오늘 급식이 아니면 리뷰 불가
    if meal_date != current_date:
        return {
            "allowed": False,
            "reason": f"오늘({current_date}) 급식이 아닙니다. 급식 날짜: {meal_date}",
            "open_time": get_meal_open_time_string(meal_type),
            "current_time": current_time_only.strftime('%H:%M')
        }
    
    # 오픈시간 체크
    if not is_meal_time_open(meal_type, current_time):
        return {
            "allowed": False,
            "reason": f"{meal_type} 오픈시간이 아닙니다.",
            "open_time": get_meal_open_time_string(meal_type),
            "current_time": current_time_only.strftime('%H:%M')
        }
    
    return {
        "allowed": True,
        "reason": "리뷰 작성 가능",
        "open_time": get_meal_open_time_string(meal_type),
        "current_time": current_time_only.strftime('%H:%M')
    }
