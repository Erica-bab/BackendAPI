// Service Worker for 한양대 급식 PWA
const CACHE_NAME = 'erica-meal-v1.0.1';
const STATIC_CACHE = 'erica-meal-static-v1';
const DYNAMIC_CACHE = 'erica-meal-dynamic-v1';

// 캐시할 정적 파일들
const STATIC_FILES = [
  '/',
  '/index.html',
  '/app.js',
  '/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// 설치 이벤트
self.addEventListener('install', (event) => {
  console.log('Service Worker 설치 중...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('정적 파일 캐싱 중...');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker 설치 완료');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker 설치 실패:', error);
      })
  );
});

// 활성화 이벤트
self.addEventListener('activate', (event) => {
  console.log('Service Worker 활성화 중...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('오래된 캐시 삭제:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker 활성화 완료');
        return self.clients.claim();
      })
  );
});

// 네트워크 요청 가로채기
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // API 요청은 네트워크 우선
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // API 응답을 동적 캐시에 저장
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE)
              .then((cache) => {
                cache.put(request, responseClone);
              });
          }
          return response;
        })
        .catch(() => {
          // 네트워크 실패 시 캐시에서 응답
          return caches.match(request);
        })
    );
    return;
  }
  
  // 정적 파일은 캐시 우선
  event.respondWith(
    caches.match(request)
      .then((response) => {
        if (response) {
          return response;
        }
        
        // 캐시에 없으면 네트워크에서 가져오기
        return fetch(request)
          .then((response) => {
            // 유효한 응답인지 확인
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // 응답을 캐시에 저장
            const responseToCache = response.clone();
            caches.open(DYNAMIC_CACHE)
              .then((cache) => {
                cache.put(request, responseToCache);
              });
            
            return response;
          })
          .catch(() => {
            // 오프라인 페이지 표시
            if (request.destination === 'document') {
              return caches.match('/index.html');
            }
          });
      })
  );
});

// 백그라운드 동기화 (선택사항)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('백그라운드 동기화 실행');
    event.waitUntil(
      // 오프라인 상태에서 저장된 데이터를 서버에 동기화
      syncOfflineData()
    );
  }
});

// 푸시 알림 (선택사항)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/static/icons/icon-192x192.png',
      badge: '/static/icons/icon-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: data.primaryKey
      },
      actions: [
        {
          action: 'explore',
          title: '확인하기',
          icon: '/static/icons/icon-96x96.png'
        },
        {
          action: 'close',
          title: '닫기',
          icon: '/static/icons/icon-96x96.png'
        }
      ]
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// 오프라인 데이터 동기화 함수
async function syncOfflineData() {
  try {
    // IndexedDB에서 오프라인 데이터 가져오기
    // 실제 구현에서는 IndexedDB를 사용하여 로컬 데이터 관리
    console.log('오프라인 데이터 동기화 완료');
  } catch (error) {
    console.error('오프라인 데이터 동기화 실패:', error);
  }
}

// 캐시 크기 관리
async function manageCacheSize() {
  const cacheNames = await caches.keys();
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const requests = await cache.keys();
    
    // 캐시가 너무 크면 오래된 항목 삭제
    if (requests.length > 100) {
      const requestsToDelete = requests.slice(0, 50);
      await Promise.all(
        requestsToDelete.map(request => cache.delete(request))
      );
    }
  }
}

// 주기적으로 캐시 크기 관리
setInterval(manageCacheSize, 60000); // 1분마다 실행

// 메시지 이벤트 처리 (자동 업데이트를 위해)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// 주기적으로 업데이트 확인 (5분마다)
self.addEventListener('activate', () => {
  setInterval(() => {
    self.registration.update();
  }, 300000); // 5분마다 업데이트 확인
});
