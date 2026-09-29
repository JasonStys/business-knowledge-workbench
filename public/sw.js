/* @index-begin
 * @symbol variable/parameter: CACHE L11
 * @symbol variable/parameter: SHELL L12
 * @symbol variable/parameter: event L13
 * @symbol variable/parameter: cache L14
 * @symbol variable/parameter: keys L21
 * @symbol variable/parameter: key L25
 * @symbol variable/parameter: url L34
@index-end */
/** Shell-only PWA cache. Symbols/variables: docs/code-index.md. No business/API data is cached. */
const CACHE = "workbench-shell-v1";
const SHELL = ["/offline.html", "/icon-192.png", "/icon-512.png"];
self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter(
              (key) => key.startsWith("workbench-shell-") && key !== CACHE,
            )
            .map((key) => caches.delete(key)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (
    event.request.method !== "GET" ||
    url.origin !== self.location.origin ||
    url.pathname.startsWith("/api/")
  )
    return;
  if (event.request.mode === "navigate")
    event.respondWith(
      fetch(event.request, { cache: "no-store" }).catch(() =>
        caches.match("/offline.html"),
      ),
    );
});
