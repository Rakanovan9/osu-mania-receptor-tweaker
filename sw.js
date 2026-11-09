// Offline cache for the installed app. Bump CACHE when shipping changes to force a refresh.
const CACHE = 'receptor-fixer-v14';
const CORE = [
    './',
    './index.html',
    './manifest.webmanifest',
    './icons/icon.svg',
    './icons/icon-192.png',
    './icons/icon-512.png',
    './vendor/jszip.min.js'
];

self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

// App files: network-first so updates show up immediately, cache as the offline fallback.
// Other origins: stale-while-revalidate.
self.addEventListener('fetch', event => {
    const req = event.request;
    if (req.method !== 'GET') return;
    const sameOrigin = new URL(req.url).origin === self.location.origin;
    event.respondWith(
        caches.open(CACHE).then(async cache => {
            const store = res => {
                if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
                return res;
            };
            if (sameOrigin) {
                try {
                    // 'no-cache' revalidates with the server instead of reusing a stale HTTP-cached copy
                    return store(await fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' }));
                } catch (err) {
                    const cached = await cache.match(req, { ignoreSearch: req.mode === 'navigate' });
                    if (cached) return cached;
                    throw err;
                }
            }
            const cached = await cache.match(req);
            const network = fetch(req).then(store).catch(() => cached);
            return cached || network;
        })
    );
});
