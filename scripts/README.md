# 🛠️ Scripts

데이터베이스 초기화 및 설정을 위한 공식 스크립트 모음입니다.

## 📋 스크립트 목록

### 1️⃣ `setup_env.py` - 환경변수 설정 (최우선)

`.env` 파일을 생성하고 데이터베이스 설정 및 관리자 API 키를 자동으로 설정합니다.

**사용법:**
```bash
python scripts/setup_env.py
```

**기능:**
- ✅ 대화형 방식으로 설정 입력
- ✅ 데이터베이스 연결 정보 설정
- ✅ 관리자 API 키 자동 생성 (여러 개 가능)
- ✅ 급식 데이터 수집 설정
- ✅ API 키 백업 파일 생성 (`API_KEYS.txt`)

**입력 항목:**
- DB 사용자명 (기본값: mealuser)
- DB 비밀번호 (필수)
- DB 호스트 (기본값: localhost)
- DB 포트 (기본값: 3306)
- DB 이름 (기본값: meal_db)
- 수집할 일수 (기본값: 14)
- 자동 수집 스케줄 (기본값: 0 2 * * *)

**생성 파일:**
- `.env` - 환경변수 파일
- `API_KEYS.txt` - API 키 백업 (안전하게 보관!)

**API 키 특징:**
- 🔐 256비트 랜덤 문자열로 안전하게 생성
- 🔑 여러 개의 API 키 생성 가능 (팀원별, 용도별)
- 📝 자동으로 백업 파일 생성
- 🚫 Git에 커밋되지 않음 (.gitignore에 포함)

---

### 2️⃣ `setup_db.py` - 데이터베이스 초기화

데이터베이스 테이블 생성 및 기본 데이터를 자동으로 설정합니다.

**사용법:**
```bash
python scripts/setup_db.py
```

**기능:**
- ✅ 모든 테이블 자동 생성
  - `restaurants` (식당)
  - `meals` (급식 메뉴)
  - `ratings` (평점)
  - `keywords` (키워드)
  - `meal_keyword_reviews` (키워드 리뷰)
- ✅ 기본 식당 데이터 삽입 (4개)
  - re11: 교직원식당
  - re12: 학생식당
  - re13: 창의인재원식당
  - re15: 창업보육센터
- ✅ 기본 키워드 데이터 삽입 (30개)
  - 긍정 키워드 15개
  - 부정 키워드 15개

**요구사항:**
- 환경변수 `.env` 파일에 `DATABASE_URL` 설정 필요
- 예: `DATABASE_URL=mysql+pymysql://user:password@localhost:3306/meal_db?charset=utf8mb4`

---

### 3️⃣ `fetch_meals.py` - 급식 데이터 수집

특정 연도/월의 전체 급식 데이터를 한양대 서버에서 수집하여 DB에 저장합니다.

**사용법:**
```bash
# 기본 형식
python scripts/fetch_meals.py [연도] [월]

# 예제
python scripts/fetch_meals.py 2025 9    # 2025년 9월 전체
python scripts/fetch_meals.py 2024 12   # 2024년 12월 전체
```

**기능:**
- ✅ 지정한 월의 모든 날짜 데이터 자동 수집 (1일~말일)
- ✅ 4개 식당 데이터 동시 수집
- ✅ 중복 데이터 자동 처리 (신규 저장 or 업데이트)
- ✅ 상세한 진행 상황 로깅
- ✅ 식당별/전체 통계 제공

**특징:**
- 🗓️ 각 월의 마지막 날짜 자동 계산 (28일, 30일, 31일)
- 🔄 이미 존재하는 데이터는 자동으로 업데이트
- 📊 실시간 진행 상황 및 통계 출력
- ⚠️ 오류 발생 시에도 계속 진행

**출력 예시:**
```
📅 2025년 9월 급식 정보 수집 시작
수집 기간: 2025-09-01 ~ 2025-09-30 (총 30일)

🍽️  [교직원식당] 데이터 수집 시작
📆 2025-09-01 (Monday)
   ✓ 신규 3개, 업데이트 0개
...

🎉 2025년 9월 급식 정보 수집 완료!
📊 전체 통계:
   총 신규 저장: 245개
   총 업데이트: 12개
   총 오류: 0개
```

**요구사항:**
- 환경변수 `.env` 파일 설정 필요
- 유효 연도 범위: 2020 ~ 현재+1년

---

## 📝 참고사항

### 개인 스크립트 보관

개인적인 용도의 스크립트(테스트, 일회성 작업 등)는 `my_scripts/` 폴더에 보관하세요.  
해당 폴더는 `.gitignore`에 포함되어 Git에 추적되지 않습니다.

```bash
my_scripts/
├── test_parsing.py
├── fetch_specific_data.py
└── custom_migration.py
```

### 초기 설정 순서

1. **데이터베이스 생성** (MySQL/MariaDB)
   ```sql
   CREATE DATABASE meal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'mealuser'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON meal_db.* TO 'mealuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **환경변수 설정** (대화형)
   ```bash
   python scripts/setup_env.py
   ```
   이 단계에서 다음이 자동으로 생성됩니다:
   - `.env` 파일
   - `API_KEYS.txt` (백업)
   - 관리자 API 키 자동 생성

3. **데이터베이스 초기화**
   ```bash
   python scripts/setup_db.py
   ```

4. **서버 실행**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 5401
   ```

5. **급식 데이터 수집**
   
   **방법 1: 스크립트 (권장)**
   ```bash
   python scripts/fetch_meals.py 2025 9
   ```
   
   **방법 2: API (생성된 API 키 사용)**
   ```bash
   # API_KEYS.txt 파일에서 키 확인
   curl -X POST http://localhost:5401/api/v1/meals/fetch \
     -H "X-API-Key: meal_api_xxxxxxxxxxxxx"
   ```

