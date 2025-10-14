// API 설정
const API_BASE_URL = 'https://xn--oy2b88bd4n32i.com/api/v1';

// 전역 변수
let availableDates = [];
let currentDateIndex = 0;

// 시간 기반 날짜 결정 함수
function getInitialDate() {
    const now = new Date();
    const koreaTime = new Date(now.getTime() + (9 * 60 * 60 * 1000)); // UTC+9 (한국 시간)
    const hour = koreaTime.getUTCHours();
    
    // 19시 이후면 내일, 그렇지 않으면 오늘
    if (hour >= 19) {
        // 내일 날짜 계산
        const tomorrow = new Date(koreaTime);
        tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
        return tomorrow.toISOString().split('T')[0];
    } else {
        // 오늘 날짜
        return koreaTime.toISOString().split('T')[0];
    }
}

// 현재 시간이 오늘인지 내일인지 확인하는 함수
function isTomorrowMode() {
    const now = new Date();
    const koreaTime = new Date(now.getTime() + (9 * 60 * 60 * 1000));
    const hour = koreaTime.getUTCHours();
    return hour >= 19;
}

// 자정 체크 및 리셋 함수
function checkMidnightReset() {
    const now = new Date();
    const koreaTime = new Date(now.getTime() + (9 * 60 * 60 * 1000));
    const hour = koreaTime.getUTCHours();
    
    // 00시가 되면 자동으로 오늘 날짜로 리셋
    if (hour === 0 && availableDates.length > 0) {
        const today = koreaTime.toISOString().split('T')[0];
        const todayIndex = availableDates.findIndex(date => date === today);
        
        if (todayIndex !== -1) {
            currentDateIndex = todayIndex;
            updateDateDisplay();
            updateNavigationButtons();
            loadMeals();
            console.log('자정 리셋: 오늘 날짜로 변경됨');
        }
    }
}

