const CACHE = 'k-lab-v2';
const urls = [
  '/',
  '/hangul/',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(urls))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  
  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/accounts/')) {
    return;
  }

  const isStatic = e.request.destination === 'style' || 
                   e.request.destination === 'script' || 
                   e.request.destination === 'image' || 
                   e.request.destination === 'font';

  if (isStatic) {
    e.respondWith(
      caches.match(e.request).then(cachedResponse => {
        const fetchPromise = fetch(e.request).then(networkResponse => {
          if (networkResponse.ok) {
            caches.open(CACHE).then(cache => cache.put(e.request, networkResponse.clone()));
          }
          return networkResponse;
        }).catch(() => null);
        return cachedResponse || fetchPromise;
      })
    );
  } else {
    e.respondWith(
      fetch(e.request)
        .then(r => {
          if (r.ok) {
            caches.open(CACHE).then(c => c.put(e.request, r.clone()));
          }
          return r;
        })
        .catch(() => caches.match(e.request))
    );
  }
});
