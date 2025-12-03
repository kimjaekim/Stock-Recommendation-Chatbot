/**
 * Service Worker - 오프라인 지원 & 캐싱
 */

const CACHE_NAME = 'jusic-v2';
const urlsToCache = [
  '/',
  '/css/chat.css',
  '/js/chat.js',
  '/js/portfolio.js',
  '/manifest.json',
  '/icon-192x192.png',
  '/icon-512x512.png'
];

// 설치 이벤트
self.addEventListener('install', event => {
  console.log('[SW] Install');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[SW] Caching app shell');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting();
});

// 활성화 이벤트
self.addEventListener('activate', event => {
  console.log('[SW] Activate');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// Fetch 이벤트 (Network First 전략)
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // 성공하면 캐시에 저장
        if (response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
        }
        return response;
      })
      .catch(() => {
        // 네트워크 실패 시 캐시에서 가져오기
        return caches.match(event.request);
      })
  );
});

// Push 알림 이벤트
self.addEventListener('push', event => {
  console.log('[SW] Push notification received');
  
  const data = event.data ? event.data.json() : {};
  const title = data.title || '안전한 낚시터';
  const options = {
    body: data.body || '새로운 추천 종목이 있습니다!',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    vibrate: [200, 100, 200],
    data: data.url || '/',
    actions: [
      {action: 'open', title: '확인'},
      {action: 'close', title: '닫기'}
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// 알림 클릭 이벤트
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow(event.notification.data || '/')
    );
  }
});

