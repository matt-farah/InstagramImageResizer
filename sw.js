// sw.js 
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('imgproc-cache').then(cache => {
      return cache.addAll([
        './',
        './index.html',
        './about.html',
        './faq.html',
        './style.css',
        './webImageProcess.py',
        './manifest.json',
        './images/icon-192.png',
        './images/icon-512.png',
        './images/profilePhoto.jpg',
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
