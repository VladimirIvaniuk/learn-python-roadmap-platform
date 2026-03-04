// Service Worker for Learn Python (Vue 3 PWA)
const CACHE_NAME = 'learn-python-v2'

// Only cache the app shell — assets are hashed by Vite so they cache forever
const PRECACHE = ['/']

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', event => {
  const { pathname } = new URL(event.request.url)

  // API and non-GET requests → network only (never cache)
  if (pathname.startsWith('/api/') || event.request.method !== 'GET') {
    event.respondWith(fetch(event.request))
    return
  }

  // Vite-hashed assets (e.g. /assets/index-abc123.js) → cache-first forever
  if (pathname.startsWith('/assets/')) {
    event.respondWith(
      caches.match(event.request).then(cached => cached ?? fetch(event.request).then(res => {
        const clone = res.clone()
        caches.open(CACHE_NAME).then(c => c.put(event.request, clone))
        return res
      }))
    )
    return
  }

  // SPA navigation → network-first, fallback to cache
  event.respondWith(
    fetch(event.request)
      .then(res => {
        if (res.ok) {
          const clone = res.clone()
          caches.open(CACHE_NAME).then(c => c.put(event.request, clone))
        }
        return res
      })
      .catch(() => caches.match(event.request))
  )
})
