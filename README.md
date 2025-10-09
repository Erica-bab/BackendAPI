# 🍽️ 한양대학교 ERICA 급식 API v2.0

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green?style=for-the-badge&logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange?style=for-the-badge&logo=mysql)

**한양대학교 ERICA 식당의 급식 정보를 조회하고, 평점 및 키워드 리뷰를 남길 수 있는 FastAPI 기반 REST API**

[🌐 라이브 데모](https://에리카밥.com) • [📖 API 문서](https://에리카밥.com/docs) • [🚀 시작하기](#-빠른-시작) • [📋 API 목록](#-api-엔드포인트)

</div>

---

## ✨ 주요 기능

<table>
<tr>
<td width="50%">

### 🍚 **급식 정보 조회**
- 한양대 ERICA 4개 식당 실시간 메뉴
- 조식/중식/석식 분류
- 메뉴별 상세 정보 (가격, 이미지)
- **유연한 조회**: 식당/시간대 자유 조합
- 웹에서 직접 파싱 가능

</td>
<td width="50%">

### ⭐ **평점 시스템**
- 메뉴별 1~5점 평점 등록
- 평균 평점 및 통계 조회
- 사용자별 평점 관리

</td>
</tr>
<tr>
<td width="50%">

### 🏷️ **키워드 리뷰**
- 30개 사전 정의 키워드 (긍정/부정)
- 맛/양/품질/건강 카테고리
- 상위 키워드 통계

</td>
<td width="50%">

### 🗺️ **식당 위치 정보**
- 각 식당의 상세 위치 정보
- 건물명, 층수, 주소 제공
- GPS 좌표 (위도/경도)
- 위치 설명 및 안내
- **운영시간 정보** (조식/중식/석식별)

</td>
</tr>
<tr>
<td width="50%">

### 🔄 **자동 데이터 수집**
- 매일 새벽 2시 자동 수집
- 2주치 데이터 미리 저장
- 실시간 API 응답
- 관리자 인증 시스템

</td>
<td width="50%">

### 🔐 **보안 기능**
- 관리자 API 키 인증
- 패치 API 접근 제한
- 안전한 데이터 관리

</td>
</tr>
</table>

---

## 🏗️ 시스템 아키텍처

```mermaid
graph TB
    A[클라이언트] --> B[FastAPI 서버]
    B --> C[API 엔드포인트]
    C --> D[비즈니스 로직]
    D --> E[데이터베이스]
    D --> F[한양대 서버]
    
    G[스케줄러] --> D
    H[평점/리뷰] --> E
    
    subgraph "데이터베이스"
        E1[restaurants]
        E2[meals]
        E3[ratings]
        E4[keywords]
        E5[reviews]
    end
    
    E --> E1
    E --> E2
    E --> E3
    E --> E4
    E --> E5
```

---

## 📊 데이터베이스 구조

<table>
<tr>
<th>테이블</th>
<th>설명</th>
<th>주요 필드</th>
</tr>
<tr>
<td><code>restaurants</code></td>
<td>식당 정보</td>
<td>code, name, address, building, floor, latitude, longitude, description, <strong>open_times (JSON)</strong></td>
</tr>
<tr>
<td><code>meals</code></td>
<td>급식 메뉴</td>
<td>korean_name (JSON), tags (JSON), price</td>
</tr>
<tr>
<td><code>ratings</code></td>
<td>메뉴 평점</td>
<td>rating (1.0~5.0), user_id</td>
</tr>
<tr>
<td><code>keywords</code></td>
<td>키워드 마스터</td>
<td>name, category, display_order</td>
</tr>
<tr>
<td><code>meal_keyword_reviews</code></td>
<td>키워드 리뷰</td>
<td>meal_id, keyword_id, user_id</td>
</tr>
</table>

---

## 🚀 빠른 시작

### 1️⃣ **환경 설정**

```bash
# 저장소 클론
git clone https://github.com/Erica-bab/BackendAPI
cd BackendAPI

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2️⃣ **데이터베이스 설정**

```bash
# MariaDB/MySQL 설치 (Ubuntu/Debian)
sudo apt update
sudo apt install mariadb-server

# 데이터베이스 생성
mysql -u root -p
```

```sql
CREATE DATABASE meal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mealuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON meal_db.* TO 'mealuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3️⃣ **환경변수 설정**

```bash
# 대화형 설정 스크립트 실행
python scripts/setup_env.py
```

**자동으로 생성됩니다:**
- `.env` 파일 (데이터베이스 설정, API 키 등)
- `API_KEYS.txt` 파일 (관리자 API 키 백업)
- 관리자 API 키 자동 생성 (256비트 보안 키)

**또는 수동 설정:**
```bash
# .env 파일 생성
cat > .env << EOF
DATABASE_URL=mysql+pymysql://mealuser:password@localhost:3306/meal_db?charset=utf8mb4
ADMIN_API_KEYS=your_generated_api_key_here
MEAL_FETCH_DAYS_AHEAD=14
MEAL_FETCH_SCHEDULE=0 2 * * *
EOF
```

### 4️⃣ **데이터베이스 초기화**

```bash
# 환경변수(.env) 설정 후 실행
# 테이블 생성 및 기본 데이터(식당, 키워드) 삽입
python scripts/setup_db.py
```

**setup_db.py 기능:**
- 모든 테이블 자동 생성 (restaurants, meals, ratings, keywords, meal_keyword_reviews)
- 기본 식당 데이터 삽입 (4개 식당)
- 기본 키워드 데이터 삽입 (30개 키워드: 긍정 15개, 부정 15개)

### 5️⃣ **서버 실행**

```bash
# 개발 모드
uvicorn app.main:app --reload --host 0.0.0.0 --port 5401

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 5401
```

### 6️⃣ **급식 데이터 수집**

**방법 1: 스크립트 사용 (권장)**
```bash
# 특정 월의 전체 데이터 수집
python scripts/fetch_meals.py 2025 9
python scripts/fetch_meals.py 2025 10
```

**방법 2: API 사용 (관리자 키 필요)**
```bash
# 오늘부터 2주치 데이터 자동 수집
curl -X POST http://localhost:5401/api/v1/meals/fetch \
  -H "X-API-Key: your_api_key"
```

---

## 📋 API 엔드포인트

### 🍽️ 급식 정보

| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/api/v1/meals` | **급식 정보 조회** (식당/시간대 자유 조합) |
| `GET` | `/api/v1/meals/restaurants` | 식당 정보 조회 (위치 및 운영시간 포함) |
| `GET` | `/api/v1/meals/available-dates` | 저장된 급식 날짜 조회 |
| `GET` | `/api/v1/meals/parse/{restaurant_code}` | 웹에서 급식 정보 직접 파싱 |
| `POST` | `/api/v1/meals/fetch` | 급식 정보 수집 (관리자용) 🔐 |

### ⭐ 평점

| Method | Endpoint | 설명 |
|--------|----------|------|
| `POST` | `/api/v1/ratings/` | 평점 등록/수정 |
| `GET` | `/api/v1/ratings/meal/{meal_id}` | 메뉴 평점 통계 |
| `GET` | `/api/v1/ratings/meal/{meal_id}/user/{user_id}` | 사용자 평점 조회 |
| `DELETE` | `/api/v1/ratings/meal/{meal_id}/user/{user_id}` | 평점 삭제 |

### 🏷️ 키워드 리뷰

| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/api/v1/keywords/` | 키워드 목록 조회 |
| `POST` | `/api/v1/keywords/review` | 키워드 리뷰 등록 |
| `GET` | `/api/v1/keywords/stats/meal/{meal_id}` | 메뉴 키워드 통계 |
| `DELETE` | `/api/v1/keywords/review/meal/{meal_id}/keyword/{keyword_id}/user/{user_id}` | 키워드 리뷰 삭제 |

---

## 📝 API 사용 예시

### 식당 정보 조회

#### 모든 식당 정보 조회
```bash
curl -X GET "https://에리카밥.com/api/v1/meals/restaurants"
```

#### 특정 식당(들) 정보 조회
```bash
# 한 개 식당
curl -X GET "https://에리카밥.com/api/v1/meals/restaurants?restaurant_codes=re13"

# 여러 식당
curl -X GET "https://에리카밥.com/api/v1/meals/restaurants?restaurant_codes=re11,re13"
```

**응답 예시:**
```json
{
  "restaurants": [
    {
      "code": "re13",
      "name": "창의인재원식당",
      "address": "경기도 안산시 상록구 한양대학로 55",
      "building": "창의인재원",
      "floor": "1층",
      "latitude": "37.291276",
      "longitude": "126.836354",
      "description": "창의인재원 1층에 위치한 식당입니다.",
      "open_times": {
        "Breakfast": "07:40 ~ 09:00",
        "Lunch": "11:30 ~ 13:20",
        "Dinner": "17:30 ~ 19:00"
      }
    }
  ]
}
```

### 관리자 API (인증 필요)

```bash
# 급식 정보 수집 (관리자용)
curl -X POST "https://에리카밥.com/api/v1/meals/fetch" \
  -H "X-API-Key: your_api_key"
```

**응답 예시:**
```json
{
  "message": "급식 정보 수집이 백그라운드에서 시작되었습니다.",
  "days_ahead": 14
}
```

### 저장된 급식 날짜 조회

```bash
# 모든 식당의 저장된 날짜 조회
curl -X GET "https://에리카밥.com/api/v1/meals/available-dates"

# 특정 식당의 저장된 날짜 조회
curl -X GET "https://에리카밥.com/api/v1/meals/available-dates?restaurant_code=re11"
```

**응답 예시:**
```json
{
  "restaurant_code": "re11",
  "available_dates": [
    "2025-10-01",
    "2025-10-02",
    "2025-10-03",
    "2025-10-04",
    "2025-10-05"
  ],
  "total_count": 5
}
```

### 웹에서 급식 정보 직접 파싱

```bash
# 한양대 웹사이트에서 실시간 파싱
curl -X GET "https://에리카밥.com/api/v1/meals/parse/re12?year=2025&month=10&day=1"
```

**응답 예시:**
```json
{
  "restaurant": "학생식당",
  "date": "2025. 10. 01",
  "day_of_week": "수요일",
  "조식": [],
  "중식": [
    {
      "korean_name": ["스팸마요덮밥", "꼬치어묵국", "고로케&케찹"],
      "tags": ["중식A"],
      "price": "6,500",
      "image_url": "https://...",
      "source": "web_parsing"
    }
  ],
  "석식": []
}
```

### 급식 정보 조회

급식 조회 API를 사용하면 식당과 시간대를 자유롭게 조합할 수 있습니다.

#### 1️⃣ 오늘의 모든 식당, 모든 시간대
```bash
curl -X GET "https://에리카밥.com/api/v1/meals"
```

#### 2️⃣ 특정 날짜의 모든 식당
```bash
curl -X GET "https://에리카밥.com/api/v1/meals?year=2025&month=9&day=15"
```

#### 3️⃣ 오늘의 특정 식당들 (콤마로 구분)
```bash
curl -X GET "https://에리카밥.com/api/v1/meals?restaurant_codes=re11,re12"
```

#### 4️⃣ 오늘의 모든 식당, 특정 시간대만
```bash
curl -X GET "https://에리카밥.com/api/v1/meals?meal_types=중식,석식"
# 또는 숫자 사용 (1=조식, 2=중식, 3=석식)
curl -X GET "https://에리카밥.com/api/v1/meals?meal_types=2,3"
```

#### 5️⃣ 특정 식당의 특정 시간대
```bash
curl -X GET "https://에리카밥.com/api/v1/meals?restaurant_codes=re11,re12&meal_types=중식"
# 또는 숫자 사용
curl -X GET "https://에리카밥.com/api/v1/meals?restaurant_codes=re11,re12&meal_types=2"
```

#### 6️⃣ 특정 날짜, 특정 식당, 특정 시간대
```bash
curl -X GET "https://에리카밥.com/api/v1/meals?year=2025&month=9&day=15&restaurant_codes=re11,re13&meal_types=중식"
# 또는 숫자 사용
curl -X GET "https://에리카밥.com/api/v1/meals?year=2025&month=9&day=15&restaurant_codes=re11,re13&meal_types=2"
```

#### 💡 식사 종류 표기법
- **한글**: 조식, 중식, 석식
- **숫자**: 1 (조식), 2 (중식), 3 (석식)
- **혼용 가능**: `meal_types=조식,2,석식`

**응답 예시:**
```json
{
  "date": "2025. 09. 15",
  "day_of_week": "월요일",
  "restaurants": [
    {
      "restaurant_code": "re11",
      "restaurant_name": "교직원식당",
      "조식": [],
      "중식": [
        {
          "id": 1,
          "korean_name": ["스팸마요덮밥", "꼬치어묵국", "고로케&케찹"],
          "tags": ["중식A"],
          "price": "6,500",
          "image_url": "https://...",
          "average_rating": 4.2,
          "rating_count": 15
        }
      ],
      "석식": []
    },
    {
      "restaurant_code": "re12",
      "restaurant_name": "학생식당",
      "조식": [],
      "중식": [
        {
          "id": 2,
          "korean_name": ["제육볶음", "된장찌개", "김치"],
          "tags": ["중식B"],
          "price": "5,500",
          "image_url": "https://...",
          "average_rating": 4.5,
          "rating_count": 28
        }
      ],
      "석식": []
    }
  ]
}
```

### 평점 등록

```bash
curl -X POST "https://에리카밥.com/api/v1/ratings/" \
  -H "Content-Type: application/json" \
  -d '{
    "meal_id": 1,
    "user_id": "user123",
    "rating": 4.5
  }'
```

### 키워드 리뷰 등록

```bash
curl -X POST "https://에리카밥.com/api/v1/keywords/review" \
  -H "Content-Type: application/json" \
  -d '{
    "meal_id": 1,
    "keyword_id": 1,
    "user_id": "user123"
  }'
```

---

## 🏢 식당 정보

| 코드 | 식당명 | 위치 | 운영시간 |
|------|--------|------|----------|
| `re11` | 교직원식당 | 학생회관 3층 | 중식: 11:30~13:30 |
| `re12` | 학생식당 | 학생회관 2층 | 중식: 11:30~13:30 |
| `re13` | 창의인재원식당 | 창의인재원 1층 | 조식: 07:40~09:00 <br> 중식: 11:30~13:20 <br> 석식: 17:30~19:00 |
| `re15` | 창업보육센터 | 창업보육센터 지하 1층 | 중식: 11:30~13:30 <br> 석식: 17:00~18:30 |

---

## 🏷️ 키워드 카테고리

<table>
<tr>
<th>카테고리</th>
<th>키워드 (15개씩)</th>
</tr>
<tr>
<td><strong>긍정</strong></td>
<td>맛있어요, 양이 많아요, 가성비 좋아요, 신선해요, 따뜻해요, 식감이 좋아요, 건강해요, 담백해요, 재방문 의사 있어요, 추천해요, 푸짐해요, 깔끔해요, 부드러워요, 향이 좋아요, 만족해요</td>
</tr>
<tr>
<td><strong>부정</strong></td>
<td>별로예요, 양이 적어요, 비싸요, 차가워요, 식감이 별로예요, 기름져요, 비추천, 짜요, 싱거워요, 매워요, 달아요, 냄새가 나요, 딱딱해요, 질겨요, 아쉬워요</td>
</tr>
</table>

### 📊 **키워드 통계 기능**
- 메뉴별 상위 N개 키워드 조회
- 카테고리별 키워드 필터링
- 사용자 선택 빈도 기반 순위

---

## 🔧 개발

### 프로젝트 구조

```
meal_api/
├── 📁 app/                     # 메인 애플리케이션
│   ├── 🚀 main.py              # 서버 시작점
│   ├── 📁 api/v1/endpoints/    # API 엔드포인트
│   ├── 📁 services/            # 비즈니스 로직
│   ├── 📁 crud/                # 데이터베이스 작업
│   ├── 📁 models/              # SQLAlchemy 모델
│   ├── 📁 schemas/             # Pydantic 스키마
│   ├── 📁 db/                  # 데이터베이스 연결
│   └── 📁 core/                # 설정
├── 📁 scripts/                 # 초기화 및 유틸리티 스크립트
│   ├── setup_env.py            # 환경변수 설정 (최우선)
│   ├── setup_db.py             # DB 초기화 (필수)
│   ├── fetch_meals.py          # 급식 데이터 수집 (선택)
│   └── README.md               # 스크립트 사용법
├── 📄 requirements.txt         # 의존성 패키지
└── 📖 README.md               # 프로젝트 문서

※ 개인 스크립트는 my_scripts/ 폴더에 보관 (.gitignore에 포함)
```

### 데이터 흐름

```
1. 클라이언트 요청 → API 엔드포인트
2. API → 비즈니스 로직 (Services)
3. Services → 데이터베이스 작업 (CRUD)
4. CRUD → 데이터베이스 (Models)
5. 응답 ← 스키마 검증 ← 데이터베이스
```

### 주요 기술 스택

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: MySQL/MariaDB
- **Scheduler**: APScheduler
- **HTTP Client**: Requests, BeautifulSoup4
- **Deployment**: Uvicorn

---

## 🚀 배포

### Docker 배포 (권장)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5401

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5401"]
```

### Systemd 서비스

```ini
[Unit]
Description=Meal API
After=network.target

[Service]
Type=simple
User=<username>
WorkingDirectory=<your-project-path>
ExecStart=<your-project-path>/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5401
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📈 성능 최적화

- ✅ **데이터베이스 인덱싱**: 빠른 조회를 위한 복합 인덱스
- ✅ **JSON 필드**: 메뉴 정보를 효율적으로 저장
- ✅ **연결 풀링**: SQLAlchemy 연결 풀 사용
- ✅ **캐싱**: 2주치 데이터 미리 수집
- ✅ **비동기 처리**: FastAPI 비동기 지원

---

## 🌐 **라이브 서비스**

### **에리카밥.com** - 한양대 급식 정보 서비스

이 API는 실제로 [**에리카밥.com**](https://에리카밥.com)에서 운영 중입니다!

#### **주요 기능**
- ✅ **실시간 급식 정보**: 한양대 ERICA 4개 식당 메뉴 조회
- ✅ **식당 위치 정보**: 건물명, 층수, GPS 좌표 제공
- ✅ **운영시간 정보**: 조식/중식/석식별 운영시간 제공
- ✅ **평점 시스템**: 메뉴별 평점 및 통계
- ✅ **키워드 리뷰**: 긍정/부정 코멘트 시스템 (30개 키워드)
- ✅ **웹 파싱**: 실시간 웹사이트 파싱 기능
- ✅ **자동 업데이트**: 매일 새벽 2시 자동 데이터 수집
- ✅ **관리자 인증**: API 키 기반 보안 시스템

#### **API 엔드포인트**
- **기본 URL**: `https://에리카밥.com/api/v1`
- **API 문서**: `https://에리카밥.com/docs`
- **식당 목록**: `https://에리카밥.com/api/v1/meals/restaurants`

#### **사용 예시**
```bash
# 오늘의 모든 식당 급식 조회
curl "https://에리카밥.com/api/v1/meals"

# 특정 식당들의 중식만 조회
curl "https://에리카밥.com/api/v1/meals?restaurant_codes=re11,re12&meal_types=중식"
# 또는 숫자 사용 (1=조식, 2=중식, 3=석식)
curl "https://에리카밥.com/api/v1/meals?restaurant_codes=re11,re12&meal_types=2"

# 교직원식당 오늘 메뉴 조회
curl "https://에리카밥.com/api/v1/meals?restaurant_codes=re11"

# 특정 날짜의 특정 식당 조회
curl "https://에리카밥.com/api/v1/meals?year=2025&month=9&day=15&restaurant_codes=re11"

# 식당 정보 조회 (모든 식당)
curl "https://에리카밥.com/api/v1/meals/restaurants"

# 특정 식당 정보 조회
curl "https://에리카밥.com/api/v1/meals/restaurants?restaurant_codes=re13"

# 웹에서 실시간 파싱
curl "https://에리카밥.com/api/v1/meals/parse/re12?year=2025&month=10&day=1"

# 저장된 급식 날짜 조회
curl "https://에리카밥.com/api/v1/meals/available-dates"

# 관리자용 데이터 수집 (인증 필요)
curl -X POST "https://에리카밥.com/api/v1/meals/fetch" \
  -H "X-API-Key: admin_meal_api_2025"

# 메뉴 평점 등록
curl -X POST "https://에리카밥.com/api/v1/ratings/" \
  -H "Content-Type: application/json" \
  -d '{"meal_id": 1, "user_id": "user123", "rating": 4.5}'
```

---

<div align="center">

🌐 **라이브 서비스**: [에리카밥.com](https://에리카밥.com)

</div>


