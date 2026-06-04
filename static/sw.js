const CACHE = 'k-lab-v3';
const OFFLINE_URL = '/static/offline.html';

const PRECACHE_URLS = [
  '/',
  '/hangul/',
  '/library/',
  '/review/',
  '/quiz/',
  '/vocabulary/',
  '/grammar/',
  '/progress/',
  '/accounts/profile/',
  '/accounts/achievements/',
  OFFLINE_URL,
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache =>
      cache.addAll(PRECACHE_URLS).catch(() => {
        PRECACHE_URLS.forEach(url => {
          fetch(url).then(r => { if (r.ok) cache.put(url, r); }).catch(() => {});
        });
      })
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  const { request } = e;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    e.respondWith(
      fetch(request).catch(() => caches.match(request))
    );
    return;
  }

  const path = url.pathname;

  if (path.startsWith('/admin/') || path.startsWith('/accounts/login') || path.startsWith('/accounts/register')) {
    return;
  }

  if (path.startsWith('/static/')) {
    e.respondWith(
      caches.match(request).then(cached => cached || fetchAndCache(request))
    );
    return;
  }

  if (path.startsWith('/hangul/tts') || path.startsWith('/library/api')) {
    e.respondWith(
      fetch(request).catch(() => new Response(null, { status: 503 }))
    );
    return;
  }

  if (request.destination === 'document') {
    e.respondWith(
      fetch(request)
        .then(r => {
          if (r.ok) {
            caches.open(CACHE).then(cache => cache.put(request, r.clone()));
          }
          return r;
        })
        .catch(() =>
          caches.match(request).then(cached =>
            cached || caches.match(OFFLINE_URL).then(offline =>
              offline || new Response('Офлайн', { status: 503, headers: { 'Content-Type': 'text/plain' } })
            )
          )
        )
    );
    return;
  }

  e.respondWith(
    fetch(request)
      .then(r => {
        if (r.ok) caches.open(CACHE).then(cache => cache.put(request, r.clone()));
        return r;
      })
      .catch(() => caches.match(request))
  );
});

function fetchAndCache(request) {
  return fetch(request).then(r => {
    if (r.ok) {
      caches.open(CACHE).then(cache => cache.put(request, r.clone()));
    }
    return r;
  });
}
