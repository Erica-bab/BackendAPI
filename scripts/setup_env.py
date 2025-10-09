"""
환경변수 설정 스크립트
.env 파일 생성 및 API 키 자동 생성

사용법:
    python scripts/setup_env.py
"""

import os
import sys
import secrets
from pathlib import Path
from typing import List

# 프로젝트 루트 경로
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"


def generate_api_key(prefix: str = "meal_api") -> str:
    """
    안전한 API 키 생성
    
    Args:
        prefix: API 키 접두사
        
    Returns:
        생성된 API 키
    """
    random_part = secrets.token_urlsafe(32)  # 256비트 랜덤 문자열
    return f"{prefix}_{random_part}"


def get_input(prompt: str, default: str = "", required: bool = True) -> str:
    """
    사용자 입력 받기
    
    Args:
        prompt: 입력 프롬프트
        default: 기본값
        required: 필수 입력 여부
        
    Returns:
        사용자 입력값
    """
    if default:
        prompt = f"{prompt} [{default}]"
    
    prompt = f"{prompt}: "
    
    while True:
        value = input(prompt).strip()
        
        if not value:
            if default:
                return default
            elif not required:
                return ""
            else:
                print("❌ 필수 입력 항목입니다.")
                continue
        
        return value


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """
    예/아니오 입력 받기
    
    Args:
        prompt: 입력 프롬프트
        default: 기본값
        
    Returns:
        True/False
    """
    default_str = "Y/n" if default else "y/N"
    prompt = f"{prompt} [{default_str}]"
    
    while True:
        value = input(f"{prompt}: ").strip().lower()
        
        if not value:
            return default
        
        if value in ['y', 'yes']:
            return True
        elif value in ['n', 'no']:
            return False
        else:
            print("❌ 'y' 또는 'n'을 입력해주세요.")


def setup_env():
    """환경변수 설정 메인 함수"""
    print("=" * 70)
    print("🔧 한양대 급식 API - 환경변수 설정")
    print("=" * 70)
    print()
    
    # 기존 .env 파일 확인
    if env_file.exists():
        print("⚠️  .env 파일이 이미 존재합니다.")
        if not get_yes_no("기존 파일을 덮어쓰시겠습니까?", default=False):
            print("❌ 취소되었습니다.")
            sys.exit(0)
        print()
    
    print("📋 데이터베이스 설정")
    print("-" * 70)
    
    # 데이터베이스 설정
    db_user = get_input("DB 사용자명", default="mealuser")
    db_password = get_input("DB 비밀번호", required=True)
    db_host = get_input("DB 호스트", default="localhost")
    db_port = get_input("DB 포트", default="3306")
    db_name = get_input("DB 이름", default="meal_db")
    
    database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    
    print()
    print("🔑 관리자 API 키 설정")
    print("-" * 70)
    
    # API 키 설정
    api_keys: List[str] = []
    
    # 첫 번째 API 키는 자동 생성
    first_key = generate_api_key()
    api_keys.append(first_key)
    print(f"✓ API 키 #1 생성됨: {first_key}")
    
    # 추가 API 키 생성
    while True:
        if get_yes_no("추가 API 키를 생성하시겠습니까?", default=False):
            new_key = generate_api_key()
            api_keys.append(new_key)
            print(f"✓ API 키 #{len(api_keys)} 생성됨: {new_key}")
        else:
            break
    
    print()
    print("📅 급식 데이터 수집 설정")
    print("-" * 70)
    
    # 급식 수집 설정
    meal_fetch_days = get_input("수집할 일수 (현재부터)", default="14")
    meal_fetch_schedule = get_input("자동 수집 스케줄 (cron)", default="0 2 * * *")
    
    print()
    print("=" * 70)
    print("📝 설정 요약")
    print("=" * 70)
    print(f"데이터베이스: {db_user}@{db_host}:{db_port}/{db_name}")
    print(f"API 키 개수: {len(api_keys)}개")
    for i, key in enumerate(api_keys, 1):
        print(f"  #{i}: {key}")
    print(f"수집 일수: {meal_fetch_days}일")
    print(f"수집 스케줄: {meal_fetch_schedule}")
    print()
    
    if not get_yes_no("이 설정으로 .env 파일을 생성하시겠습니까?", default=True):
        print("❌ 취소되었습니다.")
        sys.exit(0)
    
    # .env 파일 생성
    env_content = f"""# 데이터베이스 설정
DATABASE_URL={database_url}

# 관리자 API 키 (콤마로 구분)
# 급식 데이터 수집 등 관리 작업에 필요합니다
ADMIN_API_KEYS={','.join(api_keys)}

# 급식 데이터 수집 설정
MEAL_FETCH_DAYS_AHEAD={meal_fetch_days}
MEAL_FETCH_SCHEDULE={meal_fetch_schedule}

# CORS 설정 (선택사항)
# BACKEND_CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print()
        print("=" * 70)
        print("✅ .env 파일이 성공적으로 생성되었습니다!")
        print("=" * 70)
        print()
        print(f"📁 파일 위치: {env_file}")
        print()
        print("🔐 중요: API 키를 안전하게 보관하세요!")
        print("-" * 70)
        for i, key in enumerate(api_keys, 1):
            print(f"API 키 #{i}: {key}")
        print("-" * 70)
        print()
        print("💡 이 API 키는 다음 작업에 사용됩니다:")
        print("   - POST /api/v1/meals/fetch (급식 데이터 수집)")
        print("   - 기타 관리자 전용 API")
        print()
        print("📝 다음 단계:")
        print("   1. python scripts/setup_db.py     # 데이터베이스 초기화")
        print("   2. uvicorn app.main:app --reload   # 서버 실행")
        print("   3. python scripts/fetch_meals.py 2025 9  # 데이터 수집")
        print()
        
        # API 키를 별도 파일로 저장 (백업)
        api_keys_file = project_root / "API_KEYS.txt"
        with open(api_keys_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("한양대 급식 API - 관리자 API 키\n")
            f.write("=" * 70 + "\n\n")
            f.write("⚠️  이 파일은 안전하게 보관하세요!\n")
            f.write("⚠️  Git에 커밋하지 마세요! (.gitignore에 포함되어 있습니다)\n\n")
            for i, key in enumerate(api_keys, 1):
                f.write(f"API 키 #{i}:\n")
                f.write(f"{key}\n\n")
            f.write("\n사용 예시:\n")
            f.write("curl -X POST http://localhost:5401/api/v1/meals/fetch \\\n")
            f.write(f'  -H "X-API-Key: {api_keys[0]}"\n')
        
        print(f"✅ API 키가 백업되었습니다: {api_keys_file}")
        print("   (이 파일은 .gitignore에 포함되어 있습니다)")
        print()
        
    except Exception as e:
        print(f"\n❌ 파일 생성 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        setup_env()
    except KeyboardInterrupt:
        print("\n\n❌ 사용자에 의해 취소되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

