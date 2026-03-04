const CACHE_NAME = "learn-python-v1";

// Ресурси що кешуються при встановленні
const PRECACHE = [
    "/",
    "/static/css/style.css",
    "/static/js/app.js",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/darcula.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/python/python.min.js",
    "https://cdn.jsdelivr.net/npm/marked/marked.min.js",
];

// API-запити ніколи не кешуємо — тільки network
const API_PATHS = ["/api/"];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (event) => {
    const url = new URL(event.request.url);

    // API-запити — тільки мережа (не кешуємо)
    if (API_PATHS.some((p) => url.pathname.startsWith(p))) {
        event.respondWith(fetch(event.request));
        return;
    }

    // Статика — cache-first, fallback на мережу
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) return cached;
            return fetch(event.request).then((response) => {
                if (!response || response.status !== 200 || response.type === "opaque") {
                    return response;
                }
                const clone = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                return response;
            });
        })
    );
});
