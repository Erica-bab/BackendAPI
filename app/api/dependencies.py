from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.core.config import settings


def verify_admin_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    관리자 API 키 인증
    
    Args:
        x_api_key: HTTP 헤더의 X-API-Key 값
        
    Returns:
        인증된 API 키
        
    Raises:
        HTTPException: 인증 실패 시 401 오류
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API 키가 필요합니다. X-API-Key 헤더를 포함해주세요."
        )
    
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 API 키입니다."
        )
    
    return x_api_key


# 의존성 별칭
AdminAuth = Depends(verify_admin_api_key)
