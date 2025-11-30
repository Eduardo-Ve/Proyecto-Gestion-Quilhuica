const CACHE_NAME = "quilhuica-dynamic-v4";

const CACHE_PATHS = [
  "/",
  "/warehouse/",
  "/application/",
  "/product/",
  "/reports/",
  "/notification/",
  "/dashboard/",
  "/errors/"
];

// Recursos iniciales (precache)
const urlsToPreCache = [
  "/static/style_nav.css",
  "/static/js/navbar.js",
  "/static/base/img/FQ_logo.png",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
  "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
  "https://cdn.jsdelivr.net/npm/sweetalert2@11",
  "https://fonts.googleapis.com/css?family=Montserrat:500&display=swap",
  "/static/pwa/offline.html"
];

// ===============================
// INSTALAR → Precache inicial
// ===============================
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToPreCache))
  );
  self.skipWaiting();
});

// ===============================
// ACTIVAR → Limpieza de versiones viejas
// ===============================
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((key) => key !== CACHE_NAME && caches.delete(key)))
    )
  );
  self.clients.claim();
});

// ===============================
// FETCH → Estrategia “offline-first” con coincidencia de prefijos
// ===============================
self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Ignorar extensiones o servicios del navegador
  if (
    request.url.startsWith("chrome-extension") ||
    request.method !== "GET" ||
    request.url.includes("analytics")
  ) return;

  // Detectar si pertenece a algún prefijo Django
  const matchesCachePath = CACHE_PATHS.some((path) => request.url.includes(path));

  if (matchesCachePath || request.url.includes("/static/")) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request)
          .then((networkResponse) => {
            // Guardar versión nueva del recurso
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, networkResponse.clone());
            });
            return networkResponse;
          })
          .catch(() => {
            // Si no hay red y no está cacheado → offline.html
            if (!cachedResponse && request.headers.get("accept").includes("text/html")) {
              return caches.match("/static/pwa/offline.html");
            }
          });

        // Prioridad al cache (offline first)
        return cachedResponse || fetchPromise;
      })
    );
  }
});
