// Offline cache so plans, specs and checklists open on site with no reception.
var CACHE = "ob-box-v1";
var FILES = [
  "index.html", "my-build.html", "compliance.html", "gateways.html", "contracts.html",
  "tenders.html", "guides.html", "faq.html",
  "css/base.css", "css/ob.css", "js/app.js", "js/my-build.js", "js/tender-tool.js",
  "assets/logo.svg", "assets/favicon.svg", "manifest.webmanifest"
];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }));
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }));
  self.clients.claim();
});

// Network first, fall back to cache when offline.
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request).then(function (res) {
      var copy = res.clone();
      caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
      return res;
    }).catch(function () { return caches.match(e.request); })
  );
});