// 사용 가능한 날짜 목록 로드
async function loadAvailableDates() {
    try {
        const response = await fetch(`${API_BASE_URL}/meals/available-dates`);
        if (!response.ok) {
            throw new Error('날짜 목록을 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        availableDates = data.available_dates || [];
        
        // 날짜를 오래된 순으로 정렬 (과거 → 미래)
        availableDates.sort((a, b) => new Date(a) - new Date(b));
        
        // 시간 기반으로 초기 날짜 결정 (19시 이후면 내일, 아니면 오늘)
        const targetDate = getInitialDate();
        console.log('초기 날짜 설정:', targetDate, '내일 모드:', isTomorrowMode());
        
        // 1. 먼저 타겟 날짜가 있는지 확인
        currentDateIndex = availableDates.findIndex(date => date === targetDate);
        
        if (currentDateIndex === -1) {
            // 2. 타겟 날짜가 없으면 타겟 날짜보다 이전 날짜 중 가장 최근 날짜 찾기
            // 배열이 과거→미래 순으로 정렬되어 있으므로, 타겟 날짜보다 작거나 같은 날짜 중 마지막 인덱스 찾기
            let closestIndex = -1;
            for (let i = availableDates.length - 1; i >= 0; i--) {
                if (availableDates[i] <= targetDate) {
                    closestIndex = i;
                    break;
                }
            }
            
            if (closestIndex !== -1) {
                currentDateIndex = closestIndex;
            } else {
                // 3. 모든 날짜가 미래 날짜면 가장 최근 날짜
                currentDateIndex = availableDates.length - 1;
            }
        }
        
        // 인덱스가 유효한지 확인
        if (currentDateIndex >= availableDates.length) {
            currentDateIndex = 0;
        }
        
        updateDateDisplay();
        updateNavigationButtons();
        
    } catch (error) {
        console.error('Error loading dates:', error);
        // 실패 시 오늘 날짜 사용
        availableDates = [];
        currentDateIndex = 0;
        updateDateDisplay();
        updateNavigationButtons();
    }
}

// 날짜 표시 업데이트
function updateDateDisplay() {
    const dateDisplay = document.getElementById('dateDisplay');
    const todayBtn = document.querySelector('.today-btn');
    
    if (availableDates.length === 0 || !availableDates[currentDateIndex]) {
        // 사용 가능한 날짜가 없으면 오늘 날짜 표시 (한국 시간 기준)
        const now = new Date();
        const koreaTime = new Date(now.getTime() + (9 * 60 * 60 * 1000)); // UTC+9 (한국 시간)
        const year = koreaTime.getUTCFullYear();
        const month = String(koreaTime.getUTCMonth() + 1).padStart(2, '0');
        const day = String(koreaTime.getUTCDate()).padStart(2, '0');
        
        // 요일 구하기
        const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
        const weekday = weekdays[koreaTime.getUTCDay()];
        
        dateDisplay.textContent = `${year}. ${month}. ${day} (${weekday})`;
        
        // 오늘 버튼 강조
        if (todayBtn) {
            todayBtn.classList.add('today-active');
        }
        return;
    }
    
    try {
        const selectedDate = new Date(availableDates[currentDateIndex] + 'T00:00:00');
        const now = new Date();
        const koreaTime = new Date(now.getTime() + (9 * 60 * 60 * 1000)); // UTC+9 (한국 시간)
        const today = new Date(koreaTime.getUTCFullYear(), koreaTime.getUTCMonth(), koreaTime.getUTCDate());
        selectedDate.setHours(0, 0, 0, 0);
        
        const year = selectedDate.getFullYear();
        const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
        const day = String(selectedDate.getDate()).padStart(2, '0');
        
        // 요일 구하기
        const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
        const weekday = weekdays[selectedDate.getDay()];
        
        const dateStr = `${year}. ${month}. ${day}`;
        const dateWithWeekday = `${dateStr} (${weekday})`;
        
        // 항상 날짜만 표시
        dateDisplay.textContent = dateWithWeekday;
        
        // 오늘 날짜인지 확인하여 오늘 버튼 강조
        // 19시 이후에는 내일 날짜도 하이라이트 표시
        const isToday = selectedDate.getTime() === today.getTime();
        const isTomorrow = isTomorrowMode() && selectedDate.getTime() === (new Date(today.getTime() + 24 * 60 * 60 * 1000)).getTime();
        
        if (isToday || isTomorrow) {
            if (todayBtn) {
                todayBtn.classList.add('today-active');
                // 내일 모드일 때는 버튼 텍스트도 변경
                if (isTomorrow) {
                    todayBtn.textContent = '내일';
                } else {
                    todayBtn.textContent = '오늘';
                }
            }
        } else {
            if (todayBtn) {
                todayBtn.classList.remove('today-active');
                todayBtn.textContent = '오늘';
            }
        }
        
    } catch (error) {
        console.error('Error in updateDateDisplay:', error);
        // 오류 발생 시 오늘 날짜로 폴백 (한국 시간 기준)
        const now = new Date();
        const koreaTime = new Date(now.getTime() + (9 * 60 * 60 * 1000)); // UTC+9 (한국 시간)
        const year = koreaTime.getUTCFullYear();
        const month = String(koreaTime.getUTCMonth() + 1).padStart(2, '0');
        const day = String(koreaTime.getUTCDate()).padStart(2, '0');
        
        // 요일 구하기
        const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
        const weekday = weekdays[koreaTime.getUTCDay()];
        
        dateDisplay.textContent = `${year}. ${month}. ${day} (${weekday})`;
        
        // 오늘 버튼 강조
        if (todayBtn) {
            todayBtn.classList.add('today-active');
        }
    }
}

// 날짜 네비게이션 버튼 상태 업데이트
function updateNavigationButtons() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (availableDates.length === 0) {
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        return;
    }
    
    // 이전 버튼 (더 최근 날짜로)
    prevBtn.disabled = (currentDateIndex <= 0);
    
    // 다음 버튼 (더 과거 날짜로)
    nextBtn.disabled = (currentDateIndex >= availableDates.length - 1);
}

// 날짜 네비게이션
function navigateDate(direction) {
    if (availableDates.length === 0) return;
    
    const newIndex = currentDateIndex + direction;
    
    if (newIndex >= 0 && newIndex < availableDates.length) {
        currentDateIndex = newIndex;
        updateDateDisplay();
        updateNavigationButtons();
        loadMeals();
    }
}

// 현재 날짜 표시 (더 이상 사용하지 않음 - 헤더에서 제거됨)
function displayCurrentDate(date) {
    // 헤더에서 날짜 표시를 제거했으므로 이 함수는 더 이상 사용하지 않음
    return;
}

// 식사 종류 선택 (슬라이더 이동)
function selectMeal(button) {
    const allButtons = document.querySelectorAll('.filter-btn');
    const sliderBg = document.querySelector('.slider-bg');
    const index = button.getAttribute('data-index');
    
    // 모든 버튼 비활성화
    allButtons.forEach(btn => btn.classList.remove('active'));
    
    // 클릭된 버튼만 활성화
    button.classList.add('active');
    
    // 슬라이더 배경 이동 및 표시
    sliderBg.className = 'slider-bg';
    sliderBg.classList.add(`position-${index}`);
    sliderBg.style.opacity = '1'; // 슬라이더 보이기
    
    // 데이터 로드
    loadMeals();
}

// 선택된 식사 종류 가져오기
function getSelectedMealTypes() {
    const activeButton = document.querySelector('.filter-btn.active');
    
    if (!activeButton) {
        return []; // 모두 표시 (전체 보기)
    }
    
    const mealType = activeButton.getAttribute('data-meal');
    
    // 숫자로 변환 (조식=1, 중식=2, 석식=3)
    if (mealType === '조식') return ['1'];
    else if (mealType === '중식') return ['2'];
    else if (mealType === '석식') return ['3'];
    
    return [];
}

// 식사 종류 아이콘
function getMealIcon(mealType) {
    const icons = {
        '조식': '☕',
        '중식': '🍚',
        '석식': '🌙'
    };
    return icons[mealType] || '🍽️';
}

// 식사 종류 클래스
function getMealClass(mealType) {
    const classes = {
        '조식': 'breakfast',
        '중식': 'lunch',
        '석식': 'dinner'
    };
    return classes[mealType] || '';
}

// 급식 데이터 로드
async function loadMeals() {
    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = '<div class="loading">급식 정보를 불러오는 중...</div>';

    try {
        // URL 파라미터 구성
        const params = new URLSearchParams();
        
        // 선택된 날짜 가져오기
        if (availableDates.length > 0 && availableDates[currentDateIndex]) {
            const dateValue = availableDates[currentDateIndex];
            const [year, month, day] = dateValue.split('-');
            params.append('year', year);
            params.append('month', parseInt(month, 10));
            params.append('day', parseInt(day, 10));
        }
        
        // 선택된 식사 종류 추가
        const selectedMealTypes = getSelectedMealTypes();
        if (selectedMealTypes.length > 0) {
            // 특정 식사 종류가 선택된 경우만 파라미터 추가
            params.append('meal_types', selectedMealTypes.join(','));
        }
        // 선택된 것이 없으면 전체 보기 (파라미터 없음)
        
        const url = `${API_BASE_URL}/meals${params.toString() ? '?' + params.toString() : ''}`;
        console.log('API 호출:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('급식 정보를 불러올 수 없습니다.');
        }

        const data = await response.json();
        displayCurrentDate();
        displayMeals(data);
    } catch (error) {
        console.error('Error:', error);
        contentDiv.innerHTML = `
            <div class="error">
                ⚠️ 급식 정보를 불러오는 중 오류가 발생했습니다.<br>
                잠시 후 다시 시도해주세요.<br>
                <small style="margin-top: 8px; display: block; opacity: 0.8;">
                    ${error.message}
                </small>
            </div>
        `;
    }
}

// 급식 데이터 표시
function displayMeals(data) {
    const contentDiv = document.getElementById('content');
    
    if (!data.restaurants || data.restaurants.length === 0) {
        contentDiv.innerHTML = '<div class="no-meals">이 날짜에는 급식 정보가 없습니다.</div>';
        return;
    }

    let html = '';

    data.restaurants.forEach(restaurant => {
        html += `
            <div class="restaurant-card">
                <div class="restaurant-header">
                    <div class="restaurant-name">${restaurant.restaurant_name}</div>
                    <div class="restaurant-code">${restaurant.restaurant_code.toUpperCase()}</div>
                </div>
                <div class="meals-section">
        `;

        // 식사 종류별로 표시 (응답에 포함된 종류만)
        const mealTypes = ['조식', '중식', '석식'];
        let hasAnyMeal = false;

        mealTypes.forEach(mealType => {
            // 식당 데이터에 해당 식사 종류 키가 존재하고, 데이터가 있는 경우만 표시
            if (restaurant.hasOwnProperty(mealType) && restaurant[mealType] && restaurant[mealType].length > 0) {
                hasAnyMeal = true;
                html += `
                    <div class="meal-type">
                        <div class="meal-type-header">
                            <div class="meal-type-icon ${getMealClass(mealType)}">
                                ${getMealIcon(mealType)}
                            </div>
                            <div class="meal-type-title">${mealType}</div>
                        </div>
                `;

                restaurant[mealType].forEach(meal => {
                    html += `
                        <div class="meal-item">
                    `;

                    // 태그 표시
                    if (meal.tags && meal.tags.length > 0) {
                        html += '<div class="meal-tags">';
                        meal.tags.forEach(tag => {
                            html += `<span class="meal-tag">${tag}</span>`;
                        });
                        html += '</div>';
                    }

                    // 메뉴 표시
                    html += '<div class="meal-menu">';
                    if (meal.korean_name && meal.korean_name.length > 0) {
                        meal.korean_name.forEach(item => {
                            html += `<div class="menu-item">${item}</div>`;
                        });
                    }
                    html += '</div>';

                    // 가격 표시
                    if (meal.price) {
                        html += `<div class="meal-price">${meal.price}원</div>`;
                    }

                    html += `
                        </div>
                    `;
                });

                html += `
                    </div>
                `;
            }
        });

        if (!hasAnyMeal) {
            // 선택한 식사 종류에 데이터가 없을 때
            const selectedTypes = getSelectedMealTypes();
            let message = '이 날짜에는 급식이 없습니다.';
            if (selectedTypes.length > 0) {
                message = '선택한 시간대에 급식이 없습니다.';
            }
            html += `<div class="no-meals">${message}</div>`;
        }

        html += `
                </div>
            </div>
        `;
    });

    contentDiv.innerHTML = html;
}

// 오늘로 돌아가기
function resetToToday() {
    try {
        if (availableDates.length === 0) {
            // 사용 가능한 날짜가 없으면 오늘 날짜로 표시
            updateDateDisplay();
            loadMeals();
            return;
        }
        
        // 시간 기반으로 타겟 날짜 결정 (19시 이후면 내일, 아니면 오늘)
        const targetDate = getInitialDate();
        console.log('resetToToday - 타겟 날짜:', targetDate, '내일 모드:', isTomorrowMode());
        console.log('resetToToday - 사용 가능한 날짜들:', availableDates);
        console.log('resetToToday - 현재 인덱스:', currentDateIndex);
        
        // 1. 먼저 타겟 날짜가 있는지 확인
        const targetIndex = availableDates.findIndex(date => date === targetDate);
        console.log('resetToToday - 타겟 날짜 인덱스:', targetIndex);
        
        if (targetIndex !== -1) {
            currentDateIndex = targetIndex;
            console.log('resetToToday - 타겟 날짜 발견, 인덱스 설정:', currentDateIndex);
        } else {
            // 2. 타겟 날짜가 없으면 타겟 날짜보다 이전 날짜 중 가장 최근 날짜 찾기
            // 배열이 과거→미래 순으로 정렬되어 있으므로, 타겟 날짜보다 작거나 같은 날짜 중 마지막 인덱스 찾기
            let closestIndex = -1;
            for (let i = availableDates.length - 1; i >= 0; i--) {
                console.log(`resetToToday - 비교: ${availableDates[i]} <= ${targetDate} ? ${availableDates[i] <= targetDate}`);
                if (availableDates[i] <= targetDate) {
                    closestIndex = i;
                    break;
                }
            }
            
            if (closestIndex !== -1) {
                currentDateIndex = closestIndex;
                console.log('resetToToday - 가장 가까운 날짜 찾음, 인덱스:', currentDateIndex);
            } else {
                // 3. 모든 날짜가 미래 날짜면 가장 최근 날짜
                currentDateIndex = availableDates.length - 1;
                console.log('resetToToday - 모든 날짜가 미래, 마지막 인덱스:', currentDateIndex);
            }
        }
        
        // 인덱스 유효성 확인
        if (currentDateIndex >= availableDates.length) {
            currentDateIndex = 0;
            console.log('resetToToday - 인덱스 범위 초과, 0으로 설정');
        }
        
        console.log('resetToToday - 최종 인덱스:', currentDateIndex, '선택된 날짜:', availableDates[currentDateIndex]);
        
        updateDateDisplay();
        updateNavigationButtons();
        
        // 오늘로 돌아갈 때도 중식 자동 선택
        const lunchButton = document.querySelector('[data-meal="중식"]');
        if (lunchButton) {
            selectMeal(lunchButton);
        }
        
        loadMeals();
        
    } catch (error) {
        console.error('Error in resetToToday:', error);
        // 오류 발생 시 기본 동작
        loadMeals();
    }
}

// 페이지 로드 시 실행
async function initApp() {
    try {
        await loadAvailableDates();
        
        // 첫 로딩 시 중식 자동 선택
        const lunchButton = document.querySelector('[data-meal="중식"]');
        if (lunchButton) {
            selectMeal(lunchButton);
        }
        
        // 자정 체크 타이머 시작
        startMidnightCheck();
        
        loadMeals();
    } catch (error) {
        console.error('Error initializing app:', error);
        // 초기화 실패 시에도 기본 동작 수행
        loadMeals();
    }
}

// DOM이 로드된 후 초기화
document.addEventListener('DOMContentLoaded', initApp);

// 자정 체크를 위한 타이머 설정 (1분마다 체크)
let midnightCheckInterval;

function startMidnightCheck() {
    // 기존 타이머가 있으면 제거
    if (midnightCheckInterval) {
        clearInterval(midnightCheckInterval);
    }
    
    // 1분마다 자정 체크
    midnightCheckInterval = setInterval(checkMidnightReset, 60000);
    console.log('자정 체크 타이머 시작됨');
}

function stopMidnightCheck() {
    if (midnightCheckInterval) {
        clearInterval(midnightCheckInterval);
        midnightCheckInterval = null;
        console.log('자정 체크 타이머 중지됨');
    }
}

// 페이지 가시성 변경 시 자동 새로고침
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // 페이지가 다시 보이면 자정 체크 타이머 재시작
        startMidnightCheck();
        
        loadAvailableDates().then(() => {
            loadMeals();
        }).catch(error => {
            console.error('Error refreshing data:', error);
            loadMeals(); // 날짜 로드 실패해도 급식 데이터는 로드
        });
    } else {
        // 페이지가 숨겨지면 타이머 중지 (배터리 절약)
        stopMidnightCheck();
    }
});

